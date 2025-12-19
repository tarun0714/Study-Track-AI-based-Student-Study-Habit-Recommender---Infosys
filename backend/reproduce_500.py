from app.database import SessionLocal
from app import crud, models, schemas
import datetime

def test():
    db = SessionLocal()
    try:
        student_id = 1
        print(f"Testing student_id={student_id}")
        
        # Test 2: Create Log via CRUD directly
        print("Creating log...")
        log_data = schemas.StudyLogCreate(
            student_id=student_id,
            date=datetime.date(2025, 12, 17),
            study_hour=5.0,
            subject="English",
            method_used="videos",
            distraction_time=50.0,
            quiz_score=88.0,
            day_name="Tuesday"
        )
        try:
             # Manually do create stuff
             db_log = models.StudyLog(
                student_id=student_id,
                date=log_data.date,
                study_hour=log_data.study_hour,
                subject=log_data.subject,
                method_used=log_data.method_used,
                distraction_time=log_data.distraction_time,
                quiz_score=log_data.quiz_score,
                day_name=log_data.day_name,
            )
             db.add(db_log)
             print("Added to session")
             db.commit()
             print("Committed")
             db.refresh(db_log)
             print(f"Refreshed: {db_log.log_id}")
        except Exception as e:
            print(f"Create log failed: {e}")
            import traceback
            traceback.print_exc()

    finally:
        db.close()

if __name__ == "__main__":
    test()
