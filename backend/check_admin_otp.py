
import sys
import os
from sqlalchemy.orm import Session
sys.path.append(os.getcwd())

from app.database import SessionLocal
from app.models import Admin

def get_admin_otp():
    db = SessionLocal()
    try:
        # Assuming only one admin or specific email
        email = "admin@studytrack.com"
        admin = db.query(Admin).filter(Admin.email == email).first()
        if admin:
            print(f"Admin Found: {admin.email}")
            print(f"OTP Code: {admin.otp_code}")
            print(f"Expires At: {admin.otp_expires_at}")
        else:
            print(f"Admin with email {email} not found.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    get_admin_otp()
