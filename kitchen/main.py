from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from core.exceptions import register_exception_handlers
from db.repository import DatabaseRepository
from domains.auth.routers import router as auth_router
from domains.admin.routers import router as admin_router
from domains.profiles.routers import router as profile_router
import logging
from core.logging import configure_logging
from core.middleware import RequestIDMiddleware


# Configure logging with request ID support
logger = configure_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logger.info("Initializing database...")
        await DatabaseRepository.init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        # We don't re-raise the exception to allow the application to start
        # even if the database is not available initially
        # It will retry connecting when endpoints are accessed
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Register exception handlers
register_exception_handlers(app)

# Add request ID middleware
app.add_middleware(RequestIDMiddleware)

# Set CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health Check"])
async def root():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": "1.0.0"
    }

# Create a single API router with the API_V1_STR prefix
api_router = APIRouter(prefix=settings.API_V1_STR)

# Include domain routers
api_router.include_router(auth_router)
api_router.include_router(admin_router)
api_router.include_router(profile_router)

# Include the single api_router in the app
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        workers=4
    ) 