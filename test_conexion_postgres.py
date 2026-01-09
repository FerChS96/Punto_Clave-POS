"""
Script de prueba para verificar la conexión a PostgreSQL
"""

import sys
import os

# Agregar el directorio padre al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.postgres_manager import PostgresManager
from utils.config import Config

def test_connection():
    """Probar la conexión a PostgreSQL"""
    print("=" * 60)
    print("Prueba de Conexión a PostgreSQL")
    print("=" * 60)
    
    try:
        # Cargar configuración
        config = Config()
        db_config = config.get_postgres_config()
        
        print(f"\nConfigur ación de conexión:")
        print(f"  Host: {db_config['host']}")
        print(f"  Puerto: {db_config['port']}")
        print(f"  Base de datos: {db_config['database']}")
        print(f"  Usuario: {db_config['user']}")
        print(f"  Contraseña: {'*' * len(db_config['password'])}")
        
        # Crear gestor de base de datos
        print("\n🔄 Intentando conectar...")
        db = PostgresManager(db_config)
        
        # Verificar base de datos
        if db.initialize_database():
            print("✅ Conexión exitosa a PostgreSQL")
            print(f"✅ Base de datos '{db_config['database']}' accesible")
            
            # Probar consulta simple
            total_clientes = db.get_total_members()
            print(f"\n📊 Total de clientes en la base de datos: {total_clientes}")
            
        else:
            print("❌ Error al verificar la base de datos")
            return False
        
        # Cerrar conexión
        db.close()
        print("\n✅ Prueba completada exitosamente")
        return True
        
    except ImportError as e:
        print(f"\n❌ Error de importación: {e}")
        print("\nAsegúrate de que psycopg2-binary esté instalado:")
        print("  pip install psycopg2-binary")
        return False
        
    except Exception as e:
        print(f"\n❌ Error durante la prueba: {e}")
        print("\nVerifica que:")
        print("  1. PostgreSQL esté instalado y ejecutándose")
        print("  2. La base de datos 'pos_sivp' exista")
        print("  3. Las credenciales en .env sean correctas")
        print("  4. El usuario tenga permisos en la base de datos")
        return False

if __name__ == "__main__":
    test_connection()
