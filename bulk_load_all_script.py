"""
Complete Bulk Load Script
Loads ALL CSV files from nested folder structures automatically
Handles multiple folders per month and multiple files per folder
"""
import sys
from pathlib import Path
from datetime import datetime
from bulk_historical_loader import BulkHistoricalLoader

def main():
    """Main function to load all historical data"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Complete Bulk Load - Loads ALL CSV files from nested folders',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview all files that will be loaded
  python bulk_load_all_script.py --path "fending data" --dry-run
  
  # Load all historical data
  python bulk_load_all_script.py --path "fending data"
  
  # Load specific date range
  python bulk_load_all_script.py --path "fending data" --start-month 2024-08 --end-month 2024-12
  
  # Load with cloud database
  python bulk_load_all_script.py --path "fending data" --cloud
        """
    )
    
    parser.add_argument('--path', type=str, required=True,
                       help='Base path containing CSV files (can have nested folders)')
    parser.add_argument('--start-month', type=str,
                       help='Start month (YYYY-MM format), e.g., 2024-08')
    parser.add_argument('--end-month', type=str,
                       help='End month (YYYY-MM format), e.g., 2024-12')
    parser.add_argument('--cloud', action='store_true',
                       help='Use cloud database instead of local')
    parser.add_argument('--skip-duplicates', action='store_true', default=True,
                       help='Skip already processed files (default: True)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be processed without loading data')
    
    args = parser.parse_args()
    
    base_path = Path(args.path)
    
    if not base_path.exists():
        print(f"Error: Base path not found: {base_path}")
        print(f"Please provide a valid path to your CSV files")
        sys.exit(1)
    
    # Convert to absolute path and string for subprocess safety
    base_path = str(base_path.resolve())
    
    print("="*60)
    print("BULK LOAD - ALL CSV FILES")
    print("="*60)
    print(f"Base path: {base_path}")
    print(f"Mode: {'DRY RUN (preview only)' if args.dry_run else 'LIVE (will load data)'}")
    print(f"Database: {'Cloud' if args.cloud else 'Local'}")
    print(f"Skip duplicates: {args.skip_duplicates}")
    
    if args.start_month or args.end_month:
        print(f"Date range: {args.start_month or 'start'} to {args.end_month or 'end'}")
    else:
        print(f"Date range: ALL months")
    
    print("="*60)
    
    # Initialize loader
    loader = BulkHistoricalLoader(use_cloud=args.cloud)
    
    # Parse date range
    start_month = None
    if args.start_month:
        try:
            start_month = datetime.strptime(args.start_month, '%Y-%m').date().replace(day=1)
        except ValueError:
            print(f"Error: Invalid start month format. Use YYYY-MM (e.g., 2024-08)")
            sys.exit(1)
    
    end_month = None
    if args.end_month:
        try:
            end_month = datetime.strptime(args.end_month, '%Y-%m').date().replace(day=1)
        except ValueError:
            print(f"Error: Invalid end month format. Use YYYY-MM (e.g., 2024-12)")
            sys.exit(1)
    
    # Load all data
    try:
        results = loader.load_all_historical_data(
            base_path=base_path,
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
            
            # Show summary
            print("\n" + "="*60)
            print("FINAL SUMMARY")
            print("="*60)
            print(f"Total months processed: {results.get('total_months', 0)}")
            print(f"Total files processed: {results.get('total_files', 0)}")
            print(f"Successful: {results.get('successful_files', 0)}")
            print(f"Failed: {results.get('failed_files', 0)}")
            print(f"Skipped: {results.get('skipped_files', 0)}")
            print("="*60)
            
            if results.get('failed_files', 0) > 0:
                print("\nWarning: Some files failed to load. Check bulk_load_report.txt for details.")
                sys.exit(1)
            else:
                print("\nAll files processed successfully!")
        
    except KeyboardInterrupt:
        print("\n\nProcess interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
