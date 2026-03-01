from src.cultiva_lab.storage import JSONStorage
from src.cultiva_lab.models import User, Crop, CropType, UserRole
from datetime import datetime

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
    temp_file = tmp_path / "test_db.json"
    assert not temp_file.exists()

    storage = JSONStorage(temp_file)
    result = storage.read()
    assert isinstance(result, dict)
    assert result == {"users": [], "crops": [], "crop_types": []}


"""
Method created to see if the DataBase, effectively,
works; makes a first user and proves the registration.
"""


def test_save_and_get_users(tmp_path):
    temp_file = tmp_path / "test_db.json"
    storage = JSONStorage(temp_file)

    user = User("123", "Nicolás", "hashed_pwd", UserRole.USER, [])
    storage.save_user(user)

    users = storage.get_users()
    assert len(users) == 1
    assert users[0].id == user.id
    assert users[0].username == user.username
    assert users[0].password_hash == user.password_hash
    assert users[0].role == user.role


"""
Method created to validate the update of a user that already exists,
instead of making a new one with the same ID.
"""


def test_save_user_updates_existing_instead_of_duplicate(tmp_path):
    temp_file = tmp_path / "test_db.json"
    storage = JSONStorage(temp_file)

    user = User("123", "nikoloko", "hashed_pwd", UserRole.USER, [])
    storage.save_user(user)

    evaluating_user = User("123", "nikoloko07", "hashed_pwd", UserRole.USER, [])
    storage.save_user(evaluating_user)

    users = storage.get_users()
    assert len(users) == 1
    assert users[0].id == evaluating_user.id
    assert users[0].username == evaluating_user.username
    assert users[0].password_hash == evaluating_user.password_hash
    assert users[0].role == evaluating_user.role


"""
Method created to see if the delete_user method works;
eliminating the user from the DataBase.
"""


def test_delete_user_removes_from_storage(tmp_path):
    temp_file = tmp_path / "test_db.json"
    storage = JSONStorage(temp_file)

    user1 = User("123", "nikoloko", "hashed_pwd", UserRole.USER, [])
    storage.save_user(user1)

    user2 = User("1234", "catima", "hashed_pwd", UserRole.USER, [])
    storage.save_user(user2)

    users = storage.get_users()
    assert len(users) == 2
    assert users[0].id == user1.id
    assert users[1].id == user2.id

    storage.delete_user(user1.id)
    updated_users = storage.get_users()
    assert len(updated_users) == 1
    assert updated_users[0].id == user2.id
    assert updated_users[0].username == user2.username
    assert updated_users[0].password_hash == user2.password_hash


"""
Method created to see the operation of the get_user_by_id function.
"""


def test_get_user_by_id_works_and_returns_none_if_not_found(tmp_path):
    temp_path = tmp_path / "test_db.json"
    storage = JSONStorage(temp_path)

    user1 = User("123", "nikoloko", "hashed_pwd", UserRole.USER, [])
    storage.save_user(user1)

    user_in_db = storage.get_user_by_id(user1.id)
    assert user_in_db is not None
    assert user_in_db.id == user1.id
    assert user_in_db.username == user1.username
    assert storage.get_user_by_id("4567") is None


"""
Method created to see the operation of the get_user_by_username
function.
"""


def test_get_user_by_username_works_and_returns_none_if_not_found(tmp_path):
    temp_path = tmp_path / "test_db.json"
    storage = JSONStorage(temp_path)

    user1 = User("123", "nikoloko", "hashed_pwd", UserRole.USER, [])
    storage.save_user(user1)

    user_in_db = storage.get_user_by_username(user1.username)
    assert user_in_db is not None
    assert user_in_db.id == user1.id
    assert user_in_db.username == user1.username
    assert storage.get_user_by_username("catima") is None


"""
Test created to see the operation of the save and get crops methods
in storage.
"""


def test_save_and_get_crops(tmp_path):
    temp_path = tmp_path / "test_db.json"
    storage = JSONStorage(temp_path)

    user1 = User("123", "nikoloko", "hashed_pwd", UserRole.USER, [])
    storage.save_user(user1)

    banana_crop_type = CropType(
        "123", "Cultivo de Bananas", 27, 5.83, 12, 360, 0.75, 50
    )
    storage.save_crop_type(banana_crop_type)
    now = datetime.now()
    crop = Crop("123", "Cultivo de Bananas", "123", "123", now, now, [], True)
    storage.save_crop(crop)

    crops = storage.get_crops()

    assert len(crops) == 1
    assert crops[0].id == crop.id
    assert crops[0].name == crop.name


