from typing import Generic, TypeVar, Type, Optional, List, AsyncGenerator
import asyncio
import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from db.base import Base
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from core.config import settings

# Move these from session.py to repository.py
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create async engine with connection pooling
engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    echo=True,  # Enable SQL logging
    future=True,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Dependency to get DB session - will be used only in repositories
async def get_repository_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting async database sessions.
    This should ONLY be used by repository classes.
    
    It automatically handles session lifecycle including closing the session.
    
    Transactions must be committed or rolled back explicitly by the caller.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

ModelType = TypeVar("ModelType", bound=Base)

class DatabaseRepository:
    """
    Repository responsible for database initialization and management.
    All database initialization should go through this repository.
    """
    
    @staticmethod
    async def init_db(retries: int = 5, delay: int = 5) -> None:
        """
        Initialize the database by creating all tables defined in the models.
        
        Args:
            retries: Number of connection attempts before failing
            delay: Delay between retry attempts in seconds
        
        Raises:
            Exception: If database initialization fails after all retries
        """
        for attempt in range(retries):
            try:
                logger.info(f"Attempting database connection (attempt {attempt + 1}/{retries})")
                async with engine.begin() as conn:
                    from db.base import Base
                    await conn.run_sync(Base.metadata.create_all)
                logger.info("Database initialized successfully")
                return
            except Exception as e:
                logger.error(f"Database connection attempt {attempt + 1} failed: {str(e)}")
                if attempt == retries - 1:
                    raise Exception(f"Failed to initialize database after {retries} attempts: {str(e)}")
                logger.info(f"Waiting {delay} seconds before next attempt...")
                await asyncio.sleep(delay)

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], session: AsyncSession = Depends(get_repository_session)):
        self.model = model
        self.session = session

    async def get(self, id: int) -> Optional[ModelType]:
        query = select(self.model).where(self.model.id == id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(self) -> List[ModelType]:
        query = select(self.model)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def create(self, obj_in: dict) -> ModelType:
        db_obj = self.model(**obj_in)
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def update(self, id: int, obj_in: dict) -> Optional[ModelType]:
        db_obj = await self.get(id)
        if db_obj:
            for key, value in obj_in.items():
                setattr(db_obj, key, value)
            await self.session.commit()
            await self.session.refresh(db_obj)
        return db_obj

    async def delete(self, id: int) -> bool:
        db_obj = await self.get(id)
        if db_obj:
            await self.session.delete(db_obj)
            await self.session.commit()
            return True
        return False 