from typing import AsyncGenerator, Optional
import asyncio
import logging
import warnings
import traceback
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy.exc import SQLAlchemyError, DBAPIError

# Import from repository to maintain backward compatibility
from db.repository import engine, AsyncSessionLocal, get_repository_session, DatabaseRepository

# Set up deprecated warning
warnings.simplefilter('always', DeprecationWarning)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# DEPRECATED - Use db.repository.DatabaseRepository.init_db() instead
async def init_db(retries: int = 5, delay: int = 5) -> None:
    """
    DEPRECATED: Use DatabaseRepository.init_db() instead.
    
    This function has been moved to the repository layer to follow the principle
    that database initialization should only occur in repositories.
    """
    warnings.warn(
        "init_db() in db.session is deprecated. Use DatabaseRepository.init_db() from db.repository instead.",
        DeprecationWarning, 
        stacklevel=2
    )
    await DatabaseRepository.init_db(retries, delay)

# DEPRECATED - Use db.repository.get_repository_session() instead
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    DEPRECATED: Use get_repository_session() from db.repository instead.
    
    This function has been moved to the repository layer to follow the principle
    that database sessions should only be used in repositories.
    """
    warnings.warn(
        "get_session() in db.session is deprecated. Use get_repository_session() from db.repository instead.",
        DeprecationWarning,
        stacklevel=2
    )
    async for session in get_repository_session():
        yield session

# Keeping this for backward compatibility, but marking as deprecated
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    DEPRECATED: Use get_repository_session() from db.repository instead.
    
    This function automatically commits successful transactions,
    which may not be the desired behavior in all cases.
    
    Database session handling should only occur in repositories.
    """
    warnings.warn(
        "get_db() in db.session is deprecated. Use get_repository_session() from db.repository instead.",
        DeprecationWarning,
        stacklevel=2
    )
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

@asynccontextmanager
async def get_db_session(max_retries: int = 3, retry_delay: int = 1) -> AsyncGenerator[AsyncSession, None]:
    """
    Create a new database session and close it when done.
    
    Unlike get_repository_session, this function is designed to be used directly
    with the 'async with' statement rather than as a FastAPI dependency.
    
    Used by the RequestIDMiddleware to log requests separately from the main
    request transaction.
    
    Args:
        max_retries: Maximum number of retries on connection failure
        retry_delay: Delay in seconds between retries
    
    Example:
        async with get_db_session() as session:
            # Use session
            await session.commit()
    """
    retry_count = 0
    last_error: Optional[Exception] = None
    
    while retry_count <= max_retries:
        try:
            async with AsyncSessionLocal() as session:
                try:
                    yield session
                    break  # Break out of retry loop if successful
                except SQLAlchemyError as e:
                    # Handle SQLAlchemy specific errors
                    error_traceback = traceback.format_exc()
                    logger.error(
                        f"SQLAlchemy error during session use: {str(e)}", 
                        extra={
                            "error_type": type(e).__name__,
                            "traceback": error_traceback
                        }
                    )
                    # Re-raise the exception after logging
                    raise
                finally:
                    await session.close()
            return  # Exit the function if we successfully yielded a session
        except (DBAPIError, ConnectionError) as e:
            # Only retry for connection-related errors
            last_error = e
            retry_count += 1
            if retry_count <= max_retries:
                error_traceback = traceback.format_exc()
                logger.warning(
                    f"Database connection error (attempt {retry_count}/{max_retries}): {str(e)}. "
                    f"Retrying in {retry_delay} seconds...",
                    extra={"error_type": type(e).__name__, "traceback": error_traceback}
                )
                await asyncio.sleep(retry_delay)
            else:
                error_traceback = traceback.format_exc()
                logger.error(
                    f"Database connection failed after {max_retries} attempts: {str(e)}",
                    extra={"error_type": type(e).__name__, "traceback": error_traceback}
                )
                raise
        except Exception as e:
            # For other unexpected errors, log and raise immediately
            error_traceback = traceback.format_exc()
            logger.error(
                f"Unexpected error creating database session: {str(e)}", 
                extra={"error_type": type(e).__name__, "traceback": error_traceback}
            )
            raise 