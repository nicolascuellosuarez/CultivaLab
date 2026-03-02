import pytest
from unittest.mock import Mock
from src.cultiva_lab.services import CropService, UserService, CropTypeService
from src.cultiva_lab.models import User, UserRole, Crop, CropType, DailyCondition
from src.cultiva_lab.exceptions import (
    UserNotFoundError,
    UserAlreadyExistsError,
    CropTypeNotFoundError,
    AuthorizationError,
    AdminAlreadyExistsError,
    InvalidInputError,
    ResourceOwnershipError,
    DuplicateDataError,
    BusinessRuleViolationError,
)
from datetime import datetime, timedelta
import bcrypt


"""
Create a crop with valid parameters.
"""


def test_create_crop_success():
    storage = Mock()

    user = User("123", "nikoloko", "hashed_pwd", UserRole.USER, [])
    storage.save_user(user)
    banana_crop_type = CropType(
        "123", "Cultivo de Bananas", 27, 5.83, 12, 360, 0.75, 50
    )
    storage.save_crop_type(banana_crop_type)

    storage.get_user_by_id.return_value = user
    storage.get_crop_type_by_id.return_value = banana_crop_type

    now = datetime.now()
    service = CropService(storage)
    crop = service.create_crop("Cultivo de Bananas", "123", "123", now)

    assert crop is not None
    assert crop.name == "Cultivo de Bananas"
    assert crop.user_id == "123"
    assert crop.crop_type_id == "123"
    assert crop.start_date == now
    assert crop.last_sim_date == now
    assert crop.conditions == []
    assert crop.active is True
    storage.save_crop.assert_called_once()


"""
Try to create a crop with a non-existent user ID.
"""


def test_create_crop_invalid_user_fails():
    storage = Mock()
    storage.get_user_by_id.return_value = None
    storage.get_crop_type_by_id.return_value = CropType(
        "123", "Cultivo de Bananas", 27, 5.83, 12, 360, 0.75, 50
    )

    service = CropService(storage)
    now = datetime.now()

    with pytest.raises(UserNotFoundError):
        service.create_crop("Cultivo de Bananas", "123", "999", now)


"""
Try to create a crop with a non-existent crop type ID.
"""


def test_create_crop_invalid_crop_type_fails():
    storage = Mock()
    user = User("123", "nikoloko", "hashed_pwd", UserRole.USER, [])
    storage.get_user_by_id.return_value = user
    storage.get_crop_type_by_id.return_value = None

    service = CropService(storage)
    now = datetime.now()

    with pytest.raises(CropTypeNotFoundError):
        service.create_crop("Cultivo de Bananas", "123", "123", now)


"""
Simulate a day successfully and verify biomass calculation and date update.
"""


def test_simulate_day_success():
    storage = Mock()

    # Setup user
    user = User("123", "nikoloko", "hashed_pwd", UserRole.USER, [])

    # Setup crop type
    banana_crop_type = CropType(
        "123", "Cultivo de Bananas", 27, 5.83, 12, 360, 0.75, 50
    )

    # Setup crop with initial condition
    start_date = datetime.now()
    initial_condition = DailyCondition(
        day=1, temperature=27, rain=5.83, sun_hours=12, estimated_biomass=0.75
    )
    crop = Crop(
        "456",
        "Cultivo de Bananas",
        "123",
        "123",
        start_date,
        start_date,
        [initial_condition],
        True,
    )

    storage.get_crop_by_id.return_value = crop
    storage.get_crop_type_by_id.return_value = banana_crop_type
    storage.get_user_by_id.return_value = user

    service = CropService(storage)
    updated_crop = service.simulate_day("456", "123", 27, 5.83, 12)

    assert updated_crop is not None
    assert len(updated_crop.conditions) == 2
    assert updated_crop.conditions[1].day == 2
    assert updated_crop.conditions[1].temperature == 27
    assert updated_crop.conditions[1].rain == 5.83
    assert updated_crop.conditions[1].sun_hours == 12
    assert updated_crop.conditions[1].estimated_biomass > 0.75
    assert updated_crop.last_sim_date == start_date + timedelta(days=1)
    storage.save_crop.assert_called_once()


"""
Try to simulate a day on an inactive (harvested) crop.
"""


def test_simulate_day_crop_inactive_fails():
    storage = Mock()

    # Setup crop type
    banana_crop_type = CropType(
        "123", "Cultivo de Bananas", 27, 5.83, 12, 360, 0.75, 50
    )

    # Setup inactive crop
    start_date = datetime.now()
    initial_condition = DailyCondition(
        day=1, temperature=27, rain=5.83, sun_hours=12, estimated_biomass=0.75
    )
    crop = Crop(
        "456",
        "Cultivo de Bananas",
        "123",
        "123",
        start_date,
        start_date,
        [initial_condition],
        False,  # inactive
    )

    storage.get_crop_by_id.return_value = crop
    storage.get_crop_type_by_id.return_value = banana_crop_type

    service = CropService(storage)

    with pytest.raises(InvalidInputError):
        service.simulate_day("456", "123", 27, 5.83, 12)


