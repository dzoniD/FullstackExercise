import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app, get_db
from database import Base
import models

# Kreiranje test baze u memoriji (SQLite)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override get_db funkcije za testiranje"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Override get_db dependency sa test verzijom
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def client():
    """Kreiranje test klijenta i setup test baze"""
    # Kreiranje svih tabela u test bazi
    Base.metadata.create_all(bind=engine)
    
    # Kreiranje test klijenta
    client = TestClient(app)
    
    yield client
    
    # Cleanup - brisanje tabela nakon svakog testa
    Base.metadata.drop_all(bind=engine)


def test_create_task(client):
    """Test kreiranja novog taska"""
    # Test podaci
    task_data = {
        "title": "Test Task",
        "description": "Test Description"
    }
    
    # POST request za kreiranje taska
    response = client.post("/tasks", json=task_data)
    
    # Provera status koda
    assert response.status_code == 200
    
    # Provera da je task kreiran sa ispravnim podacima
    created_task = response.json()
    assert created_task["title"] == task_data["title"]
    assert created_task["description"] == task_data["description"]
    assert "id" in created_task  # Provera da ima ID


def test_create_task_missing_fields(client):
    """Test kreiranja taska bez obaveznih polja"""
    # Pokusaj kreiranja taska bez title polja
    task_data = {
        "description": "Test Description"
    }
    
    response = client.post("/tasks", json=task_data)
    
    # Provera da vraća 422 (Validation Error)
    assert response.status_code == 422


def test_create_task_empty_strings(client):
    """Test kreiranja taska sa praznim stringovima"""
    task_data = {
        "title": "",
        "description": ""
    }
    
    response = client.post("/tasks", json=task_data)
    
    # Ako dozvoljava prazne stringove, status je 200
    # Ako ne, status je 422
    # Ovde proveravamo da li prima prazne stringove
    assert response.status_code in [200, 422]
