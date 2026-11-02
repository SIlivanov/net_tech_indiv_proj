from fastapi import FastAPI
from routers.catalog import router as catalog_router
from routers.pages import router as pages_router
from routers.tailoring import router as tailoring_router
from routers.users import router as users_router

app = FastAPI(
    title="KAMA APPAREL — Web-сайт фабрики одежды",
    description="Прототип микросервисной структуры: Каталог коллекций, Пошивочный цех и Ролевая авторизация",
    version="2.0.0",
)

app.include_router(pages_router)
app.include_router(users_router)
app.include_router(catalog_router)
app.include_router(tailoring_router)