"""
Try to simulate a day on a crop owned by another user.
"""


def test_simulate_day_wrong_owner_fails():
    storage = Mock()

    # Setup users
    intruder = User("999", "intruso", "hashed_pwd", UserRole.USER, [])

    # Setup crop type
    banana_crop_type = CropType(
        "123", "Cultivo de Bananas", 27, 5.83, 12, 360, 0.75, 50
    )

    # Setup crop owned by "123"
    start_date = datetime.now()
    initial_condition = DailyCondition(
        day=1, temperature=27, rain=5.83, sun_hours=12, estimated_biomass=0.75
    )
    crop = Crop(
        "456",
        "Cultivo de Bananas",
        "123",
        "123",
        start_date,
        start_date,
        [initial_condition],
        True,
    )

    storage.get_crop_by_id.return_value = crop
    storage.get_crop_type_by_id.return_value = banana_crop_type
    storage.get_user_by_id.return_value = intruder

    service = CropService(storage)

    with pytest.raises(ResourceOwnershipError):
        service.simulate_day("456", "999", 27, 5.83, 12)


"""
Simulate until completing the cycle and verify crop becomes inactive.
"""


def test_simulate_day_completes_cycle():
    storage = Mock()

    # Setup user
    user = User("123", "nikoloko", "hashed_pwd", UserRole.USER, [])

    # Setup crop type with short cycle for testing (3 days)
    banana_crop_type = CropType("123", "Cultivo de Bananas", 27, 5.83, 12, 3, 0.75, 50)

    # Setup crop with 2 conditions (day 2)
    start_date = datetime.now()
    condition1 = DailyCondition(
        day=1, temperature=27, rain=5.83, sun_hours=12, estimated_biomass=10
    )
    condition2 = DailyCondition(
        day=2, temperature=27, rain=5.83, sun_hours=12, estimated_biomass=25
    )
    crop = Crop(
        "456",
        "Cultivo de Bananas",
        "123",
        "123",
        start_date,
        start_date,
        [condition1, condition2],
        True,
    )

    storage.get_crop_by_id.return_value = crop
    storage.get_crop_type_by_id.return_value = banana_crop_type
    storage.get_user_by_id.return_value = user

    service = CropService(storage)
    updated_crop = service.simulate_day("456", "123", 27, 5.83, 12)

    assert len(updated_crop.conditions) == 3  # Day 3 added
    assert updated_crop.active is False  # Cycle completed


"""
Calculate statistics for a crop with multiple conditions.
"""


def test_get_crop_statistics_with_data():
    storage = Mock()

    # Setup users
    owner = User("123", "nikoloko", "hashed_pwd", UserRole.USER, [])

    # Setup crop type
    banana_crop_type = CropType("123", "Cultivo de Bananas", 27, 5.83, 12, 360, 10, 100)

    # Setup crop with multiple conditions
    start_date = datetime.now()
    conditions = [
        DailyCondition(
            day=1, temperature=27, rain=5.83, sun_hours=12, estimated_biomass=10
        ),
        DailyCondition(
            day=2, temperature=30, rain=4.0, sun_hours=10, estimated_biomass=15
        ),
        DailyCondition(
            day=3, temperature=25, rain=7.0, sun_hours=8, estimated_biomass=22
        ),
        DailyCondition(
            day=4, temperature=28, rain=5.0, sun_hours=11, estimated_biomass=30
        ),
        DailyCondition(
            day=5, temperature=26, rain=6.0, sun_hours=9, estimated_biomass=38
        ),
    ]
    crop = Crop(
        "456",
        "Cultivo de Bananas",
        "123",
        "123",
        start_date,
        start_date,
        conditions,
        True,
    )

    storage.get_crop_by_id.return_value = crop
    storage.get_crop_type_by_id.return_value = banana_crop_type
    storage.get_user_by_id.return_value = owner

    service = CropService(storage)
    stats = service.get_crop_statistics("456", "123")

    assert stats["average_temperature"] == pytest.approx(27.2, 0.1)
    assert stats["average_rain"] == pytest.approx(5.566, 0.1)
    assert stats["average_sun_hours"] == pytest.approx(10.0, 0.1)
    assert stats["total_growth"] == 28  # 38 - 10
    assert stats["stress_days"] >= 0
    assert 0 <= stats["performance_ratio"] <= 1


"""
Calculate statistics for a crop with no conditions.
"""


