from pydantic import BaseModel, ConfigDict, Field
from domain_enums import UserRole


class UserCreateDTO(BaseModel):
    full_name: str = Field(..., example="Смирнова Елена")
    role: UserRole = Field(default=UserRole.BUYER)
    phone: str = Field(default="+7 (917) 450-11-22")
    default_size: str = Field(default="M (46)")
    city: str = Field(default="г. Уфа, ул. Чернышевского, 88")


class UserProfileUpdateDTO(BaseModel):
    phone: str
    default_size: str
    city: str


class UserReadDTO(BaseModel):
    id: str
    full_name: str
    role: str
    phone: str
    default_size: str
    city: str
    created_at: str

    model_config = ConfigDict(from_attributes=True)