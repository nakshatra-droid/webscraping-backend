import os

from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "..", "..", "..", "templates")


@router.get("/login")
async def login_page():
    return FileResponse(os.path.join(TEMPLATES_DIR, "login.html"))


@router.get("/admin/dashboard")
async def admin_dashboard_page():
    return FileResponse(os.path.join(TEMPLATES_DIR, "admin", "dashboard.html"))


@router.get("/user/dashboard")
async def user_dashboard_page():
    return FileResponse(os.path.join(TEMPLATES_DIR, "user", "dashboard.html"))
