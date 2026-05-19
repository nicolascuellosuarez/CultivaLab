import os
from datetime import datetime
from typing import List, Optional
from dotenv import load_dotenv
from supabase import create_client, Client

from .models import User, UserRole, Crop, CropType, DailyCondition
from .exceptions import InvalidInputError

load_dotenv()


class SupabaseStorage:
    """
    SupabaseStorage class created to implement the logic of Database
    using PostgreSQL for the insertion of data in SupaBase.
    """

    def __init__(self) -> None:
        url: str = os.environ.get("SUPABASE_URL")
        key: str = os.environ.get("SUPABASE_KEY")
        if not url or not key:
            raise ValueError(
                "No hay llaves de acceso a Supabase en las variables de entorno."
            )
        self.client: Client = create_client(url, key)

    def read(self) -> dict[str, list]:
        """
        Method not implemented in Supabase, only compatible with JSON type of storage.
        """
        raise NotImplementedError("Método de lectura no implementado para Supabase.")

    def save(self, data: dict[str, list]) -> None:
        """
        Method not implemented in Supabase, only compatible with JSON type of storage.
        """
        raise NotImplementedError("Método de guardado no implementado para Supabase.")

    def get_users(self) -> list[User]:
        """
        Method get_users implemented to get the information of all users in
        DataBase.
        """

        response = self.client.table("users").select("*").execute()
        users = []
        crops_response = (
            self.client.table("crops").select("id").eq("user_id", user.id).execute()
        )
        crop_ids = [crop["id"] for crop in crops_response.data]

        for row in response.data:
            user = User(
                id=row["id"],
                username=row["username"],
                password_hash=row["password_hash"],
                role=UserRole(row["role"]),
                crop_ids=crop_ids,
            )
            users.append(user)

        return users

    def get_user_by_id(self, user_id: str) -> User | None:
        """
        Method get_user_by_id created to get an user from the DataBase by its ID,
        using PostgreSQL syntax.
        """

        response = self.client.table("users").select("*").eq("id", user_id).execute()
        if not response.data:
            return None

        crops_response = (
            self.client.table("crops").select("id").eq("user_id", user_id).execute()
        )
        crop_ids = [crop["id"] for crop in crops_response.data]
        row = response.data[0]
        return User(
            id=row["id"],
            username=row["username"],
            password_hash=row["password_hash"],
            role=UserRole(row["role"]),
            crop_ids=crop_ids,
        )

    def get_user_by_username(self, username: str, user_id: str) -> User | None:
        """
        Method get_user_by_username() created to get the information of an user from the
        DataBase from its username using the PostgreSQL syntax.
        """

        response = (
            self.client.table("users").select("*").eq("username", username).execute()
        )
        if not response.data:
            return None

        row = response.data[0]
        crops_response = (
            self.client.table("crops").select("id").eq("user_id", user_id).execute()
        )
        crop_ids = [crop["id"] for crop in crops_response.data]
        return User(
            id=row["id"],
            username=row["username"],
            password_hash=row["password_hash"],
            role=UserRole(row["role"]),
            crop_ids=crop_ids,
        )

    def save_user(self, user: User) -> None:
        """
        Method save_user() created to save an user's data in the DataBase using PostgreSQL
        syntax.
        """

        data = {
            "id": user.id,
            "username": user.username,
            "password_hash": user.password_hash,
            "role": user.role.value,
        }

        self.client.table("users").upsert(data).execute()

    def delete_user(self, user_id: str) -> None:
        """
        Method delete_user() created to delete an user's data from the DataBase
        using PostgreSQL syntax.
        """

        self.client.table("crops").delete().eq("user_id", user_id).execute()
        self.client.table("users").delete().eq("id", user_id).execute()

    def get_crop_types(self) -> list[CropType]:
        """
        Method get_crop_types() created to get the information of a crop type from
        the DataBase using PostgreSQL syntax.
        """

        response = self.client.table("crop_types").select("*").execute()
        crop_types = []

        for row in response.data:
            crop_type = CropType(
                id=row["id"],
                name=row["name"],
                optimal_temp=row["optimal_temp"],
                minimum_temp=row["minimum_temp"],
                maximum_temp=row["maximum_temp"],
                cold_sensibility=row.get("cold_sensibility", 0.5),
                heat_sensibility=row.get("heat_sensibility", 0.5),
                cold_factor=row.get("cold_factor", 0.1),
                heat_factor=row.get("heat_factor", 0.1),
                temperature_curve_length=row.get("temperature_curve_length", 5.0),
                water_wilting=row.get("water_wilting", 60.0),
                water_opt_low=row.get("water_opt_low", 70.0),
                needed_water=row["needed_water"],
                water_opt_high=row.get("water_opt_high", 100.0),
                water_capacity=row.get("water_capacity", 150.0),
                water_sensibility=row.get("water_sensibility", 1.5),
                water_stress_constant=row.get("water_stress_constant", 0.7),
                needed_light=row["needed_light"],
                needed_light_max=row.get("needed_light_max", 9.0),
                light_sensibility=row.get("light_sensibility", 1.2),
                light_km=row.get("light_km", 3.0),
                light_sigma=row.get("light_sigma", 2.0),
                phenological_initial_coefficient=row.get(
                    "phenological_initial_coefficient", 0.3
                ),
                phenological_mid_coefficient=row.get(
                    "phenological_mid_coefficient", 1.0
                ),
                phenological_end_coefficient=row.get(
                    "phenological_end_coefficient", 0.6
                ),
                days_cycle=row["days_cycle"],
                photosyntesis_max_rate=row["photosyntesis_max_rate"],
                breathing_base_rate=row["breathing_base_rate"],
                theta=row.get("theta", 1.8),
                consecutive_stress_days_limit=row.get(
                    "consecutive_stress_days_limit", 5
                ),
                theta_coefficient=row.get("theta_coefficient", 0.0023),
                initial_biomass=row["initial_biomass"],
                potential_performance=row["potential_performance"],
                activation_energy=row.get("activation_energy"),
            )
            crop_types.append(crop_type)
        return crop_types

    def get_crop_type_by_id(self, crop_type_id: str) -> CropType | None:
        """
        Method get_crop_type_by_id() created to get a Crop Type's information by
        its ID.
        """

        response = (
            self.client.table("crop_types").select("*").eq("id", crop_type_id).execute()
        )
        if not response.data:
            return None
        row = response.data[0]
        crop_type = CropType(
            id=row["id"],
            name=row["name"],
            optimal_temp=row["optimal_temp"],
            minimum_temp=row["minimum_temp"],
            maximum_temp=row["maximum_temp"],
            cold_sensibility=row.get("cold_sensibility", 0.5),
            heat_sensibility=row.get("heat_sensibility", 0.5),
            cold_factor=row.get("cold_factor", 0.1),
            heat_factor=row.get("heat_factor", 0.1),
            temperature_curve_length=row.get("temperature_curve_length", 5.0),
            water_wilting=row.get("water_wilting", 60.0),
            water_opt_low=row.get("water_opt_low", 70.0),
            needed_water=row["needed_water"],
            water_opt_high=row.get("water_opt_high", 100.0),
            water_capacity=row.get("water_capacity", 150.0),
            water_sensibility=row.get("water_sensibility", 1.5),
            water_stress_constant=row.get("water_stress_constant", 0.7),
            needed_light=row["needed_light"],
            needed_light_max=row.get("needed_light_max", 9.0),
            light_sensibility=row.get("light_sensibility", 1.2),
            light_km=row.get("light_km", 3.0),
            light_sigma=row.get("light_sigma", 2.0),
            phenological_initial_coefficient=row.get(
                "phenological_initial_coefficient", 0.3
            ),
            phenological_mid_coefficient=row.get("phenological_mid_coefficient", 1.0),
            phenological_end_coefficient=row.get("phenological_end_coefficient", 0.6),
            days_cycle=row["days_cycle"],
            photosyntesis_max_rate=row["photosyntesis_max_rate"],
            breathing_base_rate=row["breathing_base_rate"],
            theta=row.get("theta", 1.8),
            consecutive_stress_days_limit=row.get("consecutive_stress_days_limit", 5),
            theta_coefficient=row.get("theta_coefficient", 0.0023),
            initial_biomass=row["initial_biomass"],
            potential_performance=row["potential_performance"],
            activation_energy=row.get("activation_energy"),
        )
        return crop_type

    def get_crop_type_by_name(self, crop_type_name: str) -> CropType | None:
        """
        Method get_crop_type_by_id() created to get a Crop Type's information by
        its name.
        """

        response = (
            self.client.table("crop_types")
            .select("*")
            .eq("name", crop_type_name)
            .execute()
        )
        if not response.data:
            return None
        row = response.data[0]
        crop_type = CropType(
            id=row["id"],
            name=row["name"],
            optimal_temp=row["optimal_temp"],
            minimum_temp=row["minimum_temp"],
            maximum_temp=row["maximum_temp"],
            cold_sensibility=row.get("cold_sensibility", 0.5),
            heat_sensibility=row.get("heat_sensibility", 0.5),
            cold_factor=row.get("cold_factor", 0.1),
            heat_factor=row.get("heat_factor", 0.1),
            temperature_curve_length=row.get("temperature_curve_length", 5.0),
            water_wilting=row.get("water_wilting", 60.0),
            water_opt_low=row.get("water_opt_low", 70.0),
            needed_water=row["needed_water"],
            water_opt_high=row.get("water_opt_high", 100.0),
            water_capacity=row.get("water_capacity", 150.0),
            water_sensibility=row.get("water_sensibility", 1.5),
            water_stress_constant=row.get("water_stress_constant", 0.7),
            needed_light=row["needed_light"],
            needed_light_max=row.get("needed_light_max", 9.0),
            light_sensibility=row.get("light_sensibility", 1.2),
            light_km=row.get("light_km", 3.0),
            light_sigma=row.get("light_sigma", 2.0),
            phenological_initial_coefficient=row.get(
                "phenological_initial_coefficient", 0.3
            ),
            phenological_mid_coefficient=row.get("phenological_mid_coefficient", 1.0),
            phenological_end_coefficient=row.get("phenological_end_coefficient", 0.6),
            days_cycle=row["days_cycle"],
            photosyntesis_max_rate=row["photosyntesis_max_rate"],
            breathing_base_rate=row["breathing_base_rate"],
            theta=row.get("theta", 1.8),
            consecutive_stress_days_limit=row.get("consecutive_stress_days_limit", 5),
            theta_coefficient=row.get("theta_coefficient", 0.0023),
            initial_biomass=row["initial_biomass"],
            potential_performance=row["potential_performance"],
            activation_energy=row.get("activation_energy"),
        )
        return crop_type

    def save_crop_type(self, crop_type: CropType) -> None:
        """
        Method save_crop_type() created to save a new Crop Type in DataBase.
        """

        data = {
            "id": crop_type.id,
            "name": crop_type.name,
            "optimal_temp": crop_type.optimal_temp,
            "minimum_temp": crop_type.minimum_temp,
            "maximum_temp": crop_type.maximum_temp,
            "cold_sensibility": crop_type.cold_sensibility,
            "heat_sensibility": crop_type.heat_sensibility,
            "cold_factor": crop_type.cold_factor,
            "heat_factor": crop_type.heat_factor,
            "temperature_curve_length": crop_type.temperature_curve_length,
            "water_wilting": crop_type.water_wilting,
            "water_opt_low": crop_type.water_opt_low,
            "needed_water": crop_type.needed_water,
            "water_opt_high": crop_type.water_opt_high,
            "water_capacity": crop_type.water_capacity,
            "water_sensibility": crop_type.water_sensibility,
            "water_stress_constant": crop_type.water_stress_constant,
            "needed_light": crop_type.needed_light,
            "needed_light_max": crop_type.needed_light_max,
            "light_sensibility": crop_type.light_sensibility,
            "light_km": crop_type.light_km,
            "light_sigma": crop_type.light_sigma,
            "phenological_initial_coefficient": crop_type.phenological_initial_coefficient,
            "phenological_mid_coefficient": crop_type.phenological_mid_coefficient,
            "phenological_end_coefficient": crop_type.phenological_end_coefficient,
            "days_cycle": crop_type.days_cycle,
            "photosyntesis_max_rate": crop_type.photosyntesis_max_rate,
            "breathing_base_rate": crop_type.breathing_base_rate,
            "theta": crop_type.theta,
            "consecutive_stress_days_limit": crop_type.consecutive_stress_days_limit,
            "theta_coefficient": crop_type.theta_coefficient,
            "initial_biomass": crop_type.initial_biomass,
            "potential_performance": crop_type.potential_performance,
            "activation_energy": crop_type.activation_energy,
        }
        self.client.table("crop_types").upsert(data).execute()

    def delete_crop_type(self, crop_type_id: str) -> None:
        """
        Method delete_crop_type() created to delete a Crop Type
        """

        self.client.table("crops").delete().eq("crop_type_id", crop_type_id).execute()
        self.client.table("crop_types").delete().eq("id", crop_type_id).execute()

    def get_crops(self) -> list[Crop]:
        """
        Method get_crops() created to get the information of all crops in DataBase
        using PostgreSQL syntax.
        """

        response = self.client.table("crops").select("*").execute()
        crops = []

        for row in response.data:
            crop = Crop(
                id=row["id"],
                name=row["name"],
                user_id=row["user_id"],
                crop_type_id=row["crop_type_id"],
                start_date=datetime.fromisoformat(
                    row["start_date"].replace("Z", "+00:00")
                ),
                last_sim_date=datetime.fromisoformat(
                    row["last_sim_date"].replace("Z", "+00:00")
                ),
                conditions=[],  # Se cargan por separado
                active=row["active"],
                water_stored=row["water_stored"],
                consecutive_stress_days=row.get("consecutive_stress_days", 0),
                current_phase=row.get("current_phase", "Fase Inicial"),
            )

            crops.append(crop)
        return crops

    def get_crop_by_id(self, crop_id: str) -> Crop | None:
        """
        Mehtod get_crop_by_id() created to get the data of a Crop by its
        ID.
        """

        response = self.client.table("crops").select("*").eq("id", crop_id).execute()
        if not response.data:
            return None

        row = response.data[0]
        crop = Crop(
            id=row["id"],
            name=row["name"],
            user_id=row["user_id"],
            crop_type_id=row["crop_type_id"],
            start_date=datetime.fromisoformat(row["start_date"].replace("Z", "+00:00")),
            last_sim_date=datetime.fromisoformat(
                row["last_sim_date"].replace("Z", "+00:00")
            ),
            conditions=[],  # Se cargan por separado
            active=row["active"],
            water_stored=row["water_stored"],  # No está en la tabla
            consecutive_stress_days=row.get("consecutive_stress_days", 0),
            current_phase=row.get("current_phase", "Fase Inicial"),
        )
        return crop

    def get_crops_by_user(self, user_id: str) -> list[Crop]:
        """
        Mehtod get_crop_by_user() created to get the data of a Crop by its
        owner's ID.
        """

        response = (
            self.client.table("crops").select("*").eq("user_id", user_id).execute()
        )
        crops = []

        for row in response.data:
            crop = Crop(
                id=row["id"],
                name=row["name"],
                user_id=row["user_id"],
                crop_type_id=row["crop_type_id"],
                start_date=datetime.fromisoformat(
                    row["start_date"].replace("Z", "+00:00")
                ),
                last_sim_date=datetime.fromisoformat(
                    row["last_sim_date"].replace("Z", "+00:00")
                ),
                conditions=[],  # Se cargan por separado
                active=row["active"],
                water_stored=row["water_stored"],  # No está en la tabla
                consecutive_stress_days=row.get("consecutive_stress_days", 0),
                current_phase=row.get("current_phase", "Fase Inicial"),
            )

            crops.append(crop)
        return crops

    def get_crops_by_type(self, crop_type_id: str) -> list[Crop]:
        """
        Mehtod get_crop_by_type() created to get the data of a Crop by its
        type.
        """

        response = (
            self.client.table("crops")
            .select("*")
            .eq("crop_type_id", crop_type_id)
            .execute()
        )
        crops = []

        for row in response.data:
            crop = Crop(
                id=row["id"],
                name=row["name"],
                user_id=row["user_id"],
                crop_type_id=row["crop_type_id"],
                start_date=datetime.fromisoformat(
                    row["start_date"].replace("Z", "+00:00")
                ),
                last_sim_date=datetime.fromisoformat(
                    row["last_sim_date"].replace("Z", "+00:00")
                ),
                conditions=[],  # Se cargan por separado
                active=row["active"],
                water_stored=row["water_stored"],  # No está en la tabla
                consecutive_stress_days=row.get("consecutive_stress_days", 0),
                current_phase=row.get("current_phase", "Fase Inicial"),
            )

            crops.append(crop)
        return crops

    def get_active_crops(self) -> list[Crop]:
        """
        Mehtod get_active_crops() created to get the data of a Crop by its
        activeness.
        """

        response = self.client.table("crops").select("*").eq("active", True).execute()
        crops = []

        for row in response.data:
            crop = Crop(
                id=row["id"],
                name=row["name"],
                user_id=row["user_id"],
                crop_type_id=row["crop_type_id"],
                start_date=datetime.fromisoformat(
                    row["start_date"].replace("Z", "+00:00")
                ),
                last_sim_date=datetime.fromisoformat(
                    row["last_sim_date"].replace("Z", "+00:00")
                ),
                conditions=[],  # Se cargan por separado
                active=row["active"],
                water_stored=row["water_stored"],
                consecutive_stress_days=row.get("consecutive_stress_days", 0),
                current_phase=row.get("current_phase", "Fase Inicial"),
            )

            crops.append(crop)

        return crops

    def save_crop(self, crop: Crop) -> None:
        """
        Mehtod save_crop() created to save a crop in DB.
        """

        data = {
            "id": crop.id,
            "name": crop.name,
            "user_id": crop.user_id,
            "crop_type_id": crop.crop_type_id,
            "start_date": crop.start_date.isoformat(),
            "last_sim_date": crop.last_sim_date.isoformat(),
            "active": crop.active,
            "consecutive_stress_days": crop.consecutive_stress_days,
            "current_phase": crop.current_phase,
            "water_stored": crop.water_stored,
        }

        self.client.table("crops").upsert(data).execute()

    def delete_crop(self, crop_id: str) -> None:
        """
        Method delete_crop() created to delete a crop from the DB.
        """
        self.client.table("daily_conditions").delete().eq("crop_id", crop_id).execute()
        self.client.table("crops").delete().eq("id", crop_id).execute()

    def get_daily_conditions_by_crop(self, crop_id: str) -> list[DailyCondition]:
        """
        Method get_daily_conditions_by_crop() created to see the daily conditions of a crop.
        using its ID.
        """

        response = (
            self.client.table("daily_conditions")
            .select("*")
            .eq("crop_id", crop_id)
            .order("day")
            .execute()
        )
        conditions = []
        for row in response.data:
            condition = DailyCondition(
                day=row["day"],
                temperature=row["temperature"],
                rain=row["rain"],
                sun_hours=row["sun_hours"],
                estimated_biomass=row["estimated_biomass"],
            )
            conditions.append(condition)
        return conditions

    def save_daily_condition(self, crop_id: str, condition: DailyCondition) -> None:
        """
        Method save_daily_condition() created to save a daily condition of a crop
        in DataBase.
        """

        data = {
            "crop_id": crop_id,
            "day": condition.day,
            "temperature": condition.temperature,
            "rain": condition.rain,
            "sun_hours": condition.sun_hours,
            "estimated_biomass": condition.estimated_biomass,
        }
        self.client.table("daily_conditions").upsert(data).execute()
