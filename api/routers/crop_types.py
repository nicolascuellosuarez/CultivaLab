from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from src.cultiva_lab.exceptions import (CropTypeNotFoundError,
                                        ResourceOwnershipError,
                                        InvalidInputError,
                                        DuplicateDataError,
                                        BusinessRuleViolationError,
                                        UserNotFoundError)
from ..schemas.crop_type import CropTypeResponse, CropTypeCreateRequest, CropTypeUpdateRequest
from ..dependencies import get_current_user, get_crop_type_service, get_current_admin_user

router = APIRouter(prefix = "/crop-types", tags = ["Crop Types"])


