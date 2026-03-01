from .models import User, Crop, CropType, DailyCondition, UserRole
from .storage import Database
from .exceptions import (
    UserNotFoundError,
    UserAlreadyExistsError,
    InvalidCredentialsError,
    CropNotFoundError,
    CropTypeNotFoundError,
    AuthorizationError,
    UnauthorizedAccessError,
    AdminAlreadyExistsError,
    InvalidInputError,
    ResourceOwnershipError,
)
from datetime import datetime, timedelta
import uuid
import bcrypt

MASTER_KEY = "admin12345"

"""
Class CropService created to include the service logic
of crops, the pilot model to simulate their growth, and
logic restrictions based in the exceptions made.
"""


class CropService:
    def __init__(self, storage: Database) -> None:
        self.storage: Database = storage

    """
    Three factors will be used to simulate the growth.
    They will act as a pilot of the math model. The first
    factor: enviromental factor; Crop Type, temperature,
    rain and sun hours received by the crop.
    """

    def _calculate_environment_factor(
        self, crop_type: CropType, temperature: float, rain: float, sun_hours: float
    ) -> float:
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

    """
    Second part of model, the phase is also an important factor
    in the growth process of a crop. Depending on the phase,
    the crop can increase its biomass to a greater or lesser
    extent.
    """

    def _calculate_phase_factor(self, crop: Crop, crop_type: CropType) -> float:
        current_day = len(crop.conditions) + 1
        phase = current_day / crop_type.days_cycle

        if phase < 0.2:
            return 0.5 + (phase * 2.5)
        elif phase < 0.7:
            return 1.0
        return max(0.2, 1.5 - phase)

    """
    Method created to calculate the growing capacity of
    a crop, based on its potential performance and current biomass.
    """

    def _calculate_capacity_factor(self, crop: Crop, crop_type: CropType) -> float:
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

    """
    Method used to calculate the total factor, and calculates
    the growth of the crop in a day.
    """

    def _calculate_growth(
        self,
        crop_type: CropType,
        env_factor: float,
        phase_factor: float,
        capacity_factor: float,
    ) -> float:
        base_rate = 0.05  # Hardcoded Base rate, remember - this is a pilot model
        total_factor = (env_factor * phase_factor * capacity_factor) ** 1.5
        return crop_type.potential_performance * base_rate * total_factor

    """
    simulate_day method to implement the logic of what happens
    if the user simulates a day in app. Validations are made
    to have restrictions and normal data in app.
    """

    def simulate_day(
        self,
        crop_id: str,
        user_id: str,
        temperature: float,
        rain: float,
        sun_hours: float,
    ) -> Crop:
        if (temperature >= 56.7) or temperature < -10:
            raise InvalidInputError("La temperatura ingresada no es real.")
        if rain < 0:
            raise InvalidInputError("Valor de lluvia inválido.")
        if sun_hours < 0 or sun_hours > 24:
            raise InvalidInputError("Las horas sol no son válidas.")
        crop = self.storage.get_crop_by_id(crop_id)
        # Method validations
        if not crop:
            raise CropNotFoundError(crop_id)
        crop_type = self.storage.get_crop_type_by_id(crop.crop_type_id)
        if not crop_type:
            raise CropTypeNotFoundError(crop.crop_type_id)
        if not crop.active:
            raise InvalidInputError("The crop is already harvested.")
        if crop.user_id != user_id:
            raise ResourceOwnershipError("No puedes simular este crop.")
        if len(crop.conditions) >= crop_type.days_cycle:
            raise InvalidInputError("El ciclo del cultivo ya terminó")

        # Simulating logic implementation; values of factors are taken from their methods
        env_factor = self._calculate_environment_factor(
            crop_type, temperature, rain, sun_hours
        )
        phase_factor = self._calculate_phase_factor(crop, crop_type)
        capacity_factor = self._calculate_capacity_factor(crop, crop_type)
        growth = self._calculate_growth(
            crop_type, env_factor, phase_factor, capacity_factor
        )

        current_biomass = (
            crop.conditions[-1].estimated_biomass
            if crop.conditions
            else crop_type.initial_biomass
        )
        new_biomass = min(current_biomass + growth, crop_type.potential_performance)

        # New condition added to daily conditions list in crop.
        new_condition = DailyCondition(
            day=len(crop.conditions) + 1,
            temperature=temperature,
            rain=rain,
            sun_hours=sun_hours,
            estimated_biomass=new_biomass,
        )

        crop.conditions.append(new_condition)
        crop.last_sim_date += timedelta(days=1)

        self.storage.save_crop(crop)
        return crop

    """
    Method created to allow a user to make new crops.
    """

    def create_crop(
        self, name: str, crop_type_id: str, user_id: str, start_date: datetime
    ) -> Crop:
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

    """
    Method created to get a crop based on its ID.
    """

    def get_crop_by_id(self, crop_id: str, requesting_user_id: str) -> Crop:
        requesting_user = self.storage.get_user_by_id(requesting_user_id)
        crop = self.storage.get_crop_by_id(crop_id)
        if not requesting_user:
            raise UserNotFoundError(requesting_user_id)
        if not crop:
            raise CropNotFoundError(crop_id)
        if (
            requesting_user_id != crop.user_id
        ) and requesting_user.role != UserRole.ADMIN:
            raise ResourceOwnershipError("No puedes acceder a este cultivo.")
        return crop

    """
    Method created to get the crops created by an user.
    """

    def get_crops_by_user(self, user_id: str, requesting_user_id: str) -> list[Crop]:
        requesting_user = self.storage.get_user_by_id(requesting_user_id)
        crops = self.storage.get_crops_by_user(user_id)
        owner = self.storage.get_user_by_id(user_id)
        if not owner:
            raise UserNotFoundError(user_id)
        if not requesting_user:
            raise UserNotFoundError(requesting_user_id)
        if requesting_user_id != user_id and requesting_user.role != UserRole.ADMIN:
            raise ResourceOwnershipError("No puedes acceder a estos cultivos.")
        return crops

    """
    Method created to see the history of conditions of a crop.
    """

    def get_crop_history(
        self, crop_id: str, requesting_user_id: str
    ) -> list[DailyCondition]:
        requesting_user = self.storage.get_user_by_id(requesting_user_id)
        crop = self.storage.get_crop_by_id(crop_id)
        if not requesting_user:
            raise UserNotFoundError(requesting_user_id)
        if not crop:
            raise CropNotFoundError(crop_id)
        if (
            requesting_user_id != crop.user_id
            and requesting_user.role != UserRole.ADMIN
        ):
            raise ResourceOwnershipError("No puedes acceder a estos cultivos.")
        return crop.conditions

    """
    Method created to update name or state of a crop.
    """

    def update_crops(self, crop_id: str, requesting_user_id: str, **kwargs) -> Crop:
        requesting_user = self.storage.get_user_by_id(requesting_user_id)
        crop = self.storage.get_crop_by_id(crop_id)
        if not requesting_user:
            raise UserNotFoundError(requesting_user_id)
        if not crop:
            raise CropNotFoundError(crop_id)
        if (
            requesting_user_id != crop.user_id
            and requesting_user.role != UserRole.ADMIN
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

    """
    Method created to delete a crop.
    """

    def delete_crop(self, crop_id: str, requesting_user_id: str) -> None:
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
            and requesting_user.role != UserRole.ADMIN
        ):
            raise ResourceOwnershipError("No puedes acceder a estos cultivos.")

        # Eliminating crop ID from user crop ID's list
        if crop_id in owner.crop_ids:
            owner.crop_ids.remove(crop_id)
            self.storage.save_user(owner)

        self.storage.delete_crop(crop_id)

    """
    Method created to see the crop statistics in
    its history.
    """

    def get_crop_statistics(self, crop_id: str, requesting_user_id: str) -> dict:
        requesting_user = self.storage.get_user_by_id(requesting_user_id)
        if not requesting_user:
            raise UserNotFoundError(requesting_user_id)
        # Crop Validation
        crop = self.storage.get_crop_by_id(crop_id)
        if not crop:
            raise CropNotFoundError(crop_id)
        # Ownership Validation
        if (
            requesting_user_id != crop.user_id
            and requesting_user.role != UserRole.ADMIN
        ):
            raise ResourceOwnershipError("No puedes acceder a este cultivo.")
        crop_type = self.storage.get_crop_type_by_id(crop.crop_type_id)
        if not crop_type:
            raise CropTypeNotFoundError(crop.crop_type_id)
        conditions = crop.conditions

        if not conditions:
            return {
                "average_temperature": 0,
                "average_rain": 0,
                "average_sun_hours": 0,
                "total_growth": 0,
                "stress_days": 0,
                "performance_ratio": 0,
            }

        # Averaging the main factors.
        avg_temp = sum(c.temperature for c in conditions) / len(conditions)
        avg_rain = sum(c.rain for c in conditions) / len(conditions)
        avg_sun = sum(c.sun_hours for c in conditions) / len(conditions)

        initial_biomass = crop_type.initial_biomass
        final_biomass = conditions[-1].estimated_biomass
        total_growth = final_biomass - initial_biomass

        # Stress days, moving on temperatures.
        stress_days = 0
        lower_temp = crop_type.optimal_temp * 0.8
        upper_temp = crop_type.optimal_temp * 1.2

        for c in conditions:
            if c.temperature < lower_temp or c.temperature > upper_temp:
                stress_days += 1

        # Rendimiento estimado vs potencial
        performance_ratio = final_biomass / crop_type.potential_performance

        return {
            "average_temperature": avg_temp,
            "average_rain": avg_rain,
            "average_sun_hours": avg_sun,
            "total_growth": total_growth,
            "stress_days": stress_days,
            "performance_ratio": performance_ratio,
        }


