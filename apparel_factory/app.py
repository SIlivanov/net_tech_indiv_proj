from fastapi import FastAPI
from database import Base, engine
import orm_models  # Регистрация всех 3 таблиц (users, clothing_models, tailoring_orders)
from routers.catalog import router as catalog_router
from routers.pages import router as pages_router
from routers.tailoring import router as tailoring_router
from routers.users import router as users_router

# Создание таблиц всех 3 контекстов в файле factory_db.sqlite
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Web-сайт фабрики одежды",
    description=(
        "Полная реализация 3 контекстов с реляционной БД SQLite: "
        "1. Пользователи и Профили мерок, 2. Каталог коллекций, 3. Пошивочный цех и Заказы"
    ),
    version="3.0.0",
)

app.include_router(pages_router)
app.include_router(users_router)
app.include_router(catalog_router)
app.include_router(tailoring_router)