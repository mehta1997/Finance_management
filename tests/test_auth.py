import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db
from app import models

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create test tables
models.Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_register_user():
    response = client.post(
        "/auth/register",
        json={"username": "testuser", "email": "test@example.com", "password": "testpassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert "id" in data


def test_register_duplicate_user():
    # First registration
    client.post(
        "/auth/register",
        json={"username": "duplicate", "email": "duplicate@example.com", "password": "password"}
    )
    
    # Second registration with same username
    response = client.post(
        "/auth/register",
        json={"username": "duplicate", "email": "other@example.com", "password": "password"}
    )
    assert response.status_code == 400


def test_login():
    # Register user first
    client.post(
        "/auth/register",
        json={"username": "logintest", "email": "login@example.com", "password": "testpass"}
    )
    
    # Login
    response = client.post(
        "/auth/token",
        data={"username": "logintest", "password": "testpass"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password():
    # Register user first
    client.post(
        "/auth/register",
        json={"username": "wrongpass", "email": "wrong@example.com", "password": "correctpass"}
    )
    
    # Login with wrong password
    response = client.post(
        "/auth/token",
        data={"username": "wrongpass", "password": "wrongpass"}
    )
    assert response.status_code == 401
