import os
from dotenv import load_dotenv
from supabase import create_client, Client
import uuid
from datetime import datetime

load_dotenv()
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

"""
Insert 12 crop types into crop_types table.
"""

crop_types = [
    ("Café Arábica", 21.0, 13.0, 28.0, 2.5, 6.0, 365, 0.16, 0.008, 50.0, 1200.0),
    ("Café Robusta", 24.0, 15.0, 32.0, 3.0, 5.0, 300, 0.18, 0.009, 60.0, 1500.0),
    ("Maíz Dulce", 26.0, 10.0, 38.0, 6.0, 10.0, 120, 0.35, 0.012, 30.0, 2500.0),
    ("Tomate Cherry", 24.0, 12.0, 32.0, 5.0, 10.0, 90, 0.28, 0.010, 20.0, 1500.0),
    ("Fresa Monterey", 20.0, 8.0, 28.0, 4.0, 8.0, 150, 0.22, 0.008, 15.0, 600.0),
    ("Palma Africana", 28.0, 18.0, 36.0, 7.0, 7.0, 730, 0.20, 0.007, 100.0, 4000.0),
    ("Cacao Criollo", 25.0, 16.0, 32.0, 4.0, 5.0, 180, 0.14, 0.006, 40.0, 800.0),
    ("Limón Persa", 26.0, 12.0, 35.0, 5.0, 8.0, 200, 0.24, 0.009, 60.0, 1200.0),
    ("Aguacate Hass", 22.0, 10.0, 30.0, 4.5, 7.0, 300, 0.18, 0.007, 80.0, 2000.0),
    ("Piña Golden", 27.0, 15.0, 35.0, 5.0, 9.0, 180, 0.26, 0.010, 50.0, 1800.0),
    ("Lechuga Crespa", 18.0, 5.0, 25.0, 3.5, 8.0, 60, 0.30, 0.012, 5.0, 250.0),
    ("Frijol Voluble", 22.0, 12.0, 30.0, 4.0, 7.0, 90, 0.25, 0.009, 15.0, 350.0),
]

for name, opt_temp, min_temp, max_temp, water, light, days, photo, breath, init_biomass, potential in crop_types:
    supabase.table("crop_types").insert({
        "id": str(uuid.uuid4()),
        "name": name,
        "optimal_temp": opt_temp,
        "minimum_temp": min_temp,
        "maximum_temp": max_temp,
        "cold_sensibility": 0.5,
        "heat_sensibility": 0.5,
        "cold_factor": 0.1,
        "heat_factor": 0.1,
        "temperature_curve_length": 5.0,
        "water_wilting": 60.0,
        "water_opt_low": 70.0,
        "needed_water": water,
        "water_opt_high": 100.0,
        "water_capacity": 150.0,
        "water_sensibility": 1.5,
        "water_stress_constant": 0.7,
        "needed_light": light,
        "needed_light_max": 9.0,
        "light_sensibility": 1.2,
        "light_km": 3.0,
        "light_sigma": 2.0,
        "phenological_initial_coefficient": 0.3,
        "phenological_mid_coefficient": 1.0,
        "phenological_end_coefficient": 0.6,
        "days_cycle": days,
        "photosyntesis_max_rate": photo,
        "breathing_base_rate": breath,
        "theta": 1.8,
        "consecutive_stress_days_limit": 5,
        "theta_coefficient": 0.0023,
        "initial_biomass": init_biomass,
        "potential_performance": potential,
        "created_at": datetime.now().isoformat(),
    }).execute()

"""
Insert 12 users into users table.
"""

users = [
    ("agricultor2", "$2b$12$hash_example_2", "USER"),
    ("agricultor3", "$2b$12$hash_example_3", "USER"),
    ("investigador1", "$2b$12$hash_example_4", "USER"),
    ("investigador2", "$2b$12$hash_example_5", "USER"),
    ("productor1", "$2b$12$hash_example_6", "USER"),
    ("productor2", "$2b$12$hash_example_7", "USER"),
    ("asesor1", "$2b$12$hash_example_8", "USER"),
    ("estudiante1", "$2b$12$hash_example_9", "USER"),
    ("estudiante2", "$2b$12$hash_example_10", "USER"),
    ("admin_cultivalab", "$2b$12$admin_hash_example", "ADMIN"),
    ("demo_user", "$2b$12$demo_hash_example", "USER"),
]

