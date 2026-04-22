from src.cultiva_lab.storage import JSONStorage
from src.cultiva_lab.models import User, Crop, CropType, UserRole
from datetime import datetime

"""
The Storage tests for CultivaLab; here, the focus
will be on proving the operation of JSONStorage
methods implementations from a Protocol.
"""


def create_valid_crop_type(
    id: str,
    name: str,
    minimum_temp: float,
    maximum_temp: float,
    needed_water: float,
    needed_light: float,
    days_cycle: int,
    initial_biomass: float,
    potential_performance: float,
    **kwargs,
) -> CropType:
    """
    Crea un CropType con valores de agua que cumplen:
    water_wilting < water_opt_low < needed_water < water_opt_high < water_capacity
    """
    water_wilting = kwargs.get("water_wilting", 30.0)
    water_opt_low = kwargs.get("water_opt_low", 60.0)
    water_opt_high = kwargs.get("water_opt_high", 150.0)
    water_capacity = kwargs.get("water_capacity", 200.0)
    # Asegurar orden correcto
    water_wilting = min(water_wilting, water_opt_low - 1)
    water_opt_low = max(water_opt_low, water_wilting + 1)
    needed_water = max(needed_water, water_opt_low + 1)
    water_opt_high = max(water_opt_high, needed_water + 1)
    water_capacity = max(water_capacity, water_opt_high + 1)

    return CropType(
        id=id,
        name=name,
        minimum_temp=minimum_temp,
        maximum_temp=maximum_temp,
        cold_sensibility=kwargs.get("cold_sensibility", 0.5),
        heat_sensibility=kwargs.get("heat_sensibility", 0.5),
        cold_factor=kwargs.get("cold_factor", 0.1),
        heat_factor=kwargs.get("heat_factor", 0.1),
        temperature_curve_length=kwargs.get("temperature_curve_length", 5.0),
        water_wilting=water_wilting,
        water_opt_low=water_opt_low,
        needed_water=needed_water,
        water_opt_high=water_opt_high,
        water_capacity=water_capacity,
        water_sensibility=kwargs.get("water_sensibility", 0.3),
        water_stress_constant=kwargs.get("water_stress_constant", 0.4),
        needed_light=needed_light,
        needed_light_max=kwargs.get("needed_light_max", needed_light + 4),
        light_sensibility=kwargs.get("light_sensibility", 1.0),
        light_km=kwargs.get("light_km", needed_light * 0.5),
        light_sigma=kwargs.get("light_sigma", 2.0),
        phenological_initial_coefficient=kwargs.get(
            "phenological_initial_coefficient", 0.4
        ),
        phenological_mid_coefficient=kwargs.get("phenological_mid_coefficient", 1.1),
        phenological_end_coefficient=kwargs.get("phenological_end_coefficient", 0.6),
        days_cycle=days_cycle,
        photosyntesis_max_rate=kwargs.get("photosyntesis_max_rate", 0.22),
        breathing_base_rate=kwargs.get("breathing_base_rate", 0.05),
        theta=kwargs.get("theta", 1.5),
        consecutive_stress_days_limit=kwargs.get("consecutive_stress_days_limit", 5),
        theta_coefficient=kwargs.get("theta_coefficient", 0.0023),
        initial_biomass=initial_biomass,
        potential_performance=potential_performance,
    )


# ------------------------------------------------------------
# Tests
# ------------------------------------------------------------


def test_read_returns_empty_dict_when_file_dont_exists(tmp_path):
    """
    If the file does not exist yet, storage.read() should
    return the expected initial structure of the DB.
    """
    temp_file = tmp_path / "test_db.json"
    assert not temp_file.exists()

    storage = JSONStorage(temp_file)
    result = storage.read()
    assert isinstance(result, dict)
    assert result == {"users": [], "crops": [], "crop_types": []}


