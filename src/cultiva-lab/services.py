from .models import User, Crop, CropType
from .storage import Database
from .exceptions import (
    UserNotFoundError,
    UserAlreadyExistsError,
    InvalidCredentialsError,
    CropNotFoundError,
    CropTypeNotFoundError,
    AuthorizationError,
    UnauthorizedAccessError
)

class CropService:
    def __init__(self, storage: Database):
        self.storage: Database = storage

    def _calculate_environment_factor(self, crop_id: str, temperature: float, rain: float, sun_hours: float) -> float:
        crop = self.storage.get_crop_by_id(crop_id)
        if not crop:
            raise CropNotFoundError(crop_id)
        crop_type = self.storage.get_crop_type_by_id(crop.crop_type_id)
        if not crop_type:
            raise CropTypeNotFoundError(crop.crop_type_id)
        
        temperature_factor = max(0, 1 - (abs(temperature - crop_type.optimal_temp) / crop_type.optimal_temp) * 0.5)
        rain_factor = min(1, rain / crop_type.needed_water) if crop_type.needed_water > 0 else 1
        sun_hours_factor = min(1, sun_hours / crop_type.needed_light) if crop_type.needed_light > 0 else 1

        return temperature_factor * rain_factor * sun_hours_factor

    def _calculate_phase_factor(self, crop_id: str) -> float:
        crop = self.storage.get_crop_by_id(crop_id)
        if not crop:
            raise CropNotFoundError(crop_id)
        crop_type = self.storage.get_crop_type_by_id(crop.crop_type_id)
        if not crop_type:
            raise CropTypeNotFoundError(crop.crop_type_id)
        
        current_day = len(crop.conditions) + 1
        phase = current_day / crop_type.days_cycle

        if phase < 0.2:
            return 0.5 + (phase * 2.5)
        elif phase < 0.7:
            return 1.0
        return max(0.2, 1.5 - phase)

    def _calculate_capacity_factor(self, crop_id):
        crop = self.storage.get_crop_by_id(crop_id)
        if not crop:
            raise CropNotFoundError(crop_id)
        crop_type = self.storage.get_crop_type_by_id(crop.crop_type_id)
        if not crop_type:
            raise CropTypeNotFoundError(crop.crop_type_id)

    def simulate_day(self, crop_id: str, temperature: float, rain: float, sun_hours: float) -> float:
        crop = self.storage.get_crop_by_id(crop_id)
        if not crop:
            raise CropNotFoundError(crop_id)
        crop_type = self.storage.get_crop_type_by_id(crop.crop_type_id)
        if not crop_type:
            raise CropTypeNotFoundError(crop.crop_type_id)
        