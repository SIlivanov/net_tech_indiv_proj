from datetime import datetime
import uuid
from fastapi import APIRouter, HTTPException, status
from domain_enums import ModelStatus, ProductionStatus
from routers.catalog import catalog_storage
from schemas.tailoring import TailoringOrderCreate, TailoringOrderRead

router = APIRouter(prefix="/api/tailoring", tags=["Tailoring & Orders"])

workshop_orders: dict[str, dict] = {}


@router.post(
    "/orders",
    response_model=TailoringOrderRead,
    status_code=status.HTTP_201_CREATED,
    summary="Оформить заявку на пошив / отгрузку партии",
)
def submit_tailoring_order(payload: TailoringOrderCreate):
    """
    Клиент заказывает выбранный размер и количество единиц.
    Остаток тиража на складе уменьшается. Если остаток = 0, модель получает статус SOLD_OUT.
    """
    clothing = catalog_storage.get(payload.model_id)
    if not clothing:
        raise HTTPException(status_code=404, detail="Модель одежды не найдена в каталоге")

    if clothing["status"] != ModelStatus.AVAILABLE or clothing["stock_qty"] < payload.quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Недостаточно изделий на складе (доступно: {clothing['stock_qty']} шт.)",
        )

    # Списываем заказанное количество со склада фабрики
    clothing["stock_qty"] -= payload.quantity
    if clothing["stock_qty"] == 0:
        clothing["status"] = ModelStatus.SOLD_OUT

    order_num = f"ORD-{uuid.uuid4().hex[:5].upper()}"
    new_order = {
        "order_number": order_num,
        "model_id": clothing["id"],
        "model_name": f"{clothing['name']} ({clothing['sku']})",
        "client_id": payload.client_id,
        "selected_size": payload.selected_size,
        "quantity": payload.quantity,
        "total_cost": round(clothing["unit_price"] * payload.quantity, 2),
        "destination": payload.destination,
        "stage": ProductionStatus.IN_WORKSHOP,
        "created_at": datetime.now().strftime("%d.%m.%Y %H:%M"),
    }
    workshop_orders[order_num] = new_order
    return new_order


@router.get("/orders", response_model=list[TailoringOrderRead])
def list_workshop_orders():
    return list(workshop_orders.values())