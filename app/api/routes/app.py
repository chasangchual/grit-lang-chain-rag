from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi import Request
from fastapi.templating import Jinja2Templates
from pathlib import Path

templates = Jinja2Templates(directory=Path(__file__).parent.parent.parent / "templates")

app_router = APIRouter(
    prefix="/app",
    tags=["app"],
)

@app_router.get("/home", status_code=200, response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})