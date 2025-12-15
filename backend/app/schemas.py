from datetime import date
from pydantic import BaseModel, EmailStr, Field
from typing import List
from typing import Dict, Optional
from typing import Literal

LoginType = Literal["student", "admin"]

# ---------- Student ----------

class StudentBase(BaseModel):
    name: str
    email: EmailStr
    username: str
    role: str = "student"


class StudentCreate(StudentBase):
    password: str


class StudentOut(StudentBase):
    student_id: int
    cluster_label: Optional[str] = None
    cluster_insights: Optional[str] = None

    class Config:
        from_attributes = True


# ---------- Study Logs ----------

class StudyLogBase(BaseModel):
    student_id: int
    date: date
    study_hour: float = Field(..., ge=0)
    subject: str
    method_used: str
    distraction_time: float = Field(..., ge=0)
    quiz_score: float = Field(..., ge=0, le=100)
    day_name: str


class StudyLogCreate(StudyLogBase):
    pass


class StudyLogOut(StudyLogBase):
    log_id: int

    class Config:
        from_attributes = True


# ---------- Recommendations ----------

# ---------- Recommendations & Clustering ----------

class RecommendationOut(BaseModel):
    cluster_id: int
    cluster_profile: str
    recommendations: List[str]

class ClusterStat(BaseModel):
    cluster_label: str
    count: int
    percentage: float

class ClusterStatsResponse(BaseModel):
    total_students: int
    clusters: List[ClusterStat]

class ClusterDataPoint(BaseModel):
    student_id: int
    study_hour: float
    quiz_score: float
    cluster_label: str

class ClusterDataResponse(BaseModel):
    data: List[ClusterDataPoint]

class StudentStats(BaseModel):
    student_id: int
    total_logs: int
    total_study_hours: float
    avg_study_hours: float
    avg_quiz_score: float
    avg_distraction_time: float
    logs_by_subject: Dict[str, int]


class GlobalStats(BaseModel):
    total_students: int
    total_logs: int
    avg_study_hours: Optional[float] = None
    avg_quiz_score: Optional[float] = None
    avg_distraction_time: Optional[float] = None
    

# ---------- Auth / OTP ----------

class SignupInitRequest(BaseModel):
    name: str
    email: EmailStr
    username: str
    password: str


class SignupInitResponse(BaseModel):
    message: str


class LoginInitRequest(BaseModel):
    email: EmailStr
    password: str
    login_type: LoginType = "student"  # "student" or "admin"


class LoginOtpVerifyRequest(BaseModel):
    email: EmailStr
    otp_code: str
    login_type: LoginType = "student"


class LoginVerifyResponse(BaseModel):
    message: str
    student_id: int
    role: str  # "student" or "admin"

class OtpVerifyRequest(BaseModel):
    email: EmailStr
    otp_code: str


class LoginVerifyResponse(BaseModel):
    message: str
    student_id: int
    role: str
