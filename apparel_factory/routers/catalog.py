from datetime import datetime
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from domain_enums import ModelStatus
from orm_models import ClothingModelDB
from schemas.catalog import ClothingModelCreate, ClothingModelRead

router = APIRouter(prefix="/api/catalog", tags=["2. Catalog & Collections Context"])


@router.post(
    "/models",
    response_model=ClothingModelRead,
    status_code=status.HTTP_201_CREATED,
    summary="Выпустить новую модель одежды в каталог",
)
def release_clothing_model(
    payload: ClothingModelCreate, db: Session = Depends(get_db)
):
    db_item = ClothingModelDB(
        id=f"mdl_{uuid.uuid4().hex[:6]}",
        technologist_id=payload.technologist_id,
        sku=payload.sku.upper(),
        name=payload.name,
        collection=payload.collection.value,
        fabric=payload.fabric,
        stock_qty=payload.stock_qty,
        unit_price=payload.unit_price,
        status=ModelStatus.AVAILABLE.value,
        released_at=datetime.now().strftime("%d.%m.%Y %H:%M"),
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.get("/models", response_model=list[ClothingModelRead], summary="Весь каталог")
def list_clothing_models(db: Session = Depends(get_db)):
    return db.query(ClothingModelDB).all()


@router.patch(
    "/models/{model_id}/restock",
    response_model=ClothingModelRead,
    summary="Довыпустить тираж модели на склад (+шт.)",
)
def restock_clothing_model(
    model_id: str, add_qty: int = 10, db: Session = Depends(get_db)
):
    item = db.query(ClothingModelDB).filter(ClothingModelDB.id == model_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Модель не найдена")

    item.stock_qty += add_qty
    if item.stock_qty > 0:
        item.status = ModelStatus.AVAILABLE.value
    db.commit()
    db.refresh(item)
    return item


@router.patch(
    "/models/{model_id}/archive",
    response_model=ClothingModelRead,
    summary="Снять модель одежды с производства (в архив)",
)
def archive_clothing_model(model_id: str, db: Session = Depends(get_db)):
    item = db.query(ClothingModelDB).filter(ClothingModelDB.id == model_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Модель не найдена")

    item.status = ModelStatus.ARCHIVED.value
    db.commit()
    db.refresh(item)
    return item


@router.delete(
    "/models/{model_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить модель одежды из каталога",
)
def delete_clothing_model(model_id: str, db: Session = Depends(get_db)):
    item = db.query(ClothingModelDB).filter(ClothingModelDB.id == model_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Модель не найдена")
    db.delete(item)
    db.commit()