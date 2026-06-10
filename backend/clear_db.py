import asyncio
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

def clear_db():
    with Session(engine) as session:
        try:
            # Delete all workbooks (this will cascade to other tables)
            session.execute(text("DELETE FROM workbooks;"))
            session.execute(text("DELETE FROM copilot_sessions;"))
            session.commit()
            print("Successfully cleared all data from Supabase tables.")
        except Exception as e:
            session.rollback()
            print(f"Error clearing data: {e}")

if __name__ == "__main__":
    clear_db()
