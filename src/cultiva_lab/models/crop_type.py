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
    # Minimum base temperature in °C
    maximum_temp: float
    # Maximum base temperature in °C
    cold_sensibility: float
    heat_sensibility: float
    # Sensibility factors for breathing process
    cold_factor: float
    heat_factor: float
    # Exponential factors for breathing factors
    water_wilting: float
    water_opt_low: float
    needed_water: float
    water_opt_high: float
    water_capacity: float
    # Levels of water in mm
    water_sensibility: float
    # Water sensibility factor of breathing
    needed_light: float
    needed_light_max: float
    # Optimal and maximum light hours in hours per day
    light_sensibility: float
    # Sensibility to light factor
    phenological_initial_coefficient: float
    phenological_mid_coefficient: float
    phenological_end_coefficient: float
    # Coefficients of every growing phase
    days_cycle: int
    # Days needed for harvest
    photosyntesis_max_rate: float
    breathing_base_rate: float
    # Rates of photosynthesis and breathing
    theta: float
    # Logistic assymetry factor
    consecutive_stress_days: int
    consecutive_stress_days_limit: int
    # Limit counter of consecutive stress days
    theta_coefficient: float
    # Water transpiration coefficient
    initial_biomass: float
    # Initial biomass level in g / (m ^ 2)
    potential_performance: float
    # Max biomass level in g / (m ^ 2)

    def __post_init__(self):
        """Validates crop type data after initialization."""
        self._validate_id()
        self._validate_name()
        self._validate_optimal_temp()
        self._validate_minimum_temp()
        self._validate_maximum_temp()
        self._validate_cold_sensibility()
        self._validate_heat_sensibility()
        self._validate_cold_factor()
        self._validate_heat_factor()
        self._validate_needed_water()
        self._validate_needed_light()
        self._validate_needed_light_max()
        self._validate_light_sensibility()
        self._validate_phenological_initial_coefficient()
        self._validate_phenological_mid_coefficient()
        self._validate_phenological_end_coefficient()
        self._validate_days_cycle()
        self._validate_photosyntesis_max_rate()
        self._validate_breathing_base_rate()
        self._validate_theta()
        self._validate_consecutive_stress_days()
        self._validate_consecutive_stress_days_limit()
        self._validate_theta_coefficient()
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
        if self.minimum_temp and self.minimum_temp >= self.maximum_temp:
            raise InvalidInputError(
                "La mayor tenmperatura óptima no puede ser menor o igual a la menor temperatura óptima."
            )
        if self.optimal_temp < -7:
            raise InvalidInputError("La temperatura óptima no puede ser menor a -7°C.")

    def _validate_minimum_temp(self):
        """
        Validates that the minimum optimal temperature is in the right type
        """

        if not isinstance(self.minimum_temp, (int, float)):
            raise InvalidInputError(
                "La mínima temperatura óptima no está en un tipo válido."
            )
        if self.maximum_temp and self.minimum_temp >= self.maximum_temp:
            raise InvalidInputError(
                "La mínima temperatura óptima no puede ser mayor o igual a la mayor temperatura óptima."
            )
        if self.minimum_temp < -7:
            raise InvalidInputError(
                "La mínima temperatura óptima no puede ser menor a-7°C."
            )

    def _validate_maximum_temp(self):
        """
        Validates that the maximum optimal temperature is in the right type
        """

        if not isinstance(self.maximum_temp, (int, float)):
            raise InvalidInputError(
                "La máxima temperatura óptima no está en un tipo válido."
            )
        if self.minimum_temp and self.minimum_temp >= self.maximum_temp:
            raise InvalidInputError(
                "La mínima temperatura óptima no puede ser mayor o igual a la mayor temperatura óptima."
            )
        if self.maximum_temp < -7:
            raise InvalidInputError(
                "La máxima temperatura óptima no puede ser menor a -7 grados"
            )

    def _validate_cold_sensibility(self):
        """
        Validates if cold sensibility is valid.
        """

        if not isinstance(self.cold_sensibility, (int, float)):
            raise InvalidInputError(
                "La sensibilidad al frío no está en un tipo válido."
            )
        if self.cold_sensibility < 0:
            raise InvalidInputError(
                "La sensibilidad al frío de la planta no puede ser negativa."
            )

    def _validate_heat_sensibility(self):
        """
        Validates if heat sensibility is valid.
        """

        if not isinstance(self.heat_sensibility, (int, float)):
            raise InvalidInputError(
                "La sensibilidad al calor no está en un tipo válido."
            )
        if self.head_sensibility < 0:
            raise InvalidInputError(
                "La sensibilidad al calor de la planta no puede ser negativa."
            )

    def _validate_cold_factor(self):
        """
        Validates if breathing factor of cold is valid.
        """

        if not isinstance(self.cold_factor, (int, float)):
            raise InvalidInputError(
                "El factor de respiración con respecto al frío no está en un tipo válido."
            )
        if self.cold_factor <= 0:
            raise InvalidInputError(
                "El factor de respiración con respecto al frío no puede ser menor o igual a 0."
            )

    def _validate_heat_factor(self):
        """
        Validates if breathing factor of cold is valid.
        """

        if not isinstance(self.heat_factor, (int, float)):
            raise InvalidInputError(
                "El factor de respiración con respecto al calor no está en un tipo válido."
            )
        if self.heat_factor <= 0:
            raise InvalidInputError(
                "El factor de respiración con respecto al calor no puede ser menor o igual a 0."
            )

    def _validate_water_wilting(self):
        """
        Validates if wilting level of water is valid.
        """

        if not isinstance(self.water_wilting, (float, int)):
            raise InvalidInputError(
                "El valor de marchitación del agua no está en un tipo válido."
            )
        if self.water_wilting <= 0:
            raise InvalidInputError(
                "El valor de marchitación del agua no puede ser negativo ni 0."
            )
        if (
            self.water_opt_low,
            self.needed_water,
            self.water_opt_high,
            self.water_capacity,
        ) and not (
            self.water_wilting
            < self.water_opt_low
            < self.needed_Water
            < self.water_opt_high
            < self.water_capacity
        ):
            raise InvalidInputError("Los valores de niveles de agua no son válidos.")

    def _validate_water_opt_low(self):
        """
        Validates if the lower optimum level of water is valid.
        """

        if not isinstance(self.water_opt_low, (int, float)):
            raise InvalidInputError(
                "El valor de el menor valor óptimo del agua no está en un tipo válido."
            )
        if self.water_opt_low <= 0:
            raise InvalidInputError(
                "El valor de el menor valor óptimo del agua no puede ser menor o igual a 0."
            )
        if (
            self.water_wilting,
            self.needed_water,
            self.water_opt_high,
            self.water_capacity,
        ) and not (
            self.water_wilting
            < self.water_opt_low
            < self.needed_Water
            < self.water_opt_high
            < self.water_capacity
        ):
            raise InvalidInputError("Los valores de niveles de agua no son válidos.")

    def _validate_needed_water(self):
        """
        Validates that needed water is a positive number.
        """

        if not isinstance(self.needed_water, (int, float)):
            raise InvalidInputError("El agua necesaria debe ser un número.")
        if self.needed_water <= 0:
            raise InvalidInputError("El agua necesaria debe ser mayor a cero.")
        if (
            self.water_wilting,
            self.water_opt_low,
            self.water_opt_high,
            self.water_capacity,
        ) and not (
            self.water_wilting
            < self.water_opt_low
            < self.needed_Water
            < self.water_opt_high
            < self.water_capacity
        ):
            raise InvalidInputError("Los valores de niveles de agua no son válidos.")

    def _validate_water_opt_high(self):
        """
        Validates if higher optimum level of water is valid.
        """

        if not isinstance(self.water_opt_high, (int, float)):
            raise InvalidInputError(
                "El valor de el mayor valor óptimo del agua no esta en un tipo válido."
            )
        if self.water_opt_high <= 0:
            raise InvalidInputError(
                "El valor de el mayor valor óptimo del agua no puede ser menor o igual a 0."
            )
        if (
            self.water_wilting,
            self.water_opt_low,
            self.needed_water,
            self.water_capacity,
        ) and not (
            self.water_wilting
            < self.water_opt_low
            < self.needed_Water
            < self.water_opt_high
            < self.water_capacity
        ):
            raise InvalidInputError("Los valores de niveles de agua no son válidos.")

    def _validate_water_capacity(self):
        """
        Validates if water total capacity is valid.
        """

        if not isinstance(self.water_capacity, (int, float)):
            raise InvalidInputError(
                "El valor del mayor valor de crecimiento del agua no es un tipo válido."
            )
        if self.water_capacity <= 0:
            raise InvalidInputError(
                "El valor del mayor valor de crecimiento del agua no puede ser menor o igual a 0."
            )
        if (
            self.water_wilting,
            self.water_opt_low,
            self.needed_water,
            self.water_opt_high,
        ) and not (
            self.water_wilting
            < self.water_opt_low
            < self.needed_Water
            < self.water_opt_high
            < self.water_capacity
        ):
            raise InvalidInputError("Los valores de niveles de agua no son válidos.")

    def _validate_water_sensibility(self):
        """
        Validates if water breathing sensibility is valid.
        """

        if not isinstance(self.water_sensibility, (int, float)):
            raise InvalidInputError(
                "El coeficiente de sensibilidad del agua no está en un tipo válido."
            )
        if self.water_sensibility <= 0:
            raise InvalidInputError(
                "El valor del coeficiente de sensibilidad del agua no puede ser menor o igual a 0."
            )

    def _validate_needed_light(self):
        """
        Validates that needed light is a positive number.
        """

        if not isinstance(self.needed_light, (int, float)):
            raise InvalidInputError("La luz necesaria debe ser un número.")
        if self.needed_light <= 0:
            raise InvalidInputError("La luz necesaria debe ser mayor a cero.")
        if self.needed_light_max and self.needed_light_max <= self.needed_light:
            raise InvalidInputError(
                "La mayor cantidad de horas posibles no puede ser menor o igual a las horas óptimas."
            )

    def _validate_needed_light_max(self):
        """
        Validates that max value of hours before photoinhibition is valid.
        """

        if not isinstance(self.needed_light_max, (int, float)):
            raise InvalidInputError(
                "La mayor cantidad de horas posibles debe ser un número."
            )
        if self.needed_light_max <= 0:
            raise InvalidInputError(
                "La mayor cantidad de horas posibles no puede ser menor o igual a 0."
            )
        if self.needed_light and self.needed_light_max <= self.needed_light:
            raise InvalidInputError(
                "La mayor cantidad de horas posibles no puede ser menor o igual a las horas óptimas."
            )

    def _validate_light_sensibility(self):
        """
        Validates if sensibility factor of light stress is valid.
        """

        if not isinstance(self.light_sensibility, (int, float)):
            raise InvalidInputError(
                "El factor de sensibilidad a la luz no está en un tipo válido."
            )
        if self.light_sensibility <= 0:
            raise InvalidInputError(
                "El factor de sensibilidad a la luz no puede ser menor o igual a 0."
            )

    def _validate_phenological_initial_coefficient(self):
        """
        Validates if the coefficient of the first phase of growing is valid.
        """

        if not isinstance(self.phenological_initial_coefficient, (int, float)):
            raise InvalidInputError(
                "El factor fenológico de inicio no está en un tipo válido."
            )
        if self.phenological_initial_coefficient <= 0:
            raise InvalidInputError(
                "El factor fenológico de crecimiento no puede ser menor o igual a 0."
            )
        if self.phenological_mid_coefficient and (
            self.phenological_initial_coefficient > self.phenological_mid_coefficient
        ):
            raise InvalidInputError(
                "El factor fenológico de inicio no puede ser mayor al de el medio."
            )

    def _validate_phenological_mid_coefficient(self):
        """
        Validates if the coefficient of the second phase is valid.
        """

        if not isinstance(self.phenological_mid_coefficient, (int, float)):
            raise InvalidInputError(
                "El factor fenológico de la fase media de crecimiento no tiene un tipo válido."
            )
        if self.phenological_mid_coefficient <= 0:
            raise InvalidInputError(
                "El factor fenológico de la fase media del crecimiento no puede ser menor o igual a 0."
            )
        if (
            self.phenological_initial_coefficient
            and self.phenological_end_coefficient
            and (
                self.phenological_initial_coefficient
                >= self.phenological_mid_coefficient
                or self.phenological_end_coefficient
                >= self.phenological_mid_coefficient
            )
        ):
            raise InvalidInputError(
                "El factor fenológico de la fase media debe ser mayor al de la inicial y final."
            )

    def _validate_phenological_end_coefficient(self):
        """
        Validates if the coefficient of the final phase is valid.
        """

        if not isinstance(self.phenological_end_coefficient, (int, float)):
            raise InvalidInputError(
                "El factor fenológico de la última fase no está en un tipo válido."
            )
        if self.phenological_end_coefficient <= 0:
            raise InvalidInputError(
                "El factor fenológico de la última fase no puede ser menor o igual a 0."
            )
        if self.phenological_mid_coefficient and (
            self.phenological_end_coefficient > self.phenological_mid_coefficient
        ):
            raise InvalidInputError(
                "El factor fenológico final no puede ser mayor al de el medio."
            )

    def _validate_days_cycle(self):
        """
        Validates that days cycle is a positive integer.
        """

        if not isinstance(self.days_cycle, int):
            raise InvalidInputError("Los días de ciclo deben ser un número entero.")
        if self.days_cycle <= 0:
            raise InvalidInputError("Los días de ciclo deben ser mayores a cero.")

    def _validate_photosyntesis_max_rate(self):
        """
        Validates if the max rate of photosyntesis per day is valid.
        """

        if not isinstance(self.photosyntesis_max_rate, (float, int)):
            raise InvalidInputError(
                "La tasa máxima de fotosíntesis por día no está en un tipo válido."
            )
        if self.photosyntesis_max_rate <= 0:
            raise InvalidInputError(
                "La tasa máxima de fotosíntesis por día no puede ser menor o igual a 0."
            )

    def _validate_breathing_base_rate(self):
        """
        Validates if the base breathing rate per day is valid.
        """

        if not isinstance(self.breathing_base_rate, (float, int)):
            raise InvalidInputError(
                "La tasa base de respiración por día no está en un tipo válido."
            )
        if self.breathing_base_rate <= 0:
            raise InvalidInputError(
                "La tasa base de respiración no puede ser menor o igual a 0."
            )

    def _validate_theta(self):
        """
        Validates if the theta assymmetric factor is valid.
        """

        if not isinstance(self.theta, (int, float)):
            raise InvalidInputError(
                "El factor de asimetría en el crecimiento no está en un tipo válido."
            )
        if self.theta <= 0:
            raise InvalidInputError(
                "El factor de asimetría en el crecimiento no puede ser menor o igual."
            )

    def _validate_consecutive_stress_days(self):
        """
        Validates if the stress days that are consecutive are valid.
        """

        if not isinstance(self.consecutive_stress_days, (int)):
            raise InvalidInputError(
                "La cantidad de días consecutivos actual no es válida."
            )
        if self.consecutive_stress_days < 0:
            raise InvalidInputError(
                "La cantidad de días consecutivos no puede ser menor a 0."
            )

    def _validate_consecutive_stress_days_limit(self):
        """
        Validates if the maximum quantity of consecutive stress days is valid.
        """

        if not isinstance(self.consecutive_stress_days_limit, (int)):
            raise InvalidInputError(
                "La cantidad de días de estrés límite no está en el tipo adecuado."
            )
        if self.consecutive_stress_days_limit < 0:
            raise InvalidInputError(
                "La cantidad de días de estrés límite no puede ser menor a 0."
            )

    def _validate_theta_coefficient(self):
        """
        Validates if water transpiration coefficient is valid.
        """

        if not isinstance(self.theta_coefficient, (int, float)):
            raise InvalidInputError(
                "El coeficiente de transpiración no está en un tipo válido."
            )
        if self.theta_coefficient <= 0:
            raise InvalidInputError(
                "El coeficiente de transpiracion del agua no puede ser menor o igual a 0."
            )

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
