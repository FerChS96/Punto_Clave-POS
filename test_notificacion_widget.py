#!/usr/bin/env python3
"""
Script para probar el widget de notificación de entrada de miembro

Este script crea y muestra el widget NotificacionEntradaWidget con datos de ejemplo.
El widget se puede cerrar manualmente haciendo clic en el botón "CERRAR" o
automáticamente si se configura una duración.

Uso:
    python test_notificacion_widget.py

Para cambiar los datos del miembro, modifica el diccionario 'miembro_data'.
Para agregar una foto, incluye la clave 'foto' con la ruta absoluta a la imagen.
"""

import sys
import os
from datetime import datetime

# Agregar el directorio raíz del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

from ui.notificacion_entrada_widget import NotificacionEntradaWidget


def main():
    """Función principal para ejecutar el widget de notificación"""

    # Crear aplicación Qt
    app = QApplication(sys.argv)

    # Datos de ejemplo para un miembro
    # Modifica estos datos según necesites para tus pruebas
    miembro_data = {
        'id_miembro': 12345,
        'nombres': 'Juan Carlos',
        'apellido_paterno': 'Pérez',
        'apellido_materno': 'García',
        'telefono': '+52 55 1234 5678',
        'fecha_registro': '2023-01-15'
        # 'foto': 'ruta/absoluta/a/la/foto.jpg'  # Opcional: ruta a una imagen
    }

    # Crear el widget de notificación
    # duracion=5000 significa que se cerrará automáticamente en 5 segundos
    # duracion=0 significa que no se cierra automáticamente
    notificacion = NotificacionEntradaWidget(miembro_data, duracion=0)

    # Conectar señales para depuración (opcional)
    notificacion.cerrado.connect(lambda: print("Notificación cerrada"))
    notificacion.cargo_asignado.connect(lambda data: print(f"Cargo asignado: {data}"))

    # Mostrar el widget
    notificacion.show()

    # Centrar en la pantalla
    screen = app.primaryScreen().geometry()
    widget_geometry = notificacion.geometry()
    x = (screen.width() - widget_geometry.width()) // 2
    y = (screen.height() - widget_geometry.height()) // 2
    notificacion.move(x, y)

    print("Widget de notificación mostrado. Cierra la ventana para terminar el script.")

    # Ejecutar la aplicación
    sys.exit(app.exec())


if __name__ == "__main__":
    main()