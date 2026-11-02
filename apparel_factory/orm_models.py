from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from database import Base
from domain_enums import ModelStatus, ProductionStatus


class UserDB(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    full_name = Column(String, unique=True, index=True, nullable=False)
    role = Column(String, nullable=False)
    phone = Column(String, default="+7 (900) 000-00-00")
    default_size = Column(String, default="M (46)")
    city = Column(String, default="г. Уфа, ул. Ленина, 28")
    created_at = Column(String, nullable=False)

    models_released = relationship(
        "ClothingModelDB", back_populates="technologist", cascade="all, delete-orphan"
    )
    orders_placed = relationship(
        "TailoringOrderDB", back_populates="customer", cascade="all, delete-orphan"
    )


class ClothingModelDB(Base):
    __tablename__ = "clothing_models"

    id = Column(String, primary_key=True, index=True)
    technologist_id = Column(String, ForeignKey("users.id"), nullable=False)
    sku = Column(String, index=True, nullable=False)
    name = Column(String, nullable=False)
    collection = Column(String, nullable=False)
    fabric = Column(String, nullable=False)
    stock_qty = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    status = Column(String, default=ModelStatus.AVAILABLE.value)
    released_at = Column(String, nullable=False)

    technologist = relationship("UserDB", back_populates="models_released")
    orders = relationship(
        "TailoringOrderDB", back_populates="clothing_model", cascade="all, delete-orphan"
    )


class TailoringOrderDB(Base):
    __tablename__ = "tailoring_orders"

    order_number = Column(String, primary_key=True, index=True)
    model_id = Column(String, ForeignKey("clothing_models.id"), nullable=False)
    customer_id = Column(String, ForeignKey("users.id"), nullable=False)
    model_name = Column(String, nullable=False)
    client_name = Column(String, nullable=False)
    selected_size = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    total_cost = Column(Float, nullable=False)
    destination = Column(String, nullable=False)
    stage = Column(String, default=ProductionStatus.IN_WORKSHOP.value)
    created_at = Column(String, nullable=False)

    clothing_model = relationship("ClothingModelDB", back_populates="orders")
    customer = relationship("UserDB", back_populates="orders_placed")