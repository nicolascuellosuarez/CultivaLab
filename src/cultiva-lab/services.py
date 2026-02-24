from .models import User, Crop, CropType, DailyCondition
from .storage import Database
from .exceptions import (
    UserNotFoundError,
    UserAlreadyExistsError,
    InvalidCredentialsError,
    CropNotFoundError,
    CropTypeNotFoundError,
    AuthorizationError,
    UnauthorizedAccessError,
    InvalidInputError,
)
from datetime import datetime, timedelta

"""
Class CropService created to include the service logic
of crops, the pilot model to simulate their growth, and
logic restrictions based in the exceptions made.
"""


class CropService:
    def __init__(self, storage: Database) -> None:
        self.storage: Database = storage

    """
    Three factors will be used to simulate the growth.
    They will act as a pilot of the math model. The first
    factor: enviromental factor; Crop Type, temperature,
    rain and sun hours received by the crop.
    """

    def _calculate_environment_factor(
        self, crop_type: CropType, temperature: float, rain: float, sun_hours: float
    ) -> float:
        # Three factors, using the parameters
        temperature_factor = max(
            0,
            1
            - (abs(temperature - crop_type.optimal_temp) / crop_type.optimal_temp)
            * 0.5,
        )
        rain_factor = (
            min(1, rain / crop_type.needed_water) if crop_type.needed_water > 0 else 1
        )
        sun_hours_factor = (
            min(1, sun_hours / crop_type.needed_light)
            if crop_type.needed_light > 0
            else 1
        )

        return temperature_factor * rain_factor * sun_hours_factor

    """
    Second part of model, the phase is also an important factor
    in the growth process of a crop. Depending on the phase,
    the crop can increase its biomass to a greater or lesser
    extent.
    """

    def _calculate_phase_factor(self, crop: Crop, crop_type: CropType) -> float:
        current_day = len(crop.conditions) + 1
        phase = current_day / crop_type.days_cycle

        if phase < 0.2:
            return 0.5 + (phase * 2.5)
        elif phase < 0.7:
            return 1.0
        return max(0.2, 1.5 - phase)

    """
    Method created to calculate the growing capacity of
    a crop, based on its potential performance and current biomass.
    """

    def _calculate_capacity_factor(self, crop: Crop, crop_type: CropType) -> float:
        current_biomass = (
            crop.conditions[-1].estimated_biomass
            if crop.conditions
            else crop_type.initial_biomass
        )
        return max(
            0,
            (crop_type.potential_performance - current_biomass)
            / crop_type.potential_performance,
        )

    """
    Method used to calculate the total factor, and calculates
    the growth of the crop in a day.
    """

    def _calculate_growth(
        self,
        crop_type: CropType,
        env_factor: float,
        phase_factor: float,
        capacity_factor: float,
    ) -> float:
        base_rate = 0.05  # Hardcoded Base rate, remember - this is a pilot model
        total_factor = (env_factor * phase_factor * capacity_factor) ** 1.5
        return crop_type.potential_performance * base_rate * total_factor

    """
    simulate_day method to implement the logic of what happens
    if the user simulates a day in app. Validations are made
    to have restrictions and normal data in app.
    """

    def simulate_day(
        self, crop_id: str, temperature: float, rain: float, sun_hours: float
    ) -> Crop:
        crop = self.storage.get_crop_by_id(crop_id)
        if not crop:
            raise CropNotFoundError(crop_id)
        crop_type = self.storage.get_crop_type_by_id(crop.crop_type_id)
        if not crop_type:
            raise CropTypeNotFoundError(crop.crop_type_id)
        if not crop.active:
            raise InvalidInputError("The crop is already harvested.")

        # Simulating logic implementation; values of factors are taken from their methods
        env_factor = self._calculate_environment_factor(
            crop_type, temperature, rain, sun_hours
        )
        phase_factor = self._calculate_phase_factor(crop, crop_type)
        capacity_factor = self._calculate_capacity_factor(crop, crop_type)
        growth = self._calculate_growth(
            crop_type, env_factor, phase_factor, capacity_factor
        )

        current_biomass = (
            crop.conditions[-1].estimated_biomass
            if crop.conditions
            else crop_type.initial_biomass
        )
        new_biomass = min(current_biomass + growth, crop_type.potential_performance)

        # New condition added to daily conditions list in crop.
        new_condition = DailyCondition(
            day=len(crop.conditions) + 1,
            temperature=temperature,
            rain=rain,
            sun_hours=sun_hours,
            estimated_biomass=new_biomass,
        )

        crop.conditions.append(new_condition)
        crop.last_sim_date += timedelta(days=1)

        if len(crop.conditions) == crop_type.days_cycle:
            crop.active = False

        self.storage.save_crop(crop)
        return crop
