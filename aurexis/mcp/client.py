"""
AUREXIS - MCP Client
Connects to MCP servers, discovers tools, and executes them via JSON-RPC.
Compatible with: https://github.com/modelcontextprotocol/servers
"""
import json, asyncio
import httpx
from typing import Optional
from mcp.registry import MCPToolRegistry


class MCPClient:
    def __init__(self, registry: MCPToolRegistry):
        self.registry = registry
        self._sessions: dict = {}  # server_name -> base_url

    async def connect(self, url: str, name: str = "") -> dict:
        """Connect to an MCP server, discover its tools, register them."""
        if not name:
            name = url.split("/")[-1] or "mcp_server"
        
        try:
            # MCP initialize handshake
            tools = await self._discover_tools(url)
            self.registry.register_server(name, url, tools)
            self._sessions[name] = url
            return {"success": True, "server": name, "tools": len(tools),
                    "tool_names": [t["name"] for t in tools]}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _discover_tools(self, base_url: str) -> list:
        """Call tools/list on the MCP server"""
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                f"{base_url.rstrip('/')}/",
                json={"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}
            )
            data = resp.json()
            return data.get("result", {}).get("tools", [])

    async def execute_tool(self, tool_name: str, args: dict) -> str:
        """Execute a tool on its MCP server"""
        server_name = self.registry.get_server_for_tool(tool_name)
        if not server_name:
            return f"Tool '{tool_name}' not found in registry"
        
        base_url = self._sessions.get(server_name)
        if not base_url:
            return f"Server '{server_name}' not connected"
        
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    f"{base_url.rstrip('/')}/",
                    json={
                        "jsonrpc": "2.0", "id": 1,
                        "method": "tools/call",
                        "params": {"name": tool_name, "arguments": args}
                    }
                )
                result = resp.json()
                if "error" in result:
                    return f"MCP Error: {result['error']['message']}"
                content = result.get("result", {}).get("content", [])
                return "\n".join(c.get("text", "") for c in content if c.get("type") == "text")
        except Exception as e:
            return f"MCP execution error: {e}"
