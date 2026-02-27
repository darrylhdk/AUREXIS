"""
AUREXIS - Permissions / Safety Layer
The LLM NEVER executes actions directly.
All actions go through this permission gate.
"""
from typing import List

# Actions always blocked regardless of mode
BLACKLIST = {"rm -rf", "format", "delete_all", "shutdown", "reboot"}

# Mode-based permissions
PERMISSIONS = {
    "assistant":  {"allowed_tools": ["web_search", "read_file", "write_file"]},
    "cyber":      {"allowed_tools": ["web_search", "read_file", "write_file", "run_code", "network_scan"]},
    "business":   {"allowed_tools": ["web_search", "read_file", "write_file", "send_email", "calendar"]},
    "autonomous": {"allowed_tools": "*"},  # All tools, but still checked against blacklist
}


class PermissionGate:
    def __init__(self, mode: str = "assistant"):
        self.mode = mode

    def can_execute(self, tool_name: str, args: dict = None) -> tuple[bool, str]:
        # Check blacklist
        for blocked in BLACKLIST:
            if blocked in tool_name or str(args).find(blocked) != -1:
                return False, f"Tool '{tool_name}' is blocked by security policy"

        # Check mode permissions
        allowed = PERMISSIONS.get(self.mode, {}).get("allowed_tools", [])
        if allowed == "*":
            return True, "ok"
        if tool_name not in allowed:
            return False, f"Tool '{tool_name}' not allowed in mode '{self.mode}'"

        return True, "ok"

    def filter_tools(self, tools: List[dict]) -> List[dict]:
        """Filter tool list based on current mode"""
        allowed = PERMISSIONS.get(self.mode, {}).get("allowed_tools", [])
        if allowed == "*":
            return tools
        return [t for t in tools if t.get("name") in allowed]
