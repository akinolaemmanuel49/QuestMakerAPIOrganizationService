import os

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl, SecretStr


class Env(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_FILE", "./.env"), env_file_encoding='utf-8')

    MONGODB_CLUSTER: str
    MONGODB_USERNAME: str
    MONGODB_PASSWORD: SecretStr
    ENCRYPTION_SCHEMES: str
    JWT_SECRET_KEY: SecretStr
    JWT_EXPIRATION_TIME_IN_MINUTES: int
    JWT_REFRESH_EXPIRATION_TIME_IN_HOURS: int
    JWT_ALGORITHM: str
    AUTHENTICATION_SERVICE_URL: AnyHttpUrl
