from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi import Request

app_router = APIRouter(
    prefix="/app",
    tags=["app"],
)

@app_router.get("/ping", status_code=200, response_class=HTMLResponse)
async def ping(request: Request):
    return 'pong'