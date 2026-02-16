from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    access_token_expire_minutes: int = 60


    class Config:
        env_file = ".env"


settings = Settings()
