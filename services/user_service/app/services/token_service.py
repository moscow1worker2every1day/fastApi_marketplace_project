from datetime import timedelta

from app.schemas.auth import JWTAccessPayload, JWTRefreshPayload, auth_jwt
from app.schemas.user import GetUser
from app.services.auth_service import AuthService
from app.enums import TokenType


class TokenService:
    @staticmethod
    def create_jwt(
        token_type: TokenType,
        token_data: dict,
        expire_minutes: int = auth_jwt.access_token_expire_minutes,
        expire_timedelta: timedelta | None = None,
    ) -> str:
        payload = {TokenType.TOKEN_TYPE_FIELD.value: token_type.value}
        payload.update(token_data)
        return AuthService.encode_jwt(
            payload=payload,
            expire_minutes=expire_minutes,
            expire_timedelta=expire_timedelta,
        )

    @staticmethod
    def create_access_token(current_user: GetUser) -> str:
        jwt_payload = JWTAccessPayload(
            sub=str(current_user.id),
            username=current_user.email,
            hashed_password=current_user.hashed_password,
            role=current_user.role,
        ).model_dump()
        return TokenService.create_jwt(
            token_type=TokenType.ACCESS_TOKEN_TYPE, token_data=jwt_payload
        )

    @staticmethod
    def create_refresh_token(current_user: GetUser) -> str:
        jwt_payload = JWTRefreshPayload(sub=str(current_user.id)).model_dump()
        return TokenService.create_jwt(
            token_type=TokenType.REFRESH_TOKEN_TYPE,
            token_data=jwt_payload,
            expire_timedelta=timedelta(
                days=auth_jwt.refresh_token_expire_days),
        )
