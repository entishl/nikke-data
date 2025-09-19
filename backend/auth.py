from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from backend.services.user_service import UserService
from backend.utils import verify_password, get_password_hash
from . import models, schemas, services
from .database import get_async_db
from . import constants

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=constants.TOKEN_URL)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    创建 JWT 访问令牌。
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=constants.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, constants.SECRET_KEY, algorithm=constants.ALGORITHM)
    return encoded_jwt

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_async_db)
):
    """
    FastAPI 依赖项，用于解码 JWT、验证用户并从数据库中获取当前用户。
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, constants.SECRET_KEY, algorithms=[constants.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user_service = UserService(db)
    user = await user_service.get_user_by_username(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: models.User = Depends(get_current_user)):
    """
    FastAPI 依赖项，用于检查当前用户是否处于活动状态。
    """
    if getattr(current_user, "disabled", False):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_admin_user(current_user: models.User = Depends(get_current_active_user)):
    """
    FastAPI 依赖项，用于检查当前用户是否是管理员。
    """
    if not getattr(current_user, "is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user