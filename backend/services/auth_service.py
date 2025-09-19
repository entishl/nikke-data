from sqlalchemy.ext.asyncio import AsyncSession
from backend import models, schemas, constants
from backend.auth import get_password_hash, verify_password, create_access_token
from backend.repositories.user_repository import UserRepository
from datetime import timedelta
from typing import Optional

class AuthService:
    def __init__(self, db: AsyncSession):
        self.user_repo = UserRepository(db)

    async def register_user(self, user: schemas.UserCreate) -> models.User:
        """
        Registers a new user.
        """
        hashed_password = get_password_hash(user.password)
        db_user = models.User(username=user.username, hashed_password=hashed_password)
        return await self.user_repo.create(db_user)

    async def authenticate_user(self, username: str, password: str) -> Optional[models.User]:
        """
        Authenticates a user.
        """
        user = await self.user_repo.get_by_username(username)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user

    async def create_token_for_user(self, user: models.User, expires_delta: Optional[timedelta] = None) -> str:
        """
        Creates an access token for a user.
        """
        access_token_expires = expires_delta if expires_delta else timedelta(minutes=constants.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        return access_token