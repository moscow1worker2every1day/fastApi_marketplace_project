from datetime import datetime, timezone, timedelta

import jwt
import bcrypt

from app.schemas.auth import auth_jwt


class AuthService:
    @staticmethod
    def encode_jwt(
            payload: dict,
            private_key: str = auth_jwt.private_key_path.read_text(),
            algorithm: str = auth_jwt.algorithm,
            expire_minutes: int = auth_jwt.access_token_expire_minutes,
            expire_timedelta: timedelta | None = None,
    ):
        """
        Generate jwt-token with expire time (minutes or delta)
        """
        to_encode = payload.copy()
        now = datetime.now(timezone.utc)
        if expire_timedelta:
            expire = now + expire_timedelta
        else:
            expire = now + timedelta(minutes=expire_minutes)
        to_encode.update(exp=expire, iat=now)
        encoded = jwt.encode(to_encode, private_key, algorithm=algorithm)
        return encoded

    @staticmethod
    def decode_jwt(
            token: str | bytes,
            public_key: str = auth_jwt.public_key_path.read_text(),
            algorithm: str = auth_jwt.algorithm,
    ):
        """
            Get and decode jwt-token
            
        """
        decoded = jwt.decode(token, public_key, algorithms=[algorithm])
        return decoded

    @staticmethod
    def hash_password(
            password: str
    ) -> bytes:
        """
            Hash password, salt - some information to hash pw
        """
        pwd_bytes: bytes = password.encode()
        return bcrypt.hashpw(pwd_bytes, bcrypt.gensalt())

    @staticmethod
    def validate_password(
            password: str,
            hashed_password: str
    ) -> bool:
        return bcrypt.checkpw(
            password=password.encode("utf-8"),
            hashed_password=hashed_password.encode("utf-8")
        )
