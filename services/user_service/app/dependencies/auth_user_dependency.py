from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from app.services.user_service import UserService
from app.services.auth_service import AuthService
from app.services.token_service import TOKEN_TYPE_FIELD, ACCESS_TOKEN_TYPE, REFRESH_TOKEN_TYPE
from app.schemas.user import  GetUser
from app.storage.postgresql.connection import get_session, SessionFactory


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

SessionDep = Annotated[SessionFactory, Depends(get_session)]

async def get_current_token_payload(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> dict:
    try:
        payload = AuthService.decode_jwt(token=token)
    except InvalidTokenError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid Token Error")
    return payload


def get_current_token_type(ttype: str):
    async def _dep(
        payload: dict = Depends(get_current_token_payload),
    ):
        """
        Factory для сокращения дублирования кода.
        В базовом случае параметры в зависимость передавать нельзя.
        """
        token_type = payload.get(TOKEN_TYPE_FIELD)
        if token_type != ttype:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token type {token_type} expected {ttype}",
            )
        return payload
    return _dep


async def get_current_user_time_in(
    payload: dict = Depends(get_current_token_payload)
) -> str:
    iat = payload.get("iat")
    return iat


async def get_current_user_from_db(session: SessionDep, payload: dict) -> GetUser:
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token invalid")
    try:
        user = await UserService.get_user_by_id(session=session, user_id=int(user_id))
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Token invalid: current user deleted or not found")
    return user


async def get_current_user(
    session: SessionDep,
    payload: dict = Depends(get_current_token_type(ACCESS_TOKEN_TYPE)),  
) -> GetUser:
    return await get_current_user_from_db(session=session, payload=payload)


async def get_current_user_for_refresh(
    session: SessionDep,
    payload: dict = Depends(get_current_token_type(REFRESH_TOKEN_TYPE)), 
) -> GetUser:
    return await get_current_user_from_db(session=session, payload=payload)


async def get_current_active_user(
        current_user: Annotated[GetUser, Depends(get_current_user)],
) -> GetUser:
    if not current_user.active:
        raise HTTPException(status_code=403, detail="Inactive user")
    return current_user


async def get_current_user_role(
        current_user: Annotated[GetUser, Depends(get_current_active_user)],
) -> GetUser:
    if current_user.role != UserRoles.admin:
        raise HTTPException(status_code=403, detail="Forbidden")
    return current_user


async def validate_user(
        user_form: Annotated[OAuth2PasswordRequestForm, Depends()],
        session: SessionDep
):
    """
       Validate user email and password
       :param user_form: username + password
       :param session: database session
       :return: user if email exist in database and password_hash is correct
       :raise HTTPException 401 if password incorrect
       :raise HTTPException 404 if user is not find
    """

    # if not user, service send exception automatic
    user = await UserService.get_user_by_email(session=session, email=user_form.username)

    # if user in db
    if AuthService.validate_password(
            password=user_form.password,
            hashed_password=user.hashed_password
    ):
        return user

    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid password"
    )
    