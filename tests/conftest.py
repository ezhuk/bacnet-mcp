import asyncio
import pytest
import threading

from bacpypes3.argparse import SimpleArgumentParser
from bacpypes3.app import Application
from bacpypes3.local.analog import AnalogValueObject
from bacpypes3.local.binary import BinaryValueObject
from pydantic import BaseModel

from bacnet_mcp.server import BACnetMCP

import bacnet_mcp.server as server_mod


class Config(BaseModel):
    host: str = "127.0.0.1"
    port: int = 47809


async def _server_main(config: Config) -> None:
    app = None
    try:
        args = SimpleArgumentParser().parse_args(
            ["--address", f"{config.host}:{config.port}"]
        )
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
        app.add_object(
            BinaryValueObject(
                objectIdentifier=("binaryValue", 1),
                objectName="binary-value",
                presentValue="active",
                statusFlags=[0, 0, 0, 0],
                description="Binary Value",
            )
        )
        await asyncio.Future()
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        if app:
            app.close()


@pytest.fixture(scope="session")
def server():
    config = Config()
    thread = threading.Thread(
        target=lambda: asyncio.run(_server_main(config)), daemon=True
    )
    thread.start()
    yield config


@pytest.fixture(scope="session")
def mcp():
    return BACnetMCP()


@pytest.fixture
def mcp_error(monkeypatch):
    async def who_has(low: int, high: int, obj: str):
        raise RuntimeError("who_has_failed")

    async def who_is(low: int, high: int):
        raise RuntimeError("who_is_failed")

    monkeypatch.setattr(server_mod, "who_has", who_has)
    monkeypatch.setattr(server_mod, "who_is", who_is)
    return server_mod.BACnetMCP()


@pytest.fixture
def cli(monkeypatch):
    async def dummy_run_async(self, transport):
        return

    monkeypatch.setattr(
        "bacnet_mcp.cli.BACnetMCP.run_async",
        dummy_run_async,
    )