"""
Method created to supervise the correct operation save_crop method
in storage, not only saving new crops, also editing existing ones
if the ID already exists.
"""


def test_save_crop_updates_existing_instead_of_duplicate(tmp_path):
    temp_file = tmp_path / "test_db.json"
    storage = JSONStorage(temp_file)

    user1 = User("123", "nikoloko", "hashed_pwd", UserRole.USER, [])
    storage.save_user(user1)

    banana_crop_type = CropType(
        "123", "Cultivo de Bananas", 27, 5.83, 12, 360, 0.75, 50
    )
    storage.save_crop_type(banana_crop_type)
    now = datetime.now()
    crop = Crop("123", "Cultivo de Bananas", "123", "123", now, now, [], True)
    storage.save_crop(crop)

    evaluating_crop = Crop(
        "123", "Cultivo de Bananas #2", "123", "123", now, now, [], True
    )
    storage.save_crop(evaluating_crop)

    crops = storage.get_crops()
    assert len(crops) == 1
    assert crops[0].id == evaluating_crop.id
    assert crops[0].name == evaluating_crop.name
    assert crops[0].user_id == evaluating_crop.user_id


"""
Method created to see if the delete_crop method works;
eliminating the crop from the DataBase.
"""


def test_delete_crop_removes_from_storage(tmp_path):
    temp_file = tmp_path / "test_db.json"
    storage = JSONStorage(temp_file)

    user1 = User("123", "nikoloko", "hashed_pwd", UserRole.USER, [])
    storage.save_user(user1)

    banana_crop_type = CropType(
        "123", "Cultivo de Bananas", 27, 5.83, 12, 360, 0.75, 50
    )
    storage.save_crop_type(banana_crop_type)
    now = datetime.now()

    crop1 = Crop("123", "Cultivo de Bananas", "123", "123", now, now, [], True)
    storage.save_crop(crop1)
    crop2 = Crop("1234", "Cultivo de Bananas #2", "123", "123", now, now, [], True)
    storage.save_crop(crop2)

    crops = storage.get_crops()
    assert len(crops) == 2
    assert crops[0].id == crop1.id
    assert crops[1].id == crop2.id

    storage.delete_crop(crop1.id)
    updated_crops = storage.get_crops()
    assert len(updated_crops) == 1
    assert updated_crops[0].id == crop2.id
    assert updated_crops[0].name == crop2.name


"""
Method created to see the operation of the get_crop_by_id function.
"""


def test_get_crop_by_id_works_and_returns_none_if_not_found(tmp_path):
    temp_path = tmp_path / "test_db.json"
    storage = JSONStorage(temp_path)

    user1 = User("123", "nikoloko", "hashed_pwd", UserRole.USER, [])
    storage.save_user(user1)

    banana_crop_type = CropType(
        "123", "Cultivo de Bananas", 27, 5.83, 12, 360, 0.75, 50
    )
    storage.save_crop_type(banana_crop_type)
    now = datetime.now()

    crop = Crop("123", "Cultivo de Bananas", "123", "123", now, now, [], True)
    storage.save_crop(crop)

    crop_in_db = storage.get_crop_by_id(crop.id)
    assert crop_in_db is not None
    assert crop_in_db.id == crop.id
    assert crop_in_db.name == crop.name
    assert storage.get_crop_by_id("4567") is None


"""
Method created to see the operation of the get_crop_by_user
function.
"""


def test_get_crops_by_user_returns_only_that_user_crops(tmp_path):
    temp_path = tmp_path / "test_db.json"
    storage = JSONStorage(temp_path)

    user1 = User("123", "nikoloko", "hashed_pwd", UserRole.USER, [])
    storage.save_user(user1)
    user2 = User("1234", "catima", "hashed_pwd", UserRole.USER, [])
    storage.save_user(user2)

    banana_crop_type = CropType(
        "123", "Cultivo de Bananas", 27, 5.83, 12, 360, 0.75, 50
    )
    storage.save_crop_type(banana_crop_type)

    now = datetime.now()
    crop1 = Crop("c1", "Cultivo de Bananas", "123", "123", now, now, [], True)
    storage.save_crop(crop1)
    crop2 = Crop("c2", "Cultivo de Bananas #2", "1234", "123", now, now, [], True)
    storage.save_crop(crop2)

    user1_crops = storage.get_crops_by_user(user1.id)

    assert len(user1_crops) == 1
    assert user1_crops[0].id == crop1.id
    assert user1_crops[0].name == crop1.name


