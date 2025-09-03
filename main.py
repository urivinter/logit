# main.py

# 1. Import necessary tools
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List


# 2. Define your data model using Pydantic
# This tells FastAPI what kind of data to expect.
# It also provides automatic data validation.
class LogEntry(BaseModel):
    section_number: int
    contractor_type: str
    objective: str
    # We can add more fields here later, like a timestamp.


# 3. Create an instance of the FastAPI class
app = FastAPI()

# 4. Create an in-memory "database"
# This is just a Python list that will store our logs for now.
db_logs: List[LogEntry] = []


# --- API Endpoints ---

@app.get("/")
async def read_root():
    """ The root endpoint, provides a welcome message. """
    return {"message": "Hello, World! Welcome to the LogIt backend."}


@app.post("/logs/", response_model=LogEntry)
async def create_log(log: LogEntry):
    """
    Receives a new log entry and saves it to our in-memory database.
    The 'log: LogEntry' part tells FastAPI to expect a JSON object
    that matches the structure of our LogEntry model.
    """
    db_logs.append(log)
    return log


@app.get("/logs/", response_model=List[LogEntry])
async def get_all_logs():
    """
    Returns a list of all log entries currently in our database.
    """
    return db_logs
