from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    OPCUA_URL: str = "opc.tcp://localhost:4841"
    NAMESPACE_URI: str = "http://example.com/opcua/server"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()