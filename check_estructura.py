#!/usr/bin/env python3
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from database.postgres_manager import PostgresManager
from utils.config import Config

config = Config()
db = PostgresManager(config.get_postgres_config())

resultado = db.query('''
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'ca_productos'
    ORDER BY ordinal_position
''')

print('Columnas de ca_productos:')
for col in resultado:
    print(f'  - {col["column_name"]:30s} ({col["data_type"]})')
