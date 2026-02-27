"""
AUREXIS - MCP GitHub Loader
Auto-discovers and connects to popular MCP servers from the official repo.
https://github.com/modelcontextprotocol/servers
"""
import httpx
from typing import List, Dict


KNOWN_MCP_SERVERS = {
    "filesystem": "npx -y @modelcontextprotocol/server-filesystem",
    "brave_search": "npx -y @modelcontextprotocol/server-brave-search",
    "github": "npx -y @modelcontextprotocol/server-github",
    "puppeteer": "npx -y @modelcontextprotocol/server-puppeteer",
    "postgres": "npx -y @modelcontextprotocol/server-postgres",
    "sqlite": "npx -y @modelcontextprotocol/server-sqlite",
    "slack": "npx -y @modelcontextprotocol/server-slack",
    "gmail": "npx -y @modelcontextprotocol/server-gmail",
}


async def list_available_mcp_servers() -> List[Dict]:
    """Return list of known MCP servers"""
    return [{"name": k, "command": v} for k, v in KNOWN_MCP_SERVERS.items()]
