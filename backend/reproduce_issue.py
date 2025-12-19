from app.database import SessionLocal
from app import crud, models, schemas
import datetime

def test():
    db = SessionLocal()
    try:
        student_id = 1
        print(f"Testing student_id={student_id}")
        
        # Test 1: Get Student
        s = crud.get_student_by_id(db, student_id)
        print(f"Get student result: {s}")
        if not s:
            print("Student not found!")
            return

        # Test 2: Create Log
        print("Creating log...")
        log_data = schemas.StudyLogCreate(
            student_id=student_id,
            date=datetime.date(2025, 12, 17),
            study_hour=12.0,
            subject="Science",
            method_used="videos",
            distraction_time=80.0,
            quiz_score=90.0,
            day_name="Wednesday"
        )
        # We wrap in try/except to see error
        try:
             # Manually do what create_study_log does to see exactly
             # But let's verify if crud.create_study_log fails
             new_log = crud.create_study_log(db, log_data)
             print(f"Log created: {new_log.log_id}")
        except Exception as e:
            print(f"Create log failed: {e}")
            import traceback
            traceback.print_exc()

        # Test 3: Get Stats
        print("Getting stats...")
        try:
            stats = crud.get_student_stats(db, student_id)
            print(f"Stats: {stats}")
        except Exception as e:
             print(f"Get stats failed: {e}")
             import traceback
             traceback.print_exc()

    finally:
        db.close()

if __name__ == "__main__":
    test()
