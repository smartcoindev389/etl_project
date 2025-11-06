"""
ETL Merge Processor
Replicates the notebook merge logic: joins resultados_analisis_completo with metadata files
"""
import pandas as pd
from pathlib import Path
from datetime import datetime, date
from sqlalchemy import create_engine, text
import sys
from typing import Dict, Optional, List

from config import DatabaseConfig, ETLConfig
from etl_monthly_processor import ETLMonthlyProcessor

class ETLMergeProcessor(ETLMonthlyProcessor):
    """ETL processor that merges multiple CSV files like the notebook"""
    
    def find_monthly_files(self, base_path: Path, data_month: date) -> Dict[str, List[Path]]:
        """
        Find all CSV files for a specific month
        Returns dict with file types as keys
        """
        month_str = data_month.strftime('%Y%m')  # 202508
        month_str_alt = data_month.strftime('%Y-%m')  # 2025-08
        
        files = {
            'resultados': [],
            'resultados_metadata_final_nps': [],
            'pagos_atc': [],
            'pagos_galicia': [],
            'morosidad': [],
            'grabaciones_multimedia': [],
            'todas_conversaciones': [],
            'nps': []
        }
        
        # Search recursively
        all_csvs = list(base_path.rglob('*.csv'))
        
        for csv_file in all_csvs:
            filename_lower = csv_file.name.lower()
            path_str = str(csv_file)
            
            # Check if file matches the month
            if data_month is None or month_str in path_str or month_str_alt in path_str:
                
                # Updated results with metadata and NPS (already merged)
                if 'resultados_analisis_completo' in filename_lower and 'metadata_final' in filename_lower and 'nps' in filename_lower:
                    files['resultados_metadata_final_nps'].append(csv_file)
                # Original resultados files (not merged)
                elif 'resultados_analisis_completo' in filename_lower and 'metadata_final' not in filename_lower:
                    files['resultados'].append(csv_file)
                # Flags files with ATC payments
                elif 'flags_resumen_total_con_pagos_atc' in filename_lower or ('flags' in filename_lower and 'pagos_atc' in filename_lower):
                    files['pagos_atc'].append(csv_file)
                # Flags files with Galicia payments
                elif 'flags_resumen_total_con_pagos_galicia' in filename_lower or ('flags' in filename_lower and 'pagos_galicia' in filename_lower):
                    files['pagos_galicia'].append(csv_file)
                # Flags files with morosidad (delinquency)
                elif 'flags_resumen_total_con_morosidad' in filename_lower or ('flags' in filename_lower and 'morosidad' in filename_lower):
                    files['morosidad'].append(csv_file)
                elif 'grabaciones_multimedia' in filename_lower:
                    files['grabaciones_multimedia'].append(csv_file)
                elif 'todas_conversaciones' in filename_lower:
                    files['todas_conversaciones'].append(csv_file)
                elif 'nps' in filename_lower and 'metadata_final' not in filename_lower:
                    files['nps'].append(csv_file)
        
        return files
    
    def load_resultados(self, file_path: Path) -> pd.DataFrame:
        """Load resultados_analisis_completo CSV"""
        print(f"Loading resultados: {file_path.name}")
        df = pd.read_csv(file_path, encoding='utf-8', low_memory=False)
        
        # Only keep flag columns (remove frase, fraser, simil, subfrases)
        flag_cols = [col for col in df.columns if col.endswith('_flg') or col.startswith('flag_')]
        base_cols = ['nombre_archivo', 'fecha_procesamiento']
        
        cols_to_keep = base_cols + flag_cols
        cols_to_keep = [col for col in cols_to_keep if col in df.columns]
        
        df_result = df[cols_to_keep].copy()
        
        print(f"  Loaded {len(df_result)} rows, {len(df_result.columns)} columns (flags only)")
        return df_result
    
    def load_grabaciones(self, file_path: Path) -> pd.DataFrame:
        """Load grabaciones_multimedia CSV"""
        print(f"Loading grabaciones: {file_path.name}")
        df = pd.read_csv(file_path, encoding='utf-8', low_memory=False)
        print(f"  Loaded {len(df)} rows, {len(df.columns)} columns")
        return df
    
    def load_conversaciones(self, file_path: Path) -> pd.DataFrame:
        """Load todas_conversaciones CSV"""
        print(f"Loading conversaciones: {file_path.name}")
        df = pd.read_csv(file_path, encoding='utf-8', low_memory=False)
        print(f"  Loaded {len(df)} rows, {len(df.columns)} columns")
        return df
    
    def load_pagos_atc(self, file_path: Path) -> pd.DataFrame:
        """Load flags_resumen_total_con_pagos_atc CSV"""
        print(f"Loading pagos_atc: {file_path.name}")
        df = pd.read_csv(file_path, encoding='utf-8', low_memory=False)
        print(f"  Loaded {len(df)} rows, {len(df.columns)} columns")
        return df
    
    def load_pagos_galicia(self, file_path: Path) -> pd.DataFrame:
        """Load flags_resumen_total_con_pagos_galicia CSV"""
        print(f"Loading pagos_galicia: {file_path.name}")
        df = pd.read_csv(file_path, encoding='utf-8', low_memory=False)
        print(f"  Loaded {len(df)} rows, {len(df.columns)} columns")
        return df
    
    def load_morosidad(self, file_path: Path) -> pd.DataFrame:
        """Load flags_resumen_total_con_morosidad CSV"""
        print(f"Loading morosidad: {file_path.name}")
        df = pd.read_csv(file_path, encoding='utf-8', low_memory=False)
        print(f"  Loaded {len(df)} rows, {len(df.columns)} columns")
        return df
    
    def load_resultados_metadata_final_nps(self, file_path: Path) -> pd.DataFrame:
        """Load resultados_analisis_completo_metadata_final_nps CSV (already merged)"""
        print(f"Loading resultados_metadata_final_nps: {file_path.name}")
        df = pd.read_csv(file_path, encoding='utf-8', low_memory=False)
        print(f"  Loaded {len(df)} rows, {len(df.columns)} columns (already merged)")
        return df
    
    def merge_data(self, resultados_df: pd.DataFrame,
                   grabaciones_df: Optional[pd.DataFrame] = None,
                   conversaciones_df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """
        Merge all dataframes following notebook logic
        """
        print("Merging data...")
        
        # Start with resultados
        merged_df = resultados_df.copy()
        
        # Merge with grabaciones_multimedia on nombre_archivo
        if grabaciones_df is not None and not grabaciones_df.empty:
            print("  Merging with grabaciones_multimedia...")
            
            # Try different merge keys
            merge_key = None
            if 'nombre_archivo' in grabaciones_df.columns:
                merge_key = 'nombre_archivo'
            elif 'archivo_multimedia' in grabaciones_df.columns:
                grabaciones_df = grabaciones_df.rename(columns={'archivo_multimedia': 'nombre_archivo'})
                merge_key = 'nombre_archivo'
            elif 'conversation_id' in grabaciones_df.columns:
                # Need to find conversation_id in resultados
                if 'conversation_id' in merged_df.columns:
                    merge_key = 'conversation_id'
                else:
                    # Try to extract from nombre_archivo
                    # Assuming nombre_archivo might contain conversation_id
                    print("  Warning: Could not find merge key for grabaciones")
            
            if merge_key:
                merged_df = merged_df.merge(
                    grabaciones_df,
                    on=merge_key,
                    how='left',
                    suffixes=('', '_grab')
                )
                print(f"    Merged: {len(merged_df)} rows")
        
        # Merge with todas_conversaciones on conversation_id
        if conversaciones_df is not None and not conversaciones_df.empty:
            print("  Merging with todas_conversaciones...")
            
            merge_key = None
            if 'conversation_id' in conversaciones_df.columns:
                if 'conversation_id' in merged_df.columns:
                    merge_key = 'conversation_id'
                elif 'nombre_archivo' in merged_df.columns:
                    # Try to extract conversation_id from nombre_archivo
                    # This depends on the actual structure - may need adjustment
                    print("  Warning: conversation_id not found, trying to extract from nombre_archivo")
                    # For now, skip if conversation_id not available
                    merge_key = None
            
            if merge_key:
                merged_df = merged_df.merge(
                    conversaciones_df,
                    on=merge_key,
                    how='left',
                    suffixes=('', '_conv')
                )
                print(f"    Merged: {len(merged_df)} rows")
            else:
                print("  Warning: Could not merge conversaciones (no conversation_id)")
        
        print(f"Final merged: {len(merged_df)} rows, {len(merged_df.columns)} columns")
        return merged_df
    
    def process_monthly_merge(self, data_month: date, base_path: Path = None) -> Dict:
        """
        Process and merge all CSV files for a specific month
        Updated to handle new file types: resultados_metadata_final_nps, pagos_atc, pagos_galicia, morosidad
        """
        if base_path is None:
            base_path = Path(self.config.CSV_BASE_PATH)
        else:
            base_path = Path(base_path)
        
        if not base_path.exists():
            return {
                'success': False,
                'error': f'Base path not found: {base_path}'
            }
        
        print(f"Processing month: {data_month.strftime('%Y-%m')}")
        
        # Find files
        files = self.find_monthly_files(base_path, data_month)
        
        # Check if we have already merged resultados_metadata_final_nps file (preferred)
        if files['resultados_metadata_final_nps']:
            print("Found already merged resultados_metadata_final_nps file - processing directly")
            merged_df = self.load_resultados_metadata_final_nps(files['resultados_metadata_final_nps'][0])
            source_type = 'resultados_analisis_completo_metadata_final_nps'
            source_file = files['resultados_metadata_final_nps'][0].name
            file_size = files['resultados_metadata_final_nps'][0].stat().st_size
            
            # Transform
            print("Transforming data...")
            merged_df = self.transform_data(merged_df, source_type)
            
            # Create load record
            load_id = self.create_load_record(
                source_file=source_file[:500],
                source_type=source_type,
                file_path=str(base_path),
                data_month=data_month,
                file_size=file_size
            )
            
            try:
                # Load to database
                print("Loading to database...")
                rows_inserted = self.load_data_to_db(
                    merged_df, load_id, source_file, data_month
                )
                
                # Register file
                file_hash = self.calculate_file_hash(files['resultados_metadata_final_nps'][0])
                self.register_file_processing(
                    files['resultados_metadata_final_nps'][0], file_hash, source_type, data_month, file_size
                )
                
                # Update load record
                self.update_load_record(
                    load_id, 'COMPLETED',
                    rows_read=len(merged_df),
                    rows_valid=len(merged_df),
                    rows_inserted=rows_inserted,
                    rows_skipped=0
                )
                
                print(f"Successfully processed month {data_month.strftime('%Y-%m')}: {rows_inserted} rows")
                
                return {
                    'success': True,
                    'load_id': load_id,
                    'rows_inserted': rows_inserted,
                    'data_month': data_month,
                    'files_processed': 1
                }
                
            except Exception as e:
                error_msg = str(e)
                print(f"Error processing month: {error_msg}")
                
                self.update_load_record(
                    load_id, 'FAILED',
                    rows_read=len(merged_df) if 'merged_df' in locals() else 0,
                    error_message=error_msg[:500],
                    error_details=str(e)
                )
                
                return {
                    'success': False,
                    'load_id': load_id,
                    'error': error_msg
                }
        
        # Fallback: Load original resultados files and merge (legacy behavior)
        if not files['resultados']:
            return {
                'success': False,
                'error': f'No resultados files found for month {data_month.strftime("%Y-%m")}'
            }
        
        # Load first resultados file
        resultados_df = self.load_resultados(files['resultados'][0])
        
        # Load grabaciones (optional)
        grabaciones_df = None
        if files['grabaciones_multimedia']:
            grabaciones_df = self.load_grabaciones(files['grabaciones_multimedia'][0])
        
        # Load conversaciones (optional)
        conversaciones_df = None
        if files['todas_conversaciones']:
            conversaciones_df = self.load_conversaciones(files['todas_conversaciones'][0])
        
        # Merge
        merged_df = self.merge_data(resultados_df, grabaciones_df, conversaciones_df)
        
        # Transform
        print("Transforming data...")
        merged_df = self.transform_data(merged_df, 'resultados_merged')
        
        # Determine source file name
        source_files = [f.name for f in files['resultados']]
        if files['grabaciones_multimedia']:
            source_files.append(files['grabaciones_multimedia'][0].name)
        if files['todas_conversaciones']:
            source_files.append(files['todas_conversaciones'][0].name)
        
        source_file = f"merged_{data_month.strftime('%Y-%m')}_{'_'.join([f.name[:20] for f in files['resultados']])}"
        
        # Create load record
        file_size = sum(f.stat().st_size for f in files['resultados'])
        load_id = self.create_load_record(
            source_file=source_file[:500],
            source_type='resultados_merged',
            file_path=str(base_path),
            data_month=data_month,
            file_size=file_size
        )
        
        try:
            # Load to database
            print("Loading to database...")
            rows_inserted = self.load_data_to_db(
                merged_df, load_id, source_file, data_month
            )
            
            # Register files
            for csv_file in files['resultados']:
                file_hash = self.calculate_file_hash(csv_file)
                self.register_file_processing(
                    csv_file, file_hash, 'resultados', data_month, csv_file.stat().st_size
                )
            
            if files['grabaciones_multimedia']:
                file_hash = self.calculate_file_hash(files['grabaciones_multimedia'][0])
                self.register_file_processing(
                    files['grabaciones_multimedia'][0], file_hash, 'grabaciones', data_month,
                    files['grabaciones_multimedia'][0].stat().st_size
                )
            
            if files['todas_conversaciones']:
                file_hash = self.calculate_file_hash(files['todas_conversaciones'][0])
                self.register_file_processing(
                    files['todas_conversaciones'][0], file_hash, 'conversaciones', data_month,
                    files['todas_conversaciones'][0].stat().st_size
                )
            
            # Update load record
            self.update_load_record(
                load_id, 'COMPLETED',
                rows_read=len(merged_df),
                rows_valid=len(merged_df),
                rows_inserted=rows_inserted,
                rows_skipped=0
            )
            
            print(f"Successfully processed month {data_month.strftime('%Y-%m')}: {rows_inserted} rows")
            
            return {
                'success': True,
                'load_id': load_id,
                'rows_inserted': rows_inserted,
                'data_month': data_month,
                'files_processed': len(source_files)
            }
            
        except Exception as e:
            error_msg = str(e)
            print(f"Error processing month: {error_msg}")
            
            self.update_load_record(
                load_id, 'FAILED',
                rows_read=len(merged_df) if 'merged_df' in locals() else 0,
                error_message=error_msg[:500],
                error_details=str(e)
            )
            
            return {
                'success': False,
                'load_id': load_id,
                'error': error_msg
            }

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='ETL Merge Processor')
    parser.add_argument('--month', type=str, required=True, help='Process month (YYYY-MM format)')
    parser.add_argument('--path', type=str, help='Base path for CSV files')
    parser.add_argument('--cloud', action='store_true', help='Use cloud database')
    
    args = parser.parse_args()
    
    processor = ETLMergeProcessor(use_cloud=args.cloud)
    
    try:
        data_month = datetime.strptime(args.month, '%Y-%m').date().replace(day=1)
    except ValueError:
        print("Invalid month format. Use YYYY-MM")
        sys.exit(1)
    
    base_path = Path(args.path) if args.path else None
    result = processor.process_monthly_merge(data_month, base_path)
    print(f"\nResult: {result}")

