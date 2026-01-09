#!/usr/bin/env python3
"""
Script para crear un usuario administrador en PostgreSQL
"""

import sys
import os
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.postgres_manager import PostgresManager
from utils.config import Config

def main():
    """Crear usuario administrador"""
    try:
        # Cargar configuración
        config_obj = Config()
        
        # Validar configuración
        if not config_obj.validate_config():
            logging.error("❌ Configuración de PostgreSQL inválida. Verifique las variables de entorno.")
            return False
        
        # Obtener configuración
        config = config_obj.get_postgres_config()
        logging.info(f"📊 Conectando a PostgreSQL: {config['host']}:{config['port']}/{config['database']}")
        
        # Crear instancia de PostgresManager
        db = PostgresManager(db_config=config)
        
        # La conexión se abre automáticamente en __init__
        logging.info("✅ Conexión exitosa")
        
        # Datos del usuario admin
        username = "admin"
        password = "admin123"
        nombre_completo = "Administrador del Sistema"
        rol = "administrador"
        
        logging.info(f"👤 Creando usuario: {username}")
        logging.info(f"📝 Nombre completo: {nombre_completo}")
        logging.info(f"🔐 Rol: {rol}")
        
        # Crear usuario
        result = db.create_user(
            username=username,
            password=password,
            nombre_completo=nombre_completo,
            rol=rol
        )
        
        if result:
            logging.info("✅ Usuario administrador creado exitosamente")
            logging.info(f"📌 Usuario: {username}")
            logging.info(f"🔑 Contraseña: {password}")
            logging.warning("⚠️  IMPORTANTE: Cambia la contraseña después del primer login")
            return True
        else:
            logging.error("❌ Error al crear el usuario")
            return False
            
    except Exception as e:
        logging.error(f"❌ Error: {e}")
        import traceback
        logging.error(traceback.format_exc())
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
