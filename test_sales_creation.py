#!/usr/bin/env python
"""Test script to verify sales creation with default client"""

import logging
import sys
import os
from datetime import datetime
from decimal import Decimal

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Add POS_SIVP to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from database.postgres_manager import PostgresManager

# Database config
db_config = {
    'host': 'localhost',
    'port': '5432',
    'database': 'pos_sivp',
    'user': 'postgres',
    'password': 'postgres123'
}

try:
    db = PostgresManager(db_config)
    
    print("\n=== TEST: Verificar cliente genérico ===")
    clientes = db.query('SELECT id_cliente, nombres FROM clientes WHERE id_cliente = 2')
    if clientes:
        print(f"✓ Cliente genérico encontrado: ID 2 - {clientes[0][1]}")
    else:
        print("✗ Cliente genérico NO encontrado")
    
    print("\n=== TEST: Obtener productos disponibles ===")
    productos = db.query('''
        SELECT id_producto, nombre, precio_venta, codigo_interno 
        FROM ca_productos 
        WHERE activo = TRUE 
        LIMIT 5
    ''')
    
    if productos:
        print(f"Productos disponibles:")
        for p in productos:
            print(f"  ID {p[0]}: {p[1]} - ${p[2]} ({p[3]})")
        
        print("\n=== TEST: Crear venta de prueba ===")
        
        # Preparar datos de venta
        venta_data = {
            'id_usuario': 1,  # admin
            'id_turno': 1,    # turno abierto
            'productos': [
                {
                    'id_producto': productos[0][0],
                    'cantidad': 2,
                    'precio': Decimal(str(productos[0][2]))
                }
            ],
            'subtotal': Decimal('100'),
            'iva': Decimal('16'),
            'total': Decimal('116'),
            'descuento': Decimal('0'),
            'metodo_pago': 'efectivo',
            'tipo_venta': 'producto',
            # No especificamos id_cliente - debe usar 2 por defecto
        }
        
        result = db.create_sale(venta_data)
        print(f"\n✓ Venta creada exitosamente!")
        print(f"  ID Venta: {result['id_venta']}")
        print(f"  Ticket: {result['numero_ticket']}")
        print(f"  Total: ${result['total']}")
        
        print("\n=== TEST: Verificar venta en base de datos ===")
        ventas = db.query(f'''
            SELECT id_venta, numero_ticket, id_cliente, total, fecha
            FROM ventas
            WHERE id_venta = %s
        ''', (result['id_venta'],))
        
        if ventas:
            v = ventas[0]
            print(f"✓ Venta registrada en base de datos:")
            print(f"  ID: {v[0]}")
            print(f"  Ticket: {v[1]}")
            print(f"  Cliente ID: {v[2]}")
            print(f"  Total: ${v[3]}")
            print(f"  Fecha: {v[4]}")
        else:
            print("✗ Venta NO encontrada en base de datos")
            
    else:
        print("✗ No hay productos disponibles")
    
    print("\n✅ TEST COMPLETADO")
    db.close()
    
except Exception as e:
    print(f"❌ Error durante test: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
