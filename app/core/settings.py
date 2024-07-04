from dotenv import load_dotenv

load_dotenv()
from pydantic import Field
from pydantic_settings import SettingsConfigDict, BaseSettings
import os

# Determine the environment
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

# Load the appropriate .env file based on the environment
if ENVIRONMENT == 'production':
    load_dotenv('.env.production')
else:
    load_dotenv('.env.development')


class Settings(BaseSettings):
    app_name: str = Field("Jambu.AI - Tools API", validation_alias="APP_NAME")
    default_large_model: str = Field("gpt-4o", validation_alias="DEFAULT_LARGE_MODEL")

    supabase_url: str = Field(..., validation_alias="SUPABASE_URL")
    supabase_key: str = Field(..., validation_alias="SUPABASE_KEY")
    supabase_bucket_name: str = Field(..., validation_alias="SUPABASE_BUCKET_NAME")
    sentry_dsn: str = Field(..., validation_alias="SENTRY_DSN")
    firecrawl_api_key: str = Field(..., validation_alias="FIRECRAWL_API_KEY")

    posthog_api_key: str = Field(..., validation_alias="POSTHOG_API_KEY")
    posthog_host: str = Field(..., validation_alias="POSTHOG_HOST")

    openai_api_key: str = Field(..., validation_alias="OPENAI_API_KEY")
    openai_org_id: str = Field(..., validation_alias="OPENAI_ORG_ID")

    model_config = SettingsConfigDict(env_file='.env',
                                      env_file_encoding='utf-8',
                                      extra="allow")

    celery_broker_url: str = Field(..., validation_alias="CELERY_BROKER_URL")
    celery_result_backend: str = Field(..., validation_alias="CELERY_RESULT_BACKEND")


settings = Settings()

if __name__ == '__main__':
    print(settings.dict())
