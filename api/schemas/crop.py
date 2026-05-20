from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class DailyConditionResponse(BaseModel):
    day: int
    temperature: float
    rain: float
    sun_hours: float
    estimated_biomass: float

class CropResponse(BaseModel):
    id: str
    name: str
    crop_type_id: str
    start_date: datetime
    last_sim_date: datetime
    active: bool
    water_stored: float
    consecutive_stress_days: int
    current_phase: str

class CropCreateRequest(BaseModel):
    name: str = Field(..., min_length=1)
    crop_type_id: str
    water_stored: float = Field(..., ge=0)

class CropUpdateRequest(BaseModel):
    name: Optional[str] = None
    active: Optional[bool] = None

class CropStatisticsResponse(BaseModel):
    average_temperature: float
    average_rain: float
    average_sun_hours: float
    total_growth: float
    stress_days: int
    performance_ratio: float