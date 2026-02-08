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
from fastapi import Header, HTTPException
from typing import Optional


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


# models.Base.metadata.create_all(bind=engine)


class UserCreate(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserInfo(BaseModel):
    id: int
    email: str
    is_verified: bool
    role: str

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

@app.get("/auth/me", tags=["auth"], summary="Get current user from token")
def get_current_user_info(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    """Endpoint which Tasks Service call to verify token"""
    print("authorizationnnnnnnnnnnnnnn",authorization)
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    token = authorization.replace("Bearer ", "")

    try: 
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
        user_id: str | None = payload.get("sub")

        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=404, detail="Invalid or expired token")

    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserInfo(id=user.id, email=user.email, is_verified=user.is_verified, role=user.role)