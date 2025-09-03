# main.py

from fastapi import FastAPI, Depends
from pydantic import BaseModel
from typing import List

# Import SQLAlchemy components
import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

# --- Database Configuration ---

# 1. Define the database URL
DATABASE_URL = "sqlite:///./logit.db"

# 2. Create the SQLAlchemy engine
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# 3. Create a SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Create a Base class for our models
Base = declarative_base()


# --- SQLAlchemy Table Model ---

# This is our SQLAlchemy model that represents the 'logs' table in the database.
class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    section_number = Column(Integer, index=True)
    contractor_type = Column(String)
    objective = Column(String)


# --- Pydantic Data Models (for API input/output) ---

# This Pydantic model is used for creating new entries (doesn't need an ID)
class LogEntryCreate(BaseModel):
    section_number: int
    contractor_type: str
    objective: str

# This Pydantic model is used for reading data from the API (includes the ID)
class LogEntry(LogEntryCreate):
    id: int

    class Config:
        orm_mode = True # This allows the model to read data from ORM objects


# --- FastAPI Application Setup ---

app = FastAPI()

# Create the database tables
# This command looks at all the classes that inherit from Base and creates them in the DB.
Base.metadata.create_all(bind=engine)


# --- Dependency for getting a DB session ---

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


# We use LogEntry for the response_model and LogEntryCreate for the input
@app.post("/logs/", response_model=LogEntry)
async def create_log(log: LogEntryCreate, db: Session = Depends(get_db)):
    """
    Creates a new log entry in the database.
    """
    # Create a new SQLAlchemy Log object from the Pydantic model
    db_log = Log(
        section_number=log.section_number,
        contractor_type=log.contractor_type,
        objective=log.objective
    )
    db.add(db_log)  # Add the new object to the session
    db.commit()     # Commit the transaction to the database
    db.refresh(db_log) # Refresh the object to get the new ID
    return db_log


@app.get("/logs/", response_model=List[LogEntry])
async def get_all_logs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Returns a list of all log entries from the database.
    """
    logs = db.query(Log).offset(skip).limit(limit).all()
    return logs