"""
Method created to see the operation of get_crops_by_crop_type
function.
"""


def test_get_crops_by_type_returns_only_crops_of_that_type(tmp_path):
    temp_path = tmp_path / "test_db.json"
    storage = JSONStorage(temp_path)

    user1 = User("123", "nikoloko", "hashed_pwd", UserRole.USER, [])
    storage.save_user(user1)

    banana_crop_type = CropType(
        "123", "Cultivo de Bananas", 27, 5.83, 12, 360, 0.75, 50
    )
    storage.save_crop_type(banana_crop_type)
    apple_crop_type = CropType(
        "1234", "Cultivo de Manzanas", 21.5, 4, 9, 145, 2.25, 200
    )
    storage.save_crop_type(apple_crop_type)

    now = datetime.now()
    crop1 = Crop("c1", "Cultivo de Bananas", "123", "123", now, now, [], True)
    crop2 = Crop("c2", "Cultivo de Manzanas", "123", "1234", now, now, [], True)
    storage.save_crop(crop1)
    storage.save_crop(crop2)

    banana_crops = storage.get_crops_by_type("123")
    apple_crops = storage.get_crops_by_type("1234")
    assert len(banana_crops) == 1
    assert len(apple_crops) == 1
    assert banana_crops[0].id == crop1.id
    assert apple_crops[0].id == crop2.id
    assert banana_crops[0].name == crop1.name
    assert apple_crops[0].name == crop2.name


"""
Method created to see the operation of get_active_crops
function.
"""


def test_get_active_crops_only_returns_active_crops(tmp_path):
    temp_path = tmp_path / "test_db.json"
    storage = JSONStorage(temp_path)

    user = User("123", "nikoloko", "hashed_pwd", UserRole.USER, [])
    storage.save_user(user)

    banana_crop_type = CropType(
        "123", "Cultivo de Bananas", 27, 5.83, 12, 360, 0.75, 50
    )
    storage.save_crop_type(banana_crop_type)

    now = datetime.now()
    crop1 = Crop("c1", "Cultivo de Bananas", "123", "123", now, now, [], False)
    storage.save_crop(crop1)
    crop2 = Crop("c2", "Cultivo de Bananas #2", "123", "123", now, now, [], True)
    storage.save_crop(crop2)
    crop3 = Crop("c3", "Cultivo de Bananas #3", "123", "123", now, now, [], True)
    storage.save_crop(crop3)

    active_crops = storage.get_active_crops()
    active_ids = [crop.id for crop in active_crops]
    assert len(active_crops) == 2
    assert crop1.id not in active_ids
    assert crop2.id in active_ids
    assert crop3.id in active_ids


"""
Test created to supervise the operations of get_crop_type
and save_crop_type methods.
"""


def test_save_and_get_crop_types(tmp_path):
    temp_path = tmp_path / "test_db.json"
    storage = JSONStorage(temp_path)

    banana_crop_type = CropType(
        "123", "Cultivo de Bananas", 27, 5.83, 12, 360, 0.75, 50
    )
    storage.save_crop_type(banana_crop_type)

    crop_types = storage.get_crop_types()
    assert len(crop_types) == 1
    assert crop_types[0].id == banana_crop_type.id
    assert crop_types[0].name == banana_crop_type.name


"""
Method created to validate the update of a crop type
that already exists, instead of making a new one with 
the same ID.
"""


