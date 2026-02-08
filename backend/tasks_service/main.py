from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
import models
from database import get_db, engine
import os
from dotenv import load_dotenv
from datetime import timedelta
from sqlalchemy import func
from typing import Optional, List
from fastapi import Query
from helper import get_or_create_tag
import httpx
from fastapi import Header, HTTPException

# Učitaj environment varijable iz .env fajla
load_dotenv()

app = FastAPI()



# CORS middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=engine)

# Pydantic model for task creation request body
class TaskCreate(BaseModel):
    title: str
    description: str
    tag_names: List[str] = []

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8001")

async def get_current_user(authorization: str = Header(None)):
    """Endpoint which Auth Service call to verify token"""

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")

    token = authorization.replace("Bearer ", "")

    try: 
        async with httpx.AsyncClient() as client:
            print("tokeeeeeeeeeeeeeeeeen",f"{AUTH_SERVICE_URL}/auth/me")

            response = await client.get(
                f"{AUTH_SERVICE_URL}/auth/me", 
                headers={"Authorization": f"Bearer {token}"},
                timeout=5.0
            )

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code,detail="Invalid token")

            user_data = response.json()

            return user_data
            
    except httpx.RequestError:
        raise HTTPException(status_code=500, detail="Failed to connect to Auth Service")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed")

@app.get("/tags", tags=["tags"], summary="Get all tags")
def get_tags(db:Session = Depends(get_db)):
    return db.query(models.Tag).all();

@app.put("/tasks/{task_id}", tags=["tasks"], summary="Ažurira postojeći task")
def update_task(task_id: int, task: TaskCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    
    if not current_user.get("is_verified"):
        raise HTTPException(status_code=403, detail="Email not verified")

    db_task = db.query(models.Task).filter(
        models.Task.id == task_id,
        models.Task.user_id == current_user.get("id")
    ).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found or does not belong to you")
    
    db_task.title = task.title
    db_task.description = task.description
    db.commit()
    db.refresh(db_task)
    return db_task

@app.post("/tasks", tags=["tasks"], summary="Kreira novi task")
def create_task(task: TaskCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user),):
    if not current_user.get("is_verified"):
        raise HTTPException(status_code=403, detail="Email not verified")
  
    new_task = models.Task(
        title=task.title,
        description=task.description,
        user_id=current_user.get("id")
    )

    for name in task.tag_names:
        new_task.tags.append(get_or_create_tag(name, db))

    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@app.get("/tasks/{task_id}", tags=["tasks"], summary="Vraća pojedinačni task")
def read_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    
    if not current_user.get("is_verified"):
        raise HTTPException(status_code=403, detail="Email not verified")
        
    task = db.query(models.Task).filter(
        models.Task.id == task_id,
        models.Task.user_id == current_user.get("id")
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task nije pronađen")
    return task

@app.get("/tasks")
def read_tasks(
    tags: Optional[str] = Query(None, description="Comma separated tags"), 
    mode: str = Query("any", enum=["any", "all"]),
    db: Session = Depends(get_db), 
    current_user: dict = Depends(get_current_user)
):
    # Vrati samo taskove koji pripadaju trenutnom korisniku
    if not current_user.get("is_verified"):
        raise HTTPException(status_code=403, detail="Email not verified")

    tasks = db.query(models.Task).filter(models.Task.user_id == current_user["id"])
    if tags:
        tag_list = [t.strip() for t in tags.split(",") if t.strip()]

        tasks = (tasks.join(models.Task.tags).filter(models.Tag.name.in_(tag_list)))

        if mode == "all":
            tasks = (tasks.group_by(models.Task.id).having(func.count(models.Tag.id) == len(tag_list)))
        else:
            tasks = tasks.distinct()

    tasks.all()

    return [
        {
            "id": t.id,
            "title": t.title,
            "description": t.description,
            "tags": [tag.name for tag in t.tags],
        }
        for t in tasks
    ]