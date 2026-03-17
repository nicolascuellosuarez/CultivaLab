from dataclasses import dataclass
from enum import Enum


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
