import asyncio
import typer

from bacnet_mcp.server import BACnetMCP


app = typer.Typer(
    name="bacnet-mcp",
    help="BACnetMCP CLI",
)


@app.command()
def run(
    host: str | None = typer.Option(None, "--host"),
    port: int | None = typer.Option(None, "--port"),
):
    kwargs: dict[str, object] = {}
    if host is not None:
        kwargs["host"] = host
    if port is not None:
        kwargs["port"] = port
    server = BACnetMCP()
    asyncio.run(server.run_async(transport="http", **kwargs))
