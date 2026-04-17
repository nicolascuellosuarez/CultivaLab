import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(url, key)

def check_data():
    response = supabase.table("users").select("*").execute()
    print(response.data)

if __name__ == "__main__":
    check_data()