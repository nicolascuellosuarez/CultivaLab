import json
from typing import Protocol
from .models import User, Crop, CropType, UserRole, DailyCondition
from pathlib import Path
from dataclasses import asdict
from datetime import datetime

"""
Database class created as a Protocol in order to use SOLID
principles; with this, the Service logic does not depends
on the JSON implementation; if later, a connection with Supa -
Base is created, it will be easier to adapt the contract.
"""


class Database(Protocol):
    def read(self) -> dict[str, list]: ...
    def save(self, data: dict = {}) -> None: ...
    def get_users(self) -> list[User]: ...
    def get_user_by_id(self, user_id: str) -> User | None: ...
    def get_user_by_username(self, username: str) -> User | None: ...
    def save_user(self, user: User) -> None: ...
    def delete_user(self, user_id: str) -> None: ...
    def get_crops(self) -> list[Crop]: ...
    def get_crop_by_id(self, crop_id: str) -> Crop | None: ...
    def get_crops_by_user(self, user_id: str) -> list[Crop]: ...
    def get_crops_by_type(self, crop_type_id: str) -> list[Crop]: ...
    def get_active_crops(self) -> list[Crop]: ...
    def save_crop(self, crop: Crop) -> None: ...
    def delete_crop(self, crop_id: str) -> None: ...
    def get_crop_types(self) -> list[CropType]: ...
    def get_crop_type_by_id(self, crop_type_id: str) -> CropType | None: ...
    def get_crop_type_by_name(self, name: str) -> CropType | None: ...
    def save_crop_type(self, crop_type: CropType) -> None: ...
    def delete_crop_type(self, crop_type_id: str) -> None: ...
    def clear_all_data(self) -> None: ...


"""
JSONStorage class for the implementation of the logic of each
method on the Protocol for it to work on the current database.
"""


