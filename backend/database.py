from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
import os
from urllib.parse import urlparse, urlunparse

# Determine the database URL based on the environment
if os.getenv("APP_ENV") == "development":
    # Use an in-memory SQLite database for local development
    SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
else:
    # Use the DATABASE_URL from environment variables for production/Docker
    SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
    if SQLALCHEMY_DATABASE_URL:
        # Ensure the async driver is used for postgresql schemes
        if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
            SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
        elif SQLALCHEMY_DATABASE_URL.startswith("postgresql://"):
            SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# Add similar replacements if you use other database schemes

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    # connect_args is needed only for SQLite.
    connect_args={"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}
)

AsyncSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, bind=engine, expire_on_commit=False
)

Base = declarative_base()

# Dependency to get an async DB session
async def get_async_db():
    """
    FastAPI dependency that provides an async database session for a single request.
    """
    async with AsyncSessionLocal() as session:
        yield session