def test_save_and_get_users(tmp_path):
    """
    Method created to see if the DataBase, effectively,
    works; makes a first user and proves the registration.
    """
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


def test_save_user_updates_existing_instead_of_duplicate(tmp_path):
    """
    Method created to validate the update of a user that already exists,
    instead of making a new one with the same ID.
    """
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


def test_delete_user_removes_from_storage(tmp_path):
    """
    Method created to see if the delete_user method works;
    eliminating the user from the DataBase.
    """
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


def test_get_user_by_id_works_and_returns_none_if_not_found(tmp_path):
    """
    Method created to see the operation of the get_user_by_id function.
    """
    temp_path = tmp_path / "test_db.json"
    storage = JSONStorage(temp_path)

    user1 = User("123", "nikoloko", "hashed_pwd", UserRole.USER, [])
    storage.save_user(user1)

    user_in_db = storage.get_user_by_id(user1.id)
    assert user_in_db is not None
    assert user_in_db.id == user1.id
    assert user_in_db.username == user1.username
    assert storage.get_user_by_id("4567") is None


def test_get_user_by_username_works_and_returns_none_if_not_found(tmp_path):
    """
    Method created to see the operation of the get_user_by_username
    function.
    """
    temp_path = tmp_path / "test_db.json"
    storage = JSONStorage(temp_path)

    user1 = User("123", "nikoloko", "hashed_pwd", UserRole.USER, [])
    storage.save_user(user1)

    user_in_db = storage.get_user_by_username(user1.username)
    assert user_in_db is not None
    assert user_in_db.id == user1.id
    assert user_in_db.username == user1.username
    assert storage.get_user_by_username("catima") is None


def test_save_and_get_crops(tmp_path):
    """
    Test created to see the operation of the save and get crops methods
    in storage.
    """
    temp_path = tmp_path / "test_db.json"
    storage = JSONStorage(temp_path)

    user1 = User("123", "nikoloko", "hashed_pwd", UserRole.USER, [])
    storage.save_user(user1)

    banana_crop_type = create_valid_crop_type(
        id="123",
        name="Cultivo de Bananas",
        minimum_temp=22.0,
        maximum_temp=32.0,
        needed_water=100.0,
        needed_light=12.0,
        days_cycle=360,
        initial_biomass=0.75,
        potential_performance=50.0,
    )
    storage.save_crop_type(banana_crop_type)

    now = datetime.now()
    crop = Crop(
        id="123",
        name="Cultivo de Bananas",
        user_id="123",
        crop_type_id="123",
        start_date=now,
        last_sim_date=now,
        conditions=[],
        active=True,
        water_stored=0.0,
        consecutive_stress_days=0,
        current_phase="Fase Inicial",
    )
    storage.save_crop(crop)

    crops = storage.get_crops()
    assert len(crops) == 1
    assert crops[0].id == crop.id
    assert crops[0].name == crop.name


def test_save_crop_updates_existing_instead_of_duplicate(tmp_path):
    """
    Method created to supervise the correct operation save_crop method
    in storage, not only saving new crops, also editing existing ones
    if the ID already exists.
    """
    temp_file = tmp_path / "test_db.json"
    storage = JSONStorage(temp_file)

    user1 = User("123", "nikoloko", "hashed_pwd", UserRole.USER, [])
    storage.save_user(user1)

    banana_crop_type = create_valid_crop_type(
        id="123",
        name="Cultivo de Bananas",
        minimum_temp=22.0,
        maximum_temp=32.0,
        needed_water=100.0,
        needed_light=12.0,
        days_cycle=360,
        initial_biomass=0.75,
        potential_performance=50.0,
    )
    storage.save_crop_type(banana_crop_type)

    now = datetime.now()
    crop = Crop(
        id="123",
        name="Cultivo de Bananas",
        user_id="123",
        crop_type_id="123",
        start_date=now,
        last_sim_date=now,
        conditions=[],
        active=True,
        water_stored=0.0,
        consecutive_stress_days=0,
        current_phase="Fase Inicial",
    )
    storage.save_crop(crop)

    evaluating_crop = Crop(
        id="123",
        name="Cultivo de Bananas #2",
        user_id="123",
        crop_type_id="123",
        start_date=now,
        last_sim_date=now,
        conditions=[],
        active=True,
        water_stored=0.0,
        consecutive_stress_days=0,
        current_phase="Fase Inicial",
    )
    storage.save_crop(evaluating_crop)

    crops = storage.get_crops()
    assert len(crops) == 1
    assert crops[0].id == evaluating_crop.id
    assert crops[0].name == evaluating_crop.name
    assert crops[0].user_id == evaluating_crop.user_id


