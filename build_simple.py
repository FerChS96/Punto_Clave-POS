#!/usr/bin/env python
"""Script simplificado para generar el .exe"""

import subprocess
import sys
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("🔨 Iniciando construcción del ejecutable...")
print("📍 Directorio:", os.getcwd())
print("📄 Script principal: main.py")

cmd = [
    sys.executable, "-m", "PyInstaller",
    "--onefile",
    "--windowed",
    "--name", "HTF_Gimnasio_POS",
    "--clean",
    "--noconfirm",
    "main.py"
]

# Agregar icono si existe
if os.path.exists("ui/resources/icon.ico"):
    cmd.insert(5, "--icon")
    cmd.insert(6, "ui/resources/icon.ico")

print("\n✓ Comando a ejecutar:")
print(" ".join(cmd))
print("\n" + "="*60)

try:
    result = subprocess.run(cmd, check=True)
    if result.returncode == 0:
        print("\n" + "="*60)
        print("✅ ¡Ejecutable generado exitosamente!")
        print("📦 Ubicación: dist\\HTF_Gimnasio_POS.exe")
        
        if os.path.exists("dist/HTF_Gimnasio_POS.exe"):
            size = os.path.getsize("dist/HTF_Gimnasio_POS.exe") / (1024*1024)
            print(f"📊 Tamaño: {size:.1f} MB")
except subprocess.CalledProcessError as e:
    print(f"\n❌ Error durante la compilación: {e}")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ Error inesperado: {e}")
    sys.exit(1)
