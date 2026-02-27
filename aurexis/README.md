# AUREXIS — Universal AI Agent OS

> Local, modular, multi-LLM agent OS. Runs on your PC. No cloud required.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Install & create profile
python install.py

# 3. (Optional) Download Phi-2 model for local inference
wget -P models/ https://huggingface.co/TheBloke/phi-2-GGUF/resolve/main/phi-2.Q4_K_M.gguf

# 4. Start AUREXIS
python main.py

# Web UI: http://localhost:8000
# CLI only: python main.py --cli-only
```

## Project Structure

```
aurexis/
├── main.py              # Entry point (CLI + starts server)
├── install.py           # One-time setup wizard
├── server.py            # FastAPI server + WebSocket
├── requirements.txt
│
├── core/
│   ├── orchestrator.py  # Central coordinator (LLM ↔ Tools ↔ Memory)
│   ├── agent.py         # Agent facade for connectors
│   ├── planner.py       # Autonomous task planner
│   ├── memory.py        # Conversation history
│   ├── auth.py          # Encrypted API key vault
│   └── permissions.py   # Security gate (blocks unsafe tool calls)
│
├── llm/
│   ├── base.py          # Abstract LLM interface
│   ├── registry.py      # LLM catalogue (register new LLMs here)
│   ├── router.py        # Selects & instantiates LLMs
│   └── providers/       # One file per LLM provider
│
├── prompts/             # System prompts per LLM and per mode
├── mcp/                 # MCP protocol client + tool registry
├── connectors/          # Telegram, Discord, WhatsApp, Facebook
├── webui/               # Web interface (ChatGPT-style)
├── config/              # Runtime config (gitignored)
├── assets/logo/         # ASCII + image logos
├── models/              # GGUF model files (gitignored)
└── data/                # User data, memory (gitignored)
```

## Supported LLMs

| LLM | API Key Required | Notes |
|-----|-----------------|-------|
| Phi-2 (local) | No | Default, requires GGUF file |
| OpenAI | Yes | GPT-4o, GPT-4, GPT-3.5 |
| Anthropic | Yes | Claude 3.5 Sonnet, Opus, Haiku |
| Mistral | Yes | mistral-large, mistral-small |
| Groq | Yes | llama3-70b, ultra-fast inference |
| Kimi | Yes | moonshot-v1-8k |
| Custom | Optional | Any OpenAI-compatible API |

## Agent Modes

| Mode | Purpose |
|------|---------|
| `assistant` | General-purpose assistant |
| `cyber` | Cybersecurity analyst |
| `business` | Startup/business strategist |
| `autonomous` | Planner + executor (multi-step tasks) |

## Security

- API keys encrypted with **Fernet** (AES-128-CBC + HMAC-SHA256)
- Tool calls filtered through **PermissionGate** before execution
- LLM never executes system actions directly
- All keys stored locally, never sent to Anthropic servers

## Add a new LLM

See `ARCHITECTURE.md` → "How to Add a New LLM"

## License

MIT
