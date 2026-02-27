# AUREXIS — Architecture Documentation

## Overview

```
User / Connector
      │
      ▼
┌─────────────────────────────────────────────────────┐
│                   ORCHESTRATOR                       │
│  ┌───────────┐  ┌───────────┐  ┌─────────────────┐  │
│  │  Memory   │  │  Planner  │  │ Permission Gate │  │
│  └───────────┘  └───────────┘  └─────────────────┘  │
└───────┬─────────────────────────────────┬────────────┘
        │                                 │
        ▼                                 ▼
┌───────────────┐                ┌────────────────────┐
│  LLM Router   │                │    MCP Client      │
│ ┌───────────┐ │                │ ┌────────────────┐ │
│ │ phi2_local│ │                │ │  Tool Registry │ │
│ │ openai    │ │                │ │  JSON-RPC calls│ │
│ │ anthropic │ │                │ └────────────────┘ │
│ │ mistral   │ │                └────────────────────┘
│ │ groq      │ │
│ │ kimi      │ │
│ │ custom    │ │
│ └───────────┘ │
└───────────────┘
```

## Key Principles

1. **LLM ≠ Executor** — The LLM only produces text. The Orchestrator executes tool calls.
2. **Permission Gate** — Every tool call passes through PermissionGate before execution.
3. **Encrypted Keys** — API keys stored with Fernet symmetric encryption.
4. **Mode-based Context** — System prompt changes based on active mode.
5. **MCP Standard** — Tools registered via official MCP protocol (JSON-RPC).

---

## How to Add a New LLM

### Step 1: Create provider file
```python
# llm/providers/myllm_provider.py
from llm.base import BaseLLM

class MyLLM(BaseLLM):
    name = "myllm"
    description = "My custom LLM"

    def is_available(self) -> bool:
        from core.auth import KeyVault
        return bool(KeyVault().get_key("myllm"))

    async def complete(self, prompt: str) -> str:
        # Your API call here
        ...

    async def chat(self, system, messages, tools=None) -> str:
        ...

    async def stream(self, system, messages, tools=None):
        response = await self.chat(system, messages, tools)
        yield response
```

### Step 2: Register in registry
```python
# In llm/registry.py → _register_all()
from llm.providers.myllm_provider import MyLLM
LLMRegistry.register("myllm", MyLLM)
```

### Step 3: Add prompt (optional)
```
prompts/myllm.txt
```

Done! The new LLM is immediately available via CLI, API, and Web UI.

---

## How to Add a New MCP Server

### Option A: Via Web UI
1. Open Settings → MCP tab
2. Enter server URL
3. Click Connect → tools auto-discovered

### Option B: Via CLI
```
/mcp connect http://localhost:3000
```

### Option C: Via API
```bash
curl -X POST http://localhost:8000/api/mcp/connect \
  -H "Content-Type: application/json" \
  -d '{"url": "http://localhost:3000", "name": "my_server"}'
```

### Option D: Build your own MCP server
Your server must expose a JSON-RPC endpoint:
- `tools/list` → returns list of tools
- `tools/call` → executes a tool

---

## Securing API Keys

Keys are stored in `config/api_keys.enc` using **Fernet** (AES-128-CBC + HMAC-SHA256).
The encryption key is in `config/secret.key` (chmod 600).

**For production:**
1. Move `config/secret.key` to a hardware security module (HSM) or OS keyring
2. Use `keyring` library for OS-level key storage:
   ```python
   import keyring
   keyring.set_password("aurexis", "secret_key", fernet_key.decode())
   ```
3. Never commit `config/secret.key` or `config/api_keys.enc`

---

## Transform AUREXIS into SaaS

### Architecture changes needed:
```
aurexis/
├── api/          # FastAPI backend (multi-tenant)
├── workers/      # Celery/Redis async task workers  
├── auth/         # JWT + OAuth2 (auth0/clerk)
├── billing/      # Stripe integration
├── tenant/       # Per-tenant LLM config, memory, prompts
└── infra/        # Docker, K8s, Terraform
```

### Steps:
1. **Multi-tenancy**: Add `tenant_id` to all operations
2. **Auth**: Replace local bcrypt with JWT + refresh tokens
3. **Database**: Replace TinyDB with PostgreSQL
4. **Queue**: Add Celery + Redis for async LLM calls
5. **Billing**: Stripe for API key generation per plan
6. **Deployment**: Dockerize → Kubernetes → CDN (Cloudflare)
7. **Observability**: OpenTelemetry + Grafana

---

## Scale to Multi-Agent

```python
# core/agent_pool.py — Future implementation
class AgentPool:
    agents: Dict[str, Orchestrator]
    
    async def spawn_agent(self, name: str, role: str, llm: str) -> Orchestrator:
        """Create a new specialized sub-agent"""
        agent = Orchestrator()
        await agent.set_llm(llm)
        await agent.set_mode(role)
        self.agents[name] = agent
        return agent
    
    async def coordinate(self, task: str) -> str:
        """Route task to best agent or spawn new one"""
        plan = await self.planner.decompose(task)
        results = await asyncio.gather(*[
            self.agents[step['agent']].process(step['subtask'])
            for step in plan.steps
        ])
        return await self.synthesize(results)
```

Multi-agent patterns to implement:
- **Supervisor**: one orchestrator delegates to specialists
- **Pipeline**: agents pass output to next agent
- **Debate**: multiple agents produce competing answers, judge picks best
- **MapReduce**: parallel agents process chunks, reducer synthesizes
