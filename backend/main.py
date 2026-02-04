from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
import models
from database import get_db, engine
from auth import hash_password, verify_password, create_access_token
from auth import get_current_user

app = FastAPI()

# CORS middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

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
def read_tasks(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.Task).all()

@app.get("/tasks/{task_id}", tags=["tasks"], summary="Vraća pojedinačni task")
def read_task(task_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user),):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Task nije pronađen")
    return task

@app.post("/tasks", tags=["tasks"], summary="Kreira novi task")
def create_task(task: TaskCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user),):
    new_task = models.Task(title=task.title, description=task.description)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@app.put("/tasks/{task_id}", tags=["tasks"], summary="Ažurira postojeći task")
def update_task(task_id: int, task: TaskCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user),):
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not db_task:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Task nije pronađen")
    
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
    # hased_pass = 
    new_user = models.User(email=user.email, hashed_password=hash_password(user.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"id": new_user.id, "email": new_user.email }

@app.post("/auth/login", response_model=Token, tags=["auth"], summary="Login user")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token({"sub": str(db_user.id), "email": db_user.email})
    return Token(access_token=access_token)