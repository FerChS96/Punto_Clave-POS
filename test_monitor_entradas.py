#!/usr/bin/env python3
"""
Script de prueba para el monitor de entradas con Supabase Realtime
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

from utils.monitor_entradas import MonitorEntradas
from services.supabase_service import SupabaseService


def on_nueva_entrada(entrada_data):
    """Manejar nueva entrada detectada"""
    print("¡Nueva entrada detectada!")
    print(f"ID Entrada: {entrada_data.get('id_entrada')}")
    print(f"Miembro: {entrada_data.get('nombres')} {entrada_data.get('apellido_paterno')}")
    print(f"Tipo de acceso: {entrada_data.get('tipo_acceso')}")
    print(f"Fecha: {entrada_data.get('fecha_entrada')}")
    print("-" * 50)


def main():
    """Función principal para probar el monitor de entradas"""

    # Crear aplicación Qt
    app = QApplication(sys.argv)

    try:
        # Inicializar servicios
        print("Inicializando servicios...")

        # Verificar variables de entorno
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_ROLE_KEY') or os.getenv('SUPABASE_KEY')

        # Si no están configuradas, mostrar mensaje de error
        if not supabase_url or not supabase_key:
            print("❌ ERROR: Variables de entorno de Supabase no configuradas")
            print()
            print("Configura las siguientes variables de entorno:")
            print("  SUPABASE_URL=https://tu-proyecto.supabase.co")
            print("  SUPABASE_KEY=tu_service_role_key")
            print("  o SUPABASE_ROLE_KEY=tu_service_role_key")
            print()
            print("Opcionalmente, puedes editar directamente las variables en este archivo:")
            print("  supabase_url = 'tu_url_aqui'")
            print("  supabase_key = 'tu_key_aqui'")
            print()
            print("Obtén tus credenciales en: https://supabase.com/dashboard/project/_/settings/api")
            return 1

        print(f"✅ Variables de entorno encontradas")
        print(f"📍 URL: {supabase_url}")
        print(f"🔑 Key: {'Configurada' if supabase_key else 'No configurada'}")

        # Supabase service con credenciales explícitas
        supabase_service = SupabaseService(url=supabase_url, key=supabase_key)
        if not supabase_service.is_connected:
            print("❌ ERROR: No se pudo conectar a Supabase")
            print("Posibles causas:")
            print("  - URL o KEY incorrectas")
            print("  - Sin conexión a internet")
            print("  - Supabase no disponible")
            print("  - La tabla 'usuarios' no existe o no hay permisos")
            return 1

        print("✅ Conexión a Supabase exitosa")

        # Postgres manager (puede ser None para esta prueba)
        pg_manager = None

        # Crear monitor de entradas
        print("Creando monitor de entradas...")
        monitor = MonitorEntradas(pg_manager, supabase_service)

        # Conectar señal
        monitor.nueva_entrada_detectada.connect(on_nueva_entrada)

        # Iniciar monitor
        print("Iniciando monitor...")
        monitor.iniciar()

        print("✅ Monitor iniciado exitosamente")
        print("Esperando nuevas entradas...")
        print("Para probar, inserta un registro en la tabla 'registro_entradas' de Supabase")
        print("El test terminará automáticamente en 10 segundos")

        # Timer para terminar automáticamente después de 10 segundos
        def terminar_test():
            print("\n⏰ Tiempo de prueba terminado")
            monitor.detener()
            app.quit()

        QTimer.singleShot(10000, terminar_test)  # 10 segundos

        # Ejecutar aplicación
        return app.exec()

    except KeyboardInterrupt:
        print("\nDeteniendo monitor...")
        if 'monitor' in locals():
            monitor.detener()
        print("Monitor detenido.")
        return 0
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())