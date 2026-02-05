from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
import models
from database import get_db, engine
from auth import hash_password, verify_password, create_access_token
from auth import get_current_user
import os
from dotenv import load_dotenv
from jose import jwt,JWTError
from datetime import timedelta
from email_utils import send_verification_email
from sqlalchemy import func
from typing import Optional, List
from fastapi import Query
from helper import get_or_create_tag


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

# models.Base.metadata.drop_all(bind=engine)
models.Base.metadata.create_all(bind=engine)

# Dependency to get DB session
# def get_db():
#     db = database.SessionLocal()
#     try: 
#         yield db
#     finally:
#         db.close()

# Pydantic model for task creation request body
class TaskCreate(BaseModel):
    title: str
    description: str
    tag_names: List[str] = []

class UserCreate(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


@app.get("/tasks")
def read_tasks(tags: Optional[str] = Query(None, description="Comma separated tags"), mode: str = Query("any", enum=["any", "all"]),db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Vrati samo taskove koji pripadaju trenutnom korisniku
    if not current_user.is_verified:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Email not verified")

    tasks = db.query(models.Task).filter(models.Task.user_id == current_user.id)
    print("Tags:!!!!!!!!!!!!!!!!!!!!!!", tags)
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
    


@app.get("/tasks/{task_id}", tags=["tasks"], summary="Vraća pojedinačni task")
def read_task(task_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user),):
    
    if not current_user.is_verified:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Email not verified")
        
    task = db.query(models.Task).filter(
        models.Task.id == task_id,
        models.Task.user_id == current_user.id
    ).first()
    if not task:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Task nije pronađen")
    return task

@app.post("/tasks", tags=["tasks"], summary="Kreira novi task")
def create_task(task: TaskCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user),):
#   if not current_user.is_verified:
#         from fastapi import HTTPException
#         raise HTTPException(status_code=403, detail="Email not verified")
  
    new_task = models.Task(
        title=task.title,
        description=task.description,
        user_id=current_user.id
    )

    for name in task.tag_names:
        new_task.tags.append(get_or_create_tag(name, db))

    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@app.get("/tags", tags=["tags"], summary="Get all tags")
def get_tags(db:Session = Depends(get_db)):
    return db.query(models.Tag).all();

@app.put("/tasks/{task_id}", tags=["tasks"], summary="Ažurira postojeći task")
def update_task(task_id: int, task: TaskCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user),):
    
    if not current_user.is_verified:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Email not verified")

    db_task = db.query(models.Task).filter(
        models.Task.id == task_id,
        models.Task.user_id == current_user.id
    ).first()
    if not db_task:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Task not found or does not belong to you")
    
    db_task.title = task.title
    db_task.description = task.description
    db.commit()
    db.refresh(db_task)
    return db_task

@app.post("/auth/signup", tags=["auth"], summary="Register new user")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="User already exists")
   
    print("Password!!!!!!!!!!!!!!!!!!!!!!!:", user.password, type(user.password), len(user.password))
     
    new_user = models.User(email=user.email, hashed_password=hash_password(user.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token(data={"sub": new_user.email, "type": "email_verification"},
        expires_delta=timedelta(hours=1))
    send_verification_email(new_user.email, token)


    return {"id": new_user.id, "email": new_user.email, "message":'Verification email sent' }

@app.post("/auth/login", response_model=Token, tags=["auth"], summary="Login user")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()

    if not db_user.is_verified:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Email not verified")

    if not db_user or not verify_password(user.password, db_user.hashed_password):
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token({"sub": str(db_user.id), "email": db_user.email})
    return Token(access_token=access_token)

@app.get("/auth/verify", tags=["auth"], summary="Verify user email")
def verify_email(token: str, db:Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
        
        if payload.get("type") != "email_verification":
            raise HTTPException(status_code=400, detail="Invalid token type")

        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=400, detail="Invalid token")

    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_verified = True
    db.commit()

    return {"message": "Email successfully verified"}