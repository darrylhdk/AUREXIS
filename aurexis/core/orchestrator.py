"""
AUREXIS - Orchestrator
Central coordinator: LLM ↔ Tools ↔ Memory ↔ Planner
The LLM never calls tools directly — the orchestrator mediates.
"""
import json, re, asyncio
from typing import AsyncGenerator
from pathlib import Path

from core.memory import ConversationMemory
from core.permissions import PermissionGate
from core.planner import Planner
from llm.router import LLMRouter
from mcp.client import MCPClient
from mcp.registry import MCPToolRegistry


class Orchestrator:
    def __init__(self):
        self.memory = ConversationMemory()
        self.mcp_registry = MCPToolRegistry()
        self.mcp_client = MCPClient(self.mcp_registry)
        self.router = LLMRouter()
        
        # Load config
        config = self._load_config()
        self.active_llm = config.get("active_llm", "phi2_local")
        self.active_mode = config.get("active_mode", "assistant")
        
        self.llm = self.router.get(self.active_llm)
        self.gate = PermissionGate(self.active_mode)
        self.planner = Planner(self.llm, self.mcp_registry)

    def _load_config(self) -> dict:
        p = Path("config/config.json")
        if p.exists():
            return json.loads(p.read_text())
        return {}

    def _save_config(self, **kwargs):
        p = Path("config/config.json")
        cfg = self._load_config()
        cfg.update(kwargs)
        p.write_text(json.dumps(cfg, indent=2))

    def _load_prompt(self) -> str:
        """Load system prompt: mode-specific overrides LLM-specific overrides default"""
        candidates = [
            f"prompts/{self.active_mode}_mode.txt",
            f"prompts/{self.active_llm}.txt",
            "prompts/default.txt"
        ]
        for path in candidates:
            p = Path(path)
            if p.exists():
                return p.read_text()
        return "You are AUREXIS, a helpful AI agent."

    async def set_llm(self, name: str):
        self.llm = self.router.get(name)
        self.active_llm = name
        self.planner.llm = self.llm
        self._save_config(active_llm=name)

    async def set_mode(self, mode: str):
        valid = ["assistant", "cyber", "business", "autonomous"]
        if mode not in valid:
            raise ValueError(f"Mode must be one of {valid}")
        self.active_mode = mode
        self.gate = PermissionGate(mode)
        self._save_config(active_mode=mode)

    async def process(self, user_input: str) -> str:
        """Process a message and return full response"""
        chunks = []
        async for chunk in self.process_stream(user_input):
            chunks.append(chunk)
        return "".join(chunks)

    async def process_stream(self, user_input: str) -> AsyncGenerator[str, None]:
        """Stream response chunks"""
        self.memory.add_user(user_input)
        system = self._load_prompt()
        messages = self.memory.get_messages()

        # Autonomous mode: use planner for complex tasks
        if self.active_mode == "autonomous" and len(user_input) > 30:
            plan = await self.planner.create_plan(user_input)
            if len(plan.steps) > 1:
                result = await self.planner.execute_plan(plan, self._execute_tool)
                self.memory.add_assistant(result)
                yield result
                return

        # Standard LLM call with optional tool use
        tools = self.gate.filter_tools(self.mcp_registry.get_all_tools())
        
        async for chunk in self.llm.stream(system=system, messages=messages, tools=tools):
            # Check if chunk is a tool call
            if isinstance(chunk, dict) and chunk.get("type") == "tool_call":
                tool_result = await self._execute_tool(chunk["name"], chunk["args"])
                # Inject tool result back
                self.memory.add_assistant(f"[tool:{chunk['name']}] {tool_result}")
                yield f"\n[🔧 {chunk['name']}]: {tool_result}\n"
            else:
                yield chunk

        # Save final response to memory
        # (In practice you'd buffer the full response, simplified here)
        self.memory.add_assistant("[streamed response]")

    async def _execute_tool(self, tool_name: str, args: dict) -> str:
        """Execute tool through permission gate then MCP"""
        allowed, reason = self.gate.can_execute(tool_name, args)
        if not allowed:
            return f"[BLOCKED] {reason}"
        return await self.mcp_client.execute_tool(tool_name, args)

    def get_connector_status(self) -> dict:
        cfg = self._load_config()
        return {k: v.get("enabled", False) for k, v in cfg.get("connectors", {}).items()}
