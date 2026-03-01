class CultivaLabError(Exception):
    """
    CultivaLabError class that inherits from Exception
    to create specific Exceptions.
    """

    pass


class UserError(CultivaLabError):
    """
    UserError class that inherits from CultivaLabError
    to create User - Activity - related Exceptions.
    """

    pass


class UserNotFoundError(UserError):
    """
    Class UserNotFound created to raise an Error if the user_id
    does not exists in user - search contexts.
    """

    def __init__(self, user_id: str):
        self.user_id: str = user_id
        super().__init__(f"Usuario con el ID / User {user_id} no encontrado.")


class UserAlreadyExistsError(UserError):
    """
    Class UserAlreadyExists created to raise an Error if the user_id
    already exists in the database; only for user - creating operations.
    """

    def __init__(self, user_id: str):
        self.user_id: str = user_id
        super().__init__(f"Usuario con el ID / User {user_id} ya existe.")


class InvalidCredentialsError(UserError):
    """
    Class InvalidCredentialsError created to raise an Error if any
    of the credentials does not match.
    """

    def __init__(self, username: str, password_hash: str):
        self.username: str = username
        self.password_hash: str = password_hash
        super().__init__("Usuario o Contraseña incorrectos.")


class DuplicateDataError(UserError):
    """
    Class DuplicateDataError created to raise an Error if any
    of the entries in renovation - actions equals the last one.
    """

    def __init__(self, message: str):
        super.__init__(message)


class CropError(CultivaLabError):
    """
    CropError class created to report Crops - related Errors.
    """

    pass


class CropNotFoundError(CropError):
    """
    CropNotFound class created to raise an Error if the ID of
    the crop does not exists.
    """

    def __init__(self, crop_id: str):
        self.crop_id: str = crop_id
        super().__init__(f"Cultivo con ID {crop_id} no encontrado.")


class CropTypeNotFoundError(CropError):
    """
    CropTypeNotFoundError class created to raise an error if the
    ID of the CropType in a Crop does not exists.
    """

    def __init__(self, crop_type_id: str):
        self.crop_type_id: str = crop_type_id
        super().__init__(
            f"Tipo de cultivo con ID / username {crop_type_id} no encontrado."
        )


class AuthorizationError(CultivaLabError):
    """
    AuthorizationError class created to raise an Error if
    there are authorization - related errors in a Log - In or
    Sign - In.
    """

    pass


class UnauthorizedAccessError(AuthorizationError):
    def __init__(self, username: str, password_hash: str):
        self.username: str = username
        self.password_hash: str = password_hash
        super().__init__(
            f"Usuario con username: {username} no tiene acceso al perfil de administrador."
        )


class ResourceOwnershipError(AuthorizationError):
    """
    Exception raised when a consumer tries to make changes
    on resources that does not own.
    """

    def __init__(self, message):
        super().__init__(message)


class AdminAlreadyExistsError(AuthorizationError):
    """
    Exception raised when a consumer tries to create
    a new admin, but there is already one.
    """

    def __init__(self):
        super().__init__("El usuario administrador ya existe.")


class InvalidInputError(CultivaLabError):
    """
    Exception raised when data included by User is not valid (Ex:
    negative values, nonsense attributes, etc.)
    """

    def __init__(self, message: str, field: str = None):
        self.field: None = field
        super().__init__(message)
