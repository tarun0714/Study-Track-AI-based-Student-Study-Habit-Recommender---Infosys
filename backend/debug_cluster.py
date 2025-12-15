
from app.database import SessionLocal
from app import crud

def debug_cluster_data():
    db = SessionLocal()
    try:
        print("Calling get_cluster_data_for_chart...")
        data = crud.get_cluster_data_for_chart(db)
        print("Success:", data)
    except Exception as e:
        print("Error encountered:")
        print(e)
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    debug_cluster_data()
