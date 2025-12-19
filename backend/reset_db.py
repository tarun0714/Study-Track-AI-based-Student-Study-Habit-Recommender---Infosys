from app.database import engine, Base
from app.models import StudyLog
from sqlalchemy import text

def reset_table():
    print("Dropping study_logs table...")
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS study_logs CASCADE"))
        conn.commit()
    print("Dropped. Restart backend to recreate.")

if __name__ == "__main__":
    reset_table()
