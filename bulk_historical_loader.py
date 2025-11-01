"""
Bulk Historical Data Loader
Loads all historical CSV files into the database
"""
import sys
from pathlib import Path
from datetime import datetime, date
from typing import List, Dict
from collections import defaultdict

from etl_monthly_processor import ETLMonthlyProcessor
from config import ETLConfig

class BulkHistoricalLoader:
    """Bulk loader for historical data"""
    
    def __init__(self, use_cloud=False):
        """Initialize bulk loader"""
        self.processor = ETLMonthlyProcessor(use_cloud=use_cloud)
        self.config = ETLConfig()
    
    def discover_csv_files(self, base_path: Path, recursive: bool = True) -> Dict[str, List[Path]]:
        """
        Discover all CSV files organized by month
        Returns: Dict with month (YYYY-MM) as key and list of CSV files as value
        """
        base_path = Path(base_path)
        
        if not base_path.exists():
            raise FileNotFoundError(f"Base path not found: {base_path}")
        
        print(f"🔍 Discovering CSV files in: {base_path}")
        
        # Find all CSV files
        if recursive:
            csv_files = list(base_path.rglob('*.csv'))
        else:
            csv_files = list(base_path.glob('*.csv'))
        
        print(f"Found {len(csv_files)} CSV files")
        
        # Group by month
        files_by_month = defaultdict(list)
        
        for csv_file in csv_files:
            data_month = self.processor.extract_data_month_from_path(csv_file)
            
            if data_month:
                month_key = data_month.strftime('%Y-%m')
                files_by_month[month_key].append(csv_file)
            else:
                # Files without date go to "unknown"
                files_by_month['unknown'].append(csv_file)
        
        # Sort months
        sorted_months = sorted(
            [k for k in files_by_month.keys() if k != 'unknown'],
            key=lambda x: datetime.strptime(x, '%Y-%m')
        )
        
        if 'unknown' in files_by_month:
            sorted_months.append('unknown')
        
        return {month: files_by_month[month] for month in sorted_months}
    
    def load_all_historical_data(self, base_path: Path, 
                                 start_month: date = None,
                                 end_month: date = None,
                                 skip_duplicates: bool = True,
                                 dry_run: bool = False) -> Dict:
        """
        Load all historical data from CSV files
        Args:
            base_path: Base path containing CSV files
            start_month: Start month (YYYY-MM-01), None for all
            end_month: End month (YYYY-MM-01), None for all
            skip_duplicates: Skip already processed files
            dry_run: If True, only show what would be processed
        """
        base_path = Path(base_path)
        
        # Discover files
        files_by_month = self.discover_csv_files(base_path)
        
        print(f"\n📊 Found data for {len(files_by_month)} months")
        
        # Filter by date range if specified
        if start_month or end_month:
            filtered_months = {}
            for month_key, files in files_by_month.items():
                if month_key == 'unknown':
                    filtered_months[month_key] = files
                    continue
                
                month_date = datetime.strptime(month_key, '%Y-%m').date().replace(day=1)
                
                if start_month and month_date < start_month:
                    continue
                if end_month and month_date > end_month:
                    continue
                
                filtered_months[month_key] = files
            
            files_by_month = filtered_months
            print(f"📅 Filtered to {len(files_by_month)} months")
        
        if dry_run:
            print("\n🔍 DRY RUN MODE - No data will be loaded")
            print("\nFiles to be processed:")
            total_files = 0
            for month_key, files in files_by_month.items():
                print(f"\n  Month: {month_key} ({len(files)} files)")
                for f in files[:5]:  # Show first 5 files
                    print(f"    - {f.name}")
                if len(files) > 5:
                    print(f"    ... and {len(files) - 5} more files")
                total_files += len(files)
            
            print(f"\n📊 Total files: {total_files}")
            return {'dry_run': True, 'files_count': total_files}
        
        # Process files
        results = {
            'total_months': len(files_by_month),
            'total_files': 0,
            'successful_files': 0,
            'failed_files': 0,
            'skipped_files': 0,
            'month_results': {}
        }
        
        print(f"\n🚀 Starting bulk load...")
        
        for month_key, files in files_by_month.items():
            if month_key == 'unknown':
                print(f"\n⚠️  Processing files without date information...")
            else:
                print(f"\n📅 Processing month: {month_key} ({len(files)} files)")
            
            month_date = None
            if month_key != 'unknown':
                month_date = datetime.strptime(month_key, '%Y-%m').date().replace(day=1)
            
            month_results = {
                'files': len(files),
                'successful': 0,
                'failed': 0,
                'skipped': 0,
                'results': []
            }
            
            for i, csv_file in enumerate(files, 1):
                print(f"\n  [{i}/{len(files)}] Processing: {csv_file.name}")
                
                result = self.processor.process_single_file(
                    csv_file,
                    data_month=month_date,
                    skip_duplicates=skip_duplicates
                )
                
                month_results['results'].append(result)
                results['total_files'] += 1
                
                if result.get('success'):
                    if result.get('skipped'):
                        month_results['skipped'] += 1
                        results['skipped_files'] += 1
                    else:
                        month_results['successful'] += 1
                        results['successful_files'] += 1
                else:
                    month_results['failed'] += 1
                    results['failed_files'] += 1
            
            results['month_results'][month_key] = month_results
            
            print(f"\n  ✅ Month {month_key} completed: "
                  f"{month_results['successful']} successful, "
                  f"{month_results['failed']} failed, "
                  f"{month_results['skipped']} skipped")
        
        # Print summary
        print("\n" + "="*60)
        print("📊 BULK LOAD SUMMARY")
        print("="*60)
        print(f"Total months processed: {results['total_months']}")
        print(f"Total files processed: {results['total_files']}")
        print(f"Successful: {results['successful_files']}")
        print(f"Failed: {results['failed_files']}")
        print(f"Skipped (already processed): {results['skipped_files']}")
        print("="*60)
        
        return results
    
    def generate_load_report(self, results: Dict) -> str:
        """Generate a text report from load results"""
        report_lines = [
            "ETL BULK LOAD REPORT",
            "=" * 60,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "SUMMARY",
            "-" * 60,
            f"Total months: {results.get('total_months', 0)}",
            f"Total files: {results.get('total_files', 0)}",
            f"Successful: {results.get('successful_files', 0)}",
            f"Failed: {results.get('failed_files', 0)}",
            f"Skipped: {results.get('skipped_files', 0)}",
            "",
            "DETAILS BY MONTH",
            "-" * 60,
        ]
        
        for month_key, month_result in results.get('month_results', {}).items():
            report_lines.append(f"\nMonth: {month_key}")
            report_lines.append(f"  Files: {month_result.get('files', 0)}")
            report_lines.append(f"  Successful: {month_result.get('successful', 0)}")
            report_lines.append(f"  Failed: {month_result.get('failed', 0)}")
            report_lines.append(f"  Skipped: {month_result.get('skipped', 0)}")
        
        return "\n".join(report_lines)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Bulk Historical Data Loader')
    parser.add_argument('--path', type=str, required=True,
                       help='Base path containing CSV files')
    parser.add_argument('--start-month', type=str,
                       help='Start month (YYYY-MM format)')
    parser.add_argument('--end-month', type=str,
                       help='End month (YYYY-MM format)')
    parser.add_argument('--cloud', action='store_true',
                       help='Use cloud database')
    parser.add_argument('--skip-duplicates', action='store_true', default=True,
                       help='Skip already processed files')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be processed without loading')
    
    args = parser.parse_args()
    
    loader = BulkHistoricalLoader(use_cloud=args.cloud)
    
    start_month = None
    if args.start_month:
        start_month = datetime.strptime(args.start_month, '%Y-%m').date().replace(day=1)
    
    end_month = None
    if args.end_month:
        end_month = datetime.strptime(args.end_month, '%Y-%m').date().replace(day=1)
    
    results = loader.load_all_historical_data(
        base_path=Path(args.path),
        start_month=start_month,
        end_month=end_month,
        skip_duplicates=args.skip_duplicates,
        dry_run=args.dry_run
    )
    
    if not args.dry_run:
        # Generate and save report
        report = loader.generate_load_report(results)
        report_file = Path('bulk_load_report.txt')
        report_file.write_text(report, encoding='utf-8')
        print(f"\n📄 Report saved to: {report_file}")

