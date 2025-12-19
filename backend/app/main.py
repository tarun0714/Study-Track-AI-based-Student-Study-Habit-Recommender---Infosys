from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .database import Base, engine, get_db
from . import models, schemas, crud
from .recommender import generate_recommendations
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta, timezone
from .email_utils import send_otp_email



# Create tables in Postgres if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Study Recommendation System API", version="1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost",
        "http://127.0.0.1"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




@app.get("/")
def read_root():
    return {"message": "Welcome to Study Track API. Visit /docs for Swagger UI."}

@app.get("/health")
def health_check():
    return {"status": "ok"}


# ---------- Students ----------

@app.post("/students", response_model=schemas.StudentOut)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    existing = crud.get_student_by_email(db, student.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_student = crud.create_student(db, student)
    return new_student


@app.get("/students", response_model=List[schemas.StudentOut])
def list_students(db: Session = Depends(get_db)):
    return crud.list_students(db)


@app.get("/students/{student_id}", response_model=schemas.StudentOut)
def get_student(student_id: int, db: Session = Depends(get_db)):
    student = crud.get_student_by_id(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


# ---------- Study Logs ----------

@app.post("/study-logs", response_model=schemas.StudyLogOut)
def add_study_log(log: schemas.StudyLogCreate, db: Session = Depends(get_db)):
    student = crud.get_student_by_id(db, log.student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    created_log = crud.create_study_log(db, log)
    return created_log


@app.get("/study-logs/{student_id}", response_model=List[schemas.StudyLogOut])
def get_study_logs(student_id: int, db: Session = Depends(get_db)):
    student = crud.get_student_by_id(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    logs = crud.get_logs_by_student(db, student_id)
    return logs


# ---------- Recommendations (from latest log) ----------

@app.get(
    "/students/{student_id}/recommendation",
    response_model=schemas.RecommendationOut,
)
def get_recommendation(student_id: int, db: Session = Depends(get_db)):
    student = crud.get_student_by_id(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    logs = crud.get_logs_by_student(db, student_id)
    if not logs:
        raise HTTPException(status_code=404, detail="No logs for this student")

    latest = logs[0]  # latest by date desc

    reco = generate_recommendations(
        study_hour=latest.study_hour,
        distraction_time=latest.distraction_time,
        quiz_score=latest.quiz_score,
    )
    return reco

# ---------- Student analytics ----------

@app.get(
    "/students/{student_id}/stats",
    response_model=schemas.StudentStats,
)
def get_student_stats(student_id: int, db: Session = Depends(get_db)):
    student = crud.get_student_by_id(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    stats = crud.get_student_stats(db, student_id)
    if not stats:
        raise HTTPException(
            status_code=404,
            detail="No study logs available for this student",
        )
    return stats


# ---------- Global / admin analytics ----------

@app.get("/admin/stats", response_model=schemas.GlobalStats)
def admin_stats(db: Session = Depends(get_db)):
    return crud.get_global_stats(db)

# ---------- AUTH: Signup with OTP ----------

@app.post("/auth/signup/init", response_model=schemas.SignupInitResponse)
def signup_init(payload: schemas.SignupInitRequest, db: Session = Depends(get_db)):
    existing = crud.get_student_by_email(db, payload.email)
    if existing and existing.is_verified:
        raise HTTPException(status_code=400, detail="Email already registered")

    # create or reuse unverified user
    if not existing:
        student = models.Student(
            name=payload.name,
            email=payload.email,
            username=payload.username,
            password=payload.password,
            role="student",  # signups are students by default
            is_verified=False,
        )
        db.add(student)
        db.flush()  # get student_id
    else:
        student = existing
        student.name = payload.name
        student.username = payload.username
        student.password = payload.password

    # generate OTP
    import random

    otp_code = f"{random.randint(0, 999999):06d}"
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

    student.otp_code = otp_code
    student.otp_expires_at = expires_at


    db.commit()

    # send OTP email
    send_otp_email(payload.email, otp_code, context="signup")

    return schemas.SignupInitResponse(
        message="OTP sent to your email for signup verification."
    )


@app.post("/auth/signup/verify", response_model=schemas.LoginVerifyResponse)
def signup_verify(payload: schemas.OtpVerifyRequest, db: Session = Depends(get_db)):
    student = crud.get_student_by_email(db, payload.email)
    if not student:
        raise HTTPException(status_code=404, detail="User not found")

    if not student.otp_code or not student.otp_expires_at:
        raise HTTPException(status_code=400, detail="No OTP pending for this user")

    # Normalize expiry to UTC-aware before comparing
    expires_at = student.otp_expires_at
    now_utc = datetime.now(timezone.utc)

    if expires_at.tzinfo is None:
    # treat DB value as UTC and make it aware
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if now_utc > expires_at:
        raise HTTPException(status_code=400, detail="OTP expired")


    if payload.otp_code != student.otp_code:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    # mark verified & clear OTP
    student.is_verified = True
    student.otp_code = None
    student.otp_expires_at = None
    db.commit()
    db.refresh(student)

    # Auto-login response
    return schemas.LoginVerifyResponse(
        message="Signup successful",
        student_id=student.student_id,
        role=student.role,
    )



# ---------- AUTH: Login with OTP ----------

@app.post("/auth/login/init", response_model=schemas.SignupInitResponse)
def login_init(payload: schemas.LoginInitRequest, db: Session = Depends(get_db)):
    """
    Start login with OTP. If login_type == 'admin', we check the admins table.
    Otherwise, we check the students table.
    """
    # Decide whether to look in students or admins
    if payload.login_type == "admin":
        user = crud.get_admin_by_email(db, payload.email)
        if not user:
            raise HTTPException(status_code=400, detail="Invalid credentials (admin)")

        # no is_verified check for admins (DB manager controls them)
        if user.password_hash != payload.password:
            raise HTTPException(status_code=400, detail="Invalid credentials (admin)")
    else:
        user = crud.get_student_by_email(db, payload.email)
        if not user:
            raise HTTPException(status_code=400, detail="Invalid credentials")

        if not user.is_verified:
            raise HTTPException(
                status_code=400,
                detail="User not verified. Please complete signup verification.",
            )

        if user.password != payload.password:
            raise HTTPException(status_code=400, detail="Invalid credentials")

    # generate OTP
    import random
    otp_code = f"{random.randint(0, 999999):06d}"
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

    user.otp_code = otp_code
    user.otp_expires_at = expires_at

    db.commit()

    # you can customize context if you like
    send_otp_email(payload.email, otp_code, context="login")

    return schemas.SignupInitResponse(
        message="OTP sent to your email for login verification."
    )


@app.post("/auth/login/verify", response_model=schemas.LoginVerifyResponse)
def login_verify(payload: schemas.LoginOtpVerifyRequest, db: Session = Depends(get_db)):
    """
    Complete login with OTP. Checks students OR admins based on login_type.
    """
    # Pick correct table
    if payload.login_type == "admin":
        user = crud.get_admin_by_email(db, payload.email)
        if not user:
            raise HTTPException(status_code=400, detail="Invalid OTP / user (admin)")

        role = "admin"
        student_id = 0  # not used for admins
    else:
        user = crud.get_student_by_email(db, payload.email)
        if not user:
            raise HTTPException(status_code=400, detail="Invalid OTP / user")

        role = user.role  # should be "student"
        student_id = user.student_id

    # OTP checks
    if not user.otp_code or not user.otp_expires_at:
        raise HTTPException(status_code=400, detail="No OTP pending for this user")

    # Normalize expiry to UTC-aware before comparing
    expires_at = user.otp_expires_at
    now_utc = datetime.now(timezone.utc)

    if expires_at.tzinfo is None:
    # treat DB value as UTC and make it aware
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if now_utc > expires_at:
        raise HTTPException(status_code=400, detail="OTP expired")


    if payload.otp_code != user.otp_code:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    # clear OTP; keep verified flag as-is
    user.otp_code = None
    user.otp_expires_at = None
    db.commit()

    return schemas.LoginVerifyResponse(
        message="Login successful",
        student_id=student_id,
        role=role,
    )

# ---------- Admin: students & logs management ----------

@app.get("/admin/students", response_model=List[schemas.StudentOut])
def admin_list_students(db: Session = Depends(get_db)):
    """
    List all students (for admin panel).
    """
    return crud.list_students(db)


@app.delete("/admin/students/{student_id}")
def admin_delete_student(student_id: int, db: Session = Depends(get_db)):
    """
    Delete a student and all their study logs.
    This is only meant to be used from the admin panel.
    """
    success = crud.delete_student_and_logs(db, student_id)
    if not success:
        raise HTTPException(status_code=404, detail="Student not found")

    return {"message": "Student and related logs deleted successfully."}


@app.get("/admin/logs", response_model=List[schemas.StudyLogOut])
def admin_all_logs(db: Session = Depends(get_db)):
    """
    Return all study logs in the system for global analytics.
    """
    return crud.get_all_logs(db)


# ---------- Clustering (K-Means) ----------

@app.post("/admin/run-clustering")
def run_clustering(db: Session = Depends(get_db)):
    """
    Triggers K-Means clustering logic on all student data.
    """
    from .clustering import apply_clustering
    result = apply_clustering(db)
    return result


@app.get("/admin/cluster-stats", response_model=schemas.ClusterStatsResponse)
def get_cluster_stats(db: Session = Depends(get_db)):
    """
    Returns distribution of students across clusters.
    """
    return crud.get_cluster_stats(db)


@app.get("/admin/cluster-data", response_model=schemas.ClusterDataResponse)
def get_cluster_data(db: Session = Depends(get_db)):
    """
    Returns aggregated data points (Efficiency, Quiz Score, Cluster) for visualization.
    """
    return crud.get_cluster_data_for_chart(db)