def test_delete_crop_removes_from_storage(tmp_path):
    """
    Method created to see if the delete_crop method works;
    eliminating the crop from the DataBase.
    """
    temp_file = tmp_path / "test_db.json"
    storage = JSONStorage(temp_file)

    user1 = User("123", "nikoloko", "hashed_pwd", UserRole.USER, [])
    storage.save_user(user1)

    banana_crop_type = create_valid_crop_type(
        id="123",
        name="Cultivo de Bananas",
        minimum_temp=22.0,
        maximum_temp=32.0,
        needed_water=100.0,
        needed_light=12.0,
        days_cycle=360,
        initial_biomass=0.75,
        potential_performance=50.0,
    )
    storage.save_crop_type(banana_crop_type)

    now = datetime.now()
    crop1 = Crop(
        id="123",
        name="Cultivo de Bananas",
        user_id="123",
        crop_type_id="123",
        start_date=now,
        last_sim_date=now,
        conditions=[],
        active=True,
        water_stored=0.0,
        consecutive_stress_days=0,
        current_phase="Fase Inicial",
    )
    storage.save_crop(crop1)

    crop2 = Crop(
        id="1234",
        name="Cultivo de Bananas #2",
        user_id="123",
        crop_type_id="123",
        start_date=now,
        last_sim_date=now,
        conditions=[],
        active=True,
        water_stored=0.0,
        consecutive_stress_days=0,
        current_phase="Fase Inicial",
    )
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


def test_get_crop_by_id_works_and_returns_none_if_not_found(tmp_path):
    """
    Method created to see the operation of the get_crop_by_id function.
    """
    temp_path = tmp_path / "test_db.json"
    storage = JSONStorage(temp_path)

    user1 = User("123", "nikoloko", "hashed_pwd", UserRole.USER, [])
    storage.save_user(user1)

    banana_crop_type = create_valid_crop_type(
        id="123",
        name="Cultivo de Bananas",
        minimum_temp=22.0,
        maximum_temp=32.0,
        needed_water=100.0,
        needed_light=12.0,
        days_cycle=360,
        initial_biomass=0.75,
        potential_performance=50.0,
    )
    storage.save_crop_type(banana_crop_type)

    now = datetime.now()
    crop = Crop(
        id="123",
        name="Cultivo de Bananas",
        user_id="123",
        crop_type_id="123",
        start_date=now,
        last_sim_date=now,
        conditions=[],
        active=True,
        water_stored=0.0,
        consecutive_stress_days=0,
        current_phase="Fase Inicial",
    )
    storage.save_crop(crop)

    crop_in_db = storage.get_crop_by_id(crop.id)
    assert crop_in_db is not None
    assert crop_in_db.id == crop.id
    assert crop_in_db.name == crop.name
    assert storage.get_crop_by_id("4567") is None


