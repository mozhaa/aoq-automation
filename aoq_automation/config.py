from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    token: str
    model_config = SettingsConfigDict(
        env_file=Path(".") / ".." / "files" / ".env", env_file_encoding="utf-8"
    )