def test_get_crop_statistics_no_conditions():
    storage = Mock()

    # Setup users
    owner = User("123", "nikoloko", "hashed_pwd", UserRole.USER, [])

    # Setup crop type
    banana_crop_type = CropType("123", "Cultivo de Bananas", 27, 5.83, 12, 360, 10, 100)

    # Setup crop with no conditions
    start_date = datetime.now()
    crop = Crop(
        "456", "Cultivo de Bananas", "123", "123", start_date, start_date, [], True
    )

    storage.get_crop_by_id.return_value = crop
    storage.get_crop_type_by_id.return_value = banana_crop_type
    storage.get_user_by_id.return_value = owner

    service = CropService(storage)
    stats = service.get_crop_statistics("456", "123")

    assert stats["average_temperature"] == 0
    assert stats["average_rain"] == 0
    assert stats["average_sun_hours"] == 0
    assert stats["total_growth"] == 0
    assert stats["stress_days"] == 0
    assert stats["performance_ratio"] == 0


"""
User can view their own crops.
"""


def test_get_crops_by_user_own_allowed():
    storage = Mock()

    # Setup users
    owner = User("123", "nikoloko", "hashed_pwd", UserRole.USER, [])

    # Setup crops for this user
    start_date = datetime.now()
    crop1 = Crop(
        "456", "Cultivo de Bananas", "123", "123", start_date, start_date, [], True
    )
    crop2 = Crop(
        "789", "Cultivo de Manzanas", "123", "124", start_date, start_date, [], True
    )

    storage.get_user_by_id.return_value = owner
    storage.get_crops_by_user.return_value = [crop1, crop2]

    service = CropService(storage)
    crops = service.get_crops_by_user("123", "123")

    assert len(crops) == 2
    assert crops[0].id == "456"
    assert crops[1].id == "789"


"""
User cannot view another user's crops.
"""


def test_get_crops_by_user_other_forbidden():
    storage = Mock()

    # Setup users
    owner = User("123", "nikoloko", "hashed_pwd", UserRole.USER, [])
    other = User("999", "otro", "hashed_pwd", UserRole.USER, [])

    storage.get_user_by_id.side_effect = lambda uid: {"123": owner, "999": other}.get(
        uid
    )

    service = CropService(storage)
    print(other.role)

    with pytest.raises(ResourceOwnershipError):
        service.get_crops_by_user("123", "999")


"""
Admin can view any user's crops.
"""


def test_get_crops_by_user_admin_can_see_any():
    storage = Mock()

    # Setup users
    owner = User("123", "nikoloko", "hashed_pwd", UserRole.USER, [])
    admin = User("999", "admin", "hashed_pwd", UserRole.ADMIN, [])

    # Setup crops for owner
    start_date = datetime.now()
    crop1 = Crop(
        "456", "Cultivo de Bananas", "123", "123", start_date, start_date, [], True
    )
    crop2 = Crop(
        "789", "Cultivo de Manzanas", "123", "124", start_date, start_date, [], True
    )

    storage.get_user_by_id.side_effect = lambda id: admin if id == "999" else owner
    storage.get_crops_by_user.return_value = [crop1, crop2]

    service = CropService(storage)
    crops = service.get_crops_by_user("123", "999")

    assert len(crops) == 2
    storage.get_crops_by_user.assert_called_with("123")


"""
Update crop name successfully.
"""


def test_update_crop_name_success():
    storage = Mock()

    # Setup users
    owner = User("123", "nikoloko", "hashed_pwd", UserRole.USER, ["456"])

    # Setup crop
    start_date = datetime.now()
    crop = Crop(
        "456", "Cultivo de Bananas", "123", "123", start_date, start_date, [], True
    )

    storage.get_crop_by_id.return_value = crop
    storage.get_user_by_id.return_value = owner

    service = CropService(storage)
    updated_crop = service.update_crops(
        "456", "123", name="Cultivo de Bananas Renombrado"
    )

    assert updated_crop.name == "Cultivo de Bananas Renombrado"
    storage.save_crop.assert_called_once()


"""
Try to update forbidden fields like id, user_id, crop_type_id.
"""


def test_update_crop_forbidden_fields_fails():
    storage = Mock()

    # Setup users
    owner = User("123", "nikoloko", "hashed_pwd", UserRole.USER, ["456"])

    # Setup crop
    start_date = datetime.now()
    crop = Crop(
        "456", "Cultivo de Bananas", "123", "123", start_date, start_date, [], True
    )

    storage.get_crop_by_id.return_value = crop
    storage.get_user_by_id.return_value = owner

    service = CropService(storage)

    # Try to update id
    with pytest.raises(InvalidInputError):
        service.update_crops("456", "123", id="nuevo-id")

    # Try to update user_id
    with pytest.raises(InvalidInputError):
        service.update_crops("456", "123", user_id="999")

    # Try to update crop_type_id
    with pytest.raises(InvalidInputError):
        service.update_crops("456", "123", crop_type_id="nuevo-tipo")


