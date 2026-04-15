from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    project_name: str = 'QRKot'
    database_url: str = 'sqlite+aiosqlite:///./fastapi.db'

    class Config:
        env_file = '.env'


settings = Settings()
