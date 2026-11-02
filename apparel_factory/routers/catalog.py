from datetime import datetime
import uuid
from fastapi import APIRouter, HTTPException, status
from domain_enums import ModelStatus
from schemas.catalog import ClothingModelCreate, ClothingModelRead

router = APIRouter(prefix="/api/catalog", tags=["Catalog & Collections"])

catalog_storage: dict[str, dict] = {}


@router.post(
    "/models",
    response_model=ClothingModelRead,
    status_code=status.HTTP_201_CREATED,
    summary="Выпустить новую модель одежды в тираж",
)
def release_clothing_model(payload: ClothingModelCreate):
    """Технолог регистрирует новую модель одежды и задает объем выпущенной партии."""
    model_id = f"mdl_{uuid.uuid4().hex[:6]}"
    record = {
        "id": model_id,
        "technologist_id": payload.technologist_id,
        "sku": payload.sku.upper(),
        "name": payload.name,
        "collection": payload.collection,
        "fabric": payload.fabric,
        "stock_qty": payload.stock_qty,
        "unit_price": payload.unit_price,
        "status": ModelStatus.AVAILABLE,
        "released_at": datetime.now().strftime("%d.%m.%Y %H:%M"),
    }
    catalog_storage[model_id] = record
    return record


@router.get(
    "/models",
    response_model=list[ClothingModelRead],
    summary="Получить все модели одежды фабрики",
)
def list_clothing_models():
    return list(catalog_storage.values())