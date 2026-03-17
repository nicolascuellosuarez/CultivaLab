from dataclasses import dataclass


@dataclass
class CropType:
    """
    A CropType class, managed by Admin, where the Admin can add
    new available crops for Users creation.
    """

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