"""
UserService class created as a logic layer in CultivaLab;
it's the brain of business service in the app, and connects
the actions in the ICL and the Storage.
"""


class UserService:
    def __init__(self, storage: Database) -> None:
        self.storage: Database = storage

    """
    Method created to implement the logic needed to
    register a new user.
    """

    def register_user(self, username: str, password: str) -> User:
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
        new_user = User(user_unique_id, username, hashed_pwd, UserRole.USER)

        self.storage.save_user(new_user)
        return new_user

    """
    Method created to allow the unique admin registration;
    the master key is hard - coded at the beginning of this module.
    """

    def register_admin(self, admin_key: str, username: str, password: str) -> User:
        if (not username) or (not username.strip()):
            raise InvalidInputError("El nombre de usuario no puede estar vacío.")
        if (not password) or (not password.strip()):
            raise InvalidInputError("La contraseña no puede estar vacía.")
        if (not admin_key) or (not admin_key.strip()):
            raise InvalidInputError("La llave de administrador no puede estar vacía.")
        if len(password) < 8:
            raise InvalidInputError("La contraseña es demasiado corta.")
        users = self.storage.get_users()
        for user in users:
            if user.role == UserRole.ADMIN:
                raise AdminAlreadyExistsError()
        if admin_key != MASTER_KEY:
            raise UnauthorizedAccessError("La llave de administrador no es correcta.")
        if self.storage.get_user_by_username(username):
            raise UserAlreadyExistsError(username)

        user_unique_id = str(uuid.uuid4())
        hashed_pwd = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode(
            "utf-8"
        )

        new_admin = User(user_unique_id, username, hashed_pwd, UserRole.ADMIN)

        self.storage.save_user(new_admin)
        return new_admin

    """
    Method created to implement the logic of the log - in in app.
    """

    def login(self, username: str, password: str) -> User:
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

    """
    Method created to get the user information by its ID;
    it can be used by the admin or the user.
    """

    def get_user_by_id(self, user_id: str, requesting_user_id: str) -> User | None:
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
        if (requesting_user_id != user.id) and requesting_user.role != UserRole.ADMIN:
            raise ResourceOwnershipError("No puedes acceder a esta información.")

        return user

    """
    Method created to get the user information by its username;
    it can be used by the admin or the user.
    """

    def get_user_by_username(self, username: str, requesting_user_id: str):
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
        if (requesting_user_id != user.id) and requesting_user.role != UserRole.ADMIN:
            raise ResourceOwnershipError("No puedes acceder a esta información.")

        return user

    """
    Method created to get all the users registered in app;
    it can be used by the admin only.
    """

    def get_all_users(self, requesting_user_id: str) -> list[User]:
        if not (requesting_user_id) or not (requesting_user_id.strip()):
            raise InvalidInputError("El ID no puede estar vacío.")
        requesting_user = self.storage.get_user_by_id(requesting_user_id)
        if not requesting_user:
            raise UserNotFoundError(requesting_user_id)
        if requesting_user.role != UserRole.ADMIN:
            raise ResourceOwnershipError("No puedes acceder a esta información.")

        return self.storage.get_users()

    """
    Method created for the users (or admin) to change their passwords.
    """

    def update_password(
        self, user_id: str, old_password: str, new_password: str
    ) -> None:
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

    """
    Method created for the users (or admin) to change their usernames.
    """

    def update_username(
        self, user_id: str, new_username: str, requesting_user_id: str
    ) -> None:
        if (not user_id) or (not user_id.strip()):
            raise InvalidInputError("El ID del usuario no puede estar vacío.")
        if (not new_username) or (not new_username.strip()):
            raise InvalidInputError("El username nuevo no puede estar vacío.")
        if (not requesting_user_id) or (not requesting_user_id.strip()):
            raise InvalidInputError("El ID no puede estar vacío.")

        user = self.storage.get_user_by_id(user_id)
        requesting_user = self.storage.get_user_by_id(requesting_user_id)
        if not user:
            raise UserNotFoundError(user_id)
        if not requesting_user:
            raise UserNotFoundError(requesting_user_id)
        if user_id != requesting_user_id:
            raise ResourceOwnershipError("No puedes acceder a esta información.")

        searched_user = self.storage.get_user_by_username(new_username)
        if user.username == new_username:
            raise
        if searched_user:
            raise UserAlreadyExistsError("Ya existe un usuario con ese username.")

        user.username = new_username
        self.storage.save_user(user)

    """
    Method created for the users to delete their "accounts".
    It can only be used by users.
    """

    def delete_user(self, user_id: str, requesting_user_id: str) -> None:
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
        if (user_id != requesting_user_id) and (requesting_user.role != UserRole.ADMIN):
            raise ResourceOwnershipError("No puedes acceder a esta información.")
        self.storage.delete_user(user)

    """
    Method created for the users to get all their crops.
    It can be used by users and admin.
    """

    def get_user_crops(self, user_id: str, requesting_user_id: str) -> list[Crop]:
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
        if (user_id != requesting_user_id) and (requesting_user.role != UserRole.ADMIN):
            raise ResourceOwnershipError("No puedes acceder a esta información.")

        return self.storage.get_crops_by_user(user_id)
