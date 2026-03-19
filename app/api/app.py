from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routes import documents_router, embeddings_router


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Document RAG API",
        description="API for managing documents and embeddings for RAG applications",
        version="1.0.0",
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
    app.include_router(documents_router, prefix="/api/v1")
    app.include_router(embeddings_router, prefix="/api/v1")

    # Health check endpoint
    @app.get("/health", tags=["health"])
    def health_check() -> dict:
        """Health check endpoint."""
        return {"status": "healthy"}

    return app


# Create the app instance
app = create_app()
