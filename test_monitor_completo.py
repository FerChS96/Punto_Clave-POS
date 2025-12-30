#!/usr/bin/env python3
"""
Script para probar el monitor de entradas completo con UI simplificada
Simula el comportamiento del POS pero con una interfaz mínima
"""

import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton
from PySide6.QtCore import QTimer, Signal, QObject
from PySide6.QtGui import QFont

# Agregar el directorio raíz del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Cargar variables de entorno desde .env
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Variables de entorno cargadas desde .env")
except ImportError:
    print("⚠️ python-dotenv no instalado. Usando variables de entorno del sistema.")

from utils.monitor_entradas import MonitorEntradas
from services.supabase_service import SupabaseService
from ui.notificacion_entrada_widget import NotificacionEntradaWidget


class TestWindow(QMainWindow):
    """Ventana de prueba simplificada"""

    def __init__(self):
        super().__init__()
        self.notificaciones_activas = []

        self.setWindowTitle("Test Monitor Entradas")
        self.setGeometry(100, 100, 400, 300)

        # Crear widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        title = QLabel("🧪 Monitor de Entradas - Test")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title)

        status_label = QLabel("Esperando conexiones...")
        self.status_label = status_label
        layout.addWidget(status_label)

        # Botón para probar notificación manual
        test_btn = QPushButton("🔔 Probar Notificación Manual")
        test_btn.clicked.connect(self.test_notificacion_manual)
        layout.addWidget(test_btn)

        # Inicializar servicios
        self.init_services()

    def init_services(self):
        """Inicializar servicios de Supabase y monitor"""
        try:
            # Verificar variables de entorno
            supabase_url = os.getenv('SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_ROLE_KEY') or os.getenv('SUPABASE_KEY')

            if not supabase_url or not supabase_key:
                self.status_label.setText("❌ Variables de entorno no configuradas")
                return

            # Supabase service
            self.supabase_service = SupabaseService(url=supabase_url, key=supabase_key)
            if not self.supabase_service.is_connected:
                self.status_label.setText("❌ No se pudo conectar a Supabase")
                return

            self.status_label.setText("✅ Conectado a Supabase")

            # Inicializar monitor
            self.monitor = MonitorEntradas(None, self.supabase_service)
            self.monitor.nueva_entrada_detectada.connect(self.mostrar_notificacion_entrada)

            # Iniciar monitor
            self.monitor.iniciar()
            self.status_label.setText("✅ Monitor iniciado - Esperando entradas...")

        except Exception as e:
            self.status_label.setText(f"❌ Error: {str(e)}")
            print(f"Error inicializando servicios: {e}")
            import traceback
            traceback.print_exc()

    def mostrar_notificacion_entrada(self, entrada_data):
        """Mostrar notificación cuando se detecta una nueva entrada"""
        try:
            print(f"=== RECIBIDA SEÑAL DE NUEVA ENTRADA ===")
            print(f"Datos: {entrada_data}")

            self.status_label.setText("🎉 ¡Nueva entrada detectada!")

            # Usar QTimer.singleShot para diferir la creación al próximo ciclo del event loop
            QTimer.singleShot(0, lambda: self._crear_notificacion_segura(entrada_data))

        except Exception as e:
            print(f"Error en mostrar_notificacion_entrada: {e}")
            import traceback
            traceback.print_exc()

    def _crear_notificacion_segura(self, entrada_data):
        """Crear la notificación de manera segura"""
        try:
            print("Creando notificación segura...")

            # Crear ventana de notificación
            notificacion = NotificacionEntradaWidget(
                miembro_data=entrada_data,
                parent=self,
                duracion=0
            )

            # Posicionar
            self.posicionar_notificacion(notificacion)

            # Conectar señal de cierre
            notificacion.cerrado.connect(lambda: self.remover_notificacion(notificacion))

            # Agregar a lista
            self.notificaciones_activas.append(notificacion)

            # Mostrar
            notificacion.show()

            print("✅ Notificación creada y mostrada")

        except Exception as e:
            print(f"Error creando notificación segura: {e}")
            import traceback
            traceback.print_exc()

    def posicionar_notificacion(self, notificacion):
        """Posicionar notificación"""
        main_geometry = self.geometry()
        margen = 20
        x = main_geometry.right() - notificacion.width() - margen
        y = main_geometry.top() + margen

        offset_vertical = 0
        for notif in self.notificaciones_activas:
            if notif.isVisible():
                offset_vertical += notif.height() + 10

        y += offset_vertical
        notificacion.move(x, y)

    def remover_notificacion(self, notificacion):
        """Remover notificación"""
        if notificacion in self.notificaciones_activas:
            self.notificaciones_activas.remove(notificacion)

    def test_notificacion_manual(self):
        """Probar notificación con datos de ejemplo"""
        datos_prueba = {
            'id_entrada': 999,
            'id_miembro': 1,
            'tipo_acceso': 'miembro',
            'fecha_entrada': '2025-12-29T22:00:00',
            'area_accedida': 'Gimnasio',
            'dispositivo_registro': 'Test Manual',
            'notas': 'Prueba manual',
            'nombres': 'Test',
            'apellido_paterno': 'User',
            'apellido_materno': '',
            'telefono': '555-0000',
            'email': 'test@example.com',
            'codigo_qr': 'TEST123',
            'activo': True,
            'fecha_registro': '2025-01-01',
            'fecha_nacimiento': '1990-01-01',
            'foto': None
        }

        print("Enviando señal manual...")
        self.monitor.nueva_entrada_detectada.emit(datos_prueba)

    def closeEvent(self, event):
        """Al cerrar la ventana"""
        if hasattr(self, 'monitor'):
            self.monitor.detener()
        super().closeEvent(event)


def main():
    """Función principal"""
    app = QApplication(sys.argv)

    # Crear ventana de prueba
    window = TestWindow()
    window.show()

    print("🚀 Aplicación de prueba iniciada")
    print("Inserta una entrada usando test_insertar_entrada.py para probar el monitor")
    print("O usa el botón 'Probar Notificación Manual'")

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())