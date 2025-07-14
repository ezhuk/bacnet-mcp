## BACnet MCP Server

[![test](https://github.com/ezhuk/bacnet-mcp/actions/workflows/test.yml/badge.svg)](https://github.com/ezhuk/bacnet-mcp/actions/workflows/test.yml)
[![codecov](https://codecov.io/github/ezhuk/bacnet-mcp/graph/badge.svg?token=Y3N4ABR3WX)](https://codecov.io/github/ezhuk/bacnet-mcp)
[![PyPI - Version](https://img.shields.io/pypi/v/bacnet-mcp.svg)](https://pypi.org/p/bacnet-mcp)

A lightweight [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server that connects LLM agents to [BACnet](https://en.wikipedia.org/wiki/BACnet) devices in a secure, standardized way, enabling seamless integration of AI-driven workflows with Building Automation (BAS), Building Management (BMS) and Industrial Control (ICS) systems, allowing agents to monitor real-time sensor data, actuate devices, and orchestrate complex automation tasks.

## Getting Started

Use [uv](https://github.com/astral-sh/uv) to add and manage the BACnet MCP server as a dependency in your project, or install it directly via `uv pip install` or `pip install`. See the [Installation](https://github.com/ezhuk/bacnet-mcp/blob/main/docs/bacnet-mcp/installation.mdx) section of the documentation for full installation instructions and more details.

```bash
uv add bacnet-mcp
```

The server can be embedded in and run directly from your application. By default, it exposes a `Streamable HTTP` endpoint at `http://127.0.0.1:8000/mcp/`.

```python
# app.py
from bacnet_mcp import BACnetMCP

mcp = BACnetMCP()

if __name__ == "__main__":
    mcp.run(transport="http")
```

It can also be launched from the command line using the provided `CLI` without modifying the source code.

```bash
bacnet-mcp
```

Or in an ephemeral, isolated environment using `uvx`. Check out the [Using tools](https://docs.astral.sh/uv/guides/tools/) guide for more details.

```bash
uvx bacnet-mcp
```

### Configuration

For the use cases where most operations target a specific device, such as a Programmable Logic Controller (PLC) or BACnet gateway, its connection settings (`host` and `port`) can be specified at runtime using environment variables so that all prompts that omit explicit connection parameters will be routed to this device.

```bash
export BACNET_MCP_BACNET__HOST=10.0.0.1
export BACNET_MCP_BACNET__PORT=47808
```

These settings can also be specified in a `.env` file in the working directory.

```text
# .env
bacnet__host=10.0.0.1
bacnet__port=47808
```

### MCP Inspector

To confirm the server is up and running and explore available resources and tools, run the [MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector) and connect it to the BACnet MCP server at `http://127.0.0.1:8000/mcp/`. Make sure to set the transport to `Streamable HTTP`.

```bash
npx @modelcontextprotocol/inspector
```

![s01](https://github.com/user-attachments/assets/1dfcfda5-01ae-411c-8a6b-30996dec41c8)

## Core Concepts

The BACnet MCP server leverages FastMCP 2.0's core building blocks - resource templates, tools, and prompts - to streamline BACnet read and write operations with minimal boilerplate and a clean, Pythonic interface.

### Read Properties

Each object on a device is mapped to a resource (and exposed as a tool) and [resource templates](https://gofastmcp.com/servers/resources#resource-templates) are used to specify connection details (host, port) and read parameters (instance, property).

```python
@mcp.resource("udp://{host}:{port}/{obj}/{instance}/{prop}")
@mcp.tool(
    annotations={
        "title": "Read Property",
        "readOnlyHint": True,
        "openWorldHint": True,
    }
)
async def read_property(
    host: str = settings.bacnet.host,
    port: int = settings.bacnet.port,
    obj: str = "analogValue",
    instance: str = "1",
    prop: str = "presentValue",
) -> str:
    """Reads the content of a BACnet object property on a remote unit."""
    ...
```

### Write Properties

Write operations are exposed as a [tool](https://gofastmcp.com/servers/tools), accepting the same connection details (host, port) and allowing to set the content of an object property in a single, atomic call.

```python
@mcp.tool(
    annotations={
        "title": "Write Property",
        "readOnlyHint": False,
        "openWorldHint": True,
    }
)
async def write_property(
    host: str = settings.bacnet.host,
    port: int = settings.bacnet.port,
    obj: str = "analogValue,1",
    prop: str = "presentValue",
    data: str = "1.0",
) -> str:
    """Writes a BACnet object property on a remote device."""
    ...
```

### Authentication

To enable Bearer Token authentication for the `Streamable HTTP` transport, provide the RSA public key in PEM format in the `.env` file. Check out the [Bearer Token Authentication](https://gofastmcp.com/servers/auth/bearer) section for more details.

### Interactive Prompts

Structured response messages are implemented using [prompts](https://gofastmcp.com/servers/prompts) that help guide the interaction, clarify missing parameters, and handle errors gracefully.

```python
@mcp.prompt(name="bacnet_help", tags={"bacnet", "help"})
def bacnet_help() -> list[Message]:
    """Provides examples of how to use the BACnet MCP server."""
    ...
```

Here are some example text inputs that can be used to interact with the server.

```text
Read the presentValue property of analogInput,1 at 10.0.0.4.
Fetch the units property of analogInput 2.
Write the value 42 to analogValue instance 1.
Set the presentValue of binaryOutput 3 to True.
```

## Examples

The `examples` folder contains sample projects showing how to integrate with the BACnet MCP server using various client APIs to provide tools and context to LLMs.

- [openai-agents](https://github.com/ezhuk/bacnet-mcp/tree/main/examples/openai-agents) - shows how to connect to the BACnet MCP server using the [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/mcp/).
- [openai](https://github.com/ezhuk/bacnet-mcp/tree/main/examples/openai) - a minimal app leveraging remote MCP server support in the [OpenAI Python library](https://platform.openai.com/docs/guides/tools-remote-mcp).
- [pydantic-ai](https://github.com/ezhuk/bacnet-mcp/tree/main/examples/pydantic-ai) - shows how to connect to the BACnet MCP server using the [PydanticAI Agent Framework](https://ai.pydantic.dev).

## Docker

The BACnet MCP server can be deployed as a Docker container as follows:

```bash
docker run -d \
  --name bacnet-mcp \
  --restart=always \
  -p 8080:8000 \
  --env-file .env \
  ghcr.io/ezhuk/bacnet-mcp:latest
```

This maps port `8080` on the host to the MCP server's port `8000` inside the container and loads settings from the `.env` file, if present.

## License

The server is licensed under the [MIT License](https://github.com/ezhuk/bacnet-mcp?tab=MIT-1-ov-file).
