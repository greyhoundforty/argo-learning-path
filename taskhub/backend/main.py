# File: backend/main.py

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from typing import List, Optional
import os
from datetime import datetime
import redis
import json

# Configuration
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@postgres:5432/taskhub")
REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")
REDIS_CACHE_EXPIRE = 60 * 5  # 5 minutes cache

# Initialize FastAPI app
app = FastAPI(title="TaskHub API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Connect to Redis if available
try:
    redis_client = redis.from_url(REDIS_URL)
except:
    redis_client = None
    print("Warning: Redis connection failed. Running without cache.")

# Models
class TaskModel(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

# Pydantic schemas
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

class Task(TaskBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

# Create tables
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Failed to create tables: {e}")
    print("The application will continue, but may not work correctly until the database is available.")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Cache function
def get_cache(key):
    if not redis_client:
        return None
    try:
        data = redis_client.get(key)
        if data:
            return json.loads(data)
    except:
        pass
    return None

def set_cache(key, data, expire=REDIS_CACHE_EXPIRE):
    if not redis_client:
        return
    try:
        redis_client.setex(key, expire, json.dumps(data))
    except:
        pass

def invalidate_cache(key_prefix):
    if not redis_client:
        return
    try:
        for key in redis_client.keys(f"{key_prefix}*"):
            redis_client.delete(key)
    except:
        pass

# API endpoints
@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to TaskHub API"}

@app.get("/tasks", response_model=List[Task], tags=["Tasks"])
async def read_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    cache_key = f"tasks:{skip}:{limit}"
    cached_data = get_cache(cache_key)
    
    if cached_data:
        return cached_data
    
    try:
        tasks = db.query(TaskModel).offset(skip).limit(limit).all()
        
        # Convert SQLAlchemy model instances to dictionaries
        tasks_data = [
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat()
            }
            for task in tasks
        ]
        
        set_cache(cache_key, tasks_data)
        return tasks_data
    except Exception as e:
        print(f"Database error: {e}")
        # Return empty list instead of failing when the DB isn't ready yet
        return []

@app.post("/tasks", response_model=Task, tags=["Tasks"])
async def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    db_task = TaskModel(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    # Invalidate cache
    invalidate_cache("tasks")
    
    return db_task

@app.get("/tasks/{task_id}", response_model=Task, tags=["Tasks"])
async def read_task(task_id: int, db: Session = Depends(get_db)):
    cache_key = f"task:{task_id}"
    cached_data = get_cache(cache_key)
    
    if cached_data:
        return cached_data
    
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task_data = {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "completed": task.completed,
        "created_at": task.created_at.isoformat(),
        "updated_at": task.updated_at.isoformat()
    }
    
    set_cache(cache_key, task_data)
    return task_data

@app.put("/tasks/{task_id}", response_model=Task, tags=["Tasks"])
async def update_task(task_id: int, task: TaskUpdate, db: Session = Depends(get_db)):
    db_task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Update task fields only if they are provided in the request
    task_data = task.dict(exclude_unset=True)
    for key, value in task_data.items():
        setattr(db_task, key, value)
    
    db.commit()
    db.refresh(db_task)
    
    # Invalidate cache
    invalidate_cache("tasks")
    invalidate_cache(f"task:{task_id}")
    
    return db_task

@app.delete("/tasks/{task_id}", tags=["Tasks"])
async def delete_task(task_id: int, db: Session = Depends(get_db)):
    db_task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(db_task)
    db.commit()
    
    # Invalidate cache
    invalidate_cache("tasks")
    invalidate_cache(f"task:{task_id}")
    
    return {"message": "Task deleted successfully"}

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    db_status = True
    redis_status = redis_client is not None
    
    # Check database connection
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
    except Exception:
        db_status = False
    
    # Check Redis connection
    if redis_client:
        try:
            redis_client.ping()
        except Exception:
            redis_status = False
    
    return {
        "status": "healthy" if db_status and redis_status else "unhealthy",
        "database": db_status,
        "redis": redis_status
    }