#!/usr/bin/env python
"""Script para generar el .exe - Modo rápido sin --onefile"""

import subprocess
import sys
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("🔨 Iniciando construcción DEL EJECUTABLE (modo distribuible)...")
print("📍 Directorio:", os.getcwd())
print("📄 Script principal: main.py")
print()

# Primero intentar con onedir (más rápido que onefile para desarrollo)
cmd = [
    sys.executable, "-m", "PyInstaller",
    "--onedir",  # En vez de onefile
    "--windowed",
    "--name", "HTF_Gimnasio_POS",
    "--distpath", "dist_app",
    "--workpath", "build_app",  # workpath es el correcto
    "--specpath", "spec_app",
    "--clean",
    "--noconfirm",
    "main.py"
]

print("✓ Comando a ejecutar:")
print(" ".join(cmd))
print("\n" + "="*60 + "\n")

try:
    result = subprocess.run(cmd, check=True)
    if result.returncode == 0:
        print("\n" + "="*60)
        print("✅ ¡Ejecutable generado exitosamente!")
        print("📦 Ubicación: dist_app\\HTF_Gimnasio_POS\\")
        
        if os.path.exists("dist_app/HTF_Gimnasio_POS/HTF_Gimnasio_POS.exe"):
            size = os.path.getsize("dist_app/HTF_Gimnasio_POS/HTF_Gimnasio_POS.exe") / (1024*1024)
            print(f"📊 Tamaño del .exe: {size:.1f} MB")
            print("\nℹ️ Para distribución: copia la carpeta 'dist_app/HTF_Gimnasio_POS/' completa")
except subprocess.CalledProcessError as e:
    print(f"\n❌ Error durante la compilación: {e}")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ Error inesperado: {e}")
    sys.exit(1)
