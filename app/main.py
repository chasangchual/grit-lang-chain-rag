from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from app.api.routes.app import app_router
from app.api.routes.documents import router as documents_router
from app.api.routes.jobs import router as jobs_router
from app.api.routes.chat import router as chat_router
from app.config.app_config import AppConfig, get_config
from fastapi.templating import Jinja2Templates
from pathlib import Path
from fastapi.staticfiles import StaticFiles


def create_app() -> FastAPI:
    config: AppConfig = get_config()  # Load configuration at startup
    templates = Jinja2Templates(directory=Path(__file__).parent / "templates")

    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=config.app_name,
        description="API for managing documents and embeddings for RAG applications",
        version=config.app_version,
        docs_url="/api/docs",
        redoc_url="/api/redoc",  # Redocly API documentation
        openapi_url="/api/openapi.json",
    )

    # Include routers with API prefix
    app.include_router(app_router, prefix="/api/v1")
    app.include_router(documents_router, prefix="/api/v1")
    app.include_router(jobs_router, prefix="/api/v1")
    app.include_router(chat_router, prefix="/api/v1")

    static_path = Path(__file__).parent / "static"
    app.mount("/static", StaticFiles(directory=static_path), name="static")

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

    @app.get("/", response_class=HTMLResponse)
    async def root(request: Request):
        return templates.TemplateResponse("home.html", {"request": request})

    # Health check endpoint
    @app.get("/health", tags=["health"])
    def health_check() -> dict:
        """Health check endpoint."""
        return {"status": "healthy"}

    @app.get("/ping", status_code=200, response_class=HTMLResponse)
    async def ping(request: Request):
        return "pong"

    @app.get("/home", status_code=200, response_class=HTMLResponse)
    async def home(request: Request):
        return templates.TemplateResponse("home.html", {"request": request})

    return app


# Create the app instance
api_service = create_app()
