from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://em_user:em_pass@localhost:5432/eternal_moments"
    JWT_SECRET: str = "dev_secret_change_in_production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_DAYS: int = 30
    UPLOAD_DIR: str = "uploads"
    AI_PROVIDER: str = "mock"
    VOLCANO_ARK_API_KEY: str = ""
    VOLCANO_ARK_MODEL: str = "doubao-pro-32k"
    SMS_PROVIDER: str = "mock"

    class Config:
        env_file = ".env"


settings = Settings()
