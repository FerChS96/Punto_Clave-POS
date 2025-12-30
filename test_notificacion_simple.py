#!/usr/bin/env python3
"""
Script para probar la notificación de entrada sin ejecutar todo el POS
"""

import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

# Agregar el directorio raíz del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Cargar variables de entorno desde .env
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Variables de entorno cargadas desde .env")
except ImportError:
    print("⚠️ python-dotenv no instalado. Usando variables de entorno del sistema.")

from ui.notificacion_entrada_widget import NotificacionEntradaWidget


def test_notificacion():
    """Probar la creación de la notificación con datos de prueba"""

    # Datos de prueba similares a los que envía el monitor
    datos_prueba = {
        'id_entrada': 82,
        'id_miembro': 1,
        'tipo_acceso': 'miembro',
        'fecha_entrada': '2025-12-29T21:57:12',
        'area_accedida': 'Gimnasio',
        'dispositivo_registro': 'Test Script',
        'notas': 'Entrada de prueba generada automáticamente',
        'nombres': 'Admin',
        'apellido_paterno': 'HTF',
        'apellido_materno': '',
        'telefono': '555-1234',
        'email': 'admin@htf.com',
        'codigo_qr': 'QR123456',
        'activo': True,
        'fecha_registro': '2025-01-01',
        'fecha_nacimiento': '1990-01-01',
        'foto': None
    }

    print("🧪 Probando creación de notificación de entrada...")
    print(f"Datos de prueba: {datos_prueba}")

    try:
        # Crear aplicación Qt
        app = QApplication(sys.argv)

        # Crear notificación
        print("Creando NotificacionEntradaWidget...")
        notificacion = NotificacionEntradaWidget(
            miembro_data=datos_prueba,
            parent=None,
            duracion=0
        )

        print("✅ Notificación creada exitosamente")

        # Mostrar notificación
        print("Mostrando notificación...")
        notificacion.show()

        print("✅ Notificación mostrada exitosamente")

        # Cerrar automáticamente después de 3 segundos
        QTimer.singleShot(3000, lambda: app.quit())

        # Ejecutar aplicación
        print("Ejecutando aplicación Qt...")
        return app.exec()

    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(test_notificacion())