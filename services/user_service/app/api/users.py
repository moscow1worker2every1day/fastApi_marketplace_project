from fastapi import APIRouter, HTTPException, status, Depends
from app.schemas.user import NewUser, GetUser
from app.services.user_service import UserService
from app.storage.postgresql.connection import get_session, SessionFactory

router = APIRouter(prefix="/users")


@router.get("/", response_model=GetUser | dict)
async def get_user(data: int, session: SessionFactory = Depends(get_session)):
    try:
        user = await UserService.get_user_by_id(data, session)
        return GetUser.model_validate(user)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/", response_model=NewUser | dict)
async def add_user(data: NewUser, session: SessionFactory = Depends(get_session)):
    try:
        user_id = await UserService.create_new_user(data, session)
        return {"message": "ok", "user_id": user_id}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

