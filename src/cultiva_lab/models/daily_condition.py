from dataclasses import dataclass


@dataclass
class DailyCondition:
    """
    A DailyCondition class, where the User can fill out
    the day condition in each day to simule.
    """

    day: int
    temperature: float
    # Average temperature otd in °C
    rain: float
    # Rain volume in mm
    sun_hours: float
    estimated_biomass: float
    # Expected biomass otd in g / (m ^ 2)
