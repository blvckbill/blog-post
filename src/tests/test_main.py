import pytest
from fastapi.testclient import TestClient
from main import app  # Import your FastAPI app
from database import SessionLocal
from src.auth.models import User
from src.blogs.models import BlogPosts
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from src.database import get_db

#  Create a test database
TEST_DATABASE_URL = "sqlite:///./src/test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override FastAPI dependency to use test database
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

#  Create a test client
client = TestClient(app)

#  Test user login helper function
def get_auth_headers():
    """Register and log in a test user to get authentication token"""
    user_data = {"email": "testuser@example.com", "password": "password123"}
    
    # Register the user
    client.post("/users/register", json=user_data)
    
    # Login to get token
    response = client.post("/users/login", json=user_data)
    token = response.json().get("access_token")
    
    return {"Authorization": f"Bearer {token}"}

#  Test: Create a blog
def test_create_blog():
    headers = get_auth_headers()
    blog_data = {"title": "Test Blog", "content": "This is a test blog."}
    
    response = client.post("/blogs/", json=blog_data, headers=headers)
    
    assert response.status_code == 201
    assert response.json()["title"] == "Test Blog"

#  Test: Retrieve a blog
def test_get_blog():
    headers = get_auth_headers()
    
    # Create a blog
    blog_data = {"title": "Another Blog", "content": "Some content"}
    response = client.post("/blogs/", json=blog_data, headers=headers)
    blog_id = response.json()["id"]
    
    # Fetch the blog
    response = client.get(f"/blogs/{blog_id}", headers=headers)
    
    assert response.status_code == 200
    assert response.json()["id"] == blog_id

# ✅ Test: Update a blog (partial update)
def test_update_blog():
    headers = get_auth_headers()
    
    # Create a blog
    blog_data = {"title": "Initial Title", "content": "Initial Content"}
    response = client.post("/blogs/", json=blog_data, headers=headers)
    blog_id = response.json()["id"]
    
    # Update title only
    update_data = {"title": "Updated Title"}
    response = client.put(f"/blogs/{blog_id}", json=update_data, headers=headers)
    
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"
    assert response.json()["content"] == "Initial Content"  # Content should remain the same

# ✅ Test: Delete a blog
def test_delete_blog():
    headers = get_auth_headers()
    
    # Create a blog
    blog_data = {"title": "Blog to Delete", "content": "To be deleted"}
    response = client.post("/blogs/", json=blog_data, headers=headers)
    blog_id = response.json()["id"]
    
    # Delete the blog
    response = client.delete(f"/blogs/{blog_id}", headers=headers)
    
    assert response.status_code == 204  # No content

    # Verify it's deleted
    response = client.get(f"/blogs/{blog_id}", headers=headers)
    assert response.status_code == 404  # Not found