"""A lightweigth MCP server for the BACnet protocol."""

from dataclasses import dataclass

from bacpypes3.app import Application
from bacpypes3.argparse import SimpleArgumentParser
from fastmcp import FastMCP
from fastmcp.prompts.prompt import Message


@dataclass(frozen=True)
class BACnet:
    """Default BACnet connection settings."""

    HOST = "127.0.0.1"
    PORT = 47808


mcp = FastMCP(name="BACnet MCP Server")


@mcp.resource("udp://{host}:{port}/{obj}/{instance}/{prop}")
async def read_property(
    host: str = BACnet.HOST,
    port: int = BACnet.PORT,
    obj: str = "analogValue",
    instance: str = "1",
    prop: str = "presentValue",
) -> str:
    """Reads the content of a BACnet object property on a remote unit."""
    args = SimpleArgumentParser().parse_args()
    app = Application().from_args(args)
    try:
        res = await app.read_property(f"{host}:{port}", f"{obj},{instance}", f"{prop}")
        return res
    except Exception as e:
        raise RuntimeError(
            f"Could not read {obj},{instance} {prop} from {host}:{port}"
        ) from e
    finally:
        if app:
            app.close()


@mcp.tool()
async def write_property(
    host: str = BACnet.HOST,
    port: int = BACnet.PORT,
    obj: str = "analogValue,1",
    prop: str = "presentValue",
    data: str = "1.0",
) -> str:
    """Writes a BACnet object property on a remote device."""
    args = SimpleArgumentParser().parse_args()
    app = Application().from_args(args)
    try:
        await app.write_property(f"{host}:{port}", f"{obj}", f"{prop}", f"{data}")
        return f"Write to {obj} {prop} on {host}:{port} has succedeed"
    except Exception as e:
        raise RuntimeError(f"{e}") from e
    finally:
        if app:
            app.close()


@mcp.prompt(name="bacnet_help", tags={"bacnet", "help"})
def bacnet_help() -> list[Message]:
    """Provides examples of how to use the BACnet MCP server."""
    return [
        Message("Here are examples of how to read and write properties:"),
        Message("Read the presentValue property of analog-input,1 at 10.0.0.4."),
        Message("Fetch the units property of analog-input 2."),
        Message("Write the value 42 to analog-value instance 1."),
        Message("Set the presentValue of binary-output 3 to True."),
    ]


@mcp.prompt(name="bacnet_error", tags={"bacnet", "error"})
def bacnet_error(error: str | None = None) -> list[Message]:
    """Asks the user how to handle an error."""
    return (
        [
            Message(f"ERROR: {error!r}"),
            Message("Would you like to retry, change parameters, or abort?"),
        ]
        if error
        else []
    )
