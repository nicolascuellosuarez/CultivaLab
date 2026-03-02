import pytest
from unittest.mock import MagicMock, Mock
from src.cultiva_lab.services import CropService, UserService, CropTypeService
from src.cultiva_lab.models import User, UserRole, Crop, CropType, DailyCondition
from src.cultiva_lab.exceptions import (
    UserNotFoundError,
    UserAlreadyExistsError,
    CropNotFoundError,
    CropTypeNotFoundError,
    AuthorizationError,
    UnauthorizedAccessError,
    AdminAlreadyExistsError,
    InvalidInputError,
    ResourceOwnershipError,
    DuplicateDataError,
)
from datetime import datetime, timedelta


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
