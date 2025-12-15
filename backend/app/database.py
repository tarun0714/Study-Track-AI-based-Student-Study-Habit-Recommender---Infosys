import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Find project root and load .env
APP_DIR = os.path.dirname(os.path.abspath(__file__))            # .../backend/app
BACKEND_DIR = os.path.dirname(APP_DIR)                          # .../backend
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)                     # .../Study_track
ENV_PATH = os.path.join(PROJECT_ROOT, ".env")

load_dotenv(ENV_PATH)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:khushi31@localhost:5432/study_reco_db",
)

connect_args = {}
if "sqlite" in DATABASE_URL:
    connect_args["check_same_thread"] = False

engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
