"""Test Fixtures."""

import asyncio
import pytest
import threading

from bacpypes3.argparse import SimpleArgumentParser
from bacpypes3.app import Application
from bacpypes3.local.analog import AnalogValueObject
from pydantic import BaseModel


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