"""
User can delete their own crop.
"""


def test_delete_crop_own_allowed():
    storage = Mock()

    # Setup users
    owner = User("123", "nikoloko", "hashed_pwd", UserRole.USER, ["456"])

    # Setup crop
    start_date = datetime.now()
    crop = Crop(
        "456", "Cultivo de Bananas", "123", "123", start_date, start_date, [], True
    )

    storage.get_crop_by_id.return_value = crop
    storage.get_user_by_id.side_effect = lambda id: owner if id == "123" else None

    service = CropService(storage)
    service.delete_crop("456", "123")

    # Verify crop was removed from user's crop_ids
    assert "456" not in owner.crop_ids
    storage.save_user.assert_called_once_with(owner)
    storage.delete_crop.assert_called_once_with("456")


"""
User cannot delete another user's crop.
"""


def test_delete_crop_other_forbidden():
    storage = Mock()

    # Setup users
    owner = User("123", "nikoloko", "hashed_pwd", UserRole.USER, ["456"])
    other = User("999", "otro", "hashed_pwd", UserRole.USER, [])

    # Setup crop
    start_date = datetime.now()
    crop = Crop(
        "456", "Cultivo de Bananas", "123", "123", start_date, start_date, [], True
    )

    storage.get_crop_by_id.return_value = crop
    storage.get_user_by_id.side_effect = lambda id: owner if id == "123" else other

    service = CropService(storage)

    with pytest.raises(ResourceOwnershipError):
        service.delete_crop("456", "999")


"""
Register a new user successfully with role USER.
"""


def test_register_user_success():
    storage = Mock()
    storage.get_user_by_username.return_value = None

    service = UserService(storage)
    user = service.register_user("nikoloko", "password123")

    assert user is not None
    assert user.username == "nikoloko"
    assert user.role == UserRole.USER
    assert len(user.password_hash) > 0
    storage.save_user.assert_called_once()


"""
Try to register a user with a username that already exists.
"""


def test_register_user_duplicate_username_fails():
    storage = Mock()
    existing_user = User("123", "nikoloko", "hashed_pwd", UserRole.USER, [])
    storage.get_user_by_username.return_value = existing_user

    service = UserService(storage)

    with pytest.raises(UserAlreadyExistsError):
        service.register_user("nikoloko", "password123")


"""
Try to register a user with a password shorter than 8 characters.
"""


def test_register_user_password_too_short_fails():
    storage = Mock()
    storage.get_user_by_username.return_value = None

    service = UserService(storage)

    with pytest.raises(InvalidInputError):
        service.register_user("nikoloko", "short")


"""
Login successfully with correct credentials.
"""


def test_login_success():
    storage = Mock()

    # Create a real password hash
    password = "password123"
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    user = User("123", "nikoloko", hashed, UserRole.USER, [])
    storage.get_user_by_username.return_value = user

    service = UserService(storage)
    logged_user = service.login("nikoloko", password)

    assert logged_user is not None
    assert logged_user.username == "nikoloko"


"""
Try to login with wrong password.
"""


def test_login_wrong_password_fails():
    storage = Mock()

    # Create a real password hash for "correctpass"
    correct_password = "correctpass"
    hashed = bcrypt.hashpw(correct_password.encode("utf-8"), bcrypt.gensalt()).decode(
        "utf-8"
    )

    user = User("123", "nikoloko", hashed, UserRole.USER, [])
    storage.get_user_by_username.return_value = user

    service = UserService(storage)

    with pytest.raises(AuthorizationError):
        service.login("nikoloko", "wrongpass")


"""
Try to login with non-existent username.
"""


def test_login_nonexistent_user_fails():
    storage = Mock()
    storage.get_user_by_username.return_value = None

    service = UserService(storage)

    with pytest.raises(UserNotFoundError):
        service.login("nikoloko", "password123")


"""
User can view their own profile by ID.
"""


def test_get_user_by_id_own_user_allowed():
    storage = Mock()

    owner = User("123", "nikoloko", "hashed_pwd", UserRole.USER, [])

    storage.get_user_by_id.side_effect = lambda uid: {"123": owner}.get(uid)

    service = UserService(storage)
    result = service.get_user_by_id("123", "123")

    assert result is not None
    assert result.id == "123"
    assert result.username == "nikoloko"


"""
User cannot view another user's profile (non-admin).
"""


def test_get_user_by_id_other_user_forbidden():
    storage = Mock()

    owner = User("123", "nikoloko", "hashed_pwd", UserRole.USER, [])
    other = User("999", "otro", "hashed_pwd", UserRole.USER, [])

    storage.get_user_by_id.side_effect = lambda uid: {"123": owner, "999": other}.get(
        uid
    )

    service = UserService(storage)

    with pytest.raises(ResourceOwnershipError):
        service.get_user_by_id("123", "999")


