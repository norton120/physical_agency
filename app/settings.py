from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    together_api_key: str

settings = Settings()