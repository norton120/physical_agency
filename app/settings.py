from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    together_api_key: str
    langfuse_public_key: str
    langfuse_secret_key: str
    langfuse_host: str

settings = Settings()