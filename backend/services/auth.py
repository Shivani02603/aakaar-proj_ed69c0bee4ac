import os
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
import bcrypt

# Constants
JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    raise ValueError("JWT_SECRET env var is not set")

ALGORITHM = "HS256"

# Functions for password hashing and verification
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed_password.encode())

# Functions for JWT token creation and decoding
def create_access_token(data: dict) -> str:
    data["exp"] = datetime.utcnow() + timedelta(hours=24)
    return jwt.encode(data, JWT_SECRET, algorithm=ALGORITHM)

def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

# FastAPI dependency to get the current user from the token
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())) -> dict:
    token = credentials.credentials
    payload = decode_access_token(token)
    if "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing 'sub' field",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload