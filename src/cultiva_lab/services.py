from src.cultiva_lab.models import User, Crop, CropType, DailyCondition, UserRole
from .storage import Database
from src.cultiva_lab.exceptions import (
    UserNotFoundError,
    UserAlreadyExistsError,
    CropNotFoundError,
    CropTypeNotFoundError,
    AuthorizationError,
    AdminAlreadyExistsError,
    InvalidInputError,
    ResourceOwnershipError,
    DuplicateDataError,
    BusinessRuleViolationError,
)
from datetime import datetime, timedelta
import uuid
import bcrypt
import math

MASTER_KEY = "admin12345"


class CropService:
    """
    Class CropService created to include the service logic
    of crops, the pilot model to simulate their growth, and
    logic restrictions based in the exceptions made.
    """

    def __init__(self, storage: Database) -> None:
        self.storage: Database = storage

    def _calculate_production_thermal_factor(
        self, crop_type: CropType, temperature: float
    ) -> float:
        """
        Gaussian function for thermal effect on photosynthesis.
        Peak at optimal_temp, decreases as temperature deviates.
        """

        sigma = crop_type.temperature_curve_length
        return math.exp(-((temperature - crop_type.optimal_temp) ** 2) / (2 * sigma**2))

    def _calculate_water_factor_production(
        self, crop_type: CropType, water_stored: float
    ) -> float:
        """
        Water stress factor for photosynthesis.
        Penalizes both deficit and excess of water.
        """

        f_W = (
            1
            / (
                1
                + math.exp(
                    crop_type.water_stress_constant
                    * (crop_type.water_opt_low - water_stored)
                )
            )
        ) * (
            1
            / (
                1
                + math.exp(
                    crop_type.water_stress_constant
                    * (water_stored - crop_type.water_opt_high)
                )
            )  # FIX: signo positivo
        )
        return f_W

    def _calculate_light_production_factor(
        self, crop_type: CropType, sun_hours: float
    ) -> float:
        """
        Light stress factor for photosynthesis.
        Michaelis-Menten for low light, Gaussian for excess.
        """

        normalization = crop_type.needed_light / (
            crop_type.needed_light + crop_type.light_km
        )

        if sun_hours <= crop_type.needed_light:
            f_L_raw = sun_hours / (sun_hours + crop_type.light_km)
            f_L = f_L_raw / normalization if normalization > 0 else 0.0
        elif crop_type.needed_light < sun_hours <= crop_type.needed_light_max:
            f_L = math.exp(
                -((sun_hours - crop_type.needed_light) ** 2)
                / (2 * (crop_type.light_sigma**2))
            )
        else:
            f_L = math.exp(
                -((crop_type.needed_light_max - crop_type.needed_light) ** 2)
                / (2 * (crop_type.light_sigma**2))
            )

        return min(f_L, 1.0)

    def _calculate_breathing_thermal_factor(
        self, crop_type: CropType, temperature: float
    ) -> float:
        """
        Thermal effect on maintenance respiration.
        Increases exponentially outside optimal range.
        """
        if temperature < crop_type.minimum_temp:
            h_T = 1 + crop_type.cold_factor * math.exp(
                crop_type.cold_sensibility * (crop_type.minimum_temp - temperature)
            )
        elif temperature > crop_type.maximum_temp:
            h_T = 1 + crop_type.heat_factor * math.exp(
                crop_type.heat_sensibility * (temperature - crop_type.maximum_temp)
            )
        else:
            h_T = 1
        return h_T

    def _calculate_logistic_growth_term(
        self, crop_type: CropType, biomass: float
    ) -> float:
        """
        Logistic term for carrying capacity.
        """
        K = crop_type.potential_performance
        if K <= 0:
            return 1.0
        return 1 - (biomass / K) ** crop_type.theta

    def _calculate_photosynthesis(
        self,
        crop_type: CropType,
        biomass: float,
        logistic_term: float,
        f_T: float,
        f_W: float,
        f_L: float,
    ) -> float:
        """
        Net photosynthesis after environmental stress.
        El término logístico se aplica aquí y SOLO aquí (ver FIX #3).
        """
        return (
            crop_type.photosyntesis_max_rate * biomass * logistic_term * f_T * f_W * f_L
        )

    def _calculate_maintenance_respiration(
        self, crop_type: CropType, biomass: float, temperature: float
    ) -> float:
        """
        Maintenance respiration - depends on biomass and temperature only.
        """
        h_T = self._calculate_breathing_thermal_factor(crop_type, temperature)
        return crop_type.breathing_base_rate * biomass * h_T

    def _calculate_growth_respiration_coefficient(
        self, crop_type: CropType, biomass: float
    ) -> float:
        """
        Growth respiration coefficient (dynamic).
        Young plants have lower coefficient (more efficient).
        Mature plants have higher coefficient (more structural cost).
        """
        K = crop_type.potential_performance
        if K <= 0:
            return 0.2
        ratio = min(1.0, biomass / K)
        # Rango de 0.15 (planta joven) a 0.45 (planta madura)
        return 0.15 + 0.3 * ratio

    def _calculate_net_growth(
        self,
        crop_type: CropType,
        biomass: float,
        photosynthesis: float,
        temperature: float,
    ) -> float:
        """
        Net growth after growth respiration and maintenance respiration.
        """

        g_R = self._calculate_growth_respiration_coefficient(crop_type, biomass)
        growth = photosynthesis * (1.0 - g_R)  # FIX: sin logistic_term aquí
        maintenance = self._calculate_maintenance_respiration(
            crop_type, biomass, temperature
        )
        return growth - maintenance

    def _calculate_evapotranspiration_reference(
        self, crop_type: CropType, temperature: float
    ) -> float:
        """
        Reference evapotranspiration using Hargreaves method.
        """
        delta_temp = max(crop_type.maximum_temp - crop_type.minimum_temp, 0.1)
        return 0.0023 * (temperature + 17.8) * math.sqrt(delta_temp)

    def _calculate_crop_coefficient_phase(
        self, crop_type: CropType, current_day: int
    ) -> float:
        """
        Crop coefficient based on phenological phase.
        """
        ro = current_day / crop_type.days_cycle
        if ro <= 0.15:
            return crop_type.phenological_initial_coefficient
        elif 0.15 < ro < 0.40:
            return crop_type.phenological_initial_coefficient + (
                (
                    crop_type.phenological_mid_coefficient
                    - crop_type.phenological_initial_coefficient
                )
                * ((ro - 0.15) / 0.25)
            )
        elif 0.40 <= ro <= 0.85:
            return crop_type.phenological_mid_coefficient
        else:
            return crop_type.phenological_mid_coefficient + (
                (
                    crop_type.phenological_end_coefficient
                    - crop_type.phenological_mid_coefficient
                )
                * ((ro - 0.85) / 0.15)
            )

    def _calculate_evapotranspiration(
        self,
        crop_type: CropType,
        crop_coefficient_phase: float,
        evapotranspiration_reference: float,
        f_W: float,
    ) -> float:
        """
        Actual evapotranspiration.
        """
        return crop_coefficient_phase * evapotranspiration_reference * f_W

    def _update_water_balance(
        self,
        crop: Crop,
        crop_type: CropType,
        rain: float,
        irrigation: float,
        evapotranspiration: float,
    ) -> tuple[float, float]:
        """
        Updates soil water balance and calculates drainage.
        Returns (new_water_stored, drainage).
        """
        water_temp = crop.water_stored + rain + irrigation - evapotranspiration
        drainage = max(0.0, water_temp - crop_type.water_capacity)
        new_water_stored = min(water_temp, crop_type.water_capacity)
        return new_water_stored, drainage

    def _check_mortality(
        self,
        crop: Crop,
        crop_type: CropType,
        f_T: float,
        f_W: float,
        f_L: float,
        temperature: float,
        water_stored: float,
    ) -> bool:
        """
        Checks if the plant should die due to extreme or prolonged stress.
        """
        f_total = f_T * f_W * f_L

        if f_total < 0.1:
            crop.consecutive_stress_days += 1
        else:
            crop.consecutive_stress_days = max(0, crop.consecutive_stress_days - 1)

        if crop.consecutive_stress_days >= crop_type.consecutive_stress_days_limit:
            return True
        if water_stored <= 0 and crop.consecutive_stress_days > 3:
            return True
        return False

    def simulate_day(
        self,
        crop_id: str,
        user_id: str,
        temperature: float,
        rain: float,
        sun_hours: float,
        irrigation: float = 0.0,
    ) -> Crop:
        """
        Simulates one day of growth for a crop.
        """
        self._validate_environmental_inputs(temperature, rain, sun_hours, irrigation)

        crop = self._get_and_validate_crop(crop_id, user_id)
        crop_type = self._get_crop_type(crop.crop_type_id)

        if not crop.active:
            raise InvalidInputError("The crop is already harvested or dead.")

        # FIX #2: Si water_stored es 0 (valor por defecto al crear el cultivo),
        # inicializarlo al centro del rango óptimo para evitar estrés hídrico
        # artificial en el primer día de simulación.
        if crop.water_stored == 0:
            crop.water_stored = (crop_type.water_opt_low + crop_type.water_opt_high) / 2

        # Environmental factors
        f_T = self._calculate_production_thermal_factor(crop_type, temperature)
        f_W = self._calculate_water_factor_production(crop_type, crop.water_stored)
        f_L = self._calculate_light_production_factor(crop_type, sun_hours)

        # Current biomass
        current_biomass = (
            crop.conditions[-1].estimated_biomass
            if crop.conditions
            else crop_type.initial_biomass
        )

        # Photosynthesis (logistic term se aplica aquí y solo aquí)
        logistic_term = self._calculate_logistic_growth_term(crop_type, current_biomass)
        photosynthesis = self._calculate_photosynthesis(
            crop_type, current_biomass, logistic_term, f_T, f_W, f_L
        )

        # Net growth
        net_growth = self._calculate_net_growth(
            crop_type, current_biomass, photosynthesis, temperature
        )
        new_biomass = max(0.0, current_biomass + net_growth)

        # Water balance
        et0 = self._calculate_evapotranspiration_reference(crop_type, temperature)
        kc = self._calculate_crop_coefficient_phase(crop_type, len(crop.conditions) + 1)
        et = self._calculate_evapotranspiration(crop_type, kc, et0, f_W)
        new_water_stored, drainage = self._update_water_balance(
            crop, crop_type, rain, irrigation, et
        )

        # Harvest
        if new_biomass >= 0.95 * crop_type.potential_performance:
            crop.active = False

        # Mortality
        if self._check_mortality(
            crop, crop_type, f_T, f_W, f_L, temperature, crop.water_stored
        ):
            crop.active = False
            self.storage.save_crop(crop)
            raise InvalidInputError("The plant has died due to extreme conditions.")

        # Save daily record
        new_condition = DailyCondition(
            day=len(crop.conditions) + 1,
            temperature=temperature,
            rain=rain,
            sun_hours=sun_hours,
            estimated_biomass=new_biomass,
        )

        crop.conditions.append(new_condition)
        crop.last_sim_date += timedelta(days=1)
        crop.water_stored = new_water_stored

        if len(crop.conditions) >= crop_type.days_cycle:
            crop.active = False

        self.storage.save_crop(crop)

        print(f"--- DÍA {len(crop.conditions) + 1} ---")
        print(f"  water_stored      : {crop.water_stored:.4f}")
        print(f"  current_biomass   : {current_biomass:.4f}")
        print(f"  f_T               : {f_T:.6f}")
        print(f"  f_W               : {f_W:.6f}")
        print(f"  f_L               : {f_L:.6f}")
        print(f"  logistic_term     : {logistic_term:.6f}")
        print(f"  photosynthesis    : {photosynthesis:.6f}")
        print(f"  net_growth        : {net_growth:.6f}")
        print(f"  new_biomass       : {new_biomass:.4f}")
        return crop

    def get_crop_by_id(self, crop_id: str, requesting_user_id: str) -> Crop:
        """
        Retrieves a crop by its ID with permission validation.
        """
        requesting_user = self.storage.get_user_by_id(requesting_user_id)
        crop = self.storage.get_crop_by_id(crop_id)
        if not requesting_user:
            raise UserNotFoundError(requesting_user_id)
        if not crop:
            raise CropNotFoundError(crop_id)
        if (
            requesting_user_id != crop.user_id
            and requesting_user.role.value != UserRole.ADMIN.value
        ):
            raise ResourceOwnershipError("No puedes acceder a este cultivo.")
        return crop

    def _validate_environmental_inputs(
        self, temperature: float, rain: float, sun_hours: float, irrigation: float = 0.0
    ):
        """
        Validates that environmental inputs are within acceptable ranges.
        """

        if not isinstance(temperature, (int, float)):
            raise InvalidInputError("La temperatura debe ser numérica.")
        if not isinstance(rain, (int, float)):
            raise InvalidInputError("La lluvia debe ser numérica.")
        if not isinstance(sun_hours, (int, float)):
            raise InvalidInputError("Las horas de sol deben ser numéricas.")
        if not isinstance(irrigation, (int, float)):
            raise InvalidInputError("El riego debe ser numérico.")

        if temperature < -10 or temperature >= 56.7:
            raise InvalidInputError(
                "La temperatura ingresada no es real (debe estar entre -10°C y 56.7°C)."
            )
        if rain < 0:
            raise InvalidInputError("Valor de lluvia inválido (no puede ser negativo).")
        if irrigation < 0:
            raise InvalidInputError("Valor de riego inválido (no puede ser negativo).")
        if sun_hours < 0 or sun_hours > 16:
            raise InvalidInputError("Las horas de sol deben estar entre 0 y 16.")

    def _get_and_validate_crop(self, crop_id: str, user_id: str) -> Crop:
        """
        Retrieves and validates that the crop exists, is active, and belongs to the user.
        """

        crop = self.storage.get_crop_by_id(crop_id)
        if not crop:
            raise CropNotFoundError(crop_id)

        if not crop.active:
            raise InvalidInputError("El cultivo ya está cosechado.")

        if crop.user_id != user_id:
            raise ResourceOwnershipError("No puedes simular este cultivo.")

        return crop

    def _get_crop_type(self, crop_type_id: str) -> CropType:
        """
        Retrieves and validates that the crop type exists.
        """

        crop_type = self.storage.get_crop_type_by_id(crop_type_id)
        if not crop_type:
            raise CropTypeNotFoundError(crop_type_id)
        return crop_type

    def create_crop(
        self, name: str, crop_type_id: str, user_id: str, start_date: datetime
    ) -> Crop:
        """
        Method created to allow a user to make new crops.
        """

        user = self.storage.get_user_by_id(user_id)
        crop_type = self.storage.get_crop_type_by_id(crop_type_id)
        # Method validations
        if not user:
            raise UserNotFoundError(user_id)
        if not crop_type:
            raise CropTypeNotFoundError(crop_type_id)
        if not name or not name.strip():
            raise InvalidInputError("El nombre no es válido. ")

        crop_unique_id = str(uuid.uuid4())

        # New object creation.
        new_crop = Crop(
            id=crop_unique_id,
            name=name,
            user_id=user_id,
            crop_type_id=crop_type_id,
            start_date=start_date,
            last_sim_date=start_date,
            conditions=[],
            active=True,
            water_stored=(crop_type.water_opt_low + crop_type.water_opt_high) / 2,
            consecutive_stress_days=0,
            current_phase="Fase Inicial",
        )
        self.storage.save_crop(new_crop)
        return new_crop

    def get_crops_by_user(self, user_id: str, requesting_user_id: str) -> list[Crop]:
        """
        Method created to get the crops created by an user.
        """
        requesting_user = self.storage.get_user_by_id(requesting_user_id)
        crops = self.storage.get_crops_by_user(user_id)
        owner = self.storage.get_user_by_id(user_id)
        if not owner:
            raise UserNotFoundError(user_id)
        if not requesting_user:
            raise UserNotFoundError(requesting_user_id)
        if (
            requesting_user_id != user_id
            and requesting_user.role.value != UserRole.ADMIN.value
        ):
            raise ResourceOwnershipError("No puedes acceder a estos cultivos.")
        return crops

    def get_crop_history(
        self, crop_id: str, requesting_user_id: str
    ) -> list[DailyCondition]:
        """
        Method created to see the history of conditions of a crop.
        """
        requesting_user = self.storage.get_user_by_id(requesting_user_id)
        crop = self.storage.get_crop_by_id(crop_id)
        if not requesting_user:
            raise UserNotFoundError(requesting_user_id)
        if not crop:
            raise CropNotFoundError(crop_id)
        if (
            requesting_user_id != crop.user_id
            and requesting_user.role.value != UserRole.ADMIN.value
        ):
            raise ResourceOwnershipError("No puedes acceder a estos cultivos.")
        return crop.conditions

    def update_crops(self, crop_id: str, requesting_user_id: str, **kwargs) -> Crop:
        """
        Method created to update name or state of a crop.
        """
        requesting_user = self.storage.get_user_by_id(requesting_user_id)
        crop = self.storage.get_crop_by_id(crop_id)
        if not requesting_user:
            raise UserNotFoundError(requesting_user_id)
        if not crop:
            raise CropNotFoundError(crop_id)
        if (
            requesting_user_id != crop.user_id
            and requesting_user.role.value != UserRole.ADMIN.value
        ):
            raise ResourceOwnershipError("No puedes acceder a estos cultivos.")

        # Are the arguments in the changes - allowed fields ?
        allowed_fields = ["name", "active"]
        for key, value in kwargs.items():
            if key not in allowed_fields:
                raise InvalidInputError(
                    "El atributo ingresado NO existe, o no puede ser cambiado."
                )

        for key, value in kwargs.items():
            setattr(crop, key, value)

        self.storage.save_crop(crop)
        return crop

    def delete_crop(self, crop_id: str, requesting_user_id: str) -> None:
        """
        Method created to delete a crop.
        """
        # Validations
        requesting_user = self.storage.get_user_by_id(requesting_user_id)
        crop = self.storage.get_crop_by_id(crop_id)
        if not requesting_user:
            raise UserNotFoundError(requesting_user_id)
        if not crop:
            raise CropNotFoundError(crop_id)
        owner = self.storage.get_user_by_id(crop.user_id)
        if not owner:
            raise UserNotFoundError(crop.user_id)
        if (
            requesting_user_id != crop.user_id
            and requesting_user.role.value != UserRole.ADMIN.value
        ):
            raise ResourceOwnershipError("No puedes acceder a estos cultivos.")

        # Eliminating crop ID from user crop ID's list
        if crop_id in owner.crop_ids:
            owner.crop_ids.remove(crop_id)
            self.storage.save_user(owner)

        self.storage.delete_crop(crop_id)

    def get_crop_statistics(self, crop_id: str, requesting_user_id: str) -> dict:
        """
        Generates statistics for a crop based on its growth history.
        """

        self._validate_user_exists(requesting_user_id)

        crop = self._get_and_validate_crop_access(crop_id, requesting_user_id)
        crop_type = self._get_crop_type(crop.crop_type_id)

        return self._calculate_statistics(crop, crop_type)

    def _validate_user_exists(self, user_id: str):
        """
        Validates that the requesting user exists.
        """

        user = self.storage.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)

    def _get_and_validate_crop_access(self, crop_id: str, user_id: str) -> Crop:
        """
        Retrieves crop and validates that the user has access to it.
        """
        crop = self.storage.get_crop_by_id(crop_id)
        if not crop:
            raise CropNotFoundError(crop_id)

        user = self.storage.get_user_by_id(user_id)
        if user_id != crop.user_id and user.role.value != UserRole.ADMIN.value:
            raise ResourceOwnershipError("No puedes acceder a este cultivo.")

        return crop

    def _calculate_statistics(self, crop: Crop, crop_type: CropType) -> dict:
        """
        Calculates all statistics for the crop.
        """

        if not crop.conditions:
            return self._empty_statistics()

        averages = self._calculate_averages(crop.conditions)
        growth_stats = self._calculate_growth_stats(crop.conditions, crop_type)
        stress_days = self._calculate_stress_days(crop.conditions, crop_type)
        performance = self._calculate_performance(crop.conditions, crop_type)

        return {
            "average_temperature": averages["temp"],
            "average_rain": averages["rain"],
            "average_sun_hours": averages["sun"],
            "total_growth": growth_stats["total"],
            "stress_days": stress_days,
            "performance_ratio": performance,
        }

    def _empty_statistics(self) -> dict:
        """
        Returns empty statistics for crops with no conditions.
        """

        return {
            "average_temperature": 0,
            "average_rain": 0,
            "average_sun_hours": 0,
            "total_growth": 0,
            "stress_days": 0,
            "performance_ratio": 0,
        }

    def _calculate_averages(self, conditions: list) -> dict:
        """Calculates average temperature, rain, and sun hours."""
        return {
            "temp": sum(c.temperature for c in conditions) / len(conditions),
            "rain": sum(c.rain for c in conditions) / len(conditions),
            "sun": sum(c.sun_hours for c in conditions) / len(conditions),
        }

    def _calculate_growth_stats(self, conditions: list, crop_type: CropType) -> dict:
        """Calculates total growth from initial to final biomass."""
        initial = crop_type.initial_biomass
        final = conditions[-1].estimated_biomass
        return {"total": final - initial}

    def _calculate_stress_days(self, conditions: list, crop_type: CropType) -> int:
        """Counts days where temperature was outside optimal range."""
        return sum(1 for f in conditions if f < 0.1)

    def _calculate_performance(self, conditions: list, crop_type: CropType) -> float:
        """Calculates performance ratio (final / potential)."""
        final = conditions[-1].estimated_biomass
        return final / crop_type.potential_performance


