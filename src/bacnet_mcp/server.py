from bacpypes3.app import Application
from bacpypes3.argparse import SimpleArgumentParser
from fastmcp import FastMCP, Context
from fastmcp.server.lifespan import lifespan
from fastmcp.server.auth.providers.workos import AuthKitProvider
from fastmcp.prompts.prompt import Message
from fastmcp.resources import ResourceTemplate

from bacnet_mcp.settings import Settings
from bacnet_mcp.utils import get_device


@lifespan
async def app_lifespan(server: FastMCP):
    args = SimpleArgumentParser().parse_args(args=[])
    app = Application().from_args(args)
    try:
        yield {"app": app}
    finally:
        app.close()


settings = Settings()


async def read_property(
    ctx: Context,
    name: str | None = None,
    host: str | None = None,
    port: int | None = None,
    obj: str = "analogValue",
    instance: str = "1",
    prop: str = "presentValue",
) -> str:
    """Reads the content of a BACnet object property on a remote unit."""
    try:
        app: Application = ctx.lifespan_context.get("app")
        host, port = get_device(settings, name, host, port)
        res = await app.read_property(f"{host}:{port}", f"{obj},{instance}", f"{prop}")
        return str(res)
    except Exception as e:
        raise RuntimeError(
            f"Could not read {obj},{instance} {prop} from {host}:{port}"
        ) from e


async def write_property(
    ctx: Context,
    name: str | None = None,
    host: str | None = None,
    port: int | None = None,
    obj: str = "analogValue,1",
    prop: str = "presentValue",
    data: str = "1.0",
) -> str:
    """Writes a BACnet object property on a remote device."""
    try:
        app: Application = ctx.lifespan_context.get("app")
        host, port = get_device(settings, name, host, port)
        await app.write_property(f"{host}:{port}", f"{obj}", f"{prop}", f"{data}")
        return f"Write to {obj} {prop} on {host}:{port} has succedeed"
    except Exception as e:
        raise RuntimeError(f"{e}") from e


async def who_is(
    ctx: Context,
    low: int,
    high: int,
) -> list[str]:
    """Sends a 'who-is' broadcast message."""
    try:
        app: Application = ctx.lifespan_context.get("app")
        res = await app.who_is(low, high)
        return [str(x.iAmDeviceIdentifier) for x in res]
    except Exception as e:
        raise RuntimeError(f"{e}") from e


async def who_has(
    ctx: Context,
    low: int,
    high: int,
    obj: str,
) -> list[str]:
    """Sends a 'who-has' broadcast message."""
    try:
        app: Application = ctx.lifespan_context.get("app")
        res = await app.who_has(low, high, obj)
        return [str(x.deviceIdentifier) for x in res]
    except Exception as e:
        raise RuntimeError(f"{e}") from e


def bacnet_help() -> list[Message]:
    """Provides examples of how to use the BACnet MCP server."""
    return [
        Message("Here are examples of how to read and write properties:"),
        Message("Read the presentValue property of analog-input,1 at 10.0.0.4."),
        Message("Fetch the units property of analog-input 2."),
        Message("Write the value 42 to analog-value instance 1."),
        Message("Set the presentValue of binary-output 3 to True."),
    ]


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


class BACnetMCP(FastMCP):
    def __init__(self, **kwargs):
        super().__init__(
            name="BACnet MCP Server",
            lifespan=app_lifespan,
            auth=(
                AuthKitProvider(
                    authkit_domain=settings.auth.domain, base_url=settings.auth.url
                )
                if settings.auth.domain and settings.auth.url
                else None
            ),
            **kwargs,
        )

        self.add_template(
            ResourceTemplate.from_function(
                fn=read_property,
                uri_template="udp://{host}:{port}/{obj}/{instance}/{prop}",
            )
        )

        self.tool(
            read_property,
            annotations={
                "title": "Read Property",
                "readOnlyHint": True,
                "openWorldHint": True,
            },
        )

        self.tool(
            write_property,
            annotations={
                "title": "Write Property",
                "readOnlyHint": False,
                "openWorldHint": True,
            },
        )

        self.tool(
            who_is,
            annotations={
                "title": "Send Who-Is",
                "readOnlyHint": True,
                "openWorldHint": True,
            },
        )

        self.tool(
            who_has,
            annotations={
                "title": "Send Who-Has",
                "readOnlyHint": True,
                "openWorldHint": True,
            },
        )

        self.prompt(bacnet_error, name="bacnet_error", tags={"bacnet", "error"})
        self.prompt(bacnet_help, name="bacnet_help", tags={"bacnet", "help"})
