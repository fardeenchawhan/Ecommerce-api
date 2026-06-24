from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DB_CONNECTION: str
    SECRET_KEY: str
    ALGORITHM: str
    EXPIRY_TIME: int

    ADMIN_NAME: str
    ADMIN_USERNAME: str
    ADMIN_EMAIL: str
    ADMIN_PASSWORD: str

    model_config=SettingsConfigDict(env_file=".env",extra="ignore")

settings=Settings()