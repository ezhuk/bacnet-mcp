"""A lightweigth MCP server for the BACnet protocol."""

from bacpypes3.app import Application
from bacpypes3.argparse import SimpleArgumentParser
from fastmcp import FastMCP
from fastmcp.server.auth import BearerAuthProvider
from fastmcp.prompts.prompt import Message
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Auth(BaseModel):
    key: Optional[str] = None


class BACnet(BaseModel):
    host: str = "127.0.0.1"
    port: int = 47808


class Settings(BaseSettings):
    auth: Auth = Auth()
    bacnet: BACnet = BACnet()
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()


mcp = FastMCP(
    name="BACnet MCP Server",
    auth=(
        BearerAuthProvider(public_key=settings.auth.key) if settings.auth.key else None
    ),
)


@mcp.resource("udp://{host}:{port}/{obj}/{instance}/{prop}")
@mcp.tool(
    annotations={"title": "Read Property", "readOnlyHint": True, "openWorldHint": True}
)
async def read_property(
    host: str = settings.bacnet.host,
    port: int = settings.bacnet.port,
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


@mcp.tool(
    annotations={"title": "Send Who-Is", "readOnlyHint": True, "openWorldHint": True}
)
async def who_is(
    low: int,
    high: int,
) -> [str]:
    """Sends a 'who-is' broadcast message."""
    args = SimpleArgumentParser().parse_args()
    app = Application().from_args(args)
    try:
        res = await app.who_is(low, high)
        return [str(x.iAmDeviceIdentifier) for x in res]
    except Exception as e:
        raise RuntimeError(f"{e}") from e
    finally:
        if app:
            app.close()


@mcp.tool(
    annotations={"title": "Send Who-Has", "readOnlyHint": True, "openWorldHint": True}
)
async def who_has(
    low: int,
    high: int,
    obj: str,
) -> [str]:
    """Sends a 'who-has' broadcast message."""
    args = SimpleArgumentParser().parse_args()
    app = Application().from_args(args)
    try:
        res = await app.who_has(low, high, obj)
        return [str(x.deviceIdentifier) for x in res]
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
