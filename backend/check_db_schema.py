from app.database import engine
from sqlalchemy import inspect

def check_columns():
    insp = inspect(engine)
    columns = insp.get_columns('study_logs')
    col_names = [c['name'] for c in columns]
    print(f"Columns in study_logs: {col_names}")
    if 'day_name' in col_names:
        print("day_name exists.")
    else:
        print("day_name is MISSING.")

if __name__ == "__main__":
    check_columns()
