from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from cryptography.fernet import Fernet
from typing import Optional

from app.core.config import settings
from app.schemas.auth_schema import TokenData
from app.services.user_services.handler import UserService

security = HTTPBearer()

# --- Encryption/Decryption for Google Tokens ---
def get_fernet():
    return Fernet(settings.ENCRYPTION_KEY.encode())

def encrypt_token(token: str) -> str:
    fernet = get_fernet()
    return fernet.encrypt(token.encode()).decode()

def decrypt_token(encrypted_token: str) -> str:
    fernet = get_fernet()
    return fernet.decrypt(encrypted_token.encode()).decode()


def create_access_token(data: dict)->str:
    to_encode = data.copy()
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), user_service: UserService = Depends()):
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = await user_service.get_user_by_email(email=token_data.email)
    if user is None:
        raise credentials_exception
    return user