from supabase import create_client, Client
from config import Config

# Public Client (Uses Anon Key for standard user requests)
supabase_public: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)

# Admin/Service Client (Uses Service Role Key for elevated backend validation & atomic operations)
supabase_admin: Client = create_client(
    Config.SUPABASE_URL, 
    Config.SUPABASE_SERVICE_ROLE_KEY if Config.SUPABASE_SERVICE_ROLE_KEY else Config.SUPABASE_KEY
)

def get_db():
    return supabase_admin