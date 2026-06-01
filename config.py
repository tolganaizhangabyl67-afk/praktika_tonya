from pydantic_settings import BaseSettings
 
class Settings(BaseSettings):
    BOT_TOKEN: str
    GROQ_API_KEY: str
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    GROQ_MODEL_FAST: str = "llama-3.1-8b-instant"
    DB_PASSWORD: str = "postgres"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "postgres"
    DB_USER: str = "postgres"
    TAVILY_API_KEY: str = ""
    REPLICATE_API_TOKEN: str = ""
 
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
 
settings = Settings()
BOT_TOKEN = settings.BOT_TOKEN
GROQ_API_KEY = settings.GROQ_API_KEY
GROQ_MODEL = settings.GROQ_MODEL
GROQ_MODEL_FAST = settings.GROQ_MODEL_FAST
DB_URL = f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
MCP_SECRET_TOKEN = "praktika-secret-2026"
TAVILY_API_KEY = settings.TAVILY_API_KEY
REPLICATE_API_TOKEN = settings.REPLICATE_API_TOKEN