"""
Admin can view any user's profile.
"""


def test_get_user_by_id_admin_can_see_any():
    storage = Mock()

    target = User("123", "nikoloko", "hashed_pwd", UserRole.USER, [])
    admin = User("999", "admin", "hashed_pwd", UserRole.ADMIN, [])

    storage.get_user_by_id.side_effect = lambda uid: {"123": target, "999": admin}.get(
        uid
    )

    service = UserService(storage)
    result = service.get_user_by_id("123", "999")

    assert result is not None
    assert result.id == "123"


"""
Update password successfully with correct old password.
"""


def test_update_password_success():
    storage = Mock()

    # Create a real password hash for "oldpass123"
    old_password = "oldpass123"
    new_password = "newpass123"
    hashed = bcrypt.hashpw(old_password.encode("utf-8"), bcrypt.gensalt()).decode(
        "utf-8"
    )

    user = User("123", "nikoloko", hashed, UserRole.USER, [])
    storage.get_user_by_id.return_value = user

    service = UserService(storage)
    service.update_password("123", old_password, new_password)

    # Verify the password hash changed
    assert user.password_hash != hashed
    storage.save_user.assert_called_once_with(user)


"""
Try to update password with wrong old password.
"""


def test_update_password_wrong_old_password_fails():
    storage = Mock()

    # Create a real password hash for "oldpass123"
    old_password = "oldpass123"
    hashed = bcrypt.hashpw(old_password.encode("utf-8"), bcrypt.gensalt()).decode(
        "utf-8"
    )

    user = User("123", "nikoloko", hashed, UserRole.USER, [])
    storage.get_user_by_id.return_value = user

    service = UserService(storage)

    with pytest.raises(AuthorizationError):
        service.update_password("123", "wrongold", "newpass123")


"""
Update username successfully (own account).
"""


def test_update_username_success():
    storage = Mock()

    user = User("123", "nikoloko", "hashed_pwd", UserRole.USER, [])

    storage.get_user_by_id.side_effect = lambda uid: {"123": user}.get(uid)
    storage.get_user_by_username.return_value = None

    service = UserService(storage)
    service.update_username("123", "nuevo_nombre", "123")

    assert user.username == "nuevo_nombre"
    storage.save_user.assert_called_once_with(user)


"""
Try to update username to one that already exists.
"""


def test_update_username_duplicate_fails():
    storage = Mock()

    user = User("123", "nikoloko", "hashed_pwd", UserRole.USER, [])
    existing_user = User("999", "existente", "hashed_pwd", UserRole.USER, [])

    storage.get_user_by_id.side_effect = lambda uid: {"123": user}.get(uid)
    storage.get_user_by_username.return_value = existing_user

    service = UserService(storage)

    with pytest.raises(UserAlreadyExistsError):
        service.update_username("123", "existente", "123")


"""
User can delete their own account.
"""


def test_delete_user_own_account_allowed():
    storage = Mock()

    user = User("123", "nikoloko", "hashed_pwd", UserRole.USER, [])

    storage.get_user_by_id.side_effect = lambda uid: {"123": user}.get(uid)

    service = UserService(storage)
    service.delete_user("123", "123")

    storage.delete_user.assert_called_once_with(user)


"""
User cannot delete another user's account.
"""


def test_delete_user_other_account_forbidden():
    storage = Mock()

    target = User("123", "nikoloko", "hashed_pwd", UserRole.USER, [])
    other = User("999", "otro", "hashed_pwd", UserRole.USER, [])

    storage.get_user_by_id.side_effect = lambda uid: {"123": target, "999": other}.get(
        uid
    )

    service = UserService(storage)

    with pytest.raises(ResourceOwnershipError):
        service.delete_user("123", "999")


"""
Admin can delete any user account.
"""


def test_delete_user_admin_can_delete_any():
    storage = Mock()

    target = User("123", "nikoloko", "hashed_pwd", UserRole.USER, [])
    admin = User("999", "admin", "hashed_pwd", UserRole.ADMIN, [])

    storage.get_user_by_id.side_effect = lambda uid: {"123": target, "999": admin}.get(
        uid
    )

    service = UserService(storage)
    service.delete_user("123", "999")

    storage.delete_user.assert_called_once_with(target)


"""
Only one admin can exist in the system - second attempt fails.
"""


def test_register_admin_only_once():
    storage = Mock()

    # First admin exists
    existing_admin = User("123", "admin", "hashed_pwd", UserRole.ADMIN, [])
    storage.get_users.return_value = [existing_admin]

    service = UserService(storage)

    with pytest.raises(AdminAlreadyExistsError):
        service.register_admin("admin12345", "otroadmin", "password123")


