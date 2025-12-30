"""
Configuración de la aplicación POS HTF
"""

import os
from dotenv import load_dotenv

class Config:
    def __init__(self):
        # Cargar variables de entorno
        load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'), encoding='utf-8')
        
        # Configuración de la base de datos SQLite
        self.DATABASE_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'pos_htf.db')
        
        # Configuración de Supabase
        self.SUPABASE_URL = os.getenv('SUPABASE_URL', '')
        self.SUPABASE_KEY = os.getenv('SUPABASE_KEY', '')
        # SUPABASE_ROLE_KEY bypasea RLS; fallback a SUPABASE_KEY si no existe
        self.SUPABASE_ROLE_KEY = os.getenv('SUPABASE_ROLE_KEY', os.getenv('SUPABASE_KEY', ''))
        
        # Configuración de la aplicación
        self.APP_NAME = "HTF Gimnasio POS"
        self.APP_VERSION = "1.0.0"
        
        # Configuración de sincronización
        self.SYNC_INTERVAL = 300  # 5 minutos en segundos
        self.OFFLINE_MODE = True
        
        # Configuración de UI
        self.THEME_COLOR = "#2E86AB"
        self.SECONDARY_COLOR = "#A23B72"
        self.BACKGROUND_COLOR = "#F18F01"
        self.TEXT_COLOR = "#C73E1D"
        
        # Configuración de la base de datos PostgreSQL
        self.DB_HOST = os.getenv('DB_HOST', 'localhost')
        self.DB_PORT = os.getenv('DB_PORT', '5432')
        self.DB_NAME = os.getenv('DB_NAME', 'htf_gimnasio')
        self.DB_USER = os.getenv('DB_USER', 'postgres')
        # Eliminar comillas si las hay
        password = os.getenv('DB_PASSWORD', 'password')
        self.DB_PASSWORD = password.strip('"\'') if password else 'password'

    def validate_config(self):
        """Validar configuración básica"""
        required_vars = ['SUPABASE_URL', 'SUPABASE_KEY']
        missing_vars = []
        
        for var in required_vars:
            if not getattr(self, var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"Advertencia: Variables de entorno faltantes: {', '.join(missing_vars)}")
            print("La aplicación funcionará en modo offline únicamente.")
            self.OFFLINE_MODE = True
        
        return len(missing_vars) == 0
    
    def get_database_path(self):
        """Obtener ruta completa de la base de datos"""
        return os.path.abspath(self.DATABASE_PATH)
    
    def get_postgres_config(self):
        """Obtener configuración de PostgreSQL como diccionario"""
        return {
            'host': self.DB_HOST,
            'port': self.DB_PORT,
            'database': self.DB_NAME,
            'user': self.DB_USER,
            'password': self.DB_PASSWORD
        }