def test_get_crops_by_user_returns_only_that_user_crops(tmp_path):
    """
    Method created to see the operation of the get_crop_by_user
    function.
    """
    temp_path = tmp_path / "test_db.json"
    storage = JSONStorage(temp_path)

    user1 = User("123", "nikoloko", "hashed_pwd", UserRole.USER, [])
    storage.save_user(user1)
    user2 = User("1234", "catima", "hashed_pwd", UserRole.USER, [])
    storage.save_user(user2)

    banana_crop_type = create_valid_crop_type(
        id="123",
        name="Cultivo de Bananas",
        minimum_temp=22.0,
        maximum_temp=32.0,
        needed_water=100.0,
        needed_light=12.0,
        days_cycle=360,
        initial_biomass=0.75,
        potential_performance=50.0,
    )
    storage.save_crop_type(banana_crop_type)

    now = datetime.now()
    crop1 = Crop(
        id="c1",
        name="Cultivo de Bananas",
        user_id="123",
        crop_type_id="123",
        start_date=now,
        last_sim_date=now,
        conditions=[],
        active=True,
        water_stored=0.0,
        consecutive_stress_days=0,
        current_phase="Fase Inicial",
    )
    storage.save_crop(crop1)

    crop2 = Crop(
        id="c2",
        name="Cultivo de Bananas #2",
        user_id="1234",
        crop_type_id="123",
        start_date=now,
        last_sim_date=now,
        conditions=[],
        active=True,
        water_stored=0.0,
        consecutive_stress_days=0,
        current_phase="Fase Inicial",
    )
    storage.save_crop(crop2)

    user1_crops = storage.get_crops_by_user(user1.id)
    assert len(user1_crops) == 1
    assert user1_crops[0].id == crop1.id
    assert user1_crops[0].name == crop1.name


def test_get_crops_by_type_returns_only_crops_of_that_type(tmp_path):
    """
    Method created to see the operation of get_crops_by_crop_type
    function.
    """
    temp_path = tmp_path / "test_db.json"
    storage = JSONStorage(temp_path)

    user1 = User("123", "nikoloko", "hashed_pwd", UserRole.USER, [])
    storage.save_user(user1)

    banana_crop_type = create_valid_crop_type(
        id="123",
        name="Cultivo de Bananas",
        minimum_temp=22.0,
        maximum_temp=32.0,
        needed_water=100.0,
        needed_light=12.0,
        days_cycle=360,
        initial_biomass=0.75,
        potential_performance=50.0,
    )
    storage.save_crop_type(banana_crop_type)

    apple_crop_type = create_valid_crop_type(
        id="1234",
        name="Cultivo de Manzanas",
        minimum_temp=14.0,
        maximum_temp=28.0,
        needed_water=80.0,
        needed_light=9.0,
        days_cycle=200,
        initial_biomass=0.65,
        potential_performance=45.0,
    )
    storage.save_crop_type(apple_crop_type)

    now = datetime.now()
    crop1 = Crop(
        id="c1",
        name="Cultivo de Bananas",
        user_id="123",
        crop_type_id="123",
        start_date=now,
        last_sim_date=now,
        conditions=[],
        active=True,
        water_stored=0.0,
        consecutive_stress_days=0,
        current_phase="Fase Inicial",
    )
    storage.save_crop(crop1)

    crop2 = Crop(
        id="c2",
        name="Cultivo de Manzanas",
        user_id="123",
        crop_type_id="1234",
        start_date=now,
        last_sim_date=now,
        conditions=[],
        active=True,
        water_stored=0.0,
        consecutive_stress_days=0,
        current_phase="Fase Inicial",
    )
    storage.save_crop(crop2)

    banana_crops = storage.get_crops_by_type("123")
    apple_crops = storage.get_crops_by_type("1234")
    assert len(banana_crops) == 1
    assert len(apple_crops) == 1
    assert banana_crops[0].id == crop1.id
    assert apple_crops[0].id == crop2.id
    assert banana_crops[0].name == crop1.name
    assert apple_crops[0].name == crop2.name


