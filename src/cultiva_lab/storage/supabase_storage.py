import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(url, key)

supabase.table("users").insert({
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "username": "agricultor1",
    "password_hash": "hashed_password",
    "role": "USER"
}).execute()

result = supabase.table("users").select("*").execute()
print(result.data)




if __name__ == "__main__":
    check_data()
