from sqlalchemy.orm import Session
from . import models, schemas

def create_blog(db: Session, blog: schemas.BlogCreate, user_id: int, content: str):
    db_blog = models.BlogPosts(title=blog.title, content=content, user_id=user_id)
    db.add(db_blog)
    db.commit()
    db.refresh(db_blog)
    return db_blog

def get_blogs(db: Session):
    return db.query(models.BlogPosts).all()

def get_blog(db: Session, blog_id: int):
    return db.query(models.BlogPosts).filter(models.BlogPosts.id == blog_id).first()

def update_blog(db: Session, blog: schemas.BlogUpdate, blog_id: int):
    db_blog = db.query(models.BlogPosts).filter(models.BlogPosts.id == blog_id).first()
    db_blog.title = blog.title
    db_blog.content = blog.content
    db.commit()
    db.refresh(db_blog)
    return db_blog

def delete_blog(db: Session, blog_id: int):
    db_blog = db.query(models.BlogPosts).filter(models.BlogPosts.id == blog_id).first()
    db.delete(db_blog)
    db.commit()
