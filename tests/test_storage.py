import pytest
from src.cultiva_lab.storage import JSONStorage
from src.cultiva_lab.models import User, Crop, CropType, DailyCondition, UserRole

"""
The Storage tests for CultivaLab; here, the focus
will be on proving the operation of JSONStorage
methods implementations from a Protocol.
"""

"""
If the file does not exist yet, storage.read() should
return the expected initial structure of the DB.
"""
def test_read_returns_empty_dict_when_file_dont_exists(tmp_path):
    # The program will use the tmp path, not mocks to check
    # the operation of the database
    fake_file = tmp_path / "new_db.json"
    assert not fake_file.exists()

    storage = JSONStorage(fake_file)
    result = storage.read()
    assert isinstance(result, dict)
    assert result == {"users": [], "crops": [], "crop_types": []}

"""
Method created to see if the DataBase, effectively,
works; makes a first user and proves the registration.
"""
def test_save_and_get_users(tmp_path):
    db_file = tmp_path / "test_db.json"
    storage = JSONStorage(db_file)

    user = User(
        "123",
        "Nicolás",
        "hashed_pwd",
        UserRole.USER,
        []
    )

    storage.save_user(user)
    users = storage.get_users()
    assert len(users) == 1
    assert users[0].id == user.id
    assert users[0].username == user.username
    assert users[0].password_hash == user.password_hash
    assert users[0].role == user.role