def test_get_active_crops_only_returns_active_crops(tmp_path):
    """
    Method created to see the operation of get_active_crops
    function.
    """
    temp_path = tmp_path / "test_db.json"
    storage = JSONStorage(temp_path)

    user = User("123", "nikoloko", "hashed_pwd", UserRole.USER, [])
    storage.save_user(user)

    banana_crop_type = create_valid_crop_type(
        id="123",
        name="Cultivo de Bananas",
        minimum_temp=22.0,
        maximum_temp=32.0,
        needed_water=100.0,
        needed_light=12.0,
        days_cycle=360,
        initial_biomass=0.75,
        potential_performance=50.0,
    )
    storage.save_crop_type(banana_crop_type)

    now = datetime.now()
    crop1 = Crop(
        id="c1",
        name="Cultivo de Bananas",
        user_id="123",
        crop_type_id="123",
        start_date=now,
        last_sim_date=now,
        conditions=[],
        active=False,
        water_stored=0.0,
        consecutive_stress_days=0,
        current_phase="Fase Inicial",
    )
    storage.save_crop(crop1)

    crop2 = Crop(
        id="c2",
        name="Cultivo de Bananas #2",
        user_id="123",
        crop_type_id="123",
        start_date=now,
        last_sim_date=now,
        conditions=[],
        active=True,
        water_stored=0.0,
        consecutive_stress_days=0,
        current_phase="Fase Inicial",
    )
    storage.save_crop(crop2)

    crop3 = Crop(
        id="c3",
        name="Cultivo de Bananas #3",
        user_id="123",
        crop_type_id="123",
        start_date=now,
        last_sim_date=now,
        conditions=[],
        active=True,
        water_stored=0.0,
        consecutive_stress_days=0,
        current_phase="Fase Inicial",
    )
    storage.save_crop(crop3)

    active_crops = storage.get_active_crops()
    active_ids = [crop.id for crop in active_crops]
    assert len(active_crops) == 2
    assert crop1.id not in active_ids
    assert crop2.id in active_ids
    assert crop3.id in active_ids


def test_save_and_get_crop_types(tmp_path):
    """
    Test created to supervise the operations of get_crop_type
    and save_crop_type methods.
    """
    temp_path = tmp_path / "test_db.json"
    storage = JSONStorage(temp_path)

    banana_crop_type = create_valid_crop_type(
        id="123",
        name="Cultivo de Bananas",
        minimum_temp=22.0,
        maximum_temp=32.0,
        needed_water=100.0,
        needed_light=12.0,
        days_cycle=360,
        initial_biomass=0.75,
        potential_performance=50.0,
    )
    storage.save_crop_type(banana_crop_type)

    crop_types = storage.get_crop_types()
    assert len(crop_types) == 1
    assert crop_types[0].id == banana_crop_type.id
    assert crop_types[0].name == banana_crop_type.name


def test_save_crop_type_updates_instead_of_duplicate(tmp_path):
    """
    Method created to validate the update of a crop type
    that already exists, instead of making a new one with
    the same ID.
    """
    temp_path = tmp_path / "test_db.json"
    storage = JSONStorage(temp_path)

    banana_crop_type = create_valid_crop_type(
        id="123",
        name="Cultivo de Bananas",
        minimum_temp=22.0,
        maximum_temp=32.0,
        needed_water=100.0,
        needed_light=12.0,
        days_cycle=360,
        initial_biomass=0.75,
        potential_performance=50.0,
    )
    storage.save_crop_type(banana_crop_type)

    new_crop_type = create_valid_crop_type(
        id="123",
        name="Cultivo de Bananas",
        minimum_temp=23.0,
        maximum_temp=33.0,
        needed_water=100.0,
        needed_light=12.0,
        days_cycle=360,
        initial_biomass=0.75,
        potential_performance=50.0,
    )
    storage.save_crop_type(new_crop_type)

    crop_types_created = storage.get_crop_types()
    assert len(crop_types_created) == 1
    assert crop_types_created[0].id == new_crop_type.id
    assert crop_types_created[0].minimum_temp == new_crop_type.minimum_temp


