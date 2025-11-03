-- Auto-generated schema from: resultados_analisis_completo_metadata_final_nps2.csv
-- Generated columns: 111
-- Sample rows analyzed: 1000

CREATE DATABASE IF NOT EXISTS etl_project CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE etl_project;

CREATE TABLE IF NOT EXISTS fact_records (
  record_id BIGINT AUTO_INCREMENT PRIMARY KEY,

  `nombre_archivo` VARCHAR(255) NOT NULL,
  `fecha_procesamiento` DATETIME NOT NULL,
  `motivo_Anular_tarjeta_flg` TINYINT NOT NULL,
  `motivo_Bloqueo_tarjeta_flg` TINYINT NOT NULL,
  `motivo_Carta_de_no_deudo_flg` TINYINT NOT NULL,
  `motivo_Cliente_sin_atencion__flg` TINYINT NOT NULL,
  `motivo_Consulta_Deuda_flg` TINYINT NOT NULL,
  `motivo_Consulta_sobre_intereses_flg` TINYINT NOT NULL,
  `motivo_Denuncia_flg` TINYINT NOT NULL,
  `motivo_Donde_y_como_puedo_pagar_flg` TINYINT NOT NULL,
  `motivo_Estado_de_cuenta_flg` TINYINT NOT NULL,
  `motivo_Facilidad_de_pago_flg` TINYINT NOT NULL,
  `motivo_Fallecimiento_flg` TINYINT NOT NULL,
  `motivo_Fraude_flg` TINYINT NOT NULL,
  `motivo_Intereses_altos_flg` TINYINT NOT NULL,
  `motivo_Membresia_flg` TINYINT NOT NULL,
  `motivo_Monto_para_pagar_flg` TINYINT NOT NULL,
  `motivo_No_la_puedo_usar_o_no_la_uso_flg` TINYINT NOT NULL,
  `motivo_Pago_minimo_flg` TINYINT NOT NULL,
  `motivo_Perdida_de_tarjeta_flg` TINYINT NOT NULL,
  `motivo_Presento_reclamo_flg` TINYINT NOT NULL,
  `motivo_Prestamo_aprobado__flg` TINYINT NOT NULL,
  `motivo_Problemas_con_medios_de_pago_flg` TINYINT NOT NULL,
  `motivo_Refinanciacion_flg` TINYINT NOT NULL,
  `motivo_Reprogramacion_flg` TINYINT NOT NULL,
  `motivo_Seguro_flg` TINYINT NOT NULL,
  `motivo_Traslado_de_deuda_a_estudio_flg` TINYINT NOT NULL,
  `motivo_fecha_de_pago_flg` TINYINT NOT NULL,
  `motivo_no_debo_nada_flg` TINYINT NOT NULL,
  `flag_agrupacion_Anular_tarjeta` TINYINT NOT NULL,
  `flag_agrupacion_Bloqueo_Perdida_Robo_Fraude` TINYINT NOT NULL,
  `flag_agrupacion_Carta_de_no_deudo` TINYINT NOT NULL,
  `flag_agrupacion_Estado_de_cuenta` TINYINT NOT NULL,
  `flag_agrupacion_Facilidad_de_pago` TINYINT NOT NULL,
  `flag_agrupacion_Información_deuda_cuota_o_fecha` TINYINT NOT NULL,
  `flag_agrupacion_Medios_de_Pago` TINYINT NOT NULL,
  `flag_agrupacion_Prestamo_` TINYINT NOT NULL,
  `flag_agrupacion_Problemas_de_salud_o_Fallecimiento` TINYINT NOT NULL,
  `flag_agrupacion_Reclamo_del_cliente` TINYINT NOT NULL,
  `flag_agrupacion_Reprogramar_o_Refinanciar` TINYINT NOT NULL,
  `flag_agrupacion_Seguro_Membresia_e_intereses` TINYINT NOT NULL,
  `flag_agrupacion_Traslado_de_deuda_a_estudio` TINYINT NOT NULL,
  `flag_agrupacion_Uso_tarjeta` TINYINT NOT NULL,
  `motivo_Cliente_molesto_flg` TINYINT NULL,
  `motivo_Cliente_satisfecho_flg` TINYINT NULL,
  `flag_agrupacion_Satisfacción_al_cliente` TINYINT NULL,
  `archivo_multimedia` VARCHAR(255) NOT NULL,
  `conversation_id` VARCHAR(255) NOT NULL,
  `fecha_inicio` DATETIME NOT NULL,
  `fecha_fin` DATETIME NOT NULL,
  `customer_min_total` DECIMAL(15,2) NOT NULL,
  `customer_sin_callback_min` DECIMAL(15,2) NOT NULL,
  `ivr_min_total` DECIMAL(15,2) NOT NULL,
  `acd_min` DECIMAL(15,2) NOT NULL,
  `acd_callback_min` DECIMAL(15,2) NOT NULL,
  `agent_min` DECIMAL(15,2) NOT NULL,
  `agent_callback_min` DECIMAL(15,2) NOT NULL,
  `agent_interact_min` DECIMAL(15,2) NOT NULL,
  `AG_FOH_RETENCION_agent_interact_ord` TINYINT NOT NULL,
  `AG_COBRANZAS_INBOUND_agent_interact_ord` TINYINT NOT NULL,
  `AG_COBRANZAS_INBOUND_CALLBACK_agent_interact_ord` TINYINT NOT NULL,
  `AG_FOH_COBRANZAS_ATC_agent_interact_ord` TINYINT NOT NULL,
  `FOH_TOH_ATC_agent_interact_ord` TINYINT NOT NULL,
  `AG_FOH_ATC_ANEXOS_agent_interact_ord` TINYINT NOT NULL,
  `agent_colas_cobranzas_interact_ctd` TINYINT NOT NULL,
  `agent_colas_atc_interact_ctd` TINYINT NOT NULL,
  `EPA_ATC_min` DECIMAL(15,2) NOT NULL,
  `EPA_COBRANZA_PE_min` DECIMAL(15,2) NOT NULL,
  `AG_FOH_RETENCION_acd_min` DECIMAL(15,2) NOT NULL,
  `AG_FOH_RETENCION_agent_min` DECIMAL(15,2) NOT NULL,
  `AG_FOH_RETENCION_agent_interact_min` DECIMAL(15,2) NOT NULL,
  `AG_COBRANZAS_INBOUND_acd_min` DECIMAL(15,2) NOT NULL,
  `AG_COBRANZAS_INBOUND_agent_min` DECIMAL(15,2) NOT NULL,
  `AG_COBRANZAS_INBOUND_agent_interact_min` DECIMAL(15,2) NOT NULL,
  `AG_COBRANZAS_INBOUND_first_interact_sec` DECIMAL(15,2) NULL,
  `AG_COBRANZAS_INBOUND_last_wrapup_sec` DECIMAL(15,2) NULL,
  `AG_COBRANZAS_INBOUND_CALLBACK_acd_min` DECIMAL(15,2) NOT NULL,
  `AG_COBRANZAS_INBOUND_CALLBACK_agent_min` DECIMAL(15,2) NOT NULL,
  `AG_COBRANZAS_INBOUND_CALLBACK_agent_interact_min` DECIMAL(15,2) NOT NULL,
  `AG_COBRANZAS_INBOUND_CALLBACK_first_interact_sec` DECIMAL(15,2) NULL,
  `AG_COBRANZAS_INBOUND_CALLBACK_last_wrapup_sec` DECIMAL(15,2) NULL,
  `AG_COBRANZAS_INBOUND_CALLBACK_agent_callback_min` DECIMAL(15,2) NOT NULL,
  `AG_FOH_COBRANZAS_ATC_acd_min` DECIMAL(15,2) NOT NULL,
  `AG_FOH_COBRANZAS_ATC_agent_min` DECIMAL(15,2) NOT NULL,
  `AG_FOH_COBRANZAS_ATC_agent_interact_min` DECIMAL(15,2) NOT NULL,
  `AG_FOH_COBRANZAS_ATC_first_interact_sec` DECIMAL(15,2) NULL,
  `AG_FOH_COBRANZAS_ATC_last_wrapup_sec` DECIMAL(15,2) NULL,
  `FOH_TOH_ATC_acd_min` DECIMAL(15,2) NOT NULL,
  `FOH_TOH_ATC_agent_min` DECIMAL(15,2) NOT NULL,
  `FOH_TOH_ATC_agent_interact_min` DECIMAL(15,2) NOT NULL,
  `FOH_TOH_ATC_first_interact_sec` DECIMAL(15,2) NULL,
  `FOH_TOH_ATC_last_wrapup_sec` DECIMAL(15,2) NULL,
  `AG_FOH_ATC_ANEXOS_acd_min` DECIMAL(15,2) NOT NULL,
  `AG_FOH_ATC_ANEXOS_agent_min` DECIMAL(15,2) NOT NULL,
  `AG_FOH_ATC_ANEXOS_agent_interact_min` DECIMAL(15,2) NOT NULL,
  `AG_FOH_ATC_ANEXOS_first_interact_sec` DECIMAL(15,2) NULL,
  `AG_FOH_ATC_ANEXOS_last_wrapup_sec` DECIMAL(15,2) NULL,
  `conclusion_AG_COBRANZAS_INBOUND` VARCHAR(255) NULL,
  `conclusion_AG_COBRANZAS_INBOUND_CALLBACK` VARCHAR(255) NULL,
  `conclusion_AG_FOH_COBRANZAS_ATC` VARCHAR(255) NULL,
  `conclusion_FOH_TOH_ATC` VARCHAR(255) NULL,
  `conclusion_AG_FOH_ATC_ANEXOS` VARCHAR(255) NULL,
  `otras_colas_acd_min` DECIMAL(15,2) NOT NULL,
  `otras_colas_agent_min` DECIMAL(15,2) NOT NULL,
  `otras_colas_agent_interact_min` DECIMAL(15,2) NOT NULL,
  `conclusion_consolidada` VARCHAR(255) NOT NULL,
  `Grupo_Conclusion` VARCHAR(255) NOT NULL,
  `codmes` INT NOT NULL,
  `PREGUNTA` VARCHAR(255) NULL,
  `RESPUESTA` DECIMAL(15,2) NOT NULL,
  `FLG_BUENO` TINYINT NOT NULL,

  -- Metadata fields for historization
  `source_file` VARCHAR(500) NOT NULL,
  `source_type` VARCHAR(100),
  `data_month` DATE NOT NULL,
  `data_year` INT GENERATED ALWAYS AS (YEAR(data_month)) STORED,
  `data_month_num` INT GENERATED ALWAYS AS (MONTH(data_month)) STORED,

  -- Audit fields
  `load_id` BIGINT,
  `load_ts` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  -- Indexes
  INDEX idx_data_month (data_month),
  INDEX idx_source_file (source_file),
  INDEX idx_load_id (load_id),
  INDEX idx_data_year_month (data_year, data_month_num)
,  INDEX idx_nombre_archivo (`nombre_archivo`)
,  INDEX idx_conversation_id (`conversation_id`)
,  INDEX idx_codmes (`codmes`)
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
  first_load_ts TIMESTAMP NULL,
  last_load_ts TIMESTAMP NULL,
  
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