class UserService:
    """
    UserService class created as a logic layer in CultivaLab;
    it's the brain of business service in the app, and connects
    the actions in the ICL and the Storage.
    """

    def __init__(self, storage: Database) -> None:
        self.storage: Database = storage

    def register_user(self, username: str, password: str) -> User:
        """
        Method created to implement the logic needed to
        register a new user.
        """
        if (not username) or (not username.strip()):
            raise InvalidInputError("El nombre de usuario no puede estar vacío.")
        if (not password) or (not password.strip()):
            raise InvalidInputError("La contraseña no puede estar vacía.")
        if len(password) < 8:
            raise InvalidInputError("La contraseña es demasiado corta.")

        searched_user = self.storage.get_user_by_username(username)
        if searched_user:
            raise UserAlreadyExistsError(searched_user.id)

        user_unique_id = str(uuid.uuid4())
        # Password Hash
        hashed_pwd = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode(
            "utf-8"
        )

        # New user creation
        new_user = User(user_unique_id, username, hashed_pwd, UserRole.USER, [])

        self.storage.save_user(new_user)
        return new_user

    def register_admin(self, admin_key: str, username: str, password: str) -> User:
        """
        Registers the unique administrator of the system.
        Only one admin can exist, and a master key is required.
        """
        self._validate_admin_key(admin_key)
        self._validate_username_and_password(username, password)
        self._ensure_no_admin_exists()
        self._ensure_username_unique(username)

        new_admin = self._create_admin_user(username, password)
        self.storage.save_user(new_admin)
        return new_admin

    def _validate_admin_key(self, admin_key: str):
        """
        Validates that the admin key is not empty and matches the master key.
        """

        if (not admin_key) or (not admin_key.strip()):
            raise InvalidInputError("La llave de administrador no puede estar vacía.")

        from src.cultiva_lab.services import MASTER_KEY

        if admin_key != MASTER_KEY:
            raise InvalidInputError("La llave de administrador no es correcta.")

    def _validate_username_and_password(self, username: str, password: str):
        """
        Validates that username and password meet basic requirements.
        """

        if (not username) or (not username.strip()):
            raise InvalidInputError("El nombre de usuario no puede estar vacío.")

        if (not password) or (not password.strip()):
            raise InvalidInputError("La contraseña no puede estar vacía.")

        if len(password) < 8:
            raise InvalidInputError(
                "La contraseña es demasiado corta (mínimo 8 caracteres)."
            )

    def _ensure_no_admin_exists(self):
        """
        Checks that no admin user already exists in the system.
        """

        users = self.storage.get_users()
        for user in users:
            if user.role.value == UserRole.ADMIN.value:
                raise AdminAlreadyExistsError()

    def _ensure_username_unique(self, username: str):
        """
        Ensures that the username is not already taken.
        """

        if self.storage.get_user_by_username(username):
            raise UserAlreadyExistsError(username)

    def _create_admin_user(self, username: str, password: str) -> User:
        """
        Creates a new admin user with hashed password.
        """

        user_id = str(uuid.uuid4())
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode(
            "utf-8"
        )

        return User(user_id, username, hashed, UserRole.ADMIN, [])

    def login(self, username: str, password: str) -> User:
        """
        Method created to implement the logic of the log - in in app.
        """
        if (not username) or (not username.strip()):
            raise InvalidInputError("El nombre de usuario no puede estar vacío.")
        if (not password) or (not password.strip()):
            raise InvalidInputError("La contraseña no puede estar vacía.")
        user = self.storage.get_user_by_username(username)
        if not user:
            raise UserNotFoundError(username)

        entered_password = password.encode("utf-8")
        stored_hash = user.password_hash.encode("utf-8")
        # Checkpw compares two of the passwords
        if not bcrypt.checkpw(entered_password, stored_hash):
            raise AuthorizationError("La contraseña o el usuario es incorrecto.")

        return user

    def get_user_by_id(self, user_id: str, requesting_user_id: str) -> User | None:
        """
        Method created to get the user information by its ID;
        it can be used by the admin or the user.
        """
        if (not user_id) or (not user_id.strip()):
            raise InvalidInputError("El ID del usuario no puede estar vacío.")
        if (not requesting_user_id) or (not requesting_user_id.strip()):
            raise InvalidInputError("El ID no puede estar vacío.")
        requesting_user = self.storage.get_user_by_id(requesting_user_id)
        user = self.storage.get_user_by_id(user_id)

        if not requesting_user:
            raise UserNotFoundError(requesting_user_id)
        if not user:
            raise UserNotFoundError(user_id)
        if (
            requesting_user_id != user.id
        ) and requesting_user.role.value != UserRole.ADMIN.value:
            raise ResourceOwnershipError("No puedes acceder a esta información.")

        return user

    def get_user_by_username(self, username: str, requesting_user_id: str):
        """
        Method created to get the user information by its username;
        it can be used by the admin or the user.
        """
        if (not username) or (not username.strip()):
            raise InvalidInputError("El Username del usuario no puede estar vacío.")
        if (not requesting_user_id) or (not requesting_user_id.strip()):
            raise InvalidInputError("El ID no puede estar vacío.")
        requesting_user = self.storage.get_user_by_id(requesting_user_id)
        user = self.storage.get_user_by_username(username)

        if not requesting_user:
            raise UserNotFoundError(requesting_user_id)
        if not user:
            raise UserNotFoundError(username)
        if (
            requesting_user_id != user.id
        ) and requesting_user.role.value != UserRole.ADMIN.value:
            raise ResourceOwnershipError("No puedes acceder a esta información.")

        return user

    def get_all_users(self, requesting_user_id: str) -> list[User]:
        """
        Method created to get all the users registered in app;
        it can be used by the admin only.
        """
        if not (requesting_user_id) or not (requesting_user_id.strip()):
            raise InvalidInputError("El ID no puede estar vacío.")
        requesting_user = self.storage.get_user_by_id(requesting_user_id)
        if not requesting_user:
            raise UserNotFoundError(requesting_user_id)
        if requesting_user.role.value != UserRole.ADMIN.value:
            raise ResourceOwnershipError("No puedes acceder a esta información.")

        return self.storage.get_users()

    def update_password(
        self, user_id: str, old_password: str, new_password: str
    ) -> None:
        """
        Method created for the users (or admin) to change their passwords.
        """
        if not (user_id) or not (user_id.strip()):
            raise InvalidInputError("El ID del usuario no puede estar vacío.")
        if not old_password:
            raise InvalidInputError(
                "El campo de la contraseña vieja no puede estar vacío."
            )
        if not new_password:
            raise InvalidInputError(
                "El campo de la contraseña nueva no puede estar vacío."
            )
        if len(new_password) < 8:
            raise InvalidInputError("La nueva contraseña es demasiado corta.")

        user = self.storage.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)

        first_entered_password = old_password.encode("utf-8")
        stored_hash = user.password_hash.encode("utf-8")

        if not bcrypt.checkpw(first_entered_password, stored_hash):
            raise AuthorizationError("La contraseña es incorrecta.")
        new_hashed_password = bcrypt.hashpw(
            new_password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")
        if not (user.password_hash == new_hashed_password):
            user.password_hash = new_hashed_password

        self.storage.save_user(user)

    def update_username(
        self, user_id: str, new_username: str, requesting_user_id: str
    ) -> None:
        """
        Updates the username of a user.
        Only the user themselves can perform this action.
        """

        self._validate_inputs(user_id, new_username, requesting_user_id)

        user = self._get_user(user_id)
        self._validate_requesting_user(requesting_user_id)
        self._validate_ownership(user_id, requesting_user_id)

        self._validate_username_not_taken(new_username, user.username)

        user.username = new_username
        self.storage.save_user(user)

    def _validate_inputs(
        self, user_id: str, new_username: str, requesting_user_id: str
    ):
        """
        Validates that all inputs are non-empty.
        """

        if (not user_id) or (not user_id.strip()):
            raise InvalidInputError("El ID del usuario no puede estar vacío.")

        if (not new_username) or (not new_username.strip()):
            raise InvalidInputError("El username nuevo no puede estar vacío.")

        if (not requesting_user_id) or (not requesting_user_id.strip()):
            raise InvalidInputError("El ID del solicitante no puede estar vacío.")

    def _get_user(self, user_id: str) -> User:
        """
        Retrieves and validates that the user exists.
        """

        user = self.storage.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)
        return user

    def _validate_requesting_user(self, requesting_user_id: str):
        """
        Validates that the requesting user exists.
        """

        requesting_user = self.storage.get_user_by_id(requesting_user_id)
        if not requesting_user:
            raise UserNotFoundError(requesting_user_id)
        return requesting_user

    def _validate_ownership(self, user_id: str, requesting_user_id: str):
        """
        Validates that the requesting user is the same as the target user.
        """

        if user_id != requesting_user_id:
            raise ResourceOwnershipError(
                "No puedes modificar el username de otro usuario."
            )

    def _validate_username_not_taken(self, new_username: str, current_username: str):
        """
        Validates that the new username is not already taken by another user.
        """

        if new_username == current_username:
            raise InvalidInputError("El nuevo username debe ser diferente al actual.")

        existing_user = self.storage.get_user_by_username(new_username)
        if existing_user:
            raise UserAlreadyExistsError(
                f"El username '{new_username}' ya está en uso."
            )

    def delete_user(self, user_id: str, requesting_user_id: str) -> None:
        """
        Method created for the users to delete their "accounts".
        It can only be used by users.
        """
        if (not user_id) or (not user_id.strip()):
            raise InvalidInputError("El ID del usuario no puede estar vacío.")
        if (not requesting_user_id) or (not requesting_user_id.strip()):
            raise InvalidInputError("El ID no puede estar vacío.")

        user = self.storage.get_user_by_id(user_id)
        requesting_user = self.storage.get_user_by_id(requesting_user_id)
        if not user:
            raise UserNotFoundError(user_id)
        if not requesting_user:
            raise UserNotFoundError(requesting_user_id)
        if (user_id != requesting_user_id) and (
            requesting_user.role.value != UserRole.ADMIN.value
        ):
            raise ResourceOwnershipError("No puedes acceder a esta información.")
        self.storage.delete_user(user.id)

    def get_user_crops(self, user_id: str, requesting_user_id: str) -> list[Crop]:
        """
        Method created for the users to get all their crops.
        It can be used by users and admin.
        """
        if (not user_id) or (not user_id.strip()):
            raise InvalidInputError("El ID del usuario no puede estar vacío.")
        if (not requesting_user_id) or (not requesting_user_id.strip()):
            raise InvalidInputError("El ID no puede estar vacío.")

        user = self.storage.get_user_by_id(user_id)
        requesting_user = self.storage.get_user_by_id(requesting_user_id)
        if not user:
            raise UserNotFoundError(user_id)
        if not requesting_user:
            raise UserNotFoundError(requesting_user_id)
        if (user_id != requesting_user_id) and (
            requesting_user.role.value != UserRole.ADMIN.value
        ):
            raise ResourceOwnershipError("No puedes acceder a esta información.")

        return self.storage.get_crops_by_user(user_id)


