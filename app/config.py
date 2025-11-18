from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Loads application settings from environment variables.
    
    This will automatically read the DATABASE_URL you set with 'export'.
    """
    
    # This default value will be used ONLY if DATABASE_URL is not set.
    # We use 5432 here so we can be sure our 5433 export is working.
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/default_db"

    # Pydantic v2 config
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore"
    )

# Create a single, global settings object
settings = Settings()