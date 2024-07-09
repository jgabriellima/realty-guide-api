from supabase import create_client

from app.core.settings import settings


class SupabaseDB:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SupabaseDB, cls).__new__(cls)
            cls._instance._supabase = create_client(settings.supabase_url, settings.supabase_key)
        return cls._instance

    @property
    def client(self):
        return self._supabase
