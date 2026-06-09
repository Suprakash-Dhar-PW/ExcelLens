import os
import sys
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker

# Set up paths
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
sys.path.insert(0, backend_dir)

from dotenv import load_dotenv
load_dotenv(override=True)

PG_DATABASE_URL = os.getenv("DATABASE_URL")
SQLITE_DATABASE_URL = "sqlite:///./dashboard.db"

if not PG_DATABASE_URL:
    print("No DATABASE_URL found for Postgres. Exiting.")
    sys.exit(1)

print(f"Connecting to Postgres: {PG_DATABASE_URL.split('@')[1]}")
print("Connecting to SQLite: dashboard.db")

pg_engine = create_engine(PG_DATABASE_URL)
sqlite_engine = create_engine(SQLITE_DATABASE_URL)

pg_meta = MetaData()
pg_meta.reflect(bind=pg_engine)

sqlite_meta = MetaData()
sqlite_meta.reflect(bind=sqlite_engine)

# To respect foreign key constraints, order matters.
TABLES_IN_ORDER = [
    'workbooks',
    'executive_summary',
    'daily_performance',
    'category_performance',
    'offering_performance',
    'batch_performance',
    'leader_performance',
    'copilot_sessions',
    'copilot_messages'
]

with pg_engine.connect() as pg_conn:
    with sqlite_engine.connect() as sqlite_conn:
        for table_name in TABLES_IN_ORDER:
            if table_name not in sqlite_meta.tables or table_name not in pg_meta.tables:
                continue
            
            sqlite_table = sqlite_meta.tables[table_name]
            pg_table = pg_meta.tables[table_name]
            
            print(f"Migrating table: {table_name}...")
            
            # Count records
            count_query = sqlite_table.select()
            records = sqlite_conn.execute(count_query).fetchall()
            
            if not records:
                print(f"  -> 0 records found in SQLite. Skipping.")
                continue
            
            # Convert to list of dicts
            data_to_insert = [dict(row._mapping) for row in records]
            print(f"  -> {len(data_to_insert)} records found in SQLite. Inserting into Postgres...")
            
            try:
                pg_conn.execute(pg_table.insert(), data_to_insert)
                pg_conn.commit()
                print(f"  -> Successfully migrated {table_name}")
            except Exception as e:
                pg_conn.rollback()
                print(f"  -> Error migrating {table_name}: {e}")

print("Migration script completed.")
