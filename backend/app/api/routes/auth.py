from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from backend.app.api.dependencies import get_repo, get_current_user, require_admin
from backend.app.database.repository import DatabaseRepository
from backend.app.database.models import User
from backend.app.schemas.auth import Token, UserLogin, UserCreate, UserResponse
from backend.app.core.security import verify_password, get_password_hash, create_access_token

router = APIRouter()

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), repo: DatabaseRepository = Depends(get_repo)):
    user = repo.get_user_by_email(form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User account is inactive")
    
    access_token = create_access_token(subject=user.email)
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/json-login", response_model=Token)
def json_login(credentials: UserLogin, repo: DatabaseRepository = Depends(get_repo)):
    user = repo.get_user_by_email(credentials.email)
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User account is inactive")
    
    access_token = create_access_token(subject=user.email)
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(require_admin)):
    return current_user

@router.post("/register", response_model=UserResponse)
def register_user(
    user_in: UserCreate,
    current_admin: User = Depends(require_admin),
    repo: DatabaseRepository = Depends(get_repo)
):
    existing = repo.get_user_by_email(user_in.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with this email already exists")
    
    hashed = get_password_hash(user_in.password)
    user = repo.create_user(
        email=user_in.email,
        hashed_password=hashed,
        full_name=user_in.full_name,
        role=user_in.role or "analyst"
    )
    return user