class JSONStorage:
    """
    __init__ method with a filepath parameter (Path type), to
    create the path as an attribute for all methods.
    """

    def __init__(self, filepath: str | Path = "data/database.json") -> None:
        self.filepath: Path = Path(filepath)

    """
    A read method created to read the DataBase when needed.
    """

    def read(self) -> dict[str, list]:
        # If the filepath does not exists, the program returns a completely empty dictionary.
        if not self.filepath.exists():
            return {"users": [], "crops": [], "crop_types": []}

        with open(self.filepath, "r") as f:  # The file is opened in reading mode.
            db = json.load(f)  # The json.load() method is used to charge it.
        # Returns the dictionary with the keys and values.
        return {
            "users": db.get("users", []),
            "crops": db.get("crops", []),
            "crop_types": db.get("crop_types", []),
        }

    """
    A save method, created to save the DataBase every time 
    changes are made.
    """

    def save(self, data: dict[str, list]) -> None:
        with open(self.filepath, "w") as f:  # Opens the file in write method.
            json.dump(
                data, f, indent=4, ensure_ascii=False
            )  # Dumps it in a dictionary called data.

    """
    A get users method, to read all the users registered in DB.
    """

    def get_users(self) -> list[User]:
        users = self.read().get(
            "users", []
        )  # Creates a users list with the current Users registered in the DB.
        users_list = []  # Another list, to show the users registered.

        for user in users:
            user_data = user.copy()
            user_data["role"] = UserRole(
                user["role"]
            )  # User Role data type stablished.
            users_list.append(
                User(**user_data)
            )  # Appending it in the list and unpacking the dict to create the object.

        return users_list

    """
    A search method, called get user by id, where the Admin can search and
    get the information about a specific user by searching it by its ID.
    """

    def get_user_by_id(self, user_id: str) -> User | None:
        users = self.read().get(
            "users", []
        )  # Creates a users list with the current Users registered in the DB.

        for user in users:  # Searchs in every position of the list.
            if user["id"] == user_id:  # If the ID of an object equals the parameter:
                user_data = user.copy()  # User data is a copy of the user info.
                user_data["role"] = UserRole(
                    user["role"]
                )  # The user role is stablished as an UserRole type.
                return User(
                    **user_data
                )  # The user_data is unpackaged and showed as an User object.
        return None

    """
    A search method, called get user by username, where the Admin can search and
    get the information about a specific user by searching it by its username.
    """

    def get_user_by_username(self, username: str) -> User | None:
        users = self.read().get("users", [])

        for user in users:
            if (
                user["username"] == username
            ):  # If the username of an entry equals the parameter:
                user_data = user.copy()  # User data is a copy of the user info.
                user_data["role"] = UserRole(user["role"])
                return User(**user_data)
        return None

    """
    A save user method that works receiving an User object in the parameter,
    and searchs in the user list of the DB; If the user already exists,
    it overrides it, if not, then it adds it to the DB.
    """

    def save_user(self, user: User) -> None:
        data = self.read()  # Calling the dict with the registers.
        users = data["users"]
        user_dict = asdict(user)  # Transforming the object into a dictionary.
        user_dict["role"] = (
            user.role.value
        )  # Transforming the UserRole type of the dictionary into an str.

        for i, u in enumerate(users):  # Creating an index and touring the dict.
            if (
                user_dict["id"] == u["id"]
            ):  # If the parameter's ID equals the ID of an entry:
                users[i] = user_dict  # The entry is overrided with the object's data.
                self.save(data)  # Saving the operation.
                return

        users.append(user_dict)  # The object in the parameter is added to the list.
        self.save(data)  # Saving the operation.

    """
    A delete user method, that receives an ID in the parameter.
    It toures the users list in the DB, if the user id equals the ID,
    then it's deleted.
    """

    def delete_user(self, user_id: str) -> None:
        data = self.read()
        users = data["users"]

        for i, u in enumerate(users):
            if u["id"] == user_id:
                users.pop(i)  # We pop the position in DB.
                self.save(data)
                return

    """
    A get crops method, used to get all crops registered in DB.
    """

    def get_crops(self) -> list[Crop]:
        crops = self.read().get("crops", [])
        crops_list = []  # Same algorithm as get_users method

        for crop in crops:
            crop_data = crop.copy()
            conditions = crop_data.get("conditions", [])
            conditions_list = []  # List prepared for conditions conversion

            for condition in conditions:
                conditions_list.append(
                    DailyCondition(**condition)
                )  # Appending the conditions in a DailyCondition Type for the object.

            crop_data["start_date"] = datetime.fromisoformat(crop_data["start_date"])
            crop_data["last_sim_date"] = datetime.fromisoformat(
                crop_data["last_sim_date"]
            )
            # Date fields converted to datetime type from the ISO format.

            crop_data["conditions"] = (
                conditions_list  # Conditions in crop_data is conditions_list with the conditions in the right type.
            )
            crops_list.append(Crop(**crop_data))

        return crops_list

    """
    Get crop by id method created to find a crop searching by its ID.
    """

    def get_crop_by_id(self, crop_id: str) -> Crop | None:
        crops = self.read().get("crops", [])  # Init the crop list.

        for crop in crops:
            if crop["id"] == crop_id:  # If the crop id is the same as the parameter:
                crop_data = crop.copy()  # Creates a copy of the crop.
                conditions = crop_data.get("conditions", [])
                conditions_list = []  # Init a new conditions list for conditions in DailyCondition type.

                for condition in conditions:
                    conditions_list.append(
                        DailyCondition(**condition)
                    )  # Unpackage the conditions and append it on conditionslist in DailyCondition type.

                crop_data["start_date"] = datetime.fromisoformat(
                    crop_data["start_date"]
                )
                crop_data["last_sim_date"] = datetime.fromisoformat(
                    crop_data["last_sim_date"]
                )
                # Adjust the date fields to datetime type

                crop_data["conditions"] = conditions_list
                return Crop(**crop_data)  # Returning the crop searched.
        return None

    """
    Get crop by user method created to find the crops created by an user
    using their ID.
    """

    def get_crops_by_user(self, user_id: str) -> list[Crop]:
        crops = self.read().get("crops", [])
        user_crops = []  # Init a new list where the crops created by the user will be added.

        for crop in crops:
            if crop["user_id"] == user_id:
                crop_data = crop.copy()  # Using the same algorithm as last method.

                conditions = crop_data.get("conditions", [])
                conditions_list = []
                for condition in conditions:
                    conditions_list.append(
                        DailyCondition(**condition)
                    )  # Appending the conditions in the right format.
                crop_data["conditions"] = conditions_list

                crop_data["start_date"] = datetime.fromisoformat(
                    crop_data["start_date"]
                )
                crop_data["last_sim_date"] = datetime.fromisoformat(
                    crop_data["last_sim_date"]
                )

                new_crop = Crop(
                    **crop_data
                )  # Creating a new crop object for each crop that is created by the user.
                user_crops.append(new_crop)  # Appending it to our list.
        return user_crops  # Returning the list.

    """
    Get crop by user method created to find same type crops.
    """

    def get_crops_by_type(self, crop_type_id: str) -> list[Crop]:
        crops = self.read().get("crops", [])
        crops_in_crop_type = []

        for crop in crops:
            if crop["crop_type_id"] == crop_type_id:
                crop_data = crop.copy()

                conditions = crop_data.get("conditions", [])
                conditions_list = []
                for condition in conditions:
                    conditions_list.append(DailyCondition(**condition))
                crop_data["conditions"] = conditions_list

                crop_data["start_date"] = datetime.fromisoformat(
                    crop_data["start_date"]
                )
                crop_data["last_sim_date"] = datetime.fromisoformat(
                    crop_data["last_sim_date"]
                )

                new_crop = Crop(**crop_data)
                crops_in_crop_type.append(
                    new_crop
                )  # Using the same algorithm as before.
        return crops_in_crop_type  # Returning the list.

    """
    Get crop by user method created to find active crops.
    """

    def get_active_crops(self) -> list[Crop]:
        crops = self.read().get("crops", [])
        active_crops = []

        for crop in crops:
            if crop["active"]:  # If crop is active (active attribute equals True):
                crop_data = crop.copy()

                conditions = crop_data.get("conditions", [])
                conditions_list = []
                for condition in conditions:
                    conditions_list.append(DailyCondition(**condition))
                crop_data["conditions"] = conditions_list

                crop_data["start_date"] = datetime.fromisoformat(
                    crop_data["start_date"]
                )
                crop_data["last_sim_date"] = datetime.fromisoformat(
                    crop_data["last_sim_date"]
                )

                new_crop = Crop(**crop_data)
                active_crops.append(new_crop)  # Appending active crops.
        return active_crops  # Returning crops that are active.

    """
    Save crop method created to save a crop in the list if it doesn't exists yet.
    If it already exists in the DB, the method overwrites the past information.
    """

    def save_crop(self, crop: Crop) -> None:
        data = self.read()
        crops = data["crops"]
        crop_dict = asdict(
            crop
        )  # The object is created as a dictionary, the daily conditions are set to dictionaries too.

        crop_dict["start_date"] = crop.start_date.isoformat()
        crop_dict["last_sim_date"] = crop.last_sim_date.isoformat()
        # The format of dates is in ISO format now; JSON does not understand datetime type.

        for i, c in enumerate(crops):
            if c["id"] == crop_dict["id"]:
                crops[i] = crop_dict
                self.save(data)
                return  # Overwriting crop if it already exists

        crops.append(crop_dict)  # Appending it on the dictionary
        self.save(data)  # Saving the information.

    """
    Delete crop method created to delete a crop based on its ID.
    """

    def delete_crop(self, crop_id: str) -> None:
        data = self.read()
        crops = data["crops"]

        for i, c in enumerate(crops):
            if c["id"] == crop_id:
                crops.pop(i)
                self.save(data)
                return  # Deletes the crop if it finds a crop with the same ID.
