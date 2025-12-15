
import pandas as pd
import os
from app.database import SessionLocal, engine, Base
from app.models import Student, StudyLog
from sqlalchemy.exc import IntegrityError

# CSV Paths
STUDENTS_CSV = "../data/students.csv"
LOGS_CSV = "../data/study_logs.csv"

def seed_data():
    # Create tables if not exist (though main app likely did it)
    Base.metadata.create_all(bind=engine)

    print("Connecting to database...")
    db = SessionLocal()

    # Load Students
    if os.path.exists(STUDENTS_CSV):
        print(f"Loading students from {STUDENTS_CSV}...")
        try:
            df_students = pd.read_csv(STUDENTS_CSV)
            count = 0
            for _, row in df_students.iterrows():
                # Check if exists by ID
                existing = db.query(Student).filter(Student.student_id == row['student_id']).first()
                if existing:
                    continue
                
                # Check if exists by Email or Username (to avoid unique constraint fail)
                existing_email = db.query(Student).filter(Student.email == row['email']).first()
                if existing_email:
                    print(f"Skipping student {row['student_id']}: Email {row['email']} already exists.")
                    continue

                existing_user = db.query(Student).filter(Student.username == row['username']).first()
                if existing_user:
                    print(f"Skipping student {row['student_id']}: Username {row['username']} already exists.")
                    continue

                student = Student(
                    student_id=row['student_id'],
                    name=row['name'],
                    email=row['email'],
                    username=row['username'],
                    password=str(row['password']),
                    role=row['role'],
                    is_verified=True
                )
                db.add(student)
                try:
                    db.commit()
                    count += 1
                except Exception as e:
                    db.rollback()
                    print(f"Error adding student {row['student_id']}: {e}")
            
            print(f"Loaded {count} new students.")
        except Exception as e:
            db.rollback()
            print(f"Failed to load students: {e}")
    else:
        print(f"Student CSV not found at {STUDENTS_CSV}")

    # Load Logs
    if os.path.exists(LOGS_CSV):
        print(f"Loading logs from {LOGS_CSV}...")
        try:
            df_logs = pd.read_csv(LOGS_CSV)
            count = 0
            for _, row in df_logs.iterrows():
                existing = db.query(StudyLog).filter(StudyLog.log_id == row['log_id']).first()
                if existing:
                    continue

                # Verify student exists before adding log
                student_exists = db.query(Student).filter(Student.student_id == row['student_id']).first()
                if not student_exists:
                    # try to find by other means? no, just skip
                    # print(f"Skipping log {row['log_id']}: Student {row['student_id']} not found.")
                    continue

                log = StudyLog(
                    log_id=row['log_id'],
                    student_id=row['student_id'],
                    date=pd.to_datetime(row['date']).date(),
                    study_hour=row['study_hour'],
                    subject=row['subject'],
                    method_used=row['method_used'],
                    distraction_time=row['distraction_time'],
                    quiz_score=row['quiz_score'],
                    day_name=row['day_name']
                )
                db.add(log)
                try:
                    db.commit()
                    count += 1
                except Exception as e:
                    db.rollback()
                    print(f"Error adding log {row['log_id']}: {e}")
            
            print(f"Loaded {count} new logs.")
        except Exception as e:
            db.rollback()
            print(f"Failed to load logs: {e}")
    else:
        print(f"Logs CSV not found at {LOGS_CSV}")

    db.close()
    print("Seeding complete.")

if __name__ == "__main__":
    seed_data()
