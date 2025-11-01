-- ETL Project Database Schema
-- Optimized for historization and monthly data processing

CREATE DATABASE IF NOT EXISTS etl_project CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE etl_project;

-- Fact table: Main data records with historization
CREATE TABLE IF NOT EXISTS fact_records (
  record_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  
  -- Data fields (adjust based on actual CSV structure)
  -- These are placeholder fields - will be updated based on actual CSV schema
  field1 VARCHAR(255),
  field2 VARCHAR(255),
  field3 VARCHAR(255),
  field4 VARCHAR(255),
  field5 DECIMAL(15,2),
  
  -- Metadata fields for historization
  source_file VARCHAR(500) NOT NULL,
  source_type VARCHAR(100),
  data_month DATE NOT NULL,
  data_year INT GENERATED ALWAYS AS (YEAR(data_month)) STORED,
  data_month_num INT GENERATED ALWAYS AS (MONTH(data_month)) STORED,
  
  -- Audit fields
  load_id BIGINT,
  load_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  -- Indexes for performance
  INDEX idx_data_month (data_month),
  INDEX idx_source_file (source_file),
  INDEX idx_load_id (load_id),
  INDEX idx_data_year_month (data_year, data_month_num)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Audit table: Track all ETL loads
CREATE TABLE IF NOT EXISTS audit_loads (
  load_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  
  -- Load information
  source_file VARCHAR(500) NOT NULL,
  source_type VARCHAR(100),
  file_path VARCHAR(1000),
  file_size_bytes BIGINT,
  
  -- Processing metrics
  rows_read INT DEFAULT 0,
  rows_valid INT DEFAULT 0,
  rows_inserted INT DEFAULT 0,
  rows_skipped INT DEFAULT 0,
  
  -- Timing
  start_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  end_ts TIMESTAMP NULL,
  processing_duration_seconds DECIMAL(10,2),
  
  -- Status tracking
  status VARCHAR(50) DEFAULT 'RUNNING', -- RUNNING, COMPLETED, FAILED, SKIPPED
  error_message TEXT,
  error_details TEXT,
  
  -- Data period
  data_month DATE,
  data_year INT,
  data_month_num INT,
  
  -- Indexes
  INDEX idx_status (status),
  INDEX idx_data_month (data_month),
  INDEX idx_start_ts (start_ts),
  INDEX idx_source_file (source_file)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Monthly summary table: Aggregated statistics per month
CREATE TABLE IF NOT EXISTS monthly_summary (
  summary_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  data_month DATE NOT NULL UNIQUE,
  data_year INT,
  data_month_num INT,
  
  total_records INT DEFAULT 0,
  total_files_processed INT DEFAULT 0,
  first_load_ts TIMESTAMP,
  last_load_ts TIMESTAMP,
  
  -- Source type breakdown
  metadata_records INT DEFAULT 0,
  speech_analytics_records INT DEFAULT 0,
  resultados_records INT DEFAULT 0,
  
  created_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  
  INDEX idx_data_month (data_month)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- File tracking table: Track processed files to prevent duplicates
CREATE TABLE IF NOT EXISTS processed_files (
  file_id BIGINT AUTO_INCREMENT PRIMARY KEY,
  file_path VARCHAR(1000) NOT NULL UNIQUE,
  file_name VARCHAR(500),
  file_hash VARCHAR(64), -- SHA256 hash of file content
  file_size_bytes BIGINT,
  
  source_type VARCHAR(100),
  data_month DATE,
  
  first_processed_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  last_processed_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  process_count INT DEFAULT 1,
  
  INDEX idx_file_hash (file_hash),
  INDEX idx_data_month (data_month),
  INDEX idx_source_type (source_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

