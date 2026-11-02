from pydantic import BaseModel, Field
from domain_enums import ProductionStatus


class TailoringOrderCreate(BaseModel):
    model_id: str = Field(..., example="mdl_102")
    client_id: str = Field(..., example="usr_552")
    selected_size: str = Field(..., example="L (48-50)")
    quantity: int = Field(..., gt=0, example=2)
    destination: str = Field(..., example="г. Уфа, шоурум на Чернышевского, 88")


class TailoringOrderRead(BaseModel):
    order_number: str
    model_id: str
    model_name: str
    client_id: str
    selected_size: str
    quantity: int
    total_cost: float
    destination: str
    stage: ProductionStatus
    created_at: str