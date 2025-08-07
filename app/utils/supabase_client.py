import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

_SUPABASE_CLIENT = None

def get_supabase_client() -> Client:
    global _SUPABASE_CLIENT
    if _SUPABASE_CLIENT is None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")  
        _SUPABASE_CLIENT = create_client(url, key)
    return _SUPABASE_CLIENT
