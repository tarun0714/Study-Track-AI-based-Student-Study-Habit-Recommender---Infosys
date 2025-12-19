from app.database import engine
from sqlalchemy import text

def list_triggers():
    sql = """
    SELECT event_object_table, trigger_name, action_statement
    FROM information_schema.triggers
    """
    with engine.connect() as conn:
        result = conn.execute(text(sql))
        triggers = result.fetchall()
        print(f"Found {len(triggers)} triggers:")
        for t in triggers:
            print(f"Table: {t[0]}, Trigger: {t[1]}")

if __name__ == "__main__":
    list_triggers()
