
import sys
import os

# Add current directory to path so we can import app modules
sys.path.append(os.getcwd())

from app.database import SessionLocal
from app import crud

def check_user(email):
    db = SessionLocal()
    try:
        user = crud.get_student_by_email(db, email)
        if user:
            print(f"User FOUND: ID={user.student_id}")
            print(f"Email={user.email}")
            print(f"Password={repr(user.password)}")
            print(f"Verified={user.is_verified}")
        else:
            print("User NOT FOUND")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        email = sys.argv[1]
        check_user(email)
    else:
        print("Please provide an email address.")
