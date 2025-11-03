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
    
    def discover_csv_files(self, base_path: Path, recursive: bool = True) -> Dict[str, Dict[str, List[Path]]]:
        """
        Discover all CSV files organized by month and folder structure
        Returns: Dict with month (YYYY-MM) as key, containing:
            - 'files': List of all CSV files for that month
            - 'folders': Dict with folder path as key and files in that folder
        """
        base_path = Path(base_path)
        
        if not base_path.exists():
            raise FileNotFoundError(f"Base path not found: {base_path}")
        
        print(f"Discovering CSV files in: {base_path}")
        print(f"Search mode: {'Recursive (all subfolders)' if recursive else 'Top level only'}")
        
        # Find all CSV files recursively
        if recursive:
            csv_files = list(base_path.rglob('*.csv'))
        else:
            csv_files = list(base_path.glob('*.csv'))
        
        print(f"Found {len(csv_files)} CSV files total")
        
        # Group by month and folder
        files_by_month = defaultdict(lambda: {'files': [], 'folders': defaultdict(list)})
        
        for csv_file in csv_files:
            # Get relative folder path from base
            try:
                rel_path = csv_file.relative_to(base_path)
                folder_path = str(rel_path.parent) if rel_path.parent != Path('.') else 'root'
            except:
                folder_path = str(csv_file.parent)
            
            data_month = self.processor.extract_data_month_from_path(csv_file)
            
            if data_month:
                month_key = data_month.strftime('%Y-%m')
                files_by_month[month_key]['files'].append(csv_file)
                files_by_month[month_key]['folders'][folder_path].append(csv_file)
            else:
                # Files without date go to "unknown"
                files_by_month['unknown']['files'].append(csv_file)
                files_by_month['unknown']['folders'][folder_path].append(csv_file)
        
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
        
        print(f"\nFound data for {len(files_by_month)} months")
        
        # Show folder structure
        for month_key, month_data in files_by_month.items():
            if month_key != 'unknown':
                folders = month_data['folders']
                print(f"  {month_key}: {len(month_data['files'])} files in {len(folders)} folder(s)")
                for folder, files in list(folders.items())[:3]:  # Show first 3 folders
                    print(f"    - {folder}: {len(files)} files")
                if len(folders) > 3:
                    print(f"    ... and {len(folders) - 3} more folders")
        
        # Filter by date range if specified
        if start_month or end_month:
            filtered_months = {}
            for month_key, month_data in files_by_month.items():
                if month_key == 'unknown':
                    filtered_months[month_key] = month_data
                    continue
                
                month_date = datetime.strptime(month_key, '%Y-%m').date().replace(day=1)
                
                if start_month and month_date < start_month:
                    continue
                if end_month and month_date > end_month:
                    continue
                
                filtered_months[month_key] = month_data
            
            files_by_month = filtered_months
            print(f"Filtered to {len(files_by_month)} months")
        
        if dry_run:
            print("\nDRY RUN MODE - No data will be loaded")
            print("\nFiles to be processed:")
            total_files = 0
            for month_key, month_data in files_by_month.items():
                files = month_data['files']
                folders = month_data['folders']
                print(f"\n  Month: {month_key} ({len(files)} files in {len(folders)} folder(s))")
                
                # Show files by folder
                for folder, folder_files in folders.items():
                    print(f"    Folder: {folder}")
                    for f in folder_files[:3]:  # Show first 3 files per folder
                        print(f"      - {f.name}")
                    if len(folder_files) > 3:
                        print(f"      ... and {len(folder_files) - 3} more files")
                
                total_files += len(files)
            
            print(f"\nTotal files: {total_files}")
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
        
        print(f"\nStarting bulk load...")
        
        for month_key, month_data in files_by_month.items():
            files = month_data['files']
            folders = month_data['folders']
            
            if month_key == 'unknown':
                print(f"\nProcessing files without date information...")
            else:
                print(f"\nProcessing month: {month_key}")
                print(f"  Total files: {len(files)}")
                print(f"  Folders: {len(folders)}")
            
            month_date = None
            if month_key != 'unknown':
                month_date = datetime.strptime(month_key, '%Y-%m').date().replace(day=1)
            
            month_results = {
                'files': len(files),
                'folders': len(folders),
                'successful': 0,
                'failed': 0,
                'skipped': 0,
                'results': []
            }
            
            # Process files by folder for better organization
            file_counter = 0
            for folder_path, folder_files in folders.items():
                if len(folders) > 1:
                    print(f"\n  Folder: {folder_path} ({len(folder_files)} files)")
                
                for csv_file in folder_files:
                    file_counter += 1
                    print(f"\n  [{file_counter}/{len(files)}] Processing: {csv_file.name}")
                    print(f"      Path: {csv_file.relative_to(base_path) if base_path in csv_file.parents else csv_file}")
                    
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
                            print(f"      Status: Skipped (already processed)")
                        else:
                            month_results['successful'] += 1
                            results['successful_files'] += 1
                            rows = result.get('rows_inserted', 0)
                            print(f"      Status: Success ({rows} rows loaded)")
                    else:
                        month_results['failed'] += 1
                        results['failed_files'] += 1
                        error = result.get('error', 'Unknown error')
                        print(f"      Status: Failed - {error[:100]}")
            
            results['month_results'][month_key] = month_results
            
            print(f"\n  Month {month_key} completed:")
            print(f"    Successful: {month_results['successful']}")
            print(f"    Failed: {month_results['failed']}")
            print(f"    Skipped: {month_results['skipped']}")
        
        # Print summary
        print("\n" + "="*60)
        print("BULK LOAD SUMMARY")
        print("="*60)
        print(f"Total months processed: {results['total_months']}")
        print(f"Total files processed: {results['total_files']}")
        print(f"Successful: {results['successful_files']}")
        print(f"Failed: {results['failed_files']}")
        print(f"Skipped (already processed): {results['skipped_files']}")
        print("="*60)
        
        # Show folder breakdown
        total_folders = sum(m.get('folders', 0) for m in results.get('month_results', {}).values())
        if total_folders > 0:
            print(f"\nTotal folders processed: {total_folders}")
        
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
            report_lines.append(f"  Folders: {month_result.get('folders', 0)}")
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
        print(f"\nReport saved to: {report_file}")

