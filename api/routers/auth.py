# api/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer

from src.cultiva_lab.exceptions import (
    UserNotFoundError,
    AuthorizationError,
    InvalidInputError,
    UserAlreadyExistsError,
    AdminAlreadyExistsError,
)

from ..schemas.auth import (
    LoginRequest,
    RegisterRequest,
    RegisterAdminRequest,
    LoginResponse,
    UserResponse,
)
from ..dependencies import get_user_service, create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, user_service=Depends(get_user_service)):
    try:
        user = user_service.login(request.username, request.password)
        access_token = create_access_token(
            data={"sub": user.id, "username": user.username, "role": user.role.value}
        )
        return LoginResponse(
            access_token=access_token, username=user.username, role=user.role.value
        )
    except (UserNotFoundError, AuthorizationError) as e:
        raise HTTPException(status_code=401, detail=str(e))
    except InvalidInputError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/register", response_model=UserResponse)
def register(request: RegisterRequest, user_service=Depends(get_user_service)):
    try:
        user = user_service.register_user(request.username, request.password)
        return UserResponse(id=user.id, username=user.username, role=user.role.value)
    except (InvalidInputError, UserAlreadyExistsError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/register-admin", response_model=UserResponse)
def register_admin(
    request: RegisterAdminRequest, user_service=Depends(get_user_service)
):
    try:
        user = user_service.register_admin(
            request.admin_key, request.username, request.password
        )
        return UserResponse(id=user.id, username=user.username, role=user.role.value)
    except (InvalidInputError, AdminAlreadyExistsError, UserAlreadyExistsError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/me", response_model=UserResponse)
def get_me(current_user: dict = Depends(get_current_user)):
    return UserResponse(
        id=current_user["id"],
        username=current_user["username"],
        role=current_user["role"],
    )
