"""
AUREXIS - MCP Tool Registry
Stores discovered tools from connected MCP servers.
"""
from typing import List, Dict, Optional


class MCPToolRegistry:
    def __init__(self):
        self._tools: Dict[str, dict] = {}      # name -> tool spec
        self._servers: Dict[str, dict] = {}    # server_name -> info

    def register_tool(self, tool: dict, server_name: str):
        name = tool.get("name")
        if name:
            self._tools[name] = {**tool, "_server": server_name}

    def register_server(self, name: str, url: str, tools: List[dict]):
        self._servers[name] = {"url": url, "tool_count": len(tools)}
        for tool in tools:
            self.register_tool(tool, name)

    def get_tool(self, name: str) -> Optional[dict]:
        return self._tools.get(name)

    def get_all_tools(self) -> List[dict]:
        return list(self._tools.values())

    def get_server_for_tool(self, tool_name: str) -> Optional[str]:
        tool = self._tools.get(tool_name)
        return tool.get("_server") if tool else None

    def count(self) -> int:
        return len(self._tools)

    def list_servers(self) -> dict:
        return self._servers
