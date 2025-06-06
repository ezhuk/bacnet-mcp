import asyncio
import os

from openai import AsyncOpenAI
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Auth(BaseModel):
    key: Optional[str] = None


class Server(BaseModel):
    name: str = "bacnet-mcp"
    url: str = "http://127.0.0.1:8000/mcp"


class Settings(BaseSettings):
    auth: Auth = Auth()
    server: Server = Server()
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()

client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


async def create_response(msg):
    print(f"Running: {msg}")
    return await client.responses.create(
        model="gpt-4.1",
        tools=[
            {
                "type": "mcp",
                "server_label": settings.server.name,
                "server_url": settings.server.url,
                "allowed_tools": ["read_property", "write_property"],
                "require_approval": "never",
                **(
                    {"headers": {"Authorization": f"Bearer {settings.auth.key}"}}
                    if settings.auth.key
                    else {}
                ),
            }
        ],
        input=msg,
    )


async def main():
    resp = await create_response("Read the presentValue property of analogInput,1.")
    print(resp.output_text)

    resp = await create_response("Write the value 42 to analogValue instance 1.")
    print(resp.output_text)

    resp = await create_response("Set the presentValue of binaryOutput 3 to True.")
    print(resp.output_text)


if __name__ == "__main__":
    asyncio.run(main())
