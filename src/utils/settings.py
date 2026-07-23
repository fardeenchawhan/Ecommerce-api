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
    REDIS_URL: str

    BREVO_API_KEY: str

    EMAIL_FROM: str

    EMAIL_FROM_NAME: str

    GROQ_API_KEY: str
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    RAZORPAY_KEY_ID: str
    RAZORPAY_KEY_SECRET: str

    model_config=SettingsConfigDict(env_file=".env",extra="ignore")

settings=Settings()