"""
Register admin fails with wrong master key.
"""


def test_register_admin_wrong_key_fails():
    storage = Mock()
    storage.get_users.return_value = []  # No admin exists

    service = UserService(storage)

    with pytest.raises(InvalidInputError):
        service.register_admin("wrongkey", "admin", "password123")


"""
Register admin successfully with correct master key.
"""


def test_register_admin_success():
    storage = Mock()
    storage.get_users.return_value = []  # No admin exists
    storage.get_user_by_username.return_value = None

    service = UserService(storage)
    admin = service.register_admin("admin12345", "admin", "password123")

    assert admin is not None
    assert admin.username == "admin"
    assert admin.role == UserRole.ADMIN
    storage.save_user.assert_called_once()


"""
Get all users (admin only).
"""


def test_get_all_users_admin_allowed():
    storage = Mock()

    admin = User("999", "admin", "hashed_pwd", UserRole.ADMIN, [])
    user1 = User("123", "nikoloko", "hashed_pwd", UserRole.USER, [])
    user2 = User("456", "otro", "hashed_pwd", UserRole.USER, [])

    storage.get_user_by_id.return_value = admin
    storage.get_users.return_value = [user1, user2]

    service = UserService(storage)
    users = service.get_all_users("999")

    assert len(users) == 2
    assert users[0].id == "123"
    assert users[1].id == "456"


"""
Get all users fails for non-admin.
"""


def test_get_all_users_non_admin_fails():
    storage = Mock()

    normal_user = User("123", "nikoloko", "hashed_pwd", UserRole.USER, [])
    storage.get_user_by_id.return_value = normal_user

    service = UserService(storage)

    with pytest.raises(ResourceOwnershipError):
        service.get_all_users("123")


"""
Get user crops (own account allowed).
"""


def test_get_user_crops_own_allowed():
    storage = Mock()

    user = User("123", "nikoloko", "hashed_pwd", UserRole.USER, ["456"])
    crops = ["crop1", "crop2"]  # Simplified for test

    storage.get_user_by_id.side_effect = lambda uid: {"123": user}.get(uid)
    storage.get_crops_by_user.return_value = crops

    service = UserService(storage)
    result = service.get_user_crops("123", "123")

    assert result == crops
    storage.get_crops_by_user.assert_called_with("123")


"""
Get user crops (other user forbidden).
"""


def test_get_user_crops_other_forbidden():
    storage = Mock()

    owner = User("123", "nikoloko", "hashed_pwd", UserRole.USER, ["456"])
    other = User("999", "otro", "hashed_pwd", UserRole.USER, [])

    storage.get_user_by_id.side_effect = lambda uid: {"123": owner, "999": other}.get(
        uid
    )

    service = UserService(storage)

    with pytest.raises(ResourceOwnershipError):
        service.get_user_crops("123", "999")


"""
Admin creates a new crop type successfully.
"""


def test_create_crop_type_admin_success():
    storage = Mock()
    user_service = Mock()

    admin = User("999", "admin", "hashed_pwd", UserRole.ADMIN, [])
    storage.get_user_by_id.return_value = admin
    storage.get_crop_type_by_name.return_value = None

    service = CropTypeService(storage, user_service)
    crop_type = service.create_crop_type(
        "999", "Cultivo de Bananas", 27, 5.83, 12, 360, 0.75, 50
    )

    assert crop_type is not None
    assert crop_type.name == "Cultivo de Bananas".capitalize()
    assert crop_type.optimal_temp == 27
    assert crop_type.needed_water == 5.83
    assert crop_type.needed_light == 12
    assert crop_type.days_cycle == 360
    assert crop_type.initial_biomass == 0.75
    assert crop_type.potential_performance == 50
    storage.save_crop_type.assert_called_once()


"""
Regular user cannot create crop types.
"""


def test_create_crop_type_non_admin_fails():
    storage = Mock()
    user_service = Mock()

    normal_user = User("123", "nikoloko", "hashed_pwd", UserRole.USER, [])
    storage.get_user_by_id.return_value = normal_user

    service = CropTypeService(storage, user_service)

    with pytest.raises(ResourceOwnershipError):
        service.create_crop_type(
            "123", "Cultivo de Bananas", 27, 5.83, 12, 360, 0.75, 50
        )


"""
Try to create a crop type with a duplicate name.
"""


