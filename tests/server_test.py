"""Server tests."""

import pytest

from fastmcp import Client
from pydantic import AnyUrl

from bacnet_mcp.server import mcp


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
