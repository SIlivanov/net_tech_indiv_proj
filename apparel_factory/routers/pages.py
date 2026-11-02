from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from database import get_db
from domain_enums import ProductionStatus, SeasonCollection, UserRole
from orm_models import ClothingModelDB, TailoringOrderDB, UserDB
from routers.catalog import (
    archive_clothing_model,
    delete_clothing_model,
    release_clothing_model,
    restock_clothing_model,
)
from routers.tailoring import (
    change_order_stage,
    delete_tailoring_order,
    submit_tailoring_order,
)
from routers.users import (
    delete_user,
    get_active_account,
    register_or_login_user,
    update_user_profile,
)
from schemas.catalog import ClothingModelCreate
from schemas.tailoring import TailoringOrderCreate
from schemas.users import UserCreateDTO, UserProfileUpdateDTO

router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
def showroom_page(request: Request, db: Session = Depends(get_db)):
    account = get_active_account(request, db)
    catalog = db.query(ClothingModelDB).all()
    orders = db.query(TailoringOrderDB).all()
    users = db.query(UserDB).all()
    return templates.TemplateResponse(
        request=request,
        name="showroom.html",
        context={
            "account": account,
            "catalog": catalog,
            "orders": orders,
            "users": users,
            "seasons": [s.value for s in SeasonCollection],
        },
    )


@router.get("/auth", response_class=HTMLResponse)
def auth_page(request: Request):
    return templates.TemplateResponse(
        request=request, name="auth.html", context={"account": None}
    )


# --- Действия Пользователей ---
@router.post("/web/users/sign-in")
def web_sign_in(
    full_name: str = Form(...),
    role: UserRole = Form(...),
    phone: str = Form("+7 (917) 000-00-00"),
    default_size: str = Form("M (46)"),
    city: str = Form("г. Уфа, ул. Ленина, 28"),
    db: Session = Depends(get_db),
):
    user = register_or_login_user(
        UserCreateDTO(
            full_name=full_name,
            role=role,
            phone=phone,
            default_size=default_size,
            city=city,
        ),
        db=db,
    )
    resp = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    resp.set_cookie(key="session_uid", value=user.id, httponly=True)
    return resp


@router.get("/web/users/sign-out")
def web_sign_out():
    resp = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    resp.delete_cookie(key="session_uid")
    return resp


@router.post("/web/users/update-profile")
def web_update_profile(
    request: Request,
    phone: str = Form(...),
    default_size: str = Form(...),
    city: str = Form(...),
    db: Session = Depends(get_db),
):
    account = get_active_account(request, db)
    if account:
        update_user_profile(
            account.id,
            UserProfileUpdateDTO(phone=phone, default_size=default_size, city=city),
            db=db,
        )
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/web/users/delete")
def web_delete_user(request: Request, db: Session = Depends(get_db)):
    account = get_active_account(request, db)
    if account:
        delete_user(user_id=account.id, db=db)
    resp = RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    resp.delete_cookie(key="session_uid")
    return resp


# --- Действия Каталога одежды ---
@router.post("/web/catalog/release")
def web_release_model(
    request: Request,
    sku: str = Form(...),
    name: str = Form(...),
    collection: SeasonCollection = Form(...),
    fabric: str = Form(...),
    stock_qty: int = Form(...),
    unit_price: float = Form(...),
    db: Session = Depends(get_db),
):
    account = get_active_account(request, db)
    if not account:
        return RedirectResponse("/auth", status_code=status.HTTP_303_SEE_OTHER)

    release_clothing_model(
        ClothingModelCreate(
            technologist_id=account.id,
            sku=sku,
            name=name,
            collection=collection,
            fabric=fabric,
            stock_qty=stock_qty,
            unit_price=unit_price,
        ),
        db=db,
    )
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/web/catalog/restock")
def web_restock_model(model_id: str = Form(...), db: Session = Depends(get_db)):
    restock_clothing_model(model_id=model_id, add_qty=10, db=db)
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/web/catalog/archive")
def web_archive_model(model_id: str = Form(...), db: Session = Depends(get_db)):
    archive_clothing_model(model_id=model_id, db=db)
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/web/catalog/delete")
def web_delete_model(model_id: str = Form(...), db: Session = Depends(get_db)):
    delete_clothing_model(model_id=model_id, db=db)
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)


# --- Действия Пошивочного цеха и Заказов ---
@router.post("/web/tailoring/order")
def web_place_order(
    request: Request,
    model_id: str = Form(...),
    selected_size: str = Form(...),
    quantity: int = Form(...),
    destination: str = Form(...),
    db: Session = Depends(get_db),
):
    account = get_active_account(request, db)
    if not account:
        return RedirectResponse("/auth", status_code=status.HTTP_303_SEE_OTHER)

    submit_tailoring_order(
        TailoringOrderCreate(
            model_id=model_id,
            customer_id=account.id,
            selected_size=selected_size,
            quantity=quantity,
            destination=destination,
        ),
        db=db,
    )
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/web/tailoring/stage")
def web_change_order_stage(
    order_number: str = Form(...),
    new_stage: ProductionStatus = Form(...),
    db: Session = Depends(get_db),
):
    change_order_stage(order_number=order_number, new_stage=new_stage, db=db)
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/web/tailoring/delete")
def web_delete_order(order_number: str = Form(...), db: Session = Depends(get_db)):
    delete_tailoring_order(order_number=order_number, db=db)
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)