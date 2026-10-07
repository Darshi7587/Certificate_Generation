import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.database.database import engine, Base
import app.models  # Ensures all ORM models are registered with Base.metadata
from app.api.router import api_router

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager for startup and shutdown events.
    Creates database tables automatically on startup.
    """
    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized.")
    yield
    logger.info("Shutting down application...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Asynchronous Bulk Certificate Generator API built for Aereo backend assignment.",
    version="1.0.0",
    lifespan=lifespan,
)

# Register API routes
app.include_router(api_router)


@app.get("/", tags=["Health Check"])
def health_check():
    """Health check endpoint to verify server is running."""
    return {
        "status": "healthy",
        "app_name": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler to intercept unhandled server errors.
    Prevents sensitive internal stack traces from leaking to API consumers.
    """
    logger.exception(f"Unhandled server error on {request.method} {request.url}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An internal server error occurred. Please contact system support.",
            "error_type": exc.__class__.__name__,
        },
    )
