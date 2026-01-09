#!/usr/bin/env python
"""Verify sales were created in the database"""

import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from database.postgres_manager import PostgresManager
from utils.config import Config

try:
    config = Config()
    db = PostgresManager(config.get_postgres_config())
    
    print("\n=== VERIFICACIÓN DE VENTAS ===\n")
    
    # Obtener la última venta
    ventas = db.query("""
        SELECT 
            v.id_venta, 
            v.numero_ticket, 
            v.fecha,
            v.total, 
            u.nombre_usuario as vendedor,
            c.nombres as cliente
        FROM ventas v
        LEFT JOIN usuarios u ON v.id_vendedor = u.id_usuario
        LEFT JOIN clientes c ON v.id_cliente = c.id_cliente
        ORDER BY v.fecha DESC
        LIMIT 5
    """)
    
    if ventas:
        print("Últimas 5 ventas:")
        for row in ventas:
            venta_id = row[0] if isinstance(row, tuple) else row['id_venta']
            numero_ticket = row[1] if isinstance(row, tuple) else row['numero_ticket']
            fecha = row[2] if isinstance(row, tuple) else row['fecha']
            total = row[3] if isinstance(row, tuple) else row['total']
            vendedor = row[4] if isinstance(row, tuple) else row['vendedor']
            cliente = row[5] if isinstance(row, tuple) else row['cliente']
            
            print(f"\n  Venta ID: {venta_id}")
            print(f"  Ticket: {numero_ticket}")
            print(f"  Fecha: {fecha}")
            print(f"  Total: ${total}")
            print(f"  Vendedor: {vendedor}")
            print(f"  Cliente: {cliente}")
    else:
        print("❌ No hay ventas en la base de datos")
    
    # Obtener detalles de la última venta
    print("\n=== DETALLES DE LA ÚLTIMA VENTA ===\n")
    
    detalles = db.query("""
        SELECT 
            dv.id_detalle,
            p.nombre,
            dv.cantidad,
            dv.precio_unitario,
            dv.subtotal_linea,
            dv.total_linea
        FROM detalles_venta dv
        JOIN ca_productos p ON dv.id_producto = p.id_producto
        WHERE dv.id_venta = (
            SELECT id_venta FROM ventas ORDER BY fecha DESC LIMIT 1
        )
    """)
    
    if detalles:
        for row in detalles:
            nombre = row[1] if isinstance(row, tuple) else row['nombre']
            cantidad = row[2] if isinstance(row, tuple) else row['cantidad']
            precio_unitario = row[3] if isinstance(row, tuple) else row['precio_unitario']
            subtotal_linea = row[4] if isinstance(row, tuple) else row['subtotal_linea']
            total_linea = row[5] if isinstance(row, tuple) else row['total_linea']
            
            print(f"Producto: {nombre}")
            print(f"  Cantidad: {cantidad}")
            print(f"  Precio: ${precio_unitario}")
            print(f"  Subtotal: ${subtotal_linea}")
            print(f"  Total Línea: ${total_linea}\n")
    else:
        print("❌ No hay detalles de ventas")
    
    print("✅ VERIFICACIÓN COMPLETADA")
    db.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