def test_delete_crop_type_removes_from_storage(tmp_path):
    """
    Method created to see if the delete_crop_type method works;
    eliminating the crop type from the DataBase.
    """
    temp_path = tmp_path / "test_db.json"
    storage = JSONStorage(temp_path)

    banana_crop_type = create_valid_crop_type(
        id="123",
        name="Cultivo de Bananas",
        minimum_temp=22.0,
        maximum_temp=32.0,
        needed_water=100.0,
        needed_light=12.0,
        days_cycle=360,
        initial_biomass=0.75,
        potential_performance=50.0,
    )
    storage.save_crop_type(banana_crop_type)

    apple_crop_type = create_valid_crop_type(
        id="1234",
        name="Cultivo de Manzanas",
        minimum_temp=14.0,
        maximum_temp=28.0,
        needed_water=80.0,
        needed_light=9.0,
        days_cycle=200,
        initial_biomass=0.65,
        potential_performance=45.0,
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


def test_get_crop_type_by_id_works_and_returns_none_if_not_found(tmp_path):
    """
    Method created to see the operation of the get_crop_type_by_id function.
    """
    temp_path = tmp_path / "test_db.json"
    storage = JSONStorage(temp_path)

    banana_crop_type = create_valid_crop_type(
        id="123",
        name="Cultivo de Bananas",
        minimum_temp=22.0,
        maximum_temp=32.0,
        needed_water=100.0,
        needed_light=12.0,
        days_cycle=360,
        initial_biomass=0.75,
        potential_performance=50.0,
    )
    storage.save_crop_type(banana_crop_type)

    crop_type_in_db = storage.get_crop_type_by_id(banana_crop_type.id)
    assert crop_type_in_db is not None
    assert crop_type_in_db.id == banana_crop_type.id
    assert crop_type_in_db.name == banana_crop_type.name
    assert storage.get_crop_type_by_id("4567") is None


def test_get_crop_type_by_name_works_and_returns_none_if_not_found(tmp_path):
    """
    Method created to see the operation of the get_crop_type_by_name function.
    """
    temp_path = tmp_path / "test_db.json"
    storage = JSONStorage(temp_path)

    banana_crop_type = create_valid_crop_type(
        id="123",
        name="Cultivo de Bananas",
        minimum_temp=22.0,
        maximum_temp=32.0,
        needed_water=100.0,
        needed_light=12.0,
        days_cycle=360,
        initial_biomass=0.75,
        potential_performance=50.0,
    )
    storage.save_crop_type(banana_crop_type)

    crop_type_in_db = storage.get_crop_type_by_name(banana_crop_type.name)
    assert crop_type_in_db is not None
    assert crop_type_in_db.id == banana_crop_type.id
    assert crop_type_in_db.name == banana_crop_type.name
    assert storage.get_crop_type_by_name("Cultivo de Manzanas") is None


def test_storage_maintains_data_integrity_after_multiple_ops(tmp_path):
    """
    Multiple operations (save, update, delete) should maintain
    consistent data in storage.
    """
    db_file = tmp_path / "test_db.json"
    storage = JSONStorage(db_file)

    user1 = User("123", "nico", "hash1", UserRole.USER, crop_ids=[])
    storage.save_user(user1)
    user2 = User("1234", "catima", "hash2", UserRole.ADMIN, crop_ids=[])
    storage.save_user(user2)

    updated_user1 = User("123", "nicolas", "hash1_updated", UserRole.USER, crop_ids=[])
    storage.save_user(updated_user1)

    banana_crop_type = create_valid_crop_type(
        id="123",
        name="Cultivo de Bananas",
        minimum_temp=22.0,
        maximum_temp=32.0,
        needed_water=100.0,
        needed_light=12.0,
        days_cycle=360,
        initial_biomass=0.75,
        potential_performance=50.0,
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
