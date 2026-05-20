from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

from src.cultiva_lab.services import UserService, CropService, CropTypeService
from src.cultiva_lab.storage_for_supabase import SupabaseStorage

load_dotenv()

SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "cultivalab_secret_key_change_me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

storage = SupabaseStorage()
user_service = UserService(storage)
crop_service = CropService(storage)
crop_type_service = CropTypeService(storage, user_service)

security = HTTPBearer()

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        username: str = payload.get("username")
        role: str = payload.get("role")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"id": user_id, "username": username, "role": role}
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_active_user(current_user: dict = Depends(get_current_user)) -> dict:
    return current_user

def get_current_admin_user(current_user: dict = Depends(get_current_user)) -> dict:
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

def get_user_service() -> UserService:
    return user_service

def get_crop_service() -> CropService:
    return crop_service

def get_crop_type_service() -> CropTypeService:
    return crop_type_service
