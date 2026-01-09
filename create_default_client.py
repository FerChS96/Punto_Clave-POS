#!/usr/bin/env python3
"""
Script para crear cliente genérico de mostrador si no existe
"""

import os
import sys
from datetime import date

os.chdir(os.path.dirname(os.path.abspath(__file__)))

from database.postgres_manager import PostgresManager
from utils.config import Config

config = Config()
db = PostgresManager(config.get_postgres_config())

try:
    # Verificar si existe cliente con id=1
    result = db.query('SELECT id_cliente, nombres FROM clientes WHERE id_cliente = 1')
    
    if result:
        print(f'✓ Cliente 1 ya existe: {result[0][1]}')
    else:
        print('⚠ Cliente 1 NO existe. Creando cliente genérico...')
        # Crear cliente genérico
        import psycopg2.extras
        conn = db.connection
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        try:
            cursor.execute('''
                INSERT INTO clientes (codigo, nombres, apellido_paterno, activo, fecha_registro)
                VALUES (%s, %s, %s, TRUE, %s)
                RETURNING id_cliente
            ''', ('MOSTRADOR', 'Cliente', 'Mostrador', date.today()))
            result = cursor.fetchone()
            cliente_id = result['id_cliente'] if result else 1
            conn.commit()
            print(f'✓ Cliente genérico creado: ID {cliente_id}')
        except Exception as e:
            conn.rollback()
            print(f'✗ Error insertando cliente: {e}')
        finally:
            cursor.close()

    # Listar todos los clientes
    result = db.query('SELECT id_cliente, nombres, apellido_paterno FROM clientes ORDER BY id_cliente LIMIT 10')
    print('\nClientes en la base de datos:')
    for row in result:
        cliente_id = row[0] if isinstance(row, (list, tuple)) else row['id_cliente']
        nombres = row[1] if isinstance(row, (list, tuple)) else row['nombres']
        apellido = row[2] if isinstance(row, (list, tuple)) else row['apellido_paterno']
        print(f'  ID: {cliente_id:2d} - {nombres} {apellido}')

except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()
