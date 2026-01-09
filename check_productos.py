from database.postgres_manager import PostgresManager
from utils.config import Config
import psycopg2.extras

config = Config()
db = PostgresManager(config.get_postgres_config())
conn = db.connection
cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

# Check ca_productos columns
cursor.execute("""
    SELECT column_name, data_type, is_nullable
    FROM information_schema.columns
    WHERE table_name = 'ca_productos'
    ORDER BY ordinal_position
""")

print('ca_productos columns:')
for row in cursor.fetchall():
    print(f'  - {row["column_name"]} ({row["data_type"]}) nullable={row["is_nullable"]}')

cursor.close()
