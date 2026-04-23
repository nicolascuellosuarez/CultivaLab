from dataclasses import dataclass
from src.cultiva_lab.exceptions import InvalidInputError


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

    def __post_init__(self):
        self._validate_day()
        self._validate_temperature()
        self._validate_rain()
        self._validate_sun_hours()
        self._validate_estimated_biomass()

    def _validate_day(self):
        """
        Restricted method created to check the type of
        a daily condition.
        """

        if not isinstance(self.day, int):
            raise InvalidInputError("El día debe ser un número entero.")

    def _validate_temperature(self):
        """
        Restricted method created to check the
        validity of the temperature of a day.
        """

        if not isinstance(self.temperature, (int, float)):
            raise InvalidInputError("La temperatura debe ser numérica.")
        if self.temperature < -10 or self.temperature > 56.7:
            raise InvalidInputError("La temperatura debe estar entre -10°C y 56.7°C.")

    def _validate_rain(self):
        """
        Restricted method created to check the validity
        of the rain received by the crop in a day (mm).
        """

        if not isinstance(self.rain, (int, float)):
            raise InvalidInputError("La lluvia debe ser numérica.")
        if self.rain < 0:
            raise InvalidInputError("La lluvia no puede ser negativa.")

    def _validate_sun_hours(self):
        """
        Restricted method created to check the validity
        of the sun hours of a created DailyCondition.
        """

        if not isinstance(self.sun_hours, (int, float)):
            raise InvalidInputError("Las horas de sol deben ser numéricas.")
        if self.sun_hours < 0 or self.sun_hours > 16:
            raise InvalidInputError("Las horas de sol deben estar entre 0 y 16.")

    def _validate_estimated_biomass(self):
        """
        Restricted method created to check the validity of the
        stimated biomass of a daily condition.
        """

        if not isinstance(self.estimated_biomass, (int, float)):
            raise InvalidInputError("La biomasa estimada debe ser numérica.")
        if self.estimated_biomass < 0:
            raise InvalidInputError("La biomasa estimada no puede ser negativa.")
