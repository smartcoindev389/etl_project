"""
Configuration management for ETL Project
Supports both local and cloud MySQL connections
"""
import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseConfig:
    """Database configuration class"""
    
    # Local MySQL (for development)
    LOCAL_DB = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', 3306)),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', 'root'),
        'database': os.getenv('DB_NAME', 'etl_project')
    }
    
    # Cloud MySQL (update with your cloud provider credentials)
    CLOUD_DB = {
        'host': os.getenv('CLOUD_DB_HOST', ''),
        'port': int(os.getenv('CLOUD_DB_PORT', 3306)),
        'user': os.getenv('CLOUD_DB_USER', ''),
        'password': os.getenv('CLOUD_DB_PASSWORD', ''),
        'database': os.getenv('CLOUD_DB_NAME', 'etl_project')
    }
    
    @staticmethod
    def get_connection_string(use_cloud=False):
        """Get SQLAlchemy connection string"""
        db_config = DatabaseConfig.CLOUD_DB if use_cloud else DatabaseConfig.LOCAL_DB
        
        if use_cloud and not db_config['host']:
            raise ValueError("Cloud database credentials not configured. Please update .env file")
        
        return f"mysql+pymysql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"

class ETLConfig:
    """ETL processing configuration"""
    # CSV file paths configuration
    CSV_BASE_PATH = os.getenv('CSV_BASE_PATH', './data')
    
    # Processing batch size
    BATCH_SIZE = int(os.getenv('BATCH_SIZE', 10000))
    
    # Date format for monthly data
    DATE_FORMAT = '%Y-%m-%d'
    
    # Supported CSV file patterns
    CSV_PATTERNS = {
        'resultados_analisis_completo': 'resultados_analisis_completo*.csv',
        'resultados_analisis_completo_metadata_final_nps': 'resultados_analisis_completo_metadata_final_nps*.csv',
        'flags_resumen_total_con_pagos_atc': 'flags_resumen_total_con_pagos_atc*.csv',
        'flags_resumen_total_con_pagos_galicia': 'flags_resumen_total_con_pagos_galicia*.csv',
        'flags_resumen_total_con_morosidad': 'flags_resumen_total_con_morosidad*.csv',
        'metadata': 'metadata*.csv',
        'speech_analytics': 'speech_analytics*.csv'
    }

