from app.models.user import user_collection
from app.utils.hashing import hash_password, verify_password
from app.services.jwt_handler import create_access_token

async def register_user(email: str, password: str):
    user = await user_collection.find_one({"email": email})
    if user:
        raise ValueError("User already exists")
    
    hashed = hash_password(password)
    await user_collection.insert_one({"email": email, "password": hashed})
    return True

async def authenticate_user(email: str, password: str):
    user = await user_collection.find_one({"email": email})
    if not user or not verify_password(password, user["password"]):
        return None

    token = create_access_token({"sub": user["email"]})
    return token
