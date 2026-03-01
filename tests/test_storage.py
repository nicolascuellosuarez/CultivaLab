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

"""
Method created to validate the update of a user that already exists,
instead of making a new one with the same ID.
"""
def test_save_user_updates_existing_instead_of_duplicate(tmp_path):
    temp_file = tmp_path / "test_db.json"
    storage = JSONStorage(temp_file)

    user = User("123",
                "nikoloko",
                "hashed_pwd",
                UserRole.USER,
                []
            )
    storage.save_user(user)

    evaluating_user = User("123",
                "nikoloko07",
                "hashed_pwd",
                UserRole.USER,
                []
            )
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

    user1 = User("123", 
                 "nikoloko", 
                 "hashed_pwd", 
                 UserRole.USER, 
                 [])
    storage.save_user(user1)
    
    user2 = User("1234", 
                 "catima", 
                 "hashed_pwd", 
                 UserRole.USER, 
                 [])
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
def test_get_user_by_id_works_and_returns_none_if_not_Found(tmp_path):
    temp_path = tmp_path / "test_db.json"
    storage = JSONStorage(temp_path)

    user1 = User("123", 
                 "nikoloko", 
                 "hashed_pwd", 
                 UserRole.USER, 
                 [])
    storage.save_user(user1)

    user_in_db = storage.get_user_by_id(user1.id)
    assert user_in_db is not None
    assert user_in_db.id == user1.id
    assert user_in_db.username == user1.username 
    assert storage.get_user_by_id("4567") == None

"""
Method created to see the operation of the get_user_by_username
function.
"""
def test_get_user_by_username_works_and_returns_none_if_not_Found(tmp_path):
    temp_path = tmp_path / "test_db.json"
    storage = JSONStorage(temp_path)

    user1 = User("123", 
                 "nikoloko", 
                 "hashed_pwd", 
                 UserRole.USER, 
                 [])
    storage.save_user(user1)

    user_in_db = storage.get_user_by_username(user1.username)
    assert user_in_db is not None
    assert user_in_db.id == user1.id
    assert user_in_db.username == user1.username 
    assert storage.get_user_by_username("catima") is None


    
