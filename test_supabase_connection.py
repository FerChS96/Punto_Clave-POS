#!/usr/bin/env python3
"""
Script simple para probar la conexión a Supabase
"""

import os
import sys

# Agregar el directorio raíz del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Cargar variables de entorno desde .env
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Variables de entorno cargadas desde .env")
except ImportError:
    print("⚠️ python-dotenv no instalado. Usando variables de entorno del sistema.")

def test_supabase_connection():
    """Probar conexión básica a Supabase"""

    print("🧪 Probando conexión a Supabase...")

    # Verificar si la librería está instalada
    try:
        from supabase import create_client
        print("✅ Librería supabase instalada")
    except ImportError:
        print("❌ Librería supabase NO instalada")
        print("Instala con: pip install supabase")
        return False

    # Verificar variables de entorno
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ROLE_KEY') or os.getenv('SUPABASE_KEY')

    if not supabase_url or not supabase_key:
        print("❌ Variables de entorno no configuradas")
        print("Configura SUPABASE_URL y SUPABASE_KEY")
        print()
        print("Ejemplo:")
        print("set SUPABASE_URL=https://tu-proyecto.supabase.co")
        print("set SUPABASE_KEY=tu_service_role_key")
        print()
        print("O puedes configurar SUPABASE_ROLE_KEY para usar la service role key")
        return False

    print(f"📍 URL: {supabase_url}")
    print(f"🔑 Key: {'*' * 10}...{'*' * 10}")

    try:
        # Intentar crear cliente
        client = create_client(supabase_url, supabase_key)
        print("✅ Cliente de Supabase creado")

        # Intentar una consulta simple
        response = client.table('usuarios').select('id_usuario').limit(1).execute()
        print("✅ Consulta de prueba exitosa")

        return True

    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

if __name__ == "__main__":
    success = test_supabase_connection()
    if success:
        print("\n🎉 ¡Conexión a Supabase funcionando!")
        print("Ahora puedes usar el monitor de entradas.")
    else:
        print("\n❌ Problemas con la conexión a Supabase.")
        print("Revisa la configuración antes de usar el monitor.")

    sys.exit(0 if success else 1)