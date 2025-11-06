import sys
import os
from pathlib import Path
from typing import List

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.sql import quoted_name
import hashlib
import unicodedata

from config import DatabaseConfig
from utils.schema_generator import infer_mysql_type


def sanitize_table_name_from_file(csv_path: Path) -> str:
	"""Return table name equal to CSV filename without extension (keep spaces/parens)."""
	return csv_path.stem


def _normalize_identifier(name: str) -> str:
	# Remove accents, keep ASCII
	name_ascii = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode('ascii')
	# Replace invalid chars with underscores
	safe = []
	for ch in name_ascii:
		if ch.isalnum() or ch == '_':
			safe.append(ch)
		else:
			safe.append('_')
	safe_name = ''.join(safe)
	# Collapse multiple underscores
	while '__' in safe_name:
		safe_name = safe_name.replace('__', '_')
	# Must not start with digit for comfort; prefix underscore if so
	if safe_name and safe_name[0].isdigit():
		safe_name = '_' + safe_name
	return safe_name

def _truncate_identifier(name: str, max_len: int = 64, suffix_seed: str | None = None) -> str:
	if len(name) <= max_len:
		return name
	# Use a short hash to preserve uniqueness when truncated
	h = hashlib.sha1((suffix_seed or name).encode('utf-8')).hexdigest()[:8]
	keep = max_len - 1 - len(h)  # one underscore + hash
	return f"{name[:keep]}_{h}"

def build_column_mapping(columns: List[str]) -> dict:
	mapping = {}
	used = set()
	for original in columns:
		base = _normalize_identifier(original)
		candidate = _truncate_identifier(base, 64, suffix_seed=original)
		# Ensure uniqueness within the table
		if candidate in used:
			candidate = _truncate_identifier(f"{candidate}_dup", 64, suffix_seed=original + '_dup')
		used.add(candidate)
		mapping[original] = candidate
	return mapping

def generate_create_table_sql(df: pd.DataFrame, table_name: str, col_map: dict) -> str:
	"""Generate CREATE TABLE with quoted table/column names and inferred MySQL types."""
	schema_lines: List[str] = []
	schema_lines.append(f"CREATE TABLE IF NOT EXISTS `{table_name}` (")
	# Columns
	for i, col in enumerate(df.columns):
		safe_col = col_map[col]
		mysql_type = infer_mysql_type(df[col], col)
		nullable = "NULL" if df[col].isna().any() else "NOT NULL"
		comma = "," if i < len(df.columns) - 1 else ""
		schema_lines.append(f"  `{safe_col}` {mysql_type} {nullable}{comma}")
	schema_lines.append(") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")
	return "\n".join(schema_lines)


def _ensure_global_report_table(conn):
	"""Create a single global report table `upload_reports` if it doesn't exist."""
	report_table = "upload_reports"
	create_sql = f"""
	CREATE TABLE IF NOT EXISTS `{report_table}` (
	  `report_id` BIGINT AUTO_INCREMENT PRIMARY KEY,
	  `table_name` VARCHAR(255) NOT NULL,
	  `source_file` VARCHAR(1000) NOT NULL,
	  `file_size_bytes` BIGINT,
	  `rows_read` BIGINT DEFAULT 0,
	  `chunksize` INT,
	  `sample_rows` INT,
	  `status` VARCHAR(50) DEFAULT 'COMPLETED',
	  `error_message` TEXT,
	  `started_ts` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	  `completed_ts` TIMESTAMP NULL,
	  `duration_seconds` DECIMAL(12,2)
	) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
	"""
	conn.execute(text(create_sql))
	return report_table


def create_table_from_csv(engine, csv_path: Path, sample_rows: int = 1000, chunksize: int = 5000):
	"""Create a table matching the CSV and load its data in chunks."""
	print(f"\nProcessing: {csv_path}")
	if not csv_path.exists():
		raise FileNotFoundError(f"CSV not found: {csv_path}")

	table_name = sanitize_table_name_from_file(csv_path)
    # Read a sample to infer schema
	print("  Reading sample to infer schema...")
	df_sample = pd.read_csv(csv_path, nrows=sample_rows, low_memory=False)
	print(f"  Sample loaded: {len(df_sample)} rows, {len(df_sample.columns)} cols")

	# Create table if not exists
	col_map = build_column_mapping(list(df_sample.columns))
	create_sql = generate_create_table_sql(df_sample, table_name, col_map)
	with engine.begin() as conn:
		print("  Recreating table to match current CSV structure...")
		conn.execute(text(f"DROP TABLE IF EXISTS `{table_name}`"))
		conn.execute(text(create_sql))
		# Ensure global report table exists
		report_table = _ensure_global_report_table(conn)

	# Prepare report metrics
	file_size = csv_path.stat().st_size
	from time import perf_counter
	start = perf_counter()

	# Load full CSV in chunks
	print("  Loading full data in chunks...")
	total = 0
	for chunk in pd.read_csv(csv_path, chunksize=chunksize, low_memory=False):
		# Use quoted_name to ensure pandas/sqlalchemy quote table with spaces/parens
		name = quoted_name(table_name, quote=True)
		# Rename columns to safe DB identifiers
		chunk = chunk.rename(columns=col_map)
		rows = chunk.to_sql(name=name, con=engine, if_exists='append', index=False)
		# pandas returns None; count chunk rows
		inserted = len(chunk)
		total += inserted
		print(f"    +{inserted} rows (total {total})")
	print(f"  Done: {total} rows inserted into `{table_name}`")

	# Write upload report
	duration = perf_counter() - start
	with engine.begin() as conn:
		report_table = "upload_reports"
		conn.execute(
			text(
				f"""
				INSERT INTO `{report_table}`
				(table_name, source_file, file_size_bytes, rows_read, chunksize, sample_rows, status, completed_ts, duration_seconds)
				VALUES (:table_name, :source_file, :file_size_bytes, :rows_read, :chunksize, :sample_rows, 'COMPLETED', CURRENT_TIMESTAMP, :duration)
				"""
			),
			{
				"table_name": table_name,
				"source_file": str(csv_path),
				"file_size_bytes": int(file_size),
				"rows_read": int(total),
				"chunksize": int(chunksize),
				"sample_rows": int(sample_rows),
				"duration": float(round(duration, 2)),
			},
		)


def main():
	import argparse

	parser = argparse.ArgumentParser(description='Create 4 MySQL tables from 4 CSV files (table names = CSV filenames)')
	parser.add_argument('--path', type=str, default='fending_data', help='Folder containing the 4 CSV files')
	parser.add_argument('--cloud', action='store_true', help='Use cloud DB from config')
	parser.add_argument('--chunksize', type=int, default=5000, help='Insert chunksize')
	parser.add_argument('--sample', type=int, default=1000, help='Rows for schema inference')
	args = parser.parse_args()

	base = Path(args.path)
	if not base.exists():
		print(f"Base folder not found: {base}")
		sys.exit(1)

	# Expect 4 CSVs in directory
	csvs = sorted([p for p in base.glob('*.csv')])
	if len(csvs) == 0:
		print(f"No CSV files found in {base}")
		sys.exit(1)

	print("Connecting to database...")
	engine = create_engine(DatabaseConfig.get_connection_string(args.cloud))

	for csv_path in csvs:
		try:
			create_table_from_csv(engine, csv_path, sample_rows=args.sample, chunksize=args.chunksize)
		except Exception as e:
			print(f"ERROR processing {csv_path.name}: {e}")
			import traceback
			traceback.print_exc()
			# continue to next file
			continue

	print("\nAll CSVs processed.")


if __name__ == '__main__':
	main()
