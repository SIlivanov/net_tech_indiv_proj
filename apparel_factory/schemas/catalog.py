from pydantic import BaseModel, Field
from domain_enums import ModelStatus, SeasonCollection


class ClothingModelCreate(BaseModel):
    technologist_id: str = Field(..., example="usr_991")
    sku: str = Field(..., example="UF-2026-01")
    name: str = Field(..., example="Тренч двубортный из габардина")
    collection: SeasonCollection = Field(default=SeasonCollection.AUTUMN_WINTER)
    fabric: str = Field(..., example="100% хлопок с водоотталкивающей пропиткой")
    stock_qty: int = Field(..., gt=0, example=25)
    unit_price: float = Field(..., gt=0, example=14500.0)


class ClothingModelRead(ClothingModelCreate):
    id: str
    status: ModelStatus
    released_at: str