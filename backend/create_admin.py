
from app.database import SessionLocal
from app.models import Admin

def create_admin():
    db = SessionLocal()
    
    email = "admin@studytrack.com"
    username = "admin"
    password = "admin"  # Stored as plain text in 'password_hash' column per current implementation

    existing = db.query(Admin).filter(Admin.email == email).first()
    if existing:
        print(f"Admin already exists: {email}")
        return

    new_admin = Admin(
        name="System Admin",
        email=email,
        username=username,
        password_hash=password 
    )
    
    db.add(new_admin)
    db.commit()
    print(f"Admin created successfully.\nEmail: {email}\nPassword: {password}")
    db.close()

if __name__ == "__main__":
    create_admin()