def test_create_crop_type_duplicate_name_fails():
    storage = Mock()
    user_service = Mock()

    admin = User("999", "admin", "hashed_pwd", UserRole.ADMIN, [])
    existing_crop_type = CropType(
        "456", "Cultivo de Bananas", 27, 5.83, 12, 360, 0.75, 50
    )

    storage.get_user_by_id.return_value = admin
    storage.get_crop_type_by_name.return_value = existing_crop_type

    service = CropTypeService(storage, user_service)

    with pytest.raises(DuplicateDataError):
        service.create_crop_type(
            "999", "Cultivo de Bananas", 27, 5.83, 12, 360, 0.75, 50
        )


"""
Admin updates an existing crop type successfully.
"""


def test_update_crop_type_admin_success():
    storage = Mock()
    user_service = Mock()

    admin = User("999", "admin", "hashed_pwd", UserRole.ADMIN, [])
    crop_type = CropType("123", "Cultivo de Bananas", 27, 5.83, 12, 360, 0.75, 50)

    storage.get_user_by_id.return_value = admin
    storage.get_crop_type_by_id.return_value = crop_type
    storage.get_crops_by_type.return_value = []  # No crops using this type

    service = CropTypeService(storage, user_service)
    updated = service.update_crop_type(
        "999",
        "123",
        name="Cultivo de Bananas Mejorado",
        optimal_temp=28,
        potential_performance=60,
    )

    assert updated.name == "Cultivo de Bananas Mejorado"
    assert updated.optimal_temp == 28
    assert updated.potential_performance == 60
    storage.save_crop_type.assert_called_once()


"""
Cannot update a crop type that has active crops using it.
"""


def test_update_crop_type_with_active_crops_fails():
    storage = Mock()
    user_service = Mock()

    admin = User("999", "admin", "hashed_pwd", UserRole.ADMIN, [])
    crop_type = CropType("123", "Cultivo de Bananas", 27, 5.83, 12, 360, 0.75, 50)

    # Create an active crop using this crop type
    start_date = datetime.now()
    active_crop = Crop(
        "456", "Mi Banano", "789", "123", start_date, start_date, [], True
    )

    storage.get_user_by_id.return_value = admin
    storage.get_crop_type_by_id.return_value = crop_type
    storage.get_crops_by_type.return_value = [active_crop]

    service = CropTypeService(storage, user_service)

    with pytest.raises(BusinessRuleViolationError):
        service.update_crop_type("999", "123", name="Cultivo de Bananas Mejorado")


"""
Delete a crop type that has no crops associated.
"""


def test_delete_crop_type_with_no_crops_success():
    storage = Mock()
    user_service = Mock()

    admin = User("999", "admin", "hashed_pwd", UserRole.ADMIN, [])
    crop_type = CropType("123", "Cultivo de Bananas", 27, 5.83, 12, 360, 0.75, 50)

    storage.get_user_by_id.return_value = admin
    storage.get_crop_type_by_id.return_value = crop_type
    storage.get_crops.return_value = []  # No crops at all

    service = CropTypeService(storage, user_service)
    service.delete_crop_type("999", "123")

    storage.delete_crop_type.assert_called_once_with("123")


"""
Cannot delete a crop type that has active crops using it.
"""


def test_delete_crop_type_with_active_crops_fails():
    storage = Mock()
    user_service = Mock()

    admin = User("999", "admin", "hashed_pwd", UserRole.ADMIN, [])
    crop_type = CropType("123", "Cultivo de Bananas", 27, 5.83, 12, 360, 0.75, 50)

    # Create an active crop using this crop type
    start_date = datetime.now()
    active_crop = Crop(
        "456", "Mi Banano", "789", "123", start_date, start_date, [], True
    )

    storage.get_user_by_id.return_value = admin
    storage.get_crop_type_by_id.return_value = crop_type
    storage.get_crops.return_value = [active_crop]

    service = CropTypeService(storage, user_service)

    with pytest.raises(BusinessRuleViolationError):
        service.delete_crop_type("999", "123")


"""
Delete a crop type that only has inactive (harvested) crops using it.
"""


def test_delete_crop_type_with_inactive_crops_allowed():
    storage = Mock()
    user_service = Mock()

    admin = User("999", "admin", "hashed_pwd", UserRole.ADMIN, [])
    crop_type = CropType("123", "Cultivo de Bananas", 27, 5.83, 12, 360, 0.75, 50)

    # Create an inactive crop using this crop type
    start_date = datetime.now()
    inactive_crop = Crop(
        "456",
        "Mi Banano",
        "789",
        "123",
        start_date,
        start_date,
        [],
        False,  # inactive (harvested)
    )

    storage.get_user_by_id.return_value = admin
    storage.get_crop_type_by_id.return_value = crop_type
    storage.get_crops.return_value = [inactive_crop]

    service = CropTypeService(storage, user_service)
    service.delete_crop_type("999", "123")

    storage.delete_crop_type.assert_called_once_with("123")


"""
Get all crop types returns a list.
"""


