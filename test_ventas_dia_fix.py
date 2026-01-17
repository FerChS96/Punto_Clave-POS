#!/usr/bin/env python3
"""
Script de prueba para verificar que VentasDiaWindow recibe turno_id correctamente
y puede consultar las ventas del turno.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.postgres_manager import PostgresManager
from utils.config import Config
from ui.ventas.ventas_dia import VentasDiaWindow

def test_ventas_dia_window():
    """Prueba que VentasDiaWindow funciona con turno_id correcto"""

    # Configurar base de datos
    config = Config()
    db_config = config.get_postgres_config()
    pg_manager = PostgresManager(db_config)

    try:
        # Obtener turno activo para usuario admin (id=1)
        turno = pg_manager.get_turno_activo(1)
        print(f"Turno activo encontrado: {turno}")

        if not turno:
            print("❌ No hay turno activo. Creando uno para prueba...")
            # Crear un turno de prueba
            pg_manager.ejecutar_query("""
                INSERT INTO ca_turnos (id_usuario, fecha_apertura, cerrado)
                VALUES (1, NOW(), false)
                RETURNING id_turno
            """)
            turno_id = pg_manager.ejecutar_query("SELECT lastval()")[0]['lastval']
            print(f"✅ Turno de prueba creado con ID: {turno_id}")
        else:
            turno_id = turno['id_turno']
            print(f"✅ Usando turno existente ID: {turno_id}")

        # Datos de usuario de prueba
        user_data = {
            'id_usuario': 1,
            'nombre_completo': 'Admin Test',
            'usuario': 'admin'
        }

        # Crear VentasDiaWindow con parámetros correctos
        print("Creando VentasDiaWindow...")
        ventas_window = VentasDiaWindow(
            pg_manager,           # pg_manager
            None,                 # supabase_service (deshabilitado)
            user_data,            # user_data
            turno_id,             # turno_id
            None                  # parent
        )

        print(f"✅ VentasDiaWindow creado exitosamente con turno_id: {ventas_window.turno_id}")

        # Intentar actualizar datos (esto debería consultar las ventas)
        print("Actualizando datos de ventas...")
        ventas_window.actualizar_datos()

        print("✅ Prueba completada exitosamente")

    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()

    finally:
        pg_manager.close()

if __name__ == "__main__":
    test_ventas_dia_window()