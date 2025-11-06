"""
Monthly CSV Loader (4-table mode)

Loads CSV files for a given month (if specified) or all CSVs in a path.
For each CSV, it (re)creates a table with the same name as the file (without .csv)
and loads the data using the same logic as create_tables_from_csvs.py.

Usage examples:
  python monthly_loader.py --path "fending_data" --month 2025-08
  python monthly_loader.py --path "fending_data"
  python monthly_loader.py --path "fending_data" --cloud --chunksize 5000 --sample 1000
"""

from pathlib import Path
from datetime import date, datetime
import sys
import re
import argparse

from sqlalchemy import create_engine

from config import DatabaseConfig
from create_tables_from_csvs import create_table_from_csv


def parse_month_arg(month_str: str) -> date:
    """Parse YYYY-MM to date(day=1)."""
    try:
        return datetime.strptime(month_str, "%Y-%m").date().replace(day=1)
    except ValueError:
        raise ValueError("Invalid --month. Use YYYY-MM (e.g., 2025-08)")


def path_matches_month(path: Path, target_month: date) -> bool:
    """Return True if the path contains the month pattern (YYYY-MM or YYYYMM)."""
    s = str(path)
    y = target_month.year
    m = target_month.month
    patterns = [
        rf"{y}-{m:02d}",
        rf"{y}{m:02d}",
        rf"{y}_{m:02d}",
    ]
    return any(re.search(p, s) for p in patterns)


def discover_csvs(base: Path, target_month: date | None) -> list[Path]:
    csvs = sorted(base.rglob("*.csv"))
    if target_month is None:
        return csvs
    filtered = [p for p in csvs if path_matches_month(p, target_month)]
    # Fallback: if no match by path, return all (user may have flat folder)
    return filtered if filtered else csvs


def main():
    parser = argparse.ArgumentParser(description="Monthly CSV loader (4-table mode)")
    parser.add_argument("--path", type=str, default="fending_data", help="Base path to search for CSVs")
    parser.add_argument("--month", type=str, help="Month to process (YYYY-MM). If omitted, process all CSVs")
    parser.add_argument("--cloud", action="store_true", help="Use cloud DB from config")
    parser.add_argument("--chunksize", type=int, default=5000, help="Insert chunksize")
    parser.add_argument("--sample", type=int, default=1000, help="Rows to sample for schema inference")
    args = parser.parse_args()

    base = Path(args.path)
    if not base.exists():
        print(f"Base folder not found: {base}")
        sys.exit(1)

    target_month = parse_month_arg(args.month) if args.month else None
    all_csvs = discover_csvs(base, target_month)
    if not all_csvs:
        print("No CSV files found to process.")
        sys.exit(0)

    print(f"Connecting to database ({'cloud' if args.cloud else 'local'}) ...")
    engine = create_engine(DatabaseConfig.get_connection_string(args.cloud))

    processed = 0
    for csv_path in all_csvs:
        try:
            create_table_from_csv(
                engine,
                csv_path,
                sample_rows=args.sample,
                chunksize=args.chunksize,
            )
            processed += 1
        except Exception as e:
            print(f"ERROR processing {csv_path.name}: {e}")
            import traceback
            traceback.print_exc()
            continue

    print(f"\nCompleted. Files processed: {processed}/{len(all_csvs)}")


if __name__ == "__main__":
    main()


