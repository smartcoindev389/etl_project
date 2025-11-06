import pandas as pd
from pathlib import Path
import sys

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from utils.schema_generator import infer_mysql_type
import hashlib
import unicodedata

def _normalize_identifier(name: str) -> str:
	name_ascii = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode('ascii')
	safe = []
	for ch in name_ascii:
		if ch.isalnum() or ch == '_':
			safe.append(ch)
		else:
			safe.append('_')
	safe_name = ''.join(safe)
	while '__' in safe_name:
		safe_name = safe_name.replace('__', '_')
	if safe_name and safe_name[0].isdigit():
		safe_name = '_' + safe_name
	return safe_name

def _truncate_identifier(name: str, max_len: int = 64, suffix_seed: str | None = None) -> str:
	if len(name) <= max_len:
		return name
	h = hashlib.sha1((suffix_seed or name).encode('utf-8')).hexdigest()[:8]
	keep = max_len - 1 - len(h)
	return f"{name[:keep]}_{h}"


def generate_sql_for_csv(csv: Path, out_dir: Path, sample_rows: int = 2000) -> Path:
	if not csv.exists():
		raise FileNotFoundError(csv)
	print(f"Generating schema for: {csv.name}")
	df = pd.read_csv(csv, nrows=sample_rows, low_memory=False)
	table_name = csv.stem
	lines = []
	lines.append(f"-- Auto-generated from {csv.name}")
	lines.append("-- Inferred from first %d rows" % sample_rows)
	lines.append("")
	# Build safe column names mapping (to keep <=64 and ASCII)
	mapping = {}
	used = set()
	for c in df.columns:
		base = _normalize_identifier(c)
		cand = _truncate_identifier(base, 64, suffix_seed=c)
		if cand in used:
			cand = _truncate_identifier(f"{cand}_dup", 64, suffix_seed=c + '_dup')
		used.add(cand)
		mapping[c] = cand

	lines.append(f"CREATE TABLE IF NOT EXISTS `{table_name}` (")
	for i, col in enumerate(df.columns):
		safe_col = mapping[col]
		mysql_type = infer_mysql_type(df[col], col)
		nullable = "NULL" if df[col].isna().any() else "NOT NULL"
		comma = "," if i < len(df.columns) - 1 else ""
		lines.append(f"  `{safe_col}` {mysql_type} {nullable}{comma}")
	lines.append(") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")
	sql = "\n".join(lines)
	out_file = out_dir / f"{table_name}.sql"
	out_file.write_text(sql, encoding='utf-8')
	print(f"  -> wrote {out_file}")
	return out_file


def main():
	import argparse
	parser = argparse.ArgumentParser(description='Generate CREATE TABLE SQL files from CSVs in a folder')
	parser.add_argument('--path', type=str, default='fending_data', help='Folder containing CSV files')
	parser.add_argument('--sample', type=int, default=2000, help='Rows to sample for type inference')
	parser.add_argument('--out', type=str, default='database', help='Output folder for .sql files')
	args = parser.parse_args()

	base = Path(args.path)
	out_dir = Path(args.out)
	out_dir.mkdir(exist_ok=True)

	if not base.exists():
		print(f"Base folder not found: {base}")
		return

	# Discover all CSVs dynamically
	csvs = sorted(base.glob('*.csv'))
	if not csvs:
		print(f"No CSV files found in {base}")
		return

	for csv in csvs:
		try:
			generate_sql_for_csv(csv, out_dir, sample_rows=args.sample)
		except Exception as e:
			print(f"ERROR for {csv.name}: {e}")


if __name__ == '__main__':
	main()
