from typing import Annotated

from jwt.exceptions import InvalidTokenError
from fastapi import Depends, APIRouter, HTTPException, status

from app.schemas.user import GetUser
from app.schemas.auth import Token
from app.services.token_service import TokenService
from app.config import UserRoles
from app.dependencies.auth_user_dependency import validate_user, get_current_user_for_refresh

router = APIRouter(prefix="/auth", tags=["JWT-auth"])




@router.post("/login", response_model=Token)
async def login_for_access_token(
        current_user: Annotated[GetUser, Depends(validate_user)]
):
    """
    Get username(email) and password
    Create payload for JWT and encode
    :return token: Token
    """
    access_token = TokenService.create_access_token(current_user)
    refresh_token = TokenService.create_refresh_token(current_user)
    return Token(
        access_token=access_token,
        refresh_token=refresh_token
    )

@router.post("/refresh", response_model=Token, response_model_exclude_none=True)
async def login_refresh_token(
    current_user: Annotated[GetUser, Depends(get_current_user_for_refresh)]
):
    access_token = create_access_token(current_user)
    return Token(
         access_token=access_token
    )