## BACnet MCP Server

A lightweight [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server that connects LLM agents to [BACnet](https://en.wikipedia.org/wiki/BACnet) devices in a secure, standardized way, enabling seamless integration of AI-driven workflows with Building Automation (BAS), Building Management (BMS) and Industrial Control (ICS) systems, allowing agents to monitor real-time sensor data, actuate devices, and orchestrate complex automation tasks.

[![test](https://github.com/ezhuk/bacnet-mcp/actions/workflows/test.yml/badge.svg)](https://github.com/ezhuk/bacnet-mcp/actions/workflows/test.yml)

## Getting Started

The server is built with [FastMCP 2.0](https://gofastmcp.com/getting-started/welcome) and uses [uv](https://github.com/astral-sh/uv) for project and dependency management. Simply run the following command to install `uv` or check out the [installation guide](https://docs.astral.sh/uv/getting-started/installation/) for more details and alternative installation methods.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Clone the repository, then use `uv` to install project dependencies and create a virtual environment.

```bash
git clone https://github.com/ezhuk/bacnet-mcp.git
cd bacnet-mcp
uv sync
```

Start the BACnet MCP server by running the following command in your terminal. It defaults to using the `Streamable HTTP` transport on port `8000`.

```bash
uv run bacnet-mcp
```

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
@mcp.tool()
async def read_property(
    host: str = BACnet.HOST,
    port: int = BACnet.PORT,
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
@mcp.tool()
async def write_property(
    host: str = BACnet.HOST,
    port: int = BACnet.PORT,
    obj: str = "analogValue,1",
    prop: str = "presentValue",
    data: str = "1.0",
) -> str:
    """Writes a BACnet object property on a remote device."""
    ...
```

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

## License

The server is licensed under the [MIT License](https://github.com/ezhuk/bacnet-mcp?tab=MIT-1-ov-file).
