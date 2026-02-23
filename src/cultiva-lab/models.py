from dataclasses import dataclass
from enum import Enum
from datetime import datetime

"""
UserRole Dataclass implementation, inherits from Enum Module.
Allows the differentiation between the two profile types.
"""


@dataclass
class UserRole(Enum):
    ADMIN = "admin"
    USER = "user"
    # Class constants


"""
User Dataclass implementation, with its respective attributes. 
"""


@dataclass
class User:
    id: str
    username: str
    password_hash: str
    role: UserRole
    # A role Attribute, it's a UserRole type attribute.
    crop_ids: list[str]
    # A list with the crops created by usr.


"""
A CropType class, managed by Admin, where the Admin can add
new available crops for Users creation.
"""


@dataclass
class CropType:
    id: str
    name: str
    optimal_temp: float
    # Optimal temperature in °C
    needed_water: float
    # Needed water in mm per day
    needed_light: float
    # Needed light in hours per day
    days_cycle: int
    # Days needed for harvest
    initial_biomass: float
    # Initial biomass level in g / (m ^ 2)
    potential_performance: float
    # Max biomass level in g / (m ^ 2)


"""
A DailyCondition class, where the User can fill out
the day condition in each day to simule.
"""


@dataclass
class DailyCondition:
    day: int
    temperature: float
    # Average temperature otd in °C
    rain: float
    # Rain volume in mm
    sun_hours: float
    expected_biomass = float
    # Expected biomass otd in g / (m ^ 2)


"""
A crop class, that the user can use to create new crops.
"""


@dataclass
class Crop:
    id: str
    user_id: str
    crop_type_id: str
    start_date: datetime
    last_sim_date: datetime
    conditions: list[DailyCondition]
    # List that will be filled
    # with DailyCondition objects per day
    active: bool
