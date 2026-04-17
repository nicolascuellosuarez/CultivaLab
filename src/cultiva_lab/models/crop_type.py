from dataclasses import dataclass
from src.cultiva_lab.exceptions import InvalidInputError


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
    minimum_temp: float
    # Minimum base temperature
    maximum_temp: float
    # Maximum base temperature
    cold_sensibility: float
    heat_sensibility: float
    # Sensibility factors for breathing process
    cold_factor: float
    heat_factor: float
    # Exponential factors for breathing factors
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

    def __post_init__(self):
        """Validates crop type data after initialization."""
        self._validate_id()
        self._validate_name()
        self._validate_optimal_temp()
        self._validate_needed_water()
        self._validate_needed_light()
        self._validate_days_cycle()
        self._validate_initial_biomass()
        self._validate_potential_performance()

    def _validate_id(self):
        """
        Validates that the crop type ID is a non-empty string.
        """

        if not isinstance(self.id, str) or not self.id.strip():
            raise InvalidInputError(
                "El ID del tipo de cultivo debe ser un texto no vacío."
            )

    def _validate_name(self):
        """
        Validates that the crop type name is a non-empty string.
        """

        if not isinstance(self.name, str) or not self.name.strip():
            raise InvalidInputError(
                "El nombre del tipo de cultivo debe ser un texto no vacío."
            )

    def _validate_optimal_temp(self):
        """
        Validates that optimal temperature is a number and within valid range.
        """

        if not isinstance(self.optimal_temp, (int, float)):
            raise InvalidInputError("La temperatura óptima debe ser un número.")
        if self.optimal_temp < -7:
            raise InvalidInputError("La temperatura óptima no puede ser menor a -7°C.")

    def _validate_minimum_temp(self):
        """
        Validates that the minimum optimal temperature is in the right type
        """

        if not isinstance(self.minimum_temp, (int, float)):
            raise InvalidInputError("La mínima temperatura óptima no esta en un tipo válido.")
        if self.minimum_temp >= self.maximum_temp:
            raise InvalidInputError("La mínima temperatura óptima no puede ser mayor o igual a la mayor temperatura óptima.")
        if self.minimum_temp < -7:
            raise InvalidInputError("La mínima temperatura óptima no puede ser menor a-7°C.")
        
    def _validate_maximum_temp(self):
        """
        Validates that the maximum optimal temperature is in the right type
        """

        if not isinstance(self.maximum_temp, (int, float)):
            raise InvalidInputError("La máxima temperatura óptima no esta en un tipo válido.")
        if self.maximum_temp < -7:
            raise InvalidInputError("La máxima temperatura óptima no puede ser menor a -7 grados")

    def _validate_needed_water(self):
        """
        Validates that needed water is a positive number.
        """

        if not isinstance(self.needed_water, (int, float)):
            raise InvalidInputError("El agua necesaria debe ser un número.")
        if self.needed_water <= 0:
            raise InvalidInputError("El agua necesaria debe ser mayor a cero.")

    def _validate_needed_light(self):
        """
        Validates that needed light is a positive number.
        """

        if not isinstance(self.needed_light, (int, float)):
            raise InvalidInputError("La luz necesaria debe ser un número.")
        if self.needed_light <= 0:
            raise InvalidInputError("La luz necesaria debe ser mayor a cero.")

    def _validate_days_cycle(self):
        """
        Validates that days cycle is a positive integer.
        """

        if not isinstance(self.days_cycle, int):
            raise InvalidInputError("Los días de ciclo deben ser un número entero.")
        if self.days_cycle <= 0:
            raise InvalidInputError("Los días de ciclo deben ser mayores a cero.")

    def _validate_initial_biomass(self):
        """
        Validates that initial biomass is a positive number.
        """

        if not isinstance(self.initial_biomass, (int, float)):
            raise InvalidInputError("La biomasa inicial debe ser un número.")
        if self.initial_biomass <= 0:
            raise InvalidInputError("La biomasa inicial debe ser mayor a cero.")

    def _validate_potential_performance(self):
        """
        Validates that potential performance is a positive number.
        """

        if not isinstance(self.potential_performance, (int, float)):
            raise InvalidInputError("El rendimiento potencial debe ser un número.")
        if self.potential_performance <= 0:
            raise InvalidInputError("El rendimiento potencial debe ser mayor a cero.")
