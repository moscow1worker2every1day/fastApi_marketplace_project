from app.dependencies.auth_user_dependency import RefreshUserDep, ValidatedUserDep
from app.schemas.auth import Token
from app.services.token_service import TokenService
from fastapi import APIRouter, status
from app.schemas.user import GetUser, NewUser
from app.services.user_service import UserService
from app.storage.postgresql.connection import SessionDep

router = APIRouter(prefix="/auth", tags=["Authorization"])


@router.post(
    "/sign_in",
    response_model=Token,
)
async def sign_in_user(current_user: ValidatedUserDep):
    """
    Get username(email) and password
    Create payload for JWT and encode
    :return token: Token
    """
    access_token = TokenService.create_access_token(current_user)
    refresh_token = TokenService.create_refresh_token(current_user)
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post(
    "/refresh",
    response_model=Token,
    # response_model_exclude_none=True,
)
async def refresh_token(current_user: RefreshUserDep):
    access_token = TokenService.create_access_token(current_user)
    return Token(access_token=access_token)


@router.post(
    "/sign_up",
    response_model=GetUser,
    status_code=status.HTTP_201_CREATED,
)
async def sign_up_user(
    data: NewUser,
    session: SessionDep,
):
    return await UserService.create_new_user(data=data, session=session)

# @router.post("/logout", response_model=Token)
# async def logout_user(current_user: ActiveUserDep):
#     return Token(access_token=access_token, refresh_token=refresh_token)
