import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

from mcp.server.fastmcp import FastMCP

from .mcp.resources import register_resources
from .mcp.tools import register_tools

mcp = FastMCP("MCP Academy")
register_tools(mcp)
register_resources(mcp)


if __name__ == "__main__":
    mcp.run(transport="stdio")
