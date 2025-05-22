import asyncio
import os

from openai import AsyncOpenAI


SERVER_NAME = "bacnet-mcp"
SERVER_URL = "http://127.0.0.1:8000/mcp"


client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


async def create_response(msg):
    print(f"Running: {msg}")
    return await client.responses.create(
        model="gpt-4.1",
        tools=[
            {
                "type": "mcp",
                "server_label": SERVER_NAME,
                "server_url": SERVER_URL,
                "allowed_tools": ["read_property", "write_property"],
                "require_approval": "never",
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
