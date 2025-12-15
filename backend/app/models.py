from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime
from sqlalchemy.sql import func


class Student(Base):
    __tablename__ = "students"

    student_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)  # plain for now; can hash later
    role = Column(String, nullable=False, default="student")

    # NEW FIELDS
    is_verified = Column(Boolean, nullable=False, default=False)
    otp_code = Column(String, nullable=True)
    otp_expires_at = Column(DateTime, nullable=True)
    
    cluster_label = Column(String, nullable=True)
    cluster_insights = Column(String, nullable=True)

    logs = relationship("StudyLog", back_populates="student")


class StudyLog(Base):
    __tablename__ = "study_logs"

    log_id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.student_id"), nullable=False)
    date = Column(Date, nullable=False)
    study_hour = Column(Float, nullable=False)
    subject = Column(String, nullable=False)
    method_used = Column(String, nullable=False)
    distraction_time = Column(Float, nullable=False)
    quiz_score = Column(Float, nullable=False)
    day_name = Column(String, nullable=False)

    student = relationship("Student", back_populates="logs")

class Admin(Base):
    __tablename__ = "admins"

    admin_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)

    otp_code = Column(String, nullable=True)
    otp_expires_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
