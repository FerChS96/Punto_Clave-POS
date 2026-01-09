from database.postgres_manager import PostgresManager
from utils.config import Config

config = Config()
db = PostgresManager(config.get_postgres_config())

# Count products
result = db.query('SELECT COUNT(*) as count FROM ca_productos')
print(f'Total productos en base de datos: {result[0]["count"]}')

# Sample products
result = db.query('SELECT codigo_interno, nombre, precio_venta FROM ca_productos ORDER BY id_producto LIMIT 5')
print(f'\nPrimeros 5 productos:')
for row in result:
    print(f'  {row["codigo_interno"]} - {row["nombre"]} (${row["precio_venta"]})')

# Check inventory stock
result = db.query('SELECT COUNT(*) as count FROM inventario')
print(f'\nTotal registros en inventario: {result[0]["count"]}')
