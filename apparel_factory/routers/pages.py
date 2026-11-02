from fastapi import APIRouter, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from domain_enums import ProductionStatus, SeasonCollection
from routers.catalog import catalog_storage, release_clothing_model
from routers.tailoring import submit_tailoring_order, workshop_orders
from routers.users import get_active_account
from schemas.catalog import ClothingModelCreate
from schemas.tailoring import TailoringOrderCreate

router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
def showroom_page(request: Request):
    account = get_active_account(request)
    return templates.TemplateResponse(
        request=request,
        name="showroom.html",
        context={
            "account": account,
            "catalog": list(catalog_storage.values()),
            "orders": list(workshop_orders.values()),
            "seasons": [s.value for s in SeasonCollection],
        },
    )


@router.get("/auth", response_class=HTMLResponse)
def auth_page(request: Request):
    return templates.TemplateResponse(
        request=request, name="auth.html", context={"account": None}
    )


@router.post("/actions/release-model")
def web_release_model(
    request: Request,
    sku: str = Form(...),
    name: str = Form(...),
    collection: SeasonCollection = Form(...),
    fabric: str = Form(...),
    stock_qty: int = Form(...),
    unit_price: float = Form(...),
):
    account = get_active_account(request)
    if not account:
        return RedirectResponse("/auth", status_code=status.HTTP_303_SEE_OTHER)

    release_clothing_model(
        ClothingModelCreate(
            technologist_id=account["id"],
            sku=sku,
            name=name,
            collection=collection,
            fabric=fabric,
            stock_qty=stock_qty,
            unit_price=unit_price,
        )
    )
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/actions/place-order")
def web_place_order(
    request: Request,
    model_id: str = Form(...),
    selected_size: str = Form(...),
    quantity: int = Form(...),
    destination: str = Form(...),
):
    account = get_active_account(request)
    if not account:
        return RedirectResponse("/auth", status_code=status.HTTP_303_SEE_OTHER)

    submit_tailoring_order(
        TailoringOrderCreate(
            model_id=model_id,
            client_id=account["full_name"],
            selected_size=selected_size,
            quantity=quantity,
            destination=destination,
        )
    )
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/actions/ship-order")
def web_ship_order(order_number: str = Form(...)):
    """Смена статуса заказа в цехе на 'ОТГРУЖЕНО СО СКЛАДА'"""
    if order_number in workshop_orders:
        workshop_orders[order_number]["stage"] = ProductionStatus.SHIPPED
    return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)