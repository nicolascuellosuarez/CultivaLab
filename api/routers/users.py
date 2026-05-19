from fastapi import APIRouter, Depends, HTTPException, status
from src.cultiva_lab.exceptions import (UserNotFoundError, 
                                        ResourceOwnershipError, 
                                        InvalidInputError, 
                                        UserAlreadyExistsError)
from ..schemas.user import UserResponse, UserUpdateRequest, PasswordUpdateRequest
from ..dependencies import get_current_user, get_user_service, get_current_admin_user

router = APIRouter(prefix = "/users", tags = ["Users"])

@router.get("/{user_id}", response_model=UserResponse)
def get_user_by_id(
    user_id: str,
    current_user: dict = Depends(get_current_user),
    user_service = Depends(get_user_service)
):
    try:
        user = user_service.get_user_by_id(user_id, current_user["id"])
        return UserResponse(id=user.id, username=user.username, role=user.role.value)
    except (UserNotFoundError, ResourceOwnershipError) as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.put("/me", response_model=UserResponse)
def update_username(
    request: UserUpdateRequest,
    current_user: dict = Depends(get_current_user),
    user_service = Depends(get_user_service)
):
    try:
        user_service.update_username(current_user["id"], request.username, current_user["id"])
        return UserResponse(id=current_user["id"], username=request.username, role=current_user["role"])
    except (InvalidInputError, UserAlreadyExistsError, ResourceOwnershipError) as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/me/password")
def update_password(
    request: PasswordUpdateRequest,
    current_user: dict = Depends(get_current_user),
    user_service = Depends(get_user_service)
):
    try:
        user_service.update_password(current_user["id"], request.old_password, request.new_password)
        return {"message": "Password updated successfully"}
    except (InvalidInputError, UserNotFoundError) as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/me")
def delete_me(
    current_user: dict = Depends(get_current_user),
    user_service = Depends(get_user_service)
):
    try:
        user_service.delete_user(current_user["id"], current_user["id"])
        return {"message": "User deleted successfully"}
    except (UserNotFoundError, ResourceOwnershipError) as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/", response_model=list[UserResponse])
def get_all_users(
    current_user: dict = Depends(get_current_admin_user),
    user_service = Depends(get_user_service)
):
    users = user_service.get_all_users(current_user["id"])
    return [UserResponse(id=u.id, username=u.username, role=u.role.value) for u in users]