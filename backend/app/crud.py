from sqlalchemy.orm import Session
from . import models, schemas
from sqlalchemy import func

# ---------- Student ----------

def create_student(db: Session, student: schemas.StudentCreate):
    db_student = models.Student(
        name=student.name,
        email=student.email,
        username=student.username,
        password=student.password,
        role=student.role,
    )
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


def get_student_by_email(db: Session, email: str):
    return db.query(models.Student).filter(models.Student.email == email).first()


def get_student_by_id(db: Session, student_id: int):
    return db.query(models.Student).filter(models.Student.student_id == student_id).first()


def list_students(db: Session):
    return db.query(models.Student).all()


# ---------- Study Logs ----------

def create_study_log(db: Session, log: schemas.StudyLogCreate):
    db_log = models.StudyLog(
        student_id=log.student_id,
        date=log.date,
        study_hour=log.study_hour,
        subject=log.subject,
        method_used=log.method_used,
        distraction_time=log.distraction_time,
        quiz_score=log.quiz_score,
        day_name=log.day_name,
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


def get_logs_by_student(db: Session, student_id: int):
    return (
        db.query(models.StudyLog)
        .filter(models.StudyLog.student_id == student_id)
        .order_by(models.StudyLog.date.desc())
        .all()
    )

# ---------- Analytics ----------

def get_student_stats(db: Session, student_id: int) -> schemas.StudentStats | None:
    # basic aggregates
    agg = (
        db.query(
            func.count(models.StudyLog.log_id),
            func.coalesce(func.sum(models.StudyLog.study_hour), 0.0),
            func.coalesce(func.avg(models.StudyLog.study_hour), 0.0),
            func.coalesce(func.avg(models.StudyLog.quiz_score), 0.0),
            func.coalesce(func.avg(models.StudyLog.distraction_time), 0.0),
        )
        .filter(models.StudyLog.student_id == student_id)
        .one()
    )

    total_logs = int(agg[0])
    if total_logs == 0:
        return None

    total_study_hours = float(agg[1])
    avg_study_hours = float(agg[2])
    avg_quiz_score = float(agg[3])
    avg_distraction_time = float(agg[4])

    # logs grouped by subject
    subject_rows = (
        db.query(models.StudyLog.subject, func.count(models.StudyLog.log_id))
        .filter(models.StudyLog.student_id == student_id)
        .group_by(models.StudyLog.subject)
        .all()
    )
    logs_by_subject = {subj: int(count) for subj, count in subject_rows}

    return schemas.StudentStats(
        student_id=student_id,
        total_logs=total_logs,
        total_study_hours=total_study_hours,
        avg_study_hours=avg_study_hours,
        avg_quiz_score=avg_quiz_score,
        avg_distraction_time=avg_distraction_time,
        logs_by_subject=logs_by_subject,
    )


def get_global_stats(db: Session) -> schemas.GlobalStats:
    from .models import Student, StudyLog

    student_count = db.query(func.count(Student.student_id)).scalar() or 0
    log_count = db.query(func.count(StudyLog.log_id)).scalar() or 0

    if log_count == 0:
        return schemas.GlobalStats(
            total_students=int(student_count),
            total_logs=int(log_count),
        )

    agg = (
        db.query(
            func.coalesce(func.avg(StudyLog.study_hour), 0.0),
            func.coalesce(func.avg(StudyLog.quiz_score), 0.0),
            func.coalesce(func.avg(StudyLog.distraction_time), 0.0),
        )
        .one()
    )

    return schemas.GlobalStats(
        total_students=int(student_count),
        total_logs=int(log_count),
        avg_study_hours=float(agg[0]),
        avg_quiz_score=float(agg[1]),
        avg_distraction_time=float(agg[2]),
    )

def get_admin_by_email(db: Session, email: str) -> models.Admin | None:
    return db.query(models.Admin).filter(models.Admin.email == email).first()



def get_all_logs(db: Session) -> list[models.StudyLog]:
  return (
      db.query(models.StudyLog)
      .order_by(models.StudyLog.date.desc())
      .all()
  )


def delete_student_and_logs(db: Session, student_id: int) -> bool:
    """
    Delete a student and all their logs.
    Returns True if deleted, False if not found.
    """
    student = (
        db.query(models.Student)
        .filter(models.Student.student_id == student_id)
        .first()
    )
    if not student:
        return False

    # Delete related logs first (if no ON DELETE CASCADE)
    db.query(models.StudyLog).filter(
        models.StudyLog.student_id == student_id
    ).delete()

    db.delete(student)
    db.commit()
    return True


def get_cluster_stats(db: Session):
    from sqlalchemy import func
    rows = (
        db.query(models.Student.cluster_label, func.count(models.Student.student_id))
        .group_by(models.Student.cluster_label)
        .all()
    )
    
    total = sum([count for _, count in rows])
    stats = []
    
    for label, count in rows:
        if not label:
            label = "Uncategorized"
        stats.append({
            "cluster_label": label,
            "count": count,
            "percentage": round((count / total) * 100, 2) if total > 0 else 0
        })
        
    return {"total_students": total, "clusters": stats}


def get_cluster_data_for_chart(db: Session):
    """
    Returns aggregated data for plotting (e.g. Scatter plot of StudyHour vs QuizScore color by Cluster)
    """
    from sqlalchemy import func
    results = (
        db.query(
            models.Student.student_id,
            models.Student.cluster_label,
            func.avg(models.StudyLog.study_hour).label("avg_hour"),
            func.avg(models.StudyLog.quiz_score).label("avg_score")
        )
        .join(models.StudyLog, models.Student.student_id == models.StudyLog.student_id)
        .group_by(models.Student.student_id)
        .all()
    )
    
    data = []
    for row in results:
        data.append({
            "student_id": row.student_id,
            "cluster_label": row.cluster_label or "Uncategorized",
            "study_hour": round(row.avg_hour, 2),
            "quiz_score": round(row.avg_score, 2)
        })
        
    return {"data": data}
