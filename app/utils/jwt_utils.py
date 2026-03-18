from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext
from app.config.config import Config

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


class JWTUtils:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta | None = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, Config.SECRET_KEY, algorithm="HS256")
        return encoded_jwt

    @staticmethod
    def create_refresh_token(data: dict, expires_delta: timedelta | None = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                days=Config.REFRESH_TOKEN_EXPIRE_DAYS
            )
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, Config.SECRET_KEY, algorithm="HS256")
        return encoded_jwt

    @staticmethod
    def hash_token(token:str) ->str:
        """Hash the token using the same hashing algorithm as passwords"""
        return pwd_context.hash(token)
    
    @staticmethod
    def verify_refresh_token(plain_token: str, hashed_token: str) -> bool:
        """Verify the refresh token by comparing the plain token with the hashed token"""
        return pwd_context.verify(plain_token, hashed_token)