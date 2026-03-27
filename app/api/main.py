from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routes.app import app_router
from app.config.config import Configurations, get_config

def create_app() -> FastAPI:
    config: Configurations = get_config()  # Load configuration at startup
    
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=config.app_name,
        description="API for managing documents and embeddings for RAG applications",
        version=config.app_version,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )

    # Register exception handlers
    @app.exception_handler(Exception)
    async def generic_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Handle unexpected exceptions."""
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )

    # Include routers with API prefix
    app.include_router(app_router, prefix="/api/v1")

    # Health check endpoint
    @app.get("/health", tags=["health"])
    def health_check() -> dict:
        """Health check endpoint."""
        return {"status": "healthy"}

    return app


# Create the app instance
api_service = create_app()
