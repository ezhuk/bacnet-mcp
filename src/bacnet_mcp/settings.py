from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class Auth(BaseModel):
    key: str | None = None


class BACnet(BaseModel):
    host: str = "127.0.0.1"
    port: int = 47808


class Settings(BaseSettings):
    auth: Auth = Auth()
    bacnet: BACnet = BACnet()
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        env_prefix="BACNET_MCP_",
    )
