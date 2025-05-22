import asyncio

from agents import Agent, Runner
from agents.mcp import MCPServer, MCPServerStreamableHttp
from agents.model_settings import ModelSettings


async def run(mcp_server: MCPServer):
    agent = Agent(
        name="Assistant",
        instructions="Use the tools to answer the questions.",
        mcp_servers=[mcp_server],
        model_settings=ModelSettings(tool_choice="required"),
    )

    message = "Read the presentValue property of analogInput,1."
    print(f"Running: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    print(result.final_output)

    message = "Write the value 42 to analogValue instance 1."
    print(f"Running: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    print(result.final_output)

    message = "Set the presentValue of binaryOutput 3 to True."
    print(f"Running: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    print(result.final_output)


async def main():
    async with MCPServerStreamableHttp(
        name="Streamable HTTP Server",
        params={
            "url": "http://localhost:8000/mcp/",
        },
    ) as server:
        await run(server)


if __name__ == "__main__":
    asyncio.run(main())
