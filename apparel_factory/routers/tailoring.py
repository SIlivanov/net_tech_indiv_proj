from datetime import datetime
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from domain_enums import ModelStatus, ProductionStatus
from orm_models import ClothingModelDB, TailoringOrderDB, UserDB
from schemas.tailoring import TailoringOrderCreate, TailoringOrderRead

router = APIRouter(prefix="/api/tailoring", tags=["3. Tailoring & Orders Context"])


@router.post(
    "/orders",
    response_model=TailoringOrderRead,
    status_code=status.HTTP_201_CREATED,
    summary="Оформить заказ на пошив/отгрузку партии",
)
def submit_tailoring_order(
    payload: TailoringOrderCreate, db: Session = Depends(get_db)
):
    clothing = (
        db.query(ClothingModelDB)
        .filter(ClothingModelDB.id == payload.model_id)
        .first()
    )
    if not clothing:
        raise HTTPException(status_code=404, detail="Модель одежды не найдена")

    customer = db.query(UserDB).filter(UserDB.id == payload.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Заказчик не найден")

    if (
        clothing.status != ModelStatus.AVAILABLE.value
        or clothing.stock_qty < payload.quantity
    ):
        raise HTTPException(
            status_code=400,
            detail=f"Изделие недоступно или недостаточный остаток ({clothing.stock_qty} шт.)",
        )

    clothing.stock_qty -= payload.quantity
    if clothing.stock_qty == 0:
        clothing.status = ModelStatus.SOLD_OUT.value

    db_order = TailoringOrderDB(
        order_number=f"ORD-{uuid.uuid4().hex[:5].upper()}",
        model_id=clothing.id,
        customer_id=customer.id,
        model_name=f"{clothing.name} ({clothing.sku})",
        client_name=customer.full_name,
        selected_size=payload.selected_size,
        quantity=payload.quantity,
        total_cost=round(clothing.unit_price * payload.quantity, 2),
        destination=payload.destination,
        stage=ProductionStatus.IN_WORKSHOP.value,
        created_at=datetime.now().strftime("%d.%m.%Y %H:%M"),
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


@router.get("/orders", response_model=list[TailoringOrderRead], summary="Все заказы")
def list_workshop_orders(db: Session = Depends(get_db)):
    return db.query(TailoringOrderDB).all()


@router.patch(
    "/orders/{order_number}/stage",
    response_model=TailoringOrderRead,
    summary="Изменить стадию заказа (Отгрузить / Подтвердить получение / Отменить)",
)
def change_order_stage(
    order_number: str, new_stage: ProductionStatus, db: Session = Depends(get_db)
):
    order = (
        db.query(TailoringOrderDB)
        .filter(TailoringOrderDB.order_number == order_number)
        .first()
    )
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")

    if (
        new_stage == ProductionStatus.CANCELLED
        and order.stage != ProductionStatus.CANCELLED.value
    ):
        clothing = (
            db.query(ClothingModelDB)
            .filter(ClothingModelDB.id == order.model_id)
            .first()
        )
        if clothing:
            clothing.stock_qty += order.quantity
            if clothing.status == ModelStatus.SOLD_OUT.value:
                clothing.status = ModelStatus.AVAILABLE.value

    order.stage = new_stage.value
    db.commit()
    db.refresh(order)
    return order


@router.delete(
    "/orders/{order_number}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить заказ из журнала цеха",
)
def delete_tailoring_order(order_number: str, db: Session = Depends(get_db)):
    order = (
        db.query(TailoringOrderDB)
        .filter(TailoringOrderDB.order_number == order_number)
        .first()
    )
    if not order:
        raise HTTPException(status_code=404, detail="Заказ не найден")

    # Если удаляется неотгруженный заказ, возвращаем партию обратно на склад
    if order.stage == ProductionStatus.IN_WORKSHOP.value:
        clothing = (
            db.query(ClothingModelDB)
            .filter(ClothingModelDB.id == order.model_id)
            .first()
        )
        if clothing:
            clothing.stock_qty += order.quantity
            if clothing.status == ModelStatus.SOLD_OUT.value:
                clothing.status = ModelStatus.AVAILABLE.value

    db.delete(order)
    db.commit()