def test_save_crop_type_updates_instead_of_duplicate(tmp_path):
    temp_path = tmp_path / "test_db.json"
    storage = JSONStorage(temp_path)

    banana_crop_type = CropType(
        "123", "Cultivo de Bananas", 27, 5.83, 12, 360, 0.75, 50
    )
    storage.save_crop_type(banana_crop_type)
    new_crop_type = CropType("123", "Cultivo de Bananas", 28, 5.83, 12, 360, 0.75, 50)
    storage.save_crop_type(new_crop_type)

    crop_types_created = storage.get_crop_types()
    assert len(crop_types_created) == 1
    assert crop_types_created[0].id == new_crop_type.id
    assert crop_types_created[0].optimal_temp == new_crop_type.optimal_temp


"""
Method created to see if the delete_crop_type method works;
eliminating the crop type from the DataBase.
"""


def test_delete_crop_type_removes_from_storage(tmp_path):
    temp_path = tmp_path / "test_db.json"
    storage = JSONStorage(temp_path)

    banana_crop_type = CropType(
        "123", "Cultivo de Bananas", 27, 5.83, 12, 360, 0.75, 50
    )
    storage.save_crop_type(banana_crop_type)
    apple_crop_type = CropType(
        "1234", "Cultivo de Manzanas", 21.5, 4, 9, 145, 2.25, 200
    )
    storage.save_crop_type(apple_crop_type)

    crop_types = storage.get_crop_types()
    assert len(crop_types) == 2
    assert crop_types[0].id == banana_crop_type.id
    assert crop_types[1].id == apple_crop_type.id

    storage.delete_crop_type(banana_crop_type.id)
    updated_crop_types = storage.get_crop_types()
    assert len(updated_crop_types) == 1
    assert updated_crop_types[0].id == apple_crop_type.id
    assert updated_crop_types[0].name == apple_crop_type.name


"""
Method created to see the operation of the get_crop_type_by_id function.
"""


def test_get_crop_type_by_id_works_and_returns_none_if_not_found(tmp_path):
    temp_path = tmp_path / "test_db.json"
    storage = JSONStorage(temp_path)

    banana_crop_type = CropType(
        "123", "Cultivo de Bananas", 27, 5.83, 12, 360, 0.75, 50
    )
    storage.save_crop_type(banana_crop_type)

    crop_type_in_db = storage.get_crop_type_by_id(banana_crop_type.id)
    assert crop_type_in_db is not None
    assert crop_type_in_db.id == banana_crop_type.id
    assert crop_type_in_db.name == banana_crop_type.name
    assert storage.get_crop_type_by_id("4567") is None


"""
Method created to see the operation of the get_crop_type_by_name function.
"""


def test_get_crop_type_by_name_works_and_returns_none_if_not_found(tmp_path):
    temp_path = tmp_path / "test_db.json"
    storage = JSONStorage(temp_path)

    banana_crop_type = CropType(
        "123", "Cultivo de Bananas", 27, 5.83, 12, 360, 0.75, 50
    )
    storage.save_crop_type(banana_crop_type)

    crop_type_in_db = storage.get_crop_type_by_name(banana_crop_type.name)
    assert crop_type_in_db is not None
    assert crop_type_in_db.id == banana_crop_type.id
    assert crop_type_in_db.name == banana_crop_type.name
    assert storage.get_crop_type_by_name("Cultivo de Manzanas") is None


"""
Multiple operations (save, update, delete) should maintain
consistent data in storage.
"""


def test_storage_maintains_data_integrity_after_multiple_ops(tmp_path):
    db_file = tmp_path / "test_db.json"
    storage = JSONStorage(db_file)

    user1 = User("123", "nico", "hash1", UserRole.USER, crop_ids=[])
    storage.save_user(user1)
    user2 = User("1234", "catima", "hash2", UserRole.ADMIN, crop_ids=[])
    storage.save_user(user2)

    updated_user1 = User("123", "nicolas", "hash1_updated", UserRole.USER, crop_ids=[])
    storage.save_user(updated_user1)

    banana_crop_type = CropType(
        "123", "Cultivo de Bananas", 27, 5.83, 12, 360, 0.75, 50
    )
    storage.save_crop_type(banana_crop_type)

    storage.delete_user("1234")
    users = storage.get_users()
    crop_types = storage.get_crop_types()

    assert len(users) == 1
    assert users[0].id == "123"
    assert users[0].username == "nicolas"
    assert users[0].password_hash == "hash1_updated"

    assert len(crop_types) == 1
    assert crop_types[0].id == "123"
    assert crop_types[0].name == "Cultivo de Bananas"
