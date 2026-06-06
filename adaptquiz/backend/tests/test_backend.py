"""
AdaptQuiz Backend Test Suite
Tests core functionality: security, schemas, models, and API endpoints.
Uses SQLite in-memory DB so no PostgreSQL is needed.
"""
import pytest
from datetime import timedelta

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base_class import Base
from app.core.security import (
    create_access_token, verify_password, get_password_hash
)
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserResponse, Token
from app.api.deps import get_db
from app.main import app

# ---------------------------------------------------------------------------
# Test database setup (in-memory SQLite)
# ---------------------------------------------------------------------------
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """Create tables before each test and drop them after."""
    # Import all models so Base.metadata knows about them
    import app.db.base  # noqa: F401
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# ===================================================================
# 1. Security utility tests
# ===================================================================
class TestSecurity:
    def test_password_hashing(self):
        password = "supersecretpassword123"
        hashed = get_password_hash(password)
        assert hashed != password
        assert verify_password(password, hashed) is True

    def test_password_verification_fails_on_wrong_password(self):
        hashed = get_password_hash("correct_password")
        assert verify_password("wrong_password", hashed) is False

    def test_create_access_token(self):
        token = create_access_token(subject="42")
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_with_expiry(self):
        token = create_access_token(
            subject="42", expires_delta=timedelta(minutes=30)
        )
        assert isinstance(token, str)


# ===================================================================
# 2. Pydantic schema tests
# ===================================================================
class TestSchemas:
    def test_user_create_schema(self):
        user = UserCreate(
            email="test@example.com",
            password="password123"
        )
        assert user.email == "test@example.com"
        assert user.role == UserRole.STUDENT

    def test_user_create_with_role(self):
        user = UserCreate(
            email="teacher@example.com",
            password="password123",
            role=UserRole.TEACHER
        )
        assert user.role == UserRole.TEACHER

    def test_token_schema(self):
        token = Token(access_token="abc123", token_type="bearer")
        assert token.access_token == "abc123"


# ===================================================================
# 3. SQLAlchemy model tests
# ===================================================================
class TestModels:
    def test_create_user(self):
        db = TestingSessionLocal()
        try:
            user = User(
                email="model_test@example.com",
                hashed_password=get_password_hash("pass"),
                role=UserRole.STUDENT
            )
            db.add(user)
            db.commit()
            db.refresh(user)

            assert user.id is not None
            assert user.email == "model_test@example.com"
            assert user.is_active is True
        finally:
            db.close()

    def test_user_role_enum(self):
        assert UserRole.STUDENT.value == "STUDENT"
        assert UserRole.TEACHER.value == "TEACHER"
        assert UserRole.ADMIN.value == "ADMIN"


# ===================================================================
# 4. API endpoint tests
# ===================================================================
class TestAPI:
    def test_root_endpoint(self):
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Welcome to AdaptQuiz API"}

    def test_register_user(self):
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "securepassword",
                "role": "STUDENT"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["role"] == "STUDENT"
        assert data["is_active"] is True
        assert "id" in data

    def test_register_duplicate_user(self):
        # Register first user
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "duplicate@example.com",
                "password": "securepassword"
            }
        )
        # Try to register same email again
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "duplicate@example.com",
                "password": "anotherpassword"
            }
        )
        assert response.status_code == 400

    def test_login_success(self):
        # Register first
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "logintest@example.com",
                "password": "mypassword"
            }
        )
        # Login
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "logintest@example.com",
                "password": "mypassword"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self):
        # Register first
        client.post(
            "/api/v1/auth/register",
            json={
                "email": "wrongpass@example.com",
                "password": "correctpassword"
            }
        )
        # Login with wrong password
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "wrongpass@example.com",
                "password": "wrongpassword"
            }
        )
        assert response.status_code == 401

    def test_login_nonexistent_user(self):
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "noone@example.com",
                "password": "anything"
            }
        )
        assert response.status_code == 401
