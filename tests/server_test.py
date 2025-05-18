"""Server tests."""

import asyncio
import pytest
import threading
import time

from bacpypes3.argparse import SimpleArgumentParser
from bacpypes3.app import Application
from bacpypes3.local.analog import AnalogValueObject
from fastmcp import Client
from pydantic import AnyUrl

from bacnet_mcp.server import mcp

async def server_main() -> None:
    app = None
    try:
        args = SimpleArgumentParser().parse_args(["--address", "127.0.0.1:47809"])
        app = Application.from_args(args)
        app.add_object(
            AnalogValueObject(
                objectIdentifier=("analogValue", 1),
                objectName="analog-value",
                presentValue=5.0,
                statusFlags=[0, 0, 0, 0],
                description="Analog Value",
            )
        )
        await asyncio.Future()
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        if app:
            app.close()


def thread_main():
    asyncio.run(server_main())


@pytest.fixture(autouse=True)
def bacnet_server():
    thread = threading.Thread(target=thread_main, daemon=True)
    thread.start()
    time.sleep(0.5)
    yield


@pytest.mark.asyncio
async def test_read_property(bacnet_server):
    """Test read_property resource."""
    async with Client(mcp) as client:
        result = await client.read_resource(
            AnyUrl("udp://127.0.0.1:47809/analogValue/1/presentValue")
        )
        assert len(result) == 1
        assert result[0].text == '5.0'

@pytest.mark.asyncio
async def test_write_property(bacnet_server):
    """Test write_property tool."""
    async with Client(mcp) as client:
        result = await client.call_tool(
            "write_property",
            {
                "host": "127.0.0.1",
                "port": 47809,
                "obj": "analogValue,1",
                "prop": "presentValue",
                "data": "11",
            },
        )
        assert len(result) == 1
        print(result)
        assert "succedeed" in result[0].text


@pytest.mark.anyio
async def test_help_prompt():
    async with Client(mcp) as client:
        result = await client.get_prompt("bacnet_help", {})
        assert len(result.messages) == 5


@pytest.mark.anyio
async def test_error_prompt():
    async with Client(mcp) as client:
        result = await client.get_prompt(
            "bacnet_error", {"error": "Could not read data"}
        )
        assert len(result.messages) == 2
