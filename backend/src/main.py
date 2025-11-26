"""
StoneKeeper FastAPI application entry point.

Initializes the FastAPI application with middleware, exception handlers,
and API routers. Serves as the main entry point for the backend service.
"""
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from src.config import APP_NAME, APP_VERSION, APP_DESCRIPTION, CORS_ORIGINS
from src.schemas.base import ErrorResponse

# Initialize FastAPI application
app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description=APP_DESCRIPTION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# =============================================================================
# CORS Middleware
# =============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# Exception Handlers
# =============================================================================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handle Pydantic validation errors with user-friendly messages.

    Per Constitution Principle II: Non-Technical User Focus,
    transforms technical validation errors into plain-language messages.
    """
    # Extract first error for simplicity
    errors = exc.errors()
    first_error = errors[0] if errors else {}

    # Create user-friendly message
    field = " -> ".join(str(loc) for loc in first_error.get("loc", []))
    msg = first_error.get("msg", "Invalid input")

    error_response = ErrorResponse(
        error="validation_error",
        message=f"Invalid value for {field}: {msg}",
        details={"errors": errors}
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response.model_dump()
    )


@app.exception_handler(SQLAlchemyError)
async def database_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """
    Handle database errors with user-friendly messages.

    Logs technical details but returns simple message to users.
    """
    # Log the actual error for debugging
    print(f"Database error: {exc}")

    error_response = ErrorResponse(
        error="database_error",
        message="A database error occurred. Please try again or contact support if the problem persists."
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.model_dump()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle unexpected errors with user-friendly messages.

    Catches all unhandled exceptions to prevent technical error messages
    from reaching non-technical users.
    """
    # Log the actual error for debugging
    print(f"Unexpected error: {exc}")

    error_response = ErrorResponse(
        error="internal_error",
        message="An unexpected error occurred. Please try again or contact support if the problem persists."
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.model_dump()
    )


# =============================================================================
# Health Check Endpoint
# =============================================================================

@app.get("/health", tags=["Health"])
async def health_check() -> dict:
    """
    Health check endpoint for Docker health checks and monitoring.

    Returns:
        dict: Simple status response
    """
    return {
        "status": "healthy",
        "service": APP_NAME,
        "version": APP_VERSION
    }


@app.get("/", tags=["Root"])
async def root() -> dict:
    """
    Root endpoint with API information.

    Returns:
        dict: API metadata and documentation links
    """
    return {
        "service": APP_NAME,
        "version": APP_VERSION,
        "description": APP_DESCRIPTION,
        "docs": "/api/docs",
        "health": "/health"
    }


# =============================================================================
# API Routers
# =============================================================================

# API routers will be included here as they are created
# Example:
# from src.api import auth, cemeteries, photos, search
# app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
# app.include_router(cemeteries.router, prefix="/api/cemeteries", tags=["Cemeteries"])
# app.include_router(photos.router, prefix="/api/photos", tags=["Photos"])
# app.include_router(search.router, prefix="/api/search", tags=["Search"])


# =============================================================================
# Startup Event
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """
    Application startup tasks.

    Performs initialization checks and setup on application start.
    """
    print(f"Starting {APP_NAME} v{APP_VERSION}")
    print(f"API documentation available at /api/docs")

    # Database initialization will be added here
    # (See Phase 7 / User Story 5 for database initialization)


# =============================================================================
# Shutdown Event
# =============================================================================

@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown tasks.

    Performs cleanup on application shutdown.
    """
    print(f"Shutting down {APP_NAME}")
