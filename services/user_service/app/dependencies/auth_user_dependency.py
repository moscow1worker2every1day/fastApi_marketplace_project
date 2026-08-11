from typing import Annotated
from uuid import UUID

from app.enums import TokenType, UserRoles
from app.schemas.user import GetUser
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.storage.postgresql.connection import SessionDep
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/sign_in")


async def get_current_token_payload(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> dict:
    try:
        return AuthService.decode_jwt(token=token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token Error",
        )


def get_current_token_type(ttype: TokenType):
    async def _dep(
        payload: Annotated[dict, Depends(get_current_token_payload)],
    ) -> dict:
        """
        Factory для сокращения дублирования кода.
        В базовом случае параметры в зависимость передавать нельзя.
        """
        token_type = payload.get(TokenType.TOKEN_TYPE_FIELD.value)
        if token_type != ttype.value:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token type {token_type}, expected {ttype.value}",
            )
        return payload

    return _dep


async def _get_current_user_from_db(
    session: SessionDep,
    payload: dict,
) -> GetUser:
    try:
        user_id = UUID(payload.get("sub"))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalid",
        )
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalid",
        )

    return await UserService.get_user_by_id(
            session=session,
            user_id=user_id,
        )


async def get_current_user(
    session: SessionDep,
    payload: Annotated[dict, Depends(get_current_token_type(TokenType.ACCESS_TOKEN_TYPE))],
) -> GetUser:
    return await _get_current_user_from_db(session, payload)


CurrentUserDep = Annotated[GetUser, Depends(get_current_user)]


async def get_current_user_for_refresh(
    session: SessionDep,
    payload: Annotated[dict, Depends(get_current_token_type(TokenType.REFRESH_TOKEN_TYPE))],
) -> GetUser:
    return await _get_current_user_from_db(session, payload)


RefreshUserDep = Annotated[GetUser, Depends(get_current_user_for_refresh)]


async def get_current_active_user(
    current_user: CurrentUserDep,
) -> GetUser:
    if not current_user.active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    return current_user


ActiveUserDep = Annotated[GetUser, Depends(get_current_active_user)]


async def get_current_user_role(
    current_user: ActiveUserDep,
) -> GetUser:
    if current_user.role != UserRoles.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden",
        )
    return current_user


AdminUserDep = Annotated[GetUser, Depends(get_current_user_role)]


async def get_current_user_self(
    current_user: ActiveUserDep,
    payload: Annotated[dict, Depends(get_current_token_type(TokenType.ACCESS_TOKEN_TYPE))],
) -> GetUser:
    if str(current_user.id) == payload.get("sub"):
        return current_user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Forbidden: you are not allowed to access this resource",
    )


SelfUserDep = Annotated[GetUser, Depends(get_current_user_self)]


async def get_current_user_self_or_admin(
    current_user: ActiveUserDep,
    payload: Annotated[dict, Depends(get_current_token_type(TokenType.ACCESS_TOKEN_TYPE))],
) -> GetUser:
    if current_user.role == UserRoles.admin or str(current_user.id) == payload.get("sub"):
        return current_user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Forbidden: you are not allowed to access this resource",
    )


SelfOrAdminUserDep = Annotated[GetUser, Depends(get_current_user_self_or_admin)]


async def get_target_user(
    user_id: UUID,
    session: SessionDep,
) -> GetUser:
    return await UserService.get_user_by_id(session=session, user_id=user_id)


TargetUserDep = Annotated[GetUser, Depends(get_target_user)]


async def validate_user(
    user_form: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SessionDep,
) -> GetUser:
    """
    Validate user email and password
    :param user_form: username + password
    :param session: database session
    :return: user if email exist in database and password_hash is correct
    :raise HTTPException 401 if password incorrect
    :raise HTTPException 404 if user is not find
    """
    user = await UserService.get_user_by_email(
        session=session,
        email=user_form.username,
    )

    if AuthService.validate_password(
        password=user_form.password,
        hashed_password=user.hashed_password,
    ):
        return user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid password",
    )


ValidatedUserDep = Annotated[GetUser, Depends(validate_user)]
