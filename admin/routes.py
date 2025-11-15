from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from admin.auth import verify_admin, create_session, delete_session, require_auth, get_current_user
from bot.services.user_service import UserService
from bot.services.room_service import RoomService
from bot.services.file_service import FileService
from bot.services.ai_service import AIService
from config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin")
templates = Jinja2Templates(directory="admin/templates")


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Admin login page"""
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    """Handle login"""
    if verify_admin(username, password):
        token = create_session(username)
        response = RedirectResponse(url="/admin", status_code=302)
        response.set_cookie(key="admin_session", value=token, httponly=True)
        return response
    
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": "Invalid credentials"}
    )


@router.get("/logout")
async def logout(request: Request):
    """Handle logout"""
    token = request.cookies.get("admin_session")
    if token:
        delete_session(token)
    
    response = RedirectResponse(url="/admin/login", status_code=302)
    response.delete_cookie("admin_session")
    return response


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Admin dashboard"""
    if not require_auth(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    
    # Get statistics
    total_users = await UserService.count_users()
    total_rooms = await RoomService.count_rooms()
    total_files = await FileService.count_all_files()
    total_ai_calls = await AIService.get_total_ai_calls()
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "total_users": total_users,
        "total_rooms": total_rooms,
        "total_files": total_files,
        "total_ai_calls": total_ai_calls,
        "active_page": "dashboard"
    })


@router.get("/users", response_class=HTMLResponse)
async def users_page(request: Request, page: int = 1):
    """Users management page"""
    if not require_auth(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    
    per_page = 20
    skip = (page - 1) * per_page
    
    users = await UserService.get_all_users(skip=skip, limit=per_page)
    total = await UserService.count_users()
    total_pages = (total + per_page - 1) // per_page
    
    return templates.TemplateResponse("users.html", {
        "request": request,
        "users": users,
        "page": page,
        "total_pages": total_pages,
        "active_page": "users"
    })


@router.post("/users/{user_id}/role")
async def update_user_role(user_id: int, role: str = Form(...)):
    """Update user role"""
    if role not in ["user", "admin"]:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    await UserService.update_user_role(user_id, role)
    return RedirectResponse(url="/admin/users", status_code=302)


@router.get("/rooms", response_class=HTMLResponse)
async def rooms_page(request: Request, page: int = 1):
    """Rooms management page"""
    if not require_auth(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    
    per_page = 20
    skip = (page - 1) * per_page
    
    rooms = await RoomService.get_all_rooms(skip=skip, limit=per_page)
    total = await RoomService.count_rooms()
    total_pages = (total + per_page - 1) // per_page
    
    return templates.TemplateResponse("rooms.html", {
        "request": request,
        "rooms": rooms,
        "page": page,
        "total_pages": total_pages,
        "active_page": "rooms"
    })


@router.post("/rooms/{code}/deactivate")
async def deactivate_room(code: str):
    """Deactivate a room"""
    await RoomService.deactivate_room(code)
    return RedirectResponse(url="/admin/rooms", status_code=302)


@router.get("/files", response_class=HTMLResponse)
async def files_page(request: Request, page: int = 1):
    """Files management page"""
    if not require_auth(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    
    per_page = 20
    skip = (page - 1) * per_page
    
    files = await FileService.get_all_files(skip=skip, limit=per_page)
    total = await FileService.count_all_files()
    total_pages = (total + per_page - 1) // per_page
    
    return templates.TemplateResponse("files.html", {
        "request": request,
        "files": files,
        "page": page,
        "total_pages": total_pages,
        "active_page": "files"
    })


@router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    """Settings page"""
    if not require_auth(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    
    current_settings = {
        "ai_model": settings.AI_MODEL,
        "ai_max_tokens": settings.AI_MAX_TOKENS,
        "ai_temperature": settings.AI_TEMPERATURE,
        "ai_calls_per_day": settings.AI_CALLS_PER_USER_PER_DAY,
    }
    
    return templates.TemplateResponse("settings.html", {
        "request": request,
        "settings": current_settings,
        "active_page": "settings"
    })