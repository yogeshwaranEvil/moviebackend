from datetime import datetime, timedelta
from jose import jwt
from app.config import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRATION_SECONDS

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(seconds=JWT_EXPIRATION_SECONDS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def decode_token(token: str):
    return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
