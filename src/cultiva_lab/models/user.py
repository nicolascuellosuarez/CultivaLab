from dataclasses import dataclass
from enum import Enum
from src.cultiva_lab.exceptions import InvalidInputError


@dataclass
class UserRole(Enum):
    """
    UserRole Dataclass implementation, inherits from Enum Module.
    Allows the differentiation between the two profile types.
    """

    ADMIN = "admin"
    USER = "user"
    # Class constants


@dataclass
class User:
    """
    User Dataclass implementation, with its respective attributes.
    """

    id: str
    username: str
    password_hash: str
    role: UserRole
    # A role Attribute, it's a UserRole type attribute.
    crop_ids: list[str]
    # A list with the crops created by usr.

    def __post_init__(self):
        self._validate_username()
        self._validate_password_hash()
        self._validate_role()
        self._validate_crop_ids()

    def _validate_username(self):
        """
        Restricted method created to validate the username
        of an user.
        """

        if not self.username or not self.username.strip():
            raise InvalidInputError("El nombre de usuario no puede estar vacío.")
        if not isinstance(self.username, str):
            raise InvalidInputError("El username no es válido.")

    def _validate_password_hash(self):
        """
        Restricted method created to validate if an user - password
        is valid.
        """

        if not self.password_hash or not self.password_hash.strip():
            raise InvalidInputError("La contraseña no puede estar vacía.")
        if not isinstance(self.password_hash, str):
            raise InvalidInputError("La contraseña no es válida. ")

    def _validate_role(self):
        """
        Restricted method created to validate if the role of an
        user is valid.
        """

        if not isinstance(self.role, UserRole):
            raise InvalidInputError("El rol debe ser una instancia de UserRole.")

    def _validate_crop_ids(self):
        """
        Restricted method created to validate the list of crops owned
        by user.
        """

        if not isinstance(self.crop_ids, list):
            raise InvalidInputError("La lista de Cultivos debe ser una lista.")
        for crop_id in self.crop_ids:
            if not isinstance(crop_id, str) or not crop_id.strip():
                raise InvalidInputError(f"ID de cultivo inválido: {crop_id}")