def test_get_all_crop_types_returns_list():
    storage = Mock()
    user_service = Mock()

    banana_type = CropType("123", "Cultivo de Bananas", 27, 5.83, 12, 360, 0.75, 50)
    apple_type = CropType("456", "Cultivo de Manzanas", 22, 4.5, 10, 300, 0.5, 40)
    corn_type = CropType("789", "Cultivo de Maíz", 25, 5.0, 8, 120, 0.8, 100)

    storage.get_crop_types.return_value = [banana_type, apple_type, corn_type]

    service = CropTypeService(storage, user_service)
    crop_types = service.get_crop_types()

    assert len(crop_types) == 3
    assert crop_types[0].name == "Cultivo de Bananas"
    assert crop_types[1].name == "Cultivo de Manzanas"
    assert crop_types[2].name == "Cultivo de Maíz"


"""
Get crop type by ID successfully.
"""


def test_get_crop_type_by_id_success():
    storage = Mock()
    user_service = Mock()

    banana_type = CropType("123", "Cultivo de Bananas", 27, 5.83, 12, 360, 0.75, 50)
    storage.get_crop_type_by_id.return_value = banana_type

    service = CropTypeService(storage, user_service)
    result = service.get_crop_type_by_id("123")

    assert result is not None
    assert result.id == "123"
    assert result.name == "Cultivo de Bananas"


"""
Get crop type by ID fails when not found.
"""


def test_get_crop_type_by_id_not_found_fails():
    storage = Mock()
    user_service = Mock()

    storage.get_crop_type_by_id.return_value = None

    service = CropTypeService(storage, user_service)

    with pytest.raises(CropTypeNotFoundError):
        service.get_crop_type_by_id("999")


"""
Get crop type by name successfully.
"""


def test_get_crop_type_by_name_success():
    storage = Mock()
    user_service = Mock()

    banana_type = CropType("123", "Cultivo de Bananas", 27, 5.83, 12, 360, 0.75, 50)
    storage.get_crop_type_by_name.return_value = banana_type

    service = CropTypeService(storage, user_service)
    result = service.get_crop_type_by_name("Cultivo de Bananas")

    assert result is not None
    assert result.id == "123"
    assert result.name == "Cultivo de Bananas"


"""
Get crop type by name fails when not found.
"""


def test_get_crop_type_by_name_not_found_fails():
    storage = Mock()
    user_service = Mock()

    storage.get_crop_type_by_name.return_value = None

    service = CropTypeService(storage, user_service)

    with pytest.raises(CropTypeNotFoundError):
        service.get_crop_type_by_name("Cultivo Inexistente")


"""
Get crop types with statistics (admin only).
"""


def test_get_crop_types_with_stats_admin_success():
    storage = Mock()
    user_service = Mock()

    admin = User("999", "admin", "hashed_pwd", UserRole.ADMIN, [])
    storage.get_user_by_id.return_value = admin

    banana_type = CropType("123", "Cultivo de Bananas", 27, 5.83, 12, 360, 10, 100)
    apple_type = CropType("456", "Cultivo de Manzanas", 22, 4.5, 10, 300, 8, 80)
    storage.get_crop_types.return_value = [banana_type, apple_type]

    # Create some crops for statistics
    start_date = datetime.now()
    crop1 = Crop(
        "c1",
        "Mi Banano",
        "u1",
        "123",
        start_date,
        start_date,
        [DailyCondition(1, 27, 5.83, 12, 50)],
        True,
    )
    crop2 = Crop(
        "c2",
        "Mi Banano 2",
        "u2",
        "123",
        start_date,
        start_date,
        [DailyCondition(1, 28, 6, 11, 60)],
        True,
    )
    crop3 = Crop(
        "c3",
        "Mi Manzana",
        "u3",
        "456",
        start_date,
        start_date,
        [DailyCondition(1, 22, 4.5, 10, 40)],
        True,
    )

    storage.get_crops.return_value = [crop1, crop2, crop3]

    service = CropTypeService(storage, user_service)
    stats = service.get_crop_types_with_stats("999")

    assert len(stats) == 2
    # Find banana stats
    banana_stats = next(s for s in stats if s["crop_type_id"] == "123")
    assert banana_stats["active_crops"] == 2

    # Find apple stats
    apple_stats = next(s for s in stats if s["crop_type_id"] == "456")
    assert apple_stats["active_crops"] == 1


"""
Get crop types with stats fails for non-admin.
"""


def test_get_crop_types_with_stats_non_admin_fails():
    storage = Mock()
    user_service = Mock()

    normal_user = User("123", "nikoloko", "hashed_pwd", UserRole.USER, [])
    storage.get_user_by_id.return_value = normal_user

    service = CropTypeService(storage, user_service)

    with pytest.raises(ResourceOwnershipError):
        service.get_crop_types_with_stats("123")