class CropTypeService:
    """
    CropTypeService class created to implement the logic
    of crop types in CultivaLab; needed for creation and elections
    of crop types.
    """

    def __init__(self, storage: Database, user_service: UserService):
        self.storage: Database = storage
        self.user_service: UserService = user_service

    def _validate_admin(self, admin_id: str):
        """
        Validates that the user exists and is an admin.
        """

        if (not admin_id) or (not admin_id.strip()):
            raise InvalidInputError("El ID no puede estar vacío.")

        admin_user = self.storage.get_user_by_id(admin_id)
        if not admin_user:
            raise UserNotFoundError(admin_id)

        if admin_user.role.value != UserRole.ADMIN.value:
            raise ResourceOwnershipError("No puedes acceder a esta información.")

    def _validate_input_types(
        self,
        needed_water: float,
        needed_light: int,
        days_cycle: float,
        initial_biomass: float,
        potential_performance: float,
    ):
        """
        Validates that all parameters have the correct types.
        """

        validations = [
            (needed_water, (int, float), "La lluvia debe ser numérica."),
            (needed_light, (int, float), "Las horas de sol deben ser numéricas."),
            (days_cycle, int, "Los días de ciclo deben ser numéricos y enteros."),
            (initial_biomass, (int, float), "La biomasa inicial debe ser numérica."),
            (
                potential_performance,
                (int, float),
                "El potencial de desempeño debe ser numérico.",
            ),
        ]

        for value, expected_type, error_msg in validations:
            if not isinstance(value, expected_type):
                raise InvalidInputError(error_msg)

    def _validate_input_ranges(
        self,
        needed_water,
        needed_light,
        days_cycle,
        initial_biomass,
        potential_performance,
    ):
        """
        Validates that all values are within acceptable ranges.
        """

        positive_params = [
            (needed_water, "Agua necesaria"),
            (needed_light, "Luz necesaria"),
            (days_cycle, "Días de ciclo"),
            (initial_biomass, "Biomasa inicial"),
            (potential_performance, "Rendimiento potencial"),
        ]

        for value, param_name in positive_params:
            if value <= 0:
                raise InvalidInputError(f"{param_name} debe ser mayor a cero.")

    def _validate_and_format_name(self, name: str) -> str:
        """
        Validates and formats the crop type name.
        """

        if (not name) or not (name.strip()):
            raise InvalidInputError("El nombre no puede estar vacío.")
        return name.strip()

    def _validate_unique_name(self, name: str):
        """
        Validates that no crop type with the same name exists.
        """

        existing_type = self.storage.get_crop_type_by_name(name)
        if existing_type:
            raise DuplicateDataError("El tipo de cultivo ya existe.")

    def _create_crop_type_instance(
        self,
        name: str,
        optimal_temp: float,
        minimum_temp: float,
        maximum_temp: float,
        cold_sensibility: float,
        heat_sensibility: float,
        cold_factor: float,
        heat_factor: float,
        temperature_curve_length: float,
        water_wilting: float,
        water_opt_low: float,
        needed_water: float,
        water_opt_high: float,
        water_capacity: float,
        water_sensibility: float,
        water_stress_constant: float,
        needed_light: float,
        needed_light_max: float,
        light_sensibility: float,
        light_km: float,
        light_sigma: float,
        phenological_initial_coefficient: float,
        phenological_mid_coefficient: float,
        phenological_end_coefficient: float,
        days_cycle: int,
        photosyntesis_max_rate: float,
        breathing_base_rate: float,
        theta: float,
        consecutive_stress_days_limit: int,
        theta_coefficient: float,
        initial_biomass: float,
        potential_performance: float,
    ) -> CropType:
        """Creates a new CropType instance."""

        return CropType(
            id=str(uuid.uuid4()),
            name=name,
            optimal_temp=optimal_temp,
            minimum_temp=minimum_temp,
            maximum_temp=maximum_temp,
            cold_sensibility=cold_sensibility,
            heat_sensibility=heat_sensibility,
            cold_factor=cold_factor,
            heat_factor=heat_factor,
            temperature_curve_length=temperature_curve_length,
            water_wilting=water_wilting,
            water_opt_low=water_opt_low,
            needed_water=needed_water,
            water_opt_high=water_opt_high,
            water_capacity=water_capacity,
            water_sensibility=water_sensibility,
            water_stress_constant=water_stress_constant,
            needed_light=needed_light,
            needed_light_max=needed_light_max,
            light_sensibility=light_sensibility,
            light_km=light_km,
            light_sigma=light_sigma,
            phenological_initial_coefficient=phenological_initial_coefficient,
            phenological_mid_coefficient=phenological_mid_coefficient,
            phenological_end_coefficient=phenological_end_coefficient,
            days_cycle=days_cycle,
            photosyntesis_max_rate=photosyntesis_max_rate,
            breathing_base_rate=breathing_base_rate,
            theta=theta,
            consecutive_stress_days_limit=consecutive_stress_days_limit,
            theta_coefficient=theta_coefficient,
            initial_biomass=initial_biomass,
            potential_performance=potential_performance,
        )

    def create_crop_type(
        self,
        admin_id: str,
        name: str,
        optimal_temp: float,
        minimum_temp: float,
        maximum_temp: float,
        cold_sensibility: float,
        heat_sensibility: float,
        cold_factor: float,
        heat_factor: float,
        temperature_curve_length: float,
        water_wilting: float,
        water_opt_low: float,
        needed_water: float,
        water_opt_high: float,
        water_capacity: float,
        water_sensibility: float,
        water_stress_constant: float,
        needed_light: float,
        needed_light_max: float,
        light_sensibility: float,
        light_km: float,
        light_sigma: float,
        phenological_initial_coefficient: float,
        phenological_mid_coefficient: float,
        phenological_end_coefficient: float,
        days_cycle: int,
        photosyntesis_max_rate: float,
        breathing_base_rate: float,
        theta: float,
        consecutive_stress_days_limit: int,
        theta_coefficient: float,
        initial_biomass: float,
        potential_performance: float,
    ) -> CropType:
        """Method implemented for the admin to create new crop types."""

        self._validate_admin(admin_id)
        self._validate_input_types(
            needed_water,
            needed_light,
            days_cycle,
            initial_biomass,
            potential_performance,
        )
        self._validate_input_ranges(
            needed_water,
            needed_light,
            days_cycle,
            initial_biomass,
            potential_performance,
        )

        name = self._validate_and_format_name(name)
        self._validate_unique_name(name)

        new_crop_type = self._create_crop_type_instance(
            name=name,
            optimal_temp=optimal_temp,
            minimum_temp=minimum_temp,
            maximum_temp=maximum_temp,
            cold_sensibility=cold_sensibility,
            heat_sensibility=heat_sensibility,
            cold_factor=cold_factor,
            heat_factor=heat_factor,
            temperature_curve_length=temperature_curve_length,
            water_wilting=water_wilting,
            water_opt_low=water_opt_low,
            needed_water=needed_water,
            water_opt_high=water_opt_high,
            water_capacity=water_capacity,
            water_sensibility=water_sensibility,
            water_stress_constant=water_stress_constant,
            needed_light=needed_light,
            needed_light_max=needed_light_max,
            light_sensibility=light_sensibility,
            light_km=light_km,
            light_sigma=light_sigma,
            phenological_initial_coefficient=phenological_initial_coefficient,
            phenological_mid_coefficient=phenological_mid_coefficient,
            phenological_end_coefficient=phenological_end_coefficient,
            days_cycle=days_cycle,
            photosyntesis_max_rate=photosyntesis_max_rate,
            breathing_base_rate=breathing_base_rate,
            theta=theta,
            consecutive_stress_days_limit=consecutive_stress_days_limit,
            theta_coefficient=theta_coefficient,
            initial_biomass=initial_biomass,
            potential_performance=potential_performance,
        )

        self.storage.save_crop_type(new_crop_type)
        return new_crop_type

    def get_crop_type_by_id(self, crop_type_id: str) -> CropType:
        """
        Method created to get a crop type based on its ID.
        """
        if (not crop_type_id) or (not crop_type_id.strip()):
            raise InvalidInputError("El valor de entrada no puede estar vacío.")

        searched_crop_type = self.storage.get_crop_type_by_id(crop_type_id)
        if not searched_crop_type:
            raise CropTypeNotFoundError(crop_type_id)

        return searched_crop_type

    def get_crop_type_by_name(self, crop_type_name: str) -> CropType:
        """
        Method created to get a crop type based on its name.
        """
        if (not crop_type_name) or (not crop_type_name.strip()):
            raise InvalidInputError("El valor de entrada no puede estar vacío.")
        crop_type_name = crop_type_name.strip().capitalize()
        searched_crop_type = self.storage.get_crop_type_by_name(crop_type_name)
        if not searched_crop_type:
            raise CropTypeNotFoundError(crop_type_name)

        return searched_crop_type

    def get_crop_types(self) -> list[CropType]:
        """
        Method created to get a list of every crop type created
        by admin.
        """
        return self.storage.get_crop_types()

    def update_crop_type(self, admin_id: str, crop_type_id: str, **kwargs) -> CropType:
        """
        Updates information of an existing crop type.
        Every attribute is allowed for changes except the ID.
        """
        self._validate_admin_access(admin_id)

        crop_type = self._get_crop_type_for_update(crop_type_id)
        self._validate_no_active_crops(crop_type_id)

        validated_kwargs = self._validate_and_filter_update_fields(kwargs)
        self._apply_updates(crop_type, validated_kwargs)

        self.storage.save_crop_type(crop_type)
        return crop_type

    def _validate_admin_access(self, admin_id: str):
        """Validates that the user exists and is an admin."""
        if (not admin_id) or (not admin_id.strip()):
            raise InvalidInputError("El ID de administrador no puede estar vacío.")

        admin_user = self.storage.get_user_by_id(admin_id)
        if not admin_user:
            raise UserNotFoundError(admin_id)

        if admin_user.role.value != UserRole.ADMIN.value:
            raise ResourceOwnershipError(
                "No tienes permisos para realizar esta acción."
            )

    def _get_crop_type_for_update(self, crop_type_id: str) -> CropType:
        """Retrieves and validates that the crop type exists."""
        if (not crop_type_id) or (not crop_type_id.strip()):
            raise InvalidInputError("El ID del tipo de cultivo no puede estar vacío.")

        crop_type = self.storage.get_crop_type_by_id(crop_type_id)
        if not crop_type:
            raise CropTypeNotFoundError(crop_type_id)

        return crop_type

    def _validate_no_active_crops(self, crop_type_id: str):
        """Validates that no active crops are using this crop type."""

        crops_using = self.storage.get_crops_by_type(crop_type_id)
        if len(crops_using) > 0:
            raise BusinessRuleViolationError(
                "No se puede editar este tipo porque hay cultivos que lo utilizan."
            )

    def _validate_name_field(self, key: str, value: any) -> str:
        """Validates that the name field is not empty."""
        if not isinstance(value, str) or not value.strip():
            raise InvalidInputError("El nombre no puede estar vacío.")
        return value.strip()

    def _validate_positive_number_field(self, key: str, value: any) -> float:
        """Validates that a numeric field is positive."""
        try:
            num_value = float(value)
        except TypeError, ValueError:
            raise InvalidInputError(f"El valor para '{key}' debe ser numérico.")

        if num_value <= 0:
            raise InvalidInputError(f"El valor para '{key}' debe ser mayor a cero.")
        return num_value

    def _validate_positive_integer_field(self, key: str, value: any) -> int:
        """Validates that an integer field is positive."""
        try:
            int_value = int(value)
        except TypeError, ValueError:
            raise InvalidInputError(f"El valor para '{key}' debe ser un número entero.")

        if int_value <= 0:
            raise InvalidInputError(f"El valor para '{key}' debe ser mayor a cero.")
        return int_value

    def _apply_updates(self, crop_type: CropType, updates: dict):
        """Applies the validated updates to the crop type with consistency checks."""
        # First, apply all updates
        for key, value in updates.items():
            setattr(crop_type, key, value)

        # Then, validate cross-field consistency
        # Temperature consistency
        if (
            hasattr(crop_type, "minimum_temp")
            and hasattr(crop_type, "maximum_temp")
            and hasattr(crop_type, "optimal_temp")
        ):
            if not (
                crop_type.minimum_temp < crop_type.optimal_temp < crop_type.maximum_temp
            ):
                raise InvalidInputError(
                    "Las temperaturas deben estár en un buen orden."
                )

        # Water levels consistency (if all are present)
        water_attrs = [
            "water_wilting",
            "water_opt_low",
            "needed_water",
            "water_opt_high",
            "water_capacity",
        ]
        if all(hasattr(crop_type, attr) for attr in water_attrs):
            if not (
                crop_type.water_wilting
                < crop_type.water_opt_low
                < crop_type.water_opt_high
                < crop_type.water_capacity
            ):
                raise InvalidInputError(
                    "Los niveles de agua deben cumplir: water_wilting < water_opt_low < water_opt_high < water_capacity"
                )

        # Light consistency
        if hasattr(crop_type, "needed_light") and hasattr(
            crop_type, "needed_light_max"
        ):
            if crop_type.needed_light >= crop_type.needed_light_max:
                raise InvalidInputError(
                    "La luz necesaria debe ser menor que la luz máxima."
                )

        # Phenological coefficients consistency
        if (
            hasattr(crop_type, "phenological_initial_coefficient")
            and hasattr(crop_type, "phenological_mid_coefficient")
            and hasattr(crop_type, "phenological_end_coefficient")
        ):
            if not (
                crop_type.phenological_initial_coefficient
                <= crop_type.phenological_mid_coefficient
                >= crop_type.phenological_end_coefficient
            ):
                raise InvalidInputError(
                    "Los coeficientes fenológicos deben cumplir: initial ≤ mid ≥ end"
                )

    def delete_crop_type(self, admin_id: str, crop_type_to_eliminate_id: str) -> None:
        """
        Deletes a crop type only if there are no active crops using it.
        """
        self._validate_admin_access(admin_id)

        crop_type = self._get_crop_type(crop_type_to_eliminate_id)
        self._validate_no_active_crops_using(crop_type)

        self.storage.delete_crop_type(crop_type_to_eliminate_id)

    def _get_crop_type(self, crop_type_id: str) -> CropType:
        """Retrieves and validates that the crop type exists."""
        if (not crop_type_id) or (not crop_type_id.strip()):
            raise InvalidInputError("El ID del tipo de cultivo no puede estar vacío.")

        crop_type = self.storage.get_crop_type_by_id(crop_type_id)
        if not crop_type:
            raise CropTypeNotFoundError(crop_type_id)

        return crop_type

    def _validate_no_active_crops_using(self, crop_type: CropType):
        """Validates that no active crops are using this crop type."""
        crops = self.storage.get_crops()

        for crop in crops:
            if crop.crop_type_id == crop_type.id and crop.active:
                raise BusinessRuleViolationError(
                    "Este tipo de cultivo está en uso por cultivos activos; no puede ser eliminado."
                )

    def get_crop_types_with_stats(self, admin_id: str) -> list[dict]:
        """
        Get the stats of active crops of every crop type, and the
        average performance of every crop type.
        """
        if (not admin_id) or (not admin_id.strip()):
            raise InvalidInputError("El valor no puede estar vacío.")
        admin_user = self.storage.get_user_by_id(admin_id)
        if not admin_user:
            raise UserNotFoundError(admin_id)
        if admin_user.role.value != UserRole.ADMIN.value:
            raise ResourceOwnershipError(
                "No estas autorizado para acceder a esta información."
            )

        crop_types = self.storage.get_crop_types()
        crops = self.storage.get_crops()
        result = []

        for crop_type in crop_types:
            related_crops = [
                crop for crop in crops if crop.crop_type_id == crop_type.id
            ]
            active_crops = [c for c in related_crops if c.active]
            active_count = len(active_crops)

            result.append(
                {
                    "crop_type_id": crop_type.id,
                    "name": crop_type.name,
                    "active_crops": active_count,
                }
            )

        return result

    def _validate_temperature_field(self, key: str, value: any) -> float:
        """Validates that a temperature field is within acceptable range."""

        try:
            num_value = float(value)
        except TypeError, ValueError:
            raise InvalidInputError(f"El valor para '{key}' debe ser numérico.")
        if num_value < -7:
            raise InvalidInputError(f"El valor para '{key}' no puede ser menor a -7°C.")
        return num_value

    def _validate_and_filter_update_fields(self, kwargs: dict) -> dict:
        """Validates and filters the fields to update."""
        allowed_fields = {
            "name": self._validate_name_field,
            "optimal_temp": self._validate_temperature_field,
            "minimum_temp": self._validate_temperature_field,
            "maximum_temp": self._validate_temperature_field,
            "cold_sensibility": self._validate_positive_number_field,
            "heat_sensibility": self._validate_positive_number_field,
            "cold_factor": self._validate_positive_number_field,
            "heat_factor": self._validate_positive_number_field,
            "temperature_curve_length": self._validate_positive_number_field,
            "water_wilting": self._validate_positive_number_field,
            "water_opt_low": self._validate_positive_number_field,
            "needed_water": self._validate_positive_number_field,
            "water_opt_high": self._validate_positive_number_field,
            "water_capacity": self._validate_positive_number_field,
            "water_sensibility": self._validate_positive_number_field,
            "water_stress_constant": self._validate_positive_number_field,
            "needed_light": self._validate_positive_number_field,
            "needed_light_max": self._validate_positive_number_field,
            "light_sensibility": self._validate_positive_number_field,
            "light_km": self._validate_positive_number_field,
            "light_sigma": self._validate_positive_number_field,
            "phenological_initial_coefficient": self._validate_positive_number_field,
            "phenological_mid_coefficient": self._validate_positive_number_field,
            "phenological_end_coefficient": self._validate_positive_number_field,
            "days_cycle": self._validate_positive_integer_field,
            "photosyntesis_max_rate": self._validate_positive_number_field,
            "breathing_base_rate": self._validate_positive_number_field,
            "theta": self._validate_positive_number_field,
            "consecutive_stress_days_limit": self._validate_positive_integer_field,
            "theta_coefficient": self._validate_positive_number_field,
            "initial_biomass": self._validate_positive_number_field,
            "potential_performance": self._validate_positive_number_field,
        }

        validated = {}
        for key, value in kwargs.items():
            if key not in allowed_fields:
                raise InvalidInputError(
                    f"El atributo '{key}' no existe o no puede ser modificado."
                )
            validator = allowed_fields[key]
            validated[key] = validator(key, value)

        return validated


"""
AuthService and a Session Manager left for a second
report; classes will be used for control of logins
in a future web app.
"""
