import asyncio
import typer

from bacnet_mcp.server import BACnetMCP


app = typer.Typer(
    name="bacnet-mcp",
    help="BACnetMCP CLI",
)


@app.command()
def run():
    server = BACnetMCP()
    asyncio.run(server.run_async(transport="http"))
