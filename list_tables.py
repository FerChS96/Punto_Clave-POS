from database.postgres_manager import PostgresManager
from utils.config import Config
import psycopg2.extras

config = Config()
db = PostgresManager(config.get_postgres_config())
conn = db.connection
cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

cursor.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public'
    ORDER BY table_name
""")

print('Tables in database:')
for row in cursor.fetchall():
    print(f'  - {row["table_name"]}')

cursor.close()
