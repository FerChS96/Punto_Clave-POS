"""
Script de prueba para la ventana de Abrir Turno
Ejecutar directamente para probar el diálogo
"""

import sys
import os
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

from PySide6.QtWidgets import QApplication
from ui.abrir_turno_dialog import AbrirTurnoDialog
from database.postgres_manager import PostgresManager
from utils.config import Config

def main():
    """Función principal"""
    app = QApplication(sys.argv)
    
    try:
        # Inicializar configuración y base de datos
        config = Config()
        db_config = config.get_postgres_config()
        pg_manager = PostgresManager(db_config)
        
        if not pg_manager.initialize_database():
            logging.error("No se pudo conectar a la base de datos")
            return 1
        
        # Datos de usuario de prueba (ajustar según tu usuario)
        user_data = {
            'id_usuario': 2,
            'nombre_usuario': 'admin',
            'nombre_completo': 'Usuario de Prueba',
            'rol': 'administrador'
        }
        
        # Crear y mostrar diálogo
        dialog = AbrirTurnoDialog(pg_manager, user_data)
        
        if dialog.exec():
            turno_id = dialog.get_turno_id()
            logging.info(f"Turno creado con ID: {turno_id}")
            print(f"\n✓ Turno creado exitosamente: ID {turno_id}")
        else:
            logging.info("Usuario canceló la apertura del turno")
            print("\n✗ Apertura de turno cancelada")
        
        return 0
        
    except Exception as e:
        logging.error(f"Error en el script de prueba: {e}")
        print(f"\n✗ Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
