from typing import Annotated

from fastapi import Depends, APIRouter, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from app.schemas.user import NewUser, GetUser
from app.services.user_service import UserService
from app.storage.postgresql.connection import get_session, SessionFactory

router = APIRouter(prefix="/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SessionDep = Annotated[SessionFactory, Depends(get_session)]


async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)]
) -> GetUser:
    return GetUser(id=123, first_name="s", last_name="f", email="xs@mail.ri")


async def get_current_active_user(
        current_user: Annotated[NewUser, Depends(get_current_user)],
) -> NewUser:
    """Мы хотим получать user только если он активен"""
    if not current_user.active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@router.post("/token", response_model=dict)
async def login(
        user_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        session: SessionDep
):
    user = await UserService.get_user_by_email(session=session, email=user_data.username)

    print(user)
    hashed_password = user_data.password
    print(hashed_password)
    print(user.hashed_password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"access_token": user.first_name, "token_type": "bearer"}


@router.get("/my_account", response_model=GetUser)
async def get_my_account(current_user: Annotated[str, Depends(get_current_active_user)]):
    return current_user
