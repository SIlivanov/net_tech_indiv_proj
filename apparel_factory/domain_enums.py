from enum import Enum


class UserRole(str, Enum):
    TECHNOLOGIST = "Технолог фабрики"
    BUYER = "Заказчик / Байер"


class SeasonCollection(str, Enum):
    SPRING_SUMMER = "Весна-Лето"
    AUTUMN_WINTER = "Осень-Зима"
    BASIC_CAPSULE = "Базовая капсула"


class ModelStatus(str, Enum):
    AVAILABLE = "AVAILABLE"      # Партия на складе / Доступна к пошиву
    SOLD_OUT = "SOLD_OUT"        # Тираж полностью выкуплен
    ARCHIVED = "ARCHIVED"        # Снято с производства


class ProductionStatus(str, Enum):
    IN_WORKSHOP = "В ПОШИВОЧНОМ ЦЕХЕ"  # Заказ принят в работу
    SHIPPED = "ОТГРУЖЕНО СО СКЛАДА"    # Передан в доставку
    COMPLETED = "ПОЛУЧЕНО КЛИЕНТОМ"    # Сделка успешно закрыта
    CANCELLED = "ОТМЕНЕН"              # Заказ отменен (возврат партии на склад)