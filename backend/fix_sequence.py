from app.database import engine
from sqlalchemy import text

def fix_sequence():
    sql = """
    SELECT setval('study_logs_log_id_seq', (SELECT MAX(log_id) FROM study_logs)+1);
    """
    try:
        with engine.connect() as conn:
            conn.execute(text(sql))
            conn.commit()
            print("Sequence fixed.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_sequence()
