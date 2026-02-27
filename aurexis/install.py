#!/usr/bin/env python3
"""
AUREXIS - Installation Script
"""
import os, sys, json, uuid, getpass
from pathlib import Path
from cryptography.fernet import Fernet
from passlib.hash import bcrypt
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

console = Console()

ASCII_LOGO = """
 █████╗ ██╗   ██╗██████╗ ███████╗██╗  ██╗██╗███████╗
██╔══██╗██║   ██║██╔══██╗██╔════╝╚██╗██╔╝██║██╔════╝
███████║██║   ██║██████╔╝█████╗   ╚███╔╝ ██║███████╗
██╔══██║██║   ██║██╔══██╗██╔══╝   ██╔██╗ ██║╚════██║
██║  ██║╚██████╔╝██║  ██║███████╗██╔╝ ██╗██║███████║
╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝╚══════╝
         Universal AI Agent OS — v1.0.0
"""

def install():
    console.print(f"[bold cyan]{ASCII_LOGO}[/bold cyan]")
    console.print(Panel("[bold green]Welcome to AUREXIS Installation[/bold green]", expand=False))

    # Create directory structure
    dirs = [
        "config", "data", "assets/logo", "prompts",
        "llm/providers", "mcp", "connectors", "webui/static"
    ]
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
    console.print("[green]✓ Directory structure created[/green]")

    # User registration
    console.print("\n[bold yellow]━━━ User Registration ━━━[/bold yellow]")
    name = Prompt.ask("[cyan]Your name[/cyan]")
    email = Prompt.ask("[cyan]Email[/cyan]")
    password = getpass.getpass("Password: ")
    confirm_pass = getpass.getpass("Confirm password: ")

    if password != confirm_pass:
        console.print("[red]✗ Passwords do not match![/red]")
        sys.exit(1)

    # Generate encryption key
    fernet_key = Fernet.generate_key()
    user_id = str(uuid.uuid4())
    password_hash = bcrypt.hash(password)

    # Save user profile
    profile = {
        "user_id": user_id,
        "name": name,
        "email": email,
        "password_hash": password_hash,
        "created_at": str(__import__("datetime").datetime.utcnow())
    }
    with open("data/profile.json", "w") as f:
        json.dump(profile, f, indent=2)

    # Save encryption key (protect this file!)
    with open("config/secret.key", "wb") as f:
        f.write(fernet_key)
    os.chmod("config/secret.key", 0o600)

    # Default config
    config = {
        "active_llm": "phi2_local",
        "active_mode": "assistant",
        "web_port": 8000,
        "mcp_enabled": True,
        "connectors": {
            "telegram": {"enabled": False, "token": ""},
            "discord": {"enabled": False, "token": ""},
            "whatsapp": {"enabled": False, "token": ""}
        },
        "llm_configs": {
            "phi2_local": {
                "type": "local",
                "model_path": "models/phi-2.Q4_K_M.gguf",
                "n_ctx": 2048,
                "n_threads": 4
            }
        }
    }
    with open("config/config.json", "w") as f:
        json.dump(config, f, indent=2)

    # Encrypted API keys store (empty)
    fernet = Fernet(fernet_key)
    encrypted_keys = fernet.encrypt(json.dumps({}).encode())
    with open("config/api_keys.enc", "wb") as f:
        f.write(encrypted_keys)

    console.print("[green]✓ Profile created[/green]")
    console.print("[green]✓ Config initialized[/green]")
    console.print("[green]✓ Encryption key generated[/green]")

    console.print(Panel(
        f"[bold green]Installation complete![/bold green]\n\n"
        f"User ID: [cyan]{user_id}[/cyan]\n\n"
        f"Run: [bold yellow]python main.py[/bold yellow]\n"
        f"Web UI: [bold yellow]http://localhost:8000[/bold yellow]",
        title="AUREXIS Ready"
    ))

if __name__ == "__main__":
    install()
