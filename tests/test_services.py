import pytest
from unittest.mock import MagicMock
from src.cultiva_lab.services import CropService, UserService, CropTypeService
from src.cultiva_lab.models import User, UserRole, Crop, CropType, DailyCondition
from src.cultiva_lab.exceptions import (
    UserNotFoundError,
    UserAlreadyExistsError,
    CropNotFoundError,
    CropTypeNotFoundError,
    AuthorizationError,
    UnauthorizedAccessError,
    AdminAlreadyExistsError,
    InvalidInputError,
    ResourceOwnershipError,
    DuplicateDataError,
)


