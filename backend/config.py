import os
from dotenv import load_dotenv

# Load .env from root directory or backend directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))
load_dotenv()

class Config:
    FLASK_APP = os.getenv("FLASK_APP", "app.py")
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    DEBUG = os.getenv("FLASK_DEBUG", "1") == "1"
    PORT = int(os.getenv("PORT", 5000))

    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    JWT_SECRET = os.getenv("JWT_SECRET", "framestudio-super-secret-jwt-key-2026")

    if not SUPABASE_URL or not SUPABASE_KEY:
        print("WARNING: Supabase URL or Anon Key is missing in environment!")