from fastapi import APIRouter, HTTPException, Depends, status, Request
from app.schemas.auth import UserCreate, UserLogin
from app.services.auth_service import register_user, authenticate_user
from app.services.jwt_handler import decode_token

router = APIRouter()

@router.post("/register")
async def register(user: UserCreate):
    try:
        await register_user(user.email, user.password)
        return {"message": "User registered successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
async def login(user: UserLogin):
    token = await authenticate_user(user.email, user.password)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me")
async def get_current_user(request: Request):
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")

    token = auth.split(" ")[1]
    try:
        payload = decode_token(token)
        return {"email": payload["sub"]}
    except:
        raise HTTPException(status_code=401, detail="Invalid token")
