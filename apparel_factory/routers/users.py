import uuid
from fastapi import APIRouter, Form, Request, status
from fastapi.responses import RedirectResponse

router = APIRouter(tags=["Users & Roles"])

users_registry: dict[str, dict] = {}


def get_active_account(request: Request):
    uid = request.cookies.get("session_uid")
    if uid and uid in users_registry:
        return users_registry[uid]
    return None


@router.post("/auth/sign-in")
def sign_in(full_name: str = Form(...), role: str = Form(...)):
    """Авторизация с выбором роли: Технолог фабрики или Заказчик (Байер/Клиент)"""
    clean_name = full_name.strip()
    existing = next(
        (u for u in users_registry.values() if u["full_name"].lower() == clean_name.lower()),
        None,
    )
    if not existing:
        uid = f"usr_{uuid.uuid4().hex[:5]}"
        existing = {"id": uid, "full_name": clean_name, "role": role}
        users_registry[uid] = existing
    else:
        existing["role"] = role

    resp = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    resp.set_cookie(key="session_uid", value=existing["id"], httponly=True)
    return resp


@router.get("/auth/sign-out")
def sign_out():
    resp = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    resp.delete_cookie(key="session_uid")
    return resp