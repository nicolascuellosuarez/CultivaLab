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

MASTER_KEY = "admin12345"


class CropService:
    """
    Class CropService created to include the service logic
    of crops, the pilot model to simulate their growth, and
    logic restrictions based in the exceptions made.
    """

    def __init__(self, storage: Database) -> None:
        self.storage: Database = storage

    def _calculate_environment_factor(
        self, crop_type: CropType, temperature: float, rain: float, sun_hours: float
    ) -> float:
        """
        Three factors will be used to simulate the growth.
        They will act as a pilot of the math model. The first
        factor: enviromental factor; Crop Type, temperature,
        rain and sun hours received by the crop.
        """

        # Three factors, using the parameters
        temperature_factor = max(
            0,
            1
            - (abs(temperature - crop_type.optimal_temp) / crop_type.optimal_temp)
            * 0.5,
        )
        rain_factor = (
            min(1, rain / crop_type.needed_water) if crop_type.needed_water > 0 else 1
        )
        sun_hours_factor = (
            min(1, sun_hours / crop_type.needed_light)
            if crop_type.needed_light > 0
            else 1
        )

        return temperature_factor * rain_factor * sun_hours_factor

    def _calculate_phase_factor(self, crop: Crop, crop_type: CropType) -> float:
        """
        Second part of model, the phase is also an important factor
        in the growth process of a crop. Depending on the phase,
        the crop can increase its biomass to a greater or lesser
        extent.
        """

        current_day = len(crop.conditions) + 1
        phase = current_day / crop_type.days_cycle

        if phase < 0.2:
            return 0.5 + (phase * 2.5)
        elif phase < 0.7:
            return 1.0
        return max(0.2, 1.5 - phase)

    def _calculate_capacity_factor(self, crop: Crop, crop_type: CropType) -> float:
        """
        Method created to calculate the growing capacity of
        a crop, based on its potential performance and current biomass.
        """

        current_biomass = (
            crop.conditions[-1].estimated_biomass
            if crop.conditions
            else crop_type.initial_biomass
        )
        return max(
            0,
            (crop_type.potential_performance - current_biomass)
            / crop_type.potential_performance,
        )

    def _calculate_growth(
        self,
        crop_type: CropType,
        env_factor: float,
        phase_factor: float,
        capacity_factor: float,
    ) -> float:
        """
        Method used to calculate the total factor, and calculates
        the growth of the crop in a day.
        """

        base_rate = 0.05  # Hardcoded Base rate, remember - this is a pilot model
        total_factor = (env_factor * phase_factor * capacity_factor) ** 1.5
        return crop_type.potential_performance * base_rate * total_factor

    def simulate_day(
        self,
        crop_id: str,
        user_id: str,
        temperature: float,
        rain: float,
        sun_hours: float,
    ) -> Crop:
        """
        Simulates one day of growth for a crop based on environmental conditions.
        """

        self._validate_environmental_inputs(temperature, rain, sun_hours)

        crop = self._get_and_validate_crop(crop_id, user_id)
        crop_type = self._get_crop_type(crop.crop_type_id)

        growth = self._calculate_daily_growth(
            crop, crop_type, temperature, rain, sun_hours
        )
        new_biomass = self._calculate_new_biomass(crop, crop_type, growth)

        updated_crop = self._update_crop_with_new_condition(
            crop, crop_type, temperature, rain, sun_hours, new_biomass
        )

        self.storage.save_crop(updated_crop)
        return updated_crop

    def _validate_environmental_inputs(
        self, temperature: float, rain: float, sun_hours: float
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

        if temperature < -10 or temperature >= 56.7:
            raise InvalidInputError(
                "La temperatura ingresada no es real (debe estar entre -10°C y 56.7°C)."
            )
        if rain < 0:
            raise InvalidInputError("Valor de lluvia inválido (no puede ser negativo).")
        if sun_hours < 0 or sun_hours > 12:
            raise InvalidInputError("Las horas de sol deben estar entre 0 y 12.")

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

    def _calculate_daily_growth(
        self,
        crop: Crop,
        crop_type: CropType,
        temperature: float,
        rain: float,
        sun_hours: float,
    ) -> float:
        """
        Calculates the growth for the current day based on environmental factors.
        """

        if len(crop.conditions) >= crop_type.days_cycle:
            raise InvalidInputError("El ciclo del cultivo ya terminó")

        env_factor = self._calculate_environment_factor(
            crop_type, temperature, rain, sun_hours
        )
        phase_factor = self._calculate_phase_factor(crop, crop_type)
        capacity_factor = self._calculate_capacity_factor(crop, crop_type)

        return self._calculate_growth(
            crop_type, env_factor, phase_factor, capacity_factor
        )

    def _calculate_new_biomass(
        self, crop: Crop, crop_type: CropType, growth: float
    ) -> float:
        """
        Calculates the new biomass after growth, without exceeding potential.
        """

        current_biomass = (
            crop.conditions[-1].estimated_biomass
            if crop.conditions
            else crop_type.initial_biomass
        )
        return min(current_biomass + growth, crop_type.potential_performance)

    def _update_crop_with_new_condition(
        self,
        crop: Crop,
        crop_type: CropType,
        temperature: float,
        rain: float,
        sun_hours: float,
        new_biomass: float,
    ) -> Crop:
        """
        Creates a new daily condition and updates the crop.
        """

        new_condition = DailyCondition(
            day=len(crop.conditions) + 1,
            temperature=temperature,
            rain=rain,
            sun_hours=sun_hours,
            estimated_biomass=new_biomass,
        )

        crop.conditions.append(new_condition)
        crop.last_sim_date += timedelta(days=1)

        if len(crop.conditions) >= crop_type.days_cycle:
            crop.active = False

        return crop

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
            crop_unique_id,
            name,
            user_id,
            crop_type_id,
            start_date,
            start_date,
            [],
            True,
        )
        self.storage.save_crop(new_crop)
        return new_crop

    def get_crop_by_id(self, crop_id: str, requesting_user_id: str) -> Crop:
        """
        Method created to get a crop based on its ID.
        """

        requesting_user = self.storage.get_user_by_id(requesting_user_id)
        crop = self.storage.get_crop_by_id(crop_id)
        if not requesting_user:
            raise UserNotFoundError(requesting_user_id)
        if not crop:
            raise CropNotFoundError(crop_id)
        if (
            requesting_user_id != crop.user_id
        ) and requesting_user.role.value != UserRole.ADMIN.value:
            raise ResourceOwnershipError("No puedes acceder a este cultivo.")
        return crop

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

    def _get_crop_type(self, crop_type_id: str) -> CropType:
        """
        Retrieves and validates that the crop type exists.
        """

        crop_type = self.storage.get_crop_type_by_id(crop_type_id)
        if not crop_type:
            raise CropTypeNotFoundError(crop_type_id)
        return crop_type

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
        lower = crop_type.optimal_temp * 0.8
        upper = crop_type.optimal_temp * 1.2

        return sum(
            1 for c in conditions if c.temperature < lower or c.temperature > upper
        )

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
        optimal_temp: float,
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
            (optimal_temp, (int, float), "La temperatura debe ser numérica."),
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
        optimal_temp,
        needed_water,
        needed_light,
        days_cycle,
        initial_biomass,
        potential_performance,
    ):
        """
        Validates that all values are within acceptable ranges.
        """
        if optimal_temp < -7:
            raise InvalidInputError("La temperatura no puede ser menor a -7°C.")

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
        return name.strip().capitalize()

    def _validate_unique_name(self, name: str):
        """
        Validates that no crop type with the same name exists.
        """

        existing_type = self.storage.get_crop_type_by_name(name)
        if existing_type:
            raise DuplicateDataError("El tipo de cultivo ya existe.")

    def _create_crop_type_instance(
        self,
        name,
        optimal_temp,
        needed_water,
        needed_light,
        days_cycle,
        initial_biomass,
        potential_performance,
    ) -> CropType:
        """
        Creates a new CropType instance.
        """

        return CropType(
            str(uuid.uuid4()),
            name,
            optimal_temp,
            needed_water,
            needed_light,
            days_cycle,
            initial_biomass,
            potential_performance,
        )

    def create_crop_type(
        self,
        admin_id: str,
        name: str,
        optimal_temp: float,
        needed_water: float,
        needed_light: float,
        days_cycle: int,
        initial_biomass: float,
        potential_performance: float,
    ) -> CropType:
        """
        Method implemented for the admin to create new crop types.
        """

        self._validate_admin(admin_id)
        self._validate_input_types(
            optimal_temp,
            needed_water,
            needed_light,
            days_cycle,
            initial_biomass,
            potential_performance,
        )
        self._validate_input_ranges(
            optimal_temp,
            needed_water,
            needed_light,
            days_cycle,
            initial_biomass,
            potential_performance,
        )

        name = self._validate_and_format_name(name)
        self._validate_unique_name(name)

        new_crop_type = self._create_crop_type_instance(
            name,
            optimal_temp,
            needed_water,
            needed_light,
            days_cycle,
            initial_biomass,
            potential_performance,
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

    def _validate_and_filter_update_fields(self, kwargs: dict) -> dict:
        """Validates and filters the fields to update."""
        allowed_fields = {
            "name": self._validate_name_field,
            "optimal_temp": self._validate_positive_number_field,
            "needed_water": self._validate_positive_number_field,
            "needed_light": self._validate_positive_number_field,
            "days_cycle": self._validate_positive_integer_field,
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
        """Applies the validated updates to the crop type."""
        for key, value in updates.items():
            setattr(crop_type, key, value)

    def delete_crop_type(self, admin_id: str, crop_type_to_eliminate_id: str) -> None:
        """
        Deletes a crop type only if there are no active crops using it.
        """
        self._validate_admin_access(admin_id)

        crop_type = self._get_crop_type(crop_type_to_eliminate_id)
        self._validate_no_active_crops_using(crop_type)

        self.storage.delete_crop_type(crop_type_to_eliminate_id)

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


"""
AuthService and a Session Manager left for a second
report; classes will be used for control of logins
in a future web app.
"""