for username, pwd_hash, role in users:
    supabase.table("users").insert({
        "id": str(uuid.uuid4()),
        "username": username,
        "password_hash": pwd_hash,
        "role": role,
        "created_at": datetime.now().isoformat(),
    }).execute()

"""
Get crop_type_ids and user_ids for foreign key references.
"""

crop_type_ids = {}
for ct in supabase.table("crop_types").select("id, name").execute().data:
    crop_type_ids[ct["name"]] = ct["id"]

user_ids = {}
for u in supabase.table("users").select("id, username").execute().data:
    user_ids[u["username"]] = u["id"]

"""
Insert 12 crops into crops table.
"""

crops = [
    ("Mi Café Finca La Paz", "agricultor1", "Café Arábica", 85.0, 0, "Fase Inicial"),
    ("Maíz Parcela Norte", "agricultor2", "Maíz Dulce", 100.0, 0, "Fase Inicial"),
    ("Tomates Invernadero", "agricultor3", "Tomate Cherry", 70.0, 0, "Fase Inicial"),
    ("Fresas Experimentales", "investigador1", "Fresa Monterey", 60.0, 0, "Fase Inicial"),
    ("Palma Zona Sur", "productor1", "Palma Africana", 120.0, 0, "Fase Inicial"),
    ("Cacao Sombra", "agricultor1", "Cacao Criollo", 90.0, 0, "Fase Inicial"),
    ("Limones Orgánicos", "productor2", "Limón Persa", 80.0, 0, "Fase Inicial"),
    ("Aguacates Premium", "agricultor2", "Aguacate Hass", 95.0, 0, "Fase Inicial"),
    ("Piña Exportación", "agricultor3", "Piña Golden", 75.0, 0, "Fase Inicial"),
    ("Café Robusta Lote B", "investigador2", "Café Robusta", 70.0, 3, "Fase Media"),
    ("Lechuga Hidropónica", "estudiante1", "Lechuga Crespa", 50.0, 0, "Fase Inicial"),
    ("Frijol Experimental", "estudiante2", "Frijol Voluble", 65.0, 0, "Fase Inicial"),
]

for name, username, crop_type_name, water_stored, stress_days, phase in crops:
    supabase.table("crops").insert({
        "id": str(uuid.uuid4()),
        "name": name,
        "user_id": user_ids[username],
        "crop_type_id": crop_type_ids[crop_type_name],
        "start_date": datetime.now().isoformat(),
        "last_sim_date": datetime.now().isoformat(),
        "active": True,
        "water_stored": water_stored,
        "consecutive_stress_days": stress_days,
        "current_phase": phase,
        "created_at": datetime.now().isoformat(),
    }).execute()

"""
Get crop_ids for daily conditions.
"""

crop_ids = {}
for c in supabase.table("crops").select("id, name").execute().data:
    crop_ids[c["name"]] = c["id"]

"""
Insert 12 daily conditions for each crop into daily_conditions table.
"""

for crop_name, crop_id in crop_ids.items():
    for day in range(1, 13):
        supabase.table("daily_conditions").insert({
            "id": str(uuid.uuid4()),
            "crop_id": crop_id,
            "day": day,
            "temperature": 21.0 + (day * 0.1),
            "rain": 2.5 + (day * 0.2),
            "sun_hours": 6.0,
            "estimated_biomass": 50.0 + (day * 8.5),
            "created_at": datetime.now().isoformat(),
        }).execute()

"""
Verification: Count records in each table.
"""

print("Verification:")
result = supabase.table('crop_types').select('*', count='exact').execute()
print(f"Crop types: {result.count}")
result = supabase.table('users').select('*', count = 'exact').execute()
print(f"Users: {result.count}")
result = supabase.table('crops').select('*', count = 'exact').execute()
print(f"Crops: {result.count}")
result = supabase.table('daily_conditions').select('*', count = 'exact').execute()
print(f"Daily Conditions: {result.count}")
