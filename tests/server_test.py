import pytest

from fastmcp import Client
from pydantic import AnyUrl


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "prop,expected",
    [
        ("analogValue/1/presentValue", "5.0"),
        ("binaryValue/1/presentValue", "1"),
    ],
)
async def test_read_property(server, mcp, prop, expected):
    """Test read_property resource."""
    async with Client(mcp) as client:
        result = await client.read_resource(
            AnyUrl(f"udp://{server.host}:{server.port}/{prop}")
        )
        assert len(result) == 1
        assert result[0].text == expected


@pytest.mark.asyncio
async def test_write_property(server, mcp):
    """Test write_property tool."""
    async with Client(mcp) as client:
        result = await client.call_tool(
            "write_property",
            {
                "host": server.host,
                "port": server.port,
                "obj": "analogValue,1",
                "prop": "presentValue",
                "data": "11",
            },
        )
        assert len(result.content) == 1
        assert "succedeed" in result.content[0].text


@pytest.mark.asyncio
async def test_who_is(server, mcp):
    """Test who_is tool."""
    async with Client(mcp) as client:
        result = await client.call_tool(
            "who_is",
            {
                "low": 999,
                "high": 1001,
            },
        )
        assert not result.is_error


@pytest.mark.asyncio
async def test_who_has(server, mcp):
    """Test who_has tool."""
    async with Client(mcp) as client:
        result = await client.call_tool(
            "who_has",
            {"low": 999, "high": 1001, "obj": "analogValue,1"},
        )
        assert not result.is_error


@pytest.mark.asyncio
async def test_help_prompt(mcp):
    """Test help prompt."""
    async with Client(mcp) as client:
        result = await client.get_prompt("bacnet_help", {})
        assert len(result.messages) == 5


@pytest.mark.asyncio
async def test_error_prompt(mcp):
    """Test error prompt."""
    async with Client(mcp) as client:
        result = await client.get_prompt(
            "bacnet_error", {"error": "Could not read data"}
        )
        assert len(result.messages) == 2
