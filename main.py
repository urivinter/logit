# main.py

# Add HTTPException to the imports
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import List

# Import SQLAlchemy components
import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

# --- Database Configuration (for SQLite) ---

DATABASE_URL = "sqlite:///./logit.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# --- SQLAlchemy Table Model ---

class Log(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True, index=True)
    section_number = Column(Integer, index=True)
    contractor_type = Column(String)
    objective = Column(String)


# --- Pydantic Data Models ---

class LogEntryCreate(BaseModel):
    section_number: int
    contractor_type: str
    objective: str


class LogEntry(LogEntryCreate):
    id: int

    class Config:
        from_attributes = True


# --- FastAPI Application Setup ---

app = FastAPI()
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- API Endpoints ---

@app.get("/")
async def read_root():
    return {"message": "Welcome to the LogIt backend."}


@app.post("/logs/", response_model=LogEntry)
async def create_log(log: LogEntryCreate, db: Session = Depends(get_db)):
    db_log = Log(**log.model_dump())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


@app.get("/logs/", response_model=List[LogEntry])
async def get_all_logs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Log).offset(skip).limit(limit).all()


# --- NEW ENDPOINT ---
@app.get("/logs/{log_id}", response_model=LogEntry)
async def get_log_by_id(log_id: int, db: Session = Depends(get_db)):
    """
    Retrieves a single log entry by its ID.
    """
    db_log = db.query(Log).filter(Log.id == log_id).first()
    if db_log is None:
        raise HTTPException(status_code=404, detail="Log not found")
    return db_log
