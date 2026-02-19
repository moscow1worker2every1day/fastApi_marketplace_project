import os

from pydantic import BaseModel, field_validator
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent


class Token(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"


class JWTRefreshPayload(BaseModel):
    sub: str


class JWTAccessPayload(JWTRefreshPayload):
    username: str
    hashed_password: str
    role: str


class AuthJWT(BaseModel):
    private_key_path: Path = BASE_DIR / "keys" / "jwt-private.pem"
    public_key_path: Path = BASE_DIR / "keys" / "jwt-public.pem"
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 30

    @field_validator("private_key_path", "public_key_path")
    @classmethod
    def check_file_exists(cls, value: Path) -> Path:
        if not value.exists():
            raise RuntimeError(f"JWT key file not found: {value}")
        return value


auth_jwt = AuthJWT()
