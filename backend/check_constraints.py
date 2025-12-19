from app.database import engine
from sqlalchemy import text

def list_constraints():
    sql = """
    SELECT conname, contype, pg_get_constraintdef(oid)
    FROM pg_constraint
    WHERE conrelid = 'study_logs'::regclass
    """
    try:
        with engine.connect() as conn:
            result = conn.execute(text(sql))
            constraints = result.fetchall()
            print(f"Found {len(constraints)} constraints:")
            for c in constraints:
                print(f"Name: {c[0]}, Type: {c[1]}, Def: {c[2]}")
    except Exception as e:
        print(e)

if __name__ == "__main__":
    list_constraints()
