# File: manager_server.py
from fastapi import FastAPI, Depends
from pydantic import BaseModel
import uvicorn
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# --- 1. Database Setup (SQLAlchemy) ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./tasks.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# --- 2. Database Models (Tables) ---
class TaskDB(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    target_url = Column(String)
    category = Column(String)
    expected_product = Column(String)
    status = Column(String, default="PENDING")  # PENDING, IN_PROGRESS, COMPLETED


class ResultDB(Base):
    __tablename__ = "results"
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    status = Column(String)
    duration_seconds = Column(Float)
    error_message = Column(String, nullable=True)


# Create the tables in the database
Base.metadata.create_all(bind=engine)

# --- 3. FastAPI App & Pydantic Models ---
app = FastAPI(title="Distributed Testing Manager API (DB Enabled)")


class TestResult(BaseModel):
    task_id: int
    status: str
    duration_seconds: float
    error_message: str = None


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --- 4. Initialize Database with dummy tasks ---
def init_db():
    db = SessionLocal()
    # Check if we already have tasks
    if db.query(TaskDB).count() == 0:
        print("SERVER: Initializing database with default tasks...")
        tasks = [
            TaskDB(target_url="https://www.demoblaze.com/", category="Monitors", expected_product="Apple monitor 24"),
            TaskDB(target_url="https://www.demoblaze.com/", category="Phones", expected_product="Samsung galaxy s6"),
            TaskDB(target_url="https://www.demoblaze.com/", category="Laptops", expected_product="Sony vaio i5")
        ]
        db.add_all(tasks)
        db.commit()
    db.close()


init_db()


# --- 5. API Endpoints ---
@app.get("/get-task")
def get_task(db: Session = Depends(get_db)):
    """Worker calls this to get a new pending task."""
    # Find the first task that is PENDING
    task = db.query(TaskDB).filter(TaskDB.status == "PENDING").first()

    if task:
        # Mark as in progress so other workers don't take it
        task.status = "IN_PROGRESS"
        db.commit()
        print(f"SERVER: Assigning Task {task.id} (Category: {task.category}) to a worker.")
        return {
            "task_id": task.id,
            "target_url": task.target_url,
            "category": task.category,
            "expected_product": task.expected_product
        }
    else:
        print("SERVER: No pending tasks available.")
        return {"message": "no_tasks_available"}


@app.post("/submit-result")
def submit_result(result: TestResult, db: Session = Depends(get_db)):
    """Worker calls this to submit the test results."""
    # 1. Update the task status to COMPLETED
    task = db.query(TaskDB).filter(TaskDB.id == result.task_id).first()
    if task:
        task.status = "COMPLETED"

    # 2. Save the result in the Results table
    new_result = ResultDB(
        task_id=result.task_id,
        status=result.status,
        duration_seconds=result.duration_seconds,
        error_message=result.error_message
    )
    db.add(new_result)
    db.commit()

    print(f"\n=== SERVER: Result Saved to DB for Task {result.task_id} ===")
    print(f"Status: {result.status} | Duration: {result.duration_seconds}s")
    print("========================================================\n")

    return {"message": "Result saved successfully"}


if __name__ == "__main__":
    print("Starting Manager Server with Database on port 8080...")
    uvicorn.run(app, host="127.0.0.1", port=8080)