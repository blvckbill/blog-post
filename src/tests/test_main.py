import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.auth.models import User
from src.database import Base
from src.blogs.models import BlogPosts
from src.auth.dependencies import get_user_by_username
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from alembic import command
from alembic.config import Config

# Setup for the test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables in the test database
Base.metadata.create_all(bind=engine)

@pytest.fixture(scope="module")
def db():
    """Fixture to setup and teardown the database"""
    db = SessionLocal()
    yield db
    db.close()

@pytest.fixture(scope="module")
def client():
    """Fixture to setup and teardown the TestClient"""
    return TestClient(app)

# Helper functions
def create_user(db, username="testuser", password="password123"):
    user = User(username=username, password=password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def create_blog_post(db, user_id, title="Test Post", content="This is a test blog post"):
    blog = BlogPosts(title=title, content=content, owner_id=user_id)
    db.add(blog)
    db.commit()
    db.refresh(blog)
    return blog

# Tests
def test_user_registration(client, db):
    user_data = {"username": "testuser", "password": "password123"}
    response = client.post("/api/v1/users/register", json=user_data)
    
    assert response.status_code == 201
    assert "access_token" in response.json()  # Assuming token is returned on success
    user = get_user_by_username(db, "testuser")
    assert user is not None

def test_user_login(client, db):
    user = create_user(db)
    login_data = {"username": user.username, "password": user.hashed_password}
    response = client.post("/api/v1/users/login", json=login_data)
    
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_create_blog_post(client, db):
    user = create_user(db)
    login_data = {"username": user.username, "password": user.hashed_password}
    login_response = client.post("/api/v1/users/login", json=login_data)
    token = login_response.json()["access_token"]
    
    blog_data = {"title": "New Blog Post", "content": "This is a new blog post"}
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/v1/blogs", json=blog_data, headers=headers)
    
    assert response.status_code == 201
    assert response.json()["title"] == blog_data["title"]

def test_get_blog_posts(client, db):
    user = create_user(db)
    blog1 = create_blog_post(db, user.id)
    blog2 = create_blog_post(db, user.id)
    
    response = client.get("/api/v1/blogs")
    
    assert response.status_code == 200
    blogs = response.json()
    assert len(blogs) >= 2
    assert any(blog["title"] == blog1.title for blog in blogs)
    assert any(blog["title"] == blog2.title for blog in blogs)

def test_get_single_blog_post(client, db):
    user = create_user(db)
    blog = create_blog_post(db, user.id)
    
    response = client.get(f"/api/v1/blogs/{blog.id}")
    
    assert response.status_code == 200
    assert response.json()["title"] == blog.title

def test_update_blog_post(client, db):
    user = create_user(db)
    blog = create_blog_post(db, user.id)
    
    updated_data = {"title": "Updated Title", "content": "Updated content"}
    
    login_data = {"username": user.username, "password": user.password}
    login_response = client.post("/api/v1/users/login", json=login_data)
    token = login_response.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    response = client.put(f"/api/v1/blogs/{blog.id}", json=updated_data, headers=headers)
    
    assert response.status_code == 200
    assert response.json()["title"] == updated_data["title"]
    assert response.json()["content"] == updated_data["content"]

def test_delete_blog_post(client, db):
    user = create_user(db)
    blog = create_blog_post(db, user.id)
    
    login_data = {"username": user.username, "password": user.password}
    login_response = client.post("/api/v1/users/login", json=login_data)
    token = login_response.json()["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    response = client.delete(f"/api/v1/blogs/{blog.id}", headers=headers)
    
    assert response.status_code == 204
    response = client.get(f"/api/v1/blogs/{blog.id}")
    assert response.status_code == 404  # Blog post should be deleted

