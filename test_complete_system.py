#!/usr/bin/env python
"""Final verification that all major POS functionalities work"""

import sys
import os
from datetime import datetime
from decimal import Decimal

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from database.postgres_manager import PostgresManager
from utils.config import Config

def test_all_systems():
    """Test all critical POS systems"""
    
    config = Config()
    db = PostgresManager(config.get_postgres_config())
    
    print("\n" + "="*60)
    print("VERIFICACIÓN COMPLETA DEL SISTEMA POS")
    print("="*60 + "\n")
    
    try:
        # 1. Test Database Connection
        print("1. Verificando conexión a PostgreSQL...")
        if db.is_connected:
            print("   ✅ Conexión exitosa\n")
        else:
            print("   ❌ Conexión fallida\n")
            return False
        
        # 2. Test Client Exists
        print("2. Verificando cliente genérico...")
        clientes = db.query('SELECT id_cliente, nombres FROM clientes WHERE id_cliente = 2')
        if clientes:
            print(f"   ✅ Cliente encontrado: ID 2 - {clientes[0][1] if isinstance(clientes[0], tuple) else clientes[0].get('nombres')}\n")
        else:
            print("   ❌ Cliente no encontrado\n")
            return False
        
        # 3. Test Authentication
        print("3. Verificando autenticación...")
        user = db.authenticate_user('admin', 'admin123')
        if user and user['role'] in ['administrador', 'sistemas']:
            print(f"   ✅ Autenticación exitosa: {user['username']} ({user['role']})\n")
        else:
            print("   ❌ Autenticación fallida\n")
            return False
        
        # 4. Test Open Shift
        print("4. Verificando turno abierto...")
        turno = db.get_turno_activo(1)  # admin id = 1
        if turno:
            print(f"   ✅ Turno abierto: ID {turno['id_turno']}\n")
        else:
            print("   ⚠️  No hay turno abierto (esperado)\n")
        
        # 5. Test Products
        print("5. Verificando productos...")
        productos = db.query('SELECT COUNT(*) as total FROM ca_productos WHERE activo = TRUE')
        if productos:
            total = productos[0][0] if isinstance(productos[0], tuple) else productos[0]['total']
            print(f"   ✅ Productos activos: {total}\n")
        else:
            print("   ❌ Error al contar productos\n")
            return False
        
        # 6. Test Recent Sales
        print("6. Verificando ventas registradas...")
        ventas = db.query("""
            SELECT COUNT(*) as total, SUM(total) as suma_total
            FROM ventas
            WHERE DATE(fecha) = CURRENT_DATE
        """)
        if ventas:
            if isinstance(ventas[0], tuple):
                total_ventas = ventas[0][0]
                suma_total = ventas[0][1]
            else:
                total_ventas = ventas[0]['total']
                suma_total = ventas[0]['suma_total']
            
            print(f"   ✅ Ventas de hoy: {total_ventas}")
            if suma_total:
                print(f"      Total vendido: ${suma_total}\n")
            else:
                print(f"      Total vendido: $0.00\n")
        else:
            print("   ❌ Error al consultar ventas\n")
            return False
        
        # 7. Test Shift Summary
        print("7. Verificando resumen de turno...")
        if turno:
            summary = db.query(f"""
                SELECT 
                    tc.monto_inicial,
                    COALESCE(SUM(v.total), 0) as total_ventas,
                    tc.monto_inicial + COALESCE(SUM(v.total), 0) as monto_esperado
                FROM turnos_caja tc
                LEFT JOIN ventas v ON v.id_turno = tc.id_turno
                WHERE tc.id_turno = {turno['id_turno']}
                GROUP BY tc.monto_inicial
            """)
            if summary:
                if isinstance(summary[0], tuple):
                    monto_inicial = Decimal(str(summary[0][0]))
                    total_ventas = Decimal(str(summary[0][1]))
                    monto_esperado = Decimal(str(summary[0][2]))
                else:
                    monto_inicial = Decimal(str(summary[0]['monto_inicial']))
                    total_ventas = Decimal(str(summary[0]['total_ventas']))
                    monto_esperado = Decimal(str(summary[0]['monto_esperado']))
                
                print(f"   ✅ Resumen del turno:")
                print(f"      Monto inicial: ${monto_inicial}")
                print(f"      Total ventas: ${total_ventas}")
                print(f"      Monto esperado: ${monto_esperado}\n")
            else:
                print("   ⚠️  No hay datos de turno\n")
        
        # 8. Test Inventory
        print("8. Verificando inventario...")
        inventario = db.query("""
            SELECT COUNT(*) as total, SUM(stock_actual) as stock_total
            FROM inventario
            WHERE activo = TRUE
        """)
        if inventario:
            if isinstance(inventario[0], tuple):
                total_items = inventario[0][0]
                stock_total = inventario[0][1]
            else:
                total_items = inventario[0]['total']
                stock_total = inventario[0]['stock_total']
            
            print(f"   ✅ Ubicaciones de inventario: {total_items}")
            print(f"      Stock total: {stock_total} unidades\n")
        else:
            print("   ❌ Error al consultar inventario\n")
            return False
        
        print("="*60)
        print("✅ VERIFICACIÓN COMPLETA - TODOS LOS SISTEMAS OPERATIVOS")
        print("="*60 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error durante verificación: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        db.close()

if __name__ == "__main__":
    success = test_all_systems()
    sys.exit(0 if success else 1)
