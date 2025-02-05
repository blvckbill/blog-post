from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from datetime import timedelta
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from src.auth.schemas import UserCreate, Token, UserResponse
from src.auth.models import User
from src.auth.service import get_password_hash, create_access_token, authenticate_user
from src.database import get_db
from src.auth.config import ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(prefix="/api/v1/users", tags=["auth"])

@router.post("/register", response_model=UserResponse)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_password = get_password_hash(user_data.password)
    new_user = User(username=user_data.username, email=user_data.email, hashed_password=hashed_password)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return UserResponse(username=user_data.username, email=user_data.email)

@router.post("/login", response_model=Token)
def login_for_access_token(
    username: str = Form(...),  # Accept only username
    password: str = Form(...),  # Accept only password
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    
    return Token(access_token=access_token, token_type="bearer")