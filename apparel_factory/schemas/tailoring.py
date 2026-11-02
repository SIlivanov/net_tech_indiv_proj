from pydantic import BaseModel, ConfigDict, Field
from domain_enums import ProductionStatus


class TailoringOrderCreate(BaseModel):
    model_id: str = Field(..., example="mdl_102")
    customer_id: str = Field(..., example="usr_552")
    selected_size: str = Field(..., example="L (48)")
    quantity: int = Field(..., gt=0, example=3)
    destination: str = Field(..., example="г. Уфа, шоурум на Чернышевского, 88")


class TailoringOrderRead(BaseModel):
    order_number: str
    model_id: str
    customer_id: str
    model_name: str
    client_name: str
    selected_size: str
    quantity: int
    total_cost: float
    destination: str
    stage: ProductionStatus
    created_at: str

    model_config = ConfigDict(from_attributes=True)