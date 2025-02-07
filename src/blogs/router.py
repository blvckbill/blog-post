from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from src.database import get_db
import asyncio
from src.blogs.models import BlogPosts
from src.blogs.schemas import BlogCreate, BlogResponse, BlogUpdate
from src.ai.service import generate_blog_content_and_save  # Assuming this function generates the blog content
from src.auth.models import User
from src.auth.dependencies import get_current_user  # Assuming user authentication exists

import logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/blogs", tags=["Blogs"])


def generate_blog_background(topic: str, db: Session, blog_id: int):
    """Background task for generating blog content"""
    try:
        logger.info(f"Background task started for topic: {topic}")
#  Retrieve the existing blog entry 
        blog = db.query(BlogPosts).filter(BlogPosts.id == blog_id).first()
        if not blog:
            logger.error(f"Blog with ID {blog_id} not found.")
            return

        # Mark status as "processing"
        blog.status = "processing"
        db.commit()

        # Generate the blog content
        content = asyncio.run(generate_blog_content_and_save(topic, db, blog_id))

        # Update the existing blog post with generated content
        blog.content = content
        blog.status = "completed"
        db.commit()

        logger.info(f"Successfully created blog post for topic: {topic}")

    except Exception as e:
        logger.error(f"Error generating blog content for topic '{topic}': {e}")

        # In case of failure, mark the blog as failed
        blog.status = "failed"
        db.commit()
        

@router.post("/", response_model=BlogResponse)
def create_blog_post(
    blog: BlogCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Trigger AI Blog Generation"""
    
    # Initially create the blog post with a status of "in_progress"
    new_blog = BlogPosts(title=blog.title, content="", status="in_progress", author_id=current_user.id)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)

    # Add the background task for blog content generation
    background_tasks.add_task(generate_blog_background, blog.title, db, new_blog.id)
    
    # Return the blog post object immediately with its title and status
    return BlogResponse(id=new_blog.id, title=blog.title, content="", status='in_progress')


@router.get("/", response_model=list[BlogResponse])
def get_blogs(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Retrieve all blogs of the current user"""
    return db.query(BlogPosts).filter(BlogPosts.author_id == current_user.id).all()


@router.get("/{id}", response_model=BlogResponse)
def get_blog(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Retrieve a specific blog"""
    blog = db.query(BlogPosts).filter(BlogPosts.id == id, BlogPosts.author_id == current_user.id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    return blog


@router.put("/{id}", response_model=BlogResponse)
def update_blog(id: int, updated_blog: BlogUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Update a blog (allowing partial updates)"""
    blog = db.query(BlogPosts).filter(BlogPosts.id == id, BlogPosts.author_id == current_user.id).first()
    
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")

    # Only update fields that are provided
    if updated_blog.title is not None:
        blog.title = updated_blog.title
    if updated_blog.content is not None:
        blog.content = updated_blog.content

    db.commit()
    db.refresh(blog)
    
    return blog

@router.delete("/{id}")
def delete_blog(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Delete a blog"""
    blog = db.query(BlogPosts).filter(BlogPosts.id == id, BlogPosts.author_id == current_user.id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")

    db.delete(blog)
    db.commit()
    return {"detail": "Blog deleted"}
