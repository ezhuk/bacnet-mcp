from importlib.metadata import version

from bacnet_mcp.server import BACnetMCP


__version__ = version("bacnet-mcp")
__all__ = ["BACnetMCP"]
