from dataclasses import dataclass
from datetime import datetime
from .daily_condition import DailyCondition
from src.cultiva_lab.exceptions import InvalidInputError


@dataclass
class Crop:
    """
    A crop class, that the user can use to create new crops.
    """

    id: str
    name: str
    user_id: str
    crop_type_id: str
    start_date: datetime
    last_sim_date: datetime
    conditions: list[DailyCondition]
    # List that will be filled
    # with DailyCondition objects per day.
    water_stored: float
    # Water stored in the floor (mm).
    consecutive_stress_days: int
    # Counter of stress days of a crop.
    current_phase: str
    # Current phenological phase
    active: bool

    def __post_init__(self):
        """
        Validates crop data after initialization.
        """

        self._validate_name()
        self._validate_user_id()
        self._validate_crop_type_id()
        self._validate_dates()
        self._validate_conditions()
        self._validate_water_stored()
        self._validate_consecutive_stress_days()
        self._validate_current_phase()
        self._validate_active()

    def _validate_name(self):
        """
        Validates that the crop name is a non-empty string.
        """

        if not isinstance(self.name, str) or not self.name.strip():
            raise InvalidInputError("El nombre del Cultivo no puede estár vacío.")

    def _validate_user_id(self):
        """
        Validates that the user ID is a non-empty string.
        """

        if not isinstance(self.user_id, str) or not self.user_id.strip():
            raise InvalidInputError("El ID del usuario dueño no puede estar vacío.")

    def _validate_crop_type_id(self):
        """
        Validates that the crop type ID is a non-empty string.
        """

        if not isinstance(self.crop_type_id, str) or not self.crop_type_id.strip():
            raise InvalidInputError("El ID del tipo de cultivo no puede estár vacío.")

    def _validate_dates(self):
        """
        Validates that start_date and last_sim_date are datetime objects.
        """

        if not isinstance(self.start_date, datetime):
            raise InvalidInputError(
                "La fecha de inicio debe estar en formato de fecha."
            )
        if not isinstance(self.last_sim_date, datetime):
            raise InvalidInputError(
                "La fecha de última simulación debe estar en formato de fecha."
            )

    def _validate_conditions(self):
        """
        Validates that conditions is a list.
        """

        if not isinstance(self.conditions, list):
            raise InvalidInputError("Las condiciones deben estár en una lista.")

    def _validate_water_stored(self):
        """
        Validates if water stored data is in the right type.
        """

        if not isinstance(self.water_stored, float):
            raise InvalidInputError(
                "El agua almacenada en el suelo no está en un tipo válido."
            )
        if self.water_stored < 0:
            raise InvalidInputError(
                "El agua almacenada no puede tener valores negativos."
            )

    def _validate_consecutive_stress_days(self):
        """
        Validates if the variable that stores the current number of consecutive
        stress days in the simulation is in the right type.
        """

        if not isinstance(self.consecutive_stress_days, int):
            raise InvalidInputError(
                "El contador de días consecutivos en este tramo no está en un tipo válido"
            )
        if self.consecutive_stress_days < 0:
            raise InvalidInputError(
                "Los días de estrés consecutivos no pueden ser negativos."
            )

    def _validate_current_phase(self):
        """
        Validates if the current phase of the growing simulation
        is valid.
        """

        valid_phases = ["Fase Inicial", "Fase Media", "Fase Final"]

        if self.current_phase not in valid_phases:
            raise InvalidInputError("La fase fenológica no es válida.")

    def _validate_active(self):
        """
        Validates that active is a boolean.
        """

        if not isinstance(self.active, bool):
            raise InvalidInputError("La actividad es un dato booleano.")
