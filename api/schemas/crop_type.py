from pydantic import BaseModel, Field
from typing import Optional


class CropTypeResponse(BaseModel):
    """
    Response for the request of a CropType's data.
    """

    id: str
    name: str
    optimal_temp: float
    minimum_temp: float
    maximum_temp: float
    cold_sensibility: float
    heat_sensibility: float
    cold_factor: float
    heat_factor: float
    water_wilting: float
    water_opt_low: float
    needed_water: float
    water_opt_high: float
    water_capacity: float
    water_sensibility: float
    needed_light: float
    needed_light_max: float
    light_sensibility: float
    light_km: float
    phenological_initial_coefficient: float
    phenological_mid_coefficient: float
    phenological_end_coefficient: float
    days_cycle: int
    photosyntesis_max_rate: float
    breathing_base_rate: float
    growth_breathing_coefficient: float
    consecutive_stress_days_limit: int
    activation_energy: float
    initial_biomass: float
    potential_performance: float


class CropTypeCreateRequest(BaseModel):
    """
    Class created to create a request for creation of
    a CropType.
    """

    name: str = Field(..., min_length=3)
    optimal_temp: float
    minimum_temp: float
    maximum_temp: float
    cold_sensibility: float
    heat_sensibility: float
    cold_factor: float
    heat_factor: float
    temperature_curve_length: float
    water_wilting: float
    water_opt_low: float
    needed_water: float
    water_opt_high: float
    water_capacity: float
    water_sensibility: float
    water_stress_constant: float
    needed_light: float
    needed_light_max: float
    light_sensibility: float
    light_km: float
    light_sigma: float
    phenological_initial_coefficient: float
    phenological_mid_coefficient: float
    phenological_end_coefficient: float
    days_cycle: int
    photosyntesis_max_rate: float
    breathing_base_rate: float
    growth_breathing_coefficient: float
    theta: float
    consecutive_stress_days_limit: int
    theta_coefficient: float
    activation_energy: float
    initial_biomass: float
    potential_performance: float


class CropTypeUpdateRequest(BaseModel):
    """
    Class created to answer the necesity of
    updating a CropType's info
    """

    name: Optional[str] = None
    optimal_temp: Optional[float] = None
    minimum_temp: Optional[float] = None
    maximum_temp: Optional[float] = None
    cold_sensibility: Optional[float] = None
    heat_sensibility: Optional[float] = None
    cold_factor: Optional[float] = None
    heat_factor: Optional[float] = None
    temperature_curve_length: Optional[float] = None
    water_wilting: Optional[float] = None
    water_opt_low: Optional[float] = None
    needed_water: Optional[float] = None
    water_opt_high: Optional[float] = None
    water_capacity: Optional[float] = None
    water_sensibility: Optional[float] = None
    water_stress_constant: Optional[float] = None
    needed_light: Optional[float] = None
    needed_light_max: Optional[float] = None
    light_sensibility: Optional[float] = None
    light_km: Optional[float] = None
    light_sigma: Optional[float] = None
    phenological_initial_coefficient: Optional[float] = None
    phenological_mid_coefficient: Optional[float] = None
    phenological_end_coefficient: Optional[float] = None
    days_cycle: Optional[int] = None
    photosyntesis_max_rate: Optional[float] = None
    breathing_base_rate: Optional[float] = None
    growth_breathing_coefficient: Optional[float] = None
    theta: Optional[float] = None
    consecutive_stress_days_limit: Optional[int] = None
    theta_coefficient: Optional[float] = None
    activation_energy: Optional[float] = None
    initial_biomass: Optional[float] = None
    potential_performance: Optional[float] = None
