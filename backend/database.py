from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
import os

# Use DATABASE_URL from environment variables, with a fallback to a local SQLite DB
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./lucky.db")

# Check if the database URL is for SQLite
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    # Add the aiosqlite driver for async support
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://", 1)
elif SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
# Add similar replacements if you use other database schemes

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    # connect_args is needed only for SQLite.
    connect_args={"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite+aiosqlite") else {}
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