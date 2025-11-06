"""
Schema Generator
Automatically generates MySQL schema from CSV files
"""
import pandas as pd
import sys
from pathlib import Path

def infer_mysql_type(series: pd.Series, col_name: str) -> str:
    """Infer MySQL data type from pandas Series"""
    col_lower = col_name.lower()
    
    # Flags: force TINYINT(1) regardless of substrings like 'fecha' in the name
    if 'flg' in col_lower or 'flag' in col_lower:
        return 'TINYINT(1)'
    
    # Datetime-like columns
    if 'fecha' in col_lower or 'date' in col_lower or 'timestamp' in col_lower:
        try:
            pd.to_datetime(series.dropna().iloc[0] if len(series.dropna()) > 0 else None, errors='raise')
            return 'DATETIME'
        except Exception:
            # fall through to regular inference if parsing fails
            pass
    
    # Check dtype
    dtype = series.dtype
    
    # Integer types
    if pd.api.types.is_integer_dtype(dtype):
        max_val = series.max()
        min_val = series.min()
        if max_val is not pd.NA and min_val is not pd.NA:
            if max_val <= 127 and min_val >= -128:
                return 'TINYINT'
            elif max_val <= 32767 and min_val >= -32768:
                return 'SMALLINT'
            elif max_val <= 2147483647 and min_val >= -2147483648:
                return 'INT'
            else:
                return 'BIGINT'
        return 'INT'
    
    # Float types
    if pd.api.types.is_float_dtype(dtype):
        return 'DECIMAL(15,2)'
    
    # Simple boolean detection (non-flag columns)
    unique_vals = series.dropna().unique()[:10]
    if len(unique_vals) > 0 and all(v in [0, 1, '0', '1', True, False] for v in unique_vals):
        return 'TINYINT(1)'
    
    # String types
    if pd.api.types.is_object_dtype(dtype) or pd.api.types.is_string_dtype(dtype):
        max_len = series.astype(str).str.len().max()
        if pd.isna(max_len):
            max_len = 255
        else:
            max_len = int(max_len)
        
        # Adjust length
        if max_len <= 50:
            length = 255
        elif max_len <= 255:
            length = 255
        elif max_len <= 500:
            length = 500
        elif max_len <= 1000:
            length = 1000
        else:
            length = 2000
        
        return f'VARCHAR({length})'
    
    return 'VARCHAR(255)'

def generate_schema_from_csv(csv_path: Path, table_name: str = 'fact_records', 
                           sample_rows: int = 1000) -> str:
    """
    Generate MySQL CREATE TABLE statement from CSV file
    """
    print(f"Reading CSV: {csv_path}")
    df = pd.read_csv(csv_path, nrows=sample_rows, low_memory=False)
    
    print(f"Loaded {len(df)} rows, {len(df.columns)} columns")
    
    schema_lines = [
        f"-- Auto-generated schema from: {csv_path.name}",
        f"-- Generated columns: {len(df.columns)}",
        f"-- Sample rows analyzed: {len(df)}",
        "",
        f"CREATE TABLE IF NOT EXISTS {table_name} (",
        "  record_id BIGINT AUTO_INCREMENT PRIMARY KEY,",
        ""
    ]
    
    # Generate column definitions
    for i, col in enumerate(df.columns):
        mysql_type = infer_mysql_type(df[col], col)
        
        # Clean column name (MySQL safe)
        safe_col = col.replace(' ', '_').replace('-', '_')
        
        # Check if NULL values exist
        null_count = df[col].isna().sum()
        nullable = "NULL" if null_count > 0 else "NOT NULL"
        
        schema_lines.append(f"  `{safe_col}` {mysql_type} {nullable},")
    
    # Add metadata columns
    schema_lines.extend([
        "",
        "  -- Metadata fields for historization",
        "  `source_file` VARCHAR(500) NOT NULL,",
        "  `source_type` VARCHAR(100),",
        "  `data_month` DATE NOT NULL,",
        "  `data_year` INT GENERATED ALWAYS AS (YEAR(data_month)) STORED,",
        "  `data_month_num` INT GENERATED ALWAYS AS (MONTH(data_month)) STORED,",
        "",
        "  -- Audit fields",
        "  `load_id` BIGINT,",
        "  `load_ts` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,",
        "",
        "  -- Indexes",
        "  INDEX idx_data_month (data_month),",
        "  INDEX idx_source_file (source_file),",
        "  INDEX idx_load_id (load_id),",
        "  INDEX idx_data_year_month (data_year, data_month_num)"
    ])
    
    # Add indexes for common search columns
    index_cols = [col for col in df.columns if any(keyword in col.lower() 
                   for keyword in ['nombre_archivo', 'conversation_id', 'codmes'])]
    
    for col in index_cols[:5]:  # Limit to 5 indexes
        safe_col = col.replace(' ', '_').replace('-', '_')
        schema_lines.append(f",  INDEX idx_{safe_col} (`{safe_col}`)")
    
    schema_lines.append(") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")
    
    return "\n".join(schema_lines)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate MySQL schema from CSV')
    parser.add_argument('csv_path', type=str, help='Path to CSV file')
    parser.add_argument('--table', type=str, default='fact_records', help='Table name')
    parser.add_argument('--sample', type=int, default=1000, help='Sample rows to analyze')
    parser.add_argument('--output', type=str, help='Output SQL file path')
    
    args = parser.parse_args()
    
    schema = generate_schema_from_csv(
        Path(args.csv_path),
        table_name=args.table,
        sample_rows=args.sample
    )
    
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(schema, encoding='utf-8')
        print(f"\nSchema saved to: {output_path}")
    else:
        print("\n" + "="*60)
        print(schema)

