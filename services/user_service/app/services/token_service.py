from app.services.auth_service import AuthService
from app.schemas.auth import auth_jwt, JWTAccessPayload, JWTRefreshPayload
from app.schemas.user import GetUser

from datetime import timedelta

TOKEN_TYPE_FIELD = "type"
ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"

class TokenService():
    @staticmethod
    def create_jwt(
        token_type: str, 
        token_data: dict,
        expire_minutes: int = auth_jwt.access_token_expire_minutes,
        expire_timedelta: timedelta | None = None
    ) -> str:
        payload = {TOKEN_TYPE_FIELD: token_type}
        payload.update(token_data)
        return AuthService.encode_jwt(
            payload=payload,
            expire_minutes=expire_minutes,
            expire_timedelta = expire_timedelta
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
            token_type=ACCESS_TOKEN_TYPE, 
            token_data=jwt_payload
        )

    @staticmethod
    def create_refresh_token(current_user: GetUser) -> str:
        jwt_payload = JWTRefreshPayload(
            sub=str(current_user.id)
        )
        return TokenService.create_jwt(
            token_type=REFRESH_TOKEN_TYPE,
            token_data=jwt_payload,
            expire_timedelta=timedelta(days=auth_jwt.refresh_token_expire_days)
        )