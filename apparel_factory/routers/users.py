from datetime import datetime
import uuid
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from database import get_db
from orm_models import UserDB
from schemas.users import UserCreateDTO, UserProfileUpdateDTO, UserReadDTO

router = APIRouter(prefix="/api/users", tags=["1. Users & Profiles Context"])


def get_active_account(request: Request, db: Session) -> UserDB | None:
    uid = request.cookies.get("session_uid")
    if uid:
        return db.query(UserDB).filter(UserDB.id == uid).first()
    return None


@router.post(
    "/",
    response_model=UserReadDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Зарегистрировать или авторизовать пользователя",
)
def register_or_login_user(payload: UserCreateDTO, db: Session = Depends(get_db)):
    clean_name = payload.full_name.strip()
    user = db.query(UserDB).filter(UserDB.full_name == clean_name).first()

    if not user:
        user = UserDB(
            id=f"usr_{uuid.uuid4().hex[:5]}",
            full_name=clean_name,
            role=payload.role.value,
            phone=payload.phone,
            default_size=payload.default_size,
            city=payload.city,
            created_at=datetime.now().strftime("%d.%m.%Y %H:%M"),
        )
        db.add(user)
    else:
        user.role = payload.role.value

    db.commit()
    db.refresh(user)
    return user


@router.get("/", response_model=list[UserReadDTO], summary="Список всех пользователей")
def get_all_users(db: Session = Depends(get_db)):
    return db.query(UserDB).all()


@router.patch(
    "/{user_id}/profile",
    response_model=UserReadDTO,
    summary="Обновить мерки, телефон и адрес доставки в профиле",
)
def update_user_profile(
    user_id: str, payload: UserProfileUpdateDTO, db: Session = Depends(get_db)
):
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    user.phone = payload.phone
    user.default_size = payload.default_size
    user.city = payload.city
    db.commit()
    db.refresh(user)
    return user


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить профиль пользователя из БД",
)
def delete_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    db.delete(user)
    db.commit()