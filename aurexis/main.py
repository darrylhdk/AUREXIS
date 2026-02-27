#!/usr/bin/env python3
"""
AUREXIS - Main Entry Point
"""
import asyncio, sys, os
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
import typer

# Ensure we're in project root
os.chdir(Path(__file__).parent)

console = Console()
app = typer.Typer()

ASCII_LOGO = """
 █████╗ ██╗   ██╗██████╗ ███████╗██╗  ██╗██╗███████╗
██╔══██╗██║   ██║██╔══██╗██╔════╝╚██╗██╔╝██║██╔════╝
███████║██║   ██║██████╔╝█████╗   ╚███╔╝ ██║███████╗
██╔══██║██║   ██║██╔══██╗██╔══╝   ██╔██╗ ██║╚════██║
██║  ██║╚██████╔╝██║  ██║███████╗██╔╝ ██╗██║███████║
╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝╚══════╝
         Universal AI Agent OS — v1.0.0
"""

def check_installation():
    if not Path("config/config.json").exists():
        console.print("[red]✗ AUREXIS not installed. Run: python install.py[/red]")
        sys.exit(1)

@app.command()
def start(
    port: int = typer.Option(8000, help="Web UI port"),
    no_web: bool = typer.Option(False, help="Disable web UI"),
    cli_only: bool = typer.Option(False, help="CLI mode only")
):
    """Start AUREXIS Agent OS"""
    check_installation()
    console.print(f"[bold cyan]{ASCII_LOGO}[/bold cyan]")

    from core.orchestrator import Orchestrator
    orchestrator = Orchestrator()

    if cli_only:
        asyncio.run(cli_loop(orchestrator))
    else:
        import uvicorn
        from server import create_app
        app_instance = create_app(orchestrator)
        console.print(Panel(
            f"[green]AUREXIS started![/green]\n"
            f"Web UI: [bold cyan]http://localhost:{port}[/bold cyan]\n"
            f"LLM: [yellow]{orchestrator.active_llm}[/yellow]\n"
            f"Mode: [yellow]{orchestrator.active_mode}[/yellow]",
            title="AUREXIS"
        ))
        uvicorn.run(app_instance, host="0.0.0.0", port=port, log_level="warning")

async def cli_loop(orchestrator):
    """Simple CLI chat loop"""
    console.print("[green]CLI mode. Type 'exit' to quit, '/help' for commands.[/green]\n")
    while True:
        try:
            user_input = input("You > ").strip()
        except (KeyboardInterrupt, EOFError):
            break
        if not user_input:
            continue
        if user_input.lower() == "exit":
            break
        if user_input.startswith("/"):
            await handle_command(user_input, orchestrator)
            continue
        response = await orchestrator.process(user_input)
        console.print(f"[cyan]Aurexis >[/cyan] {response}\n")

async def handle_command(cmd: str, orchestrator):
    parts = cmd.split()
    command = parts[0].lower()
    if command == "/help":
        console.print("""
[yellow]Commands:[/yellow]
  /llm list              — List available LLMs
  /llm use <name>        — Switch LLM
  /mode <name>           — Switch mode (assistant/cyber/business/autonomous)
  /mcp connect <url>     — Connect MCP server
  /mcp list              — List MCP tools
  /key set <llm> <key>   — Set API key
  /status                — Show current status
  /exit                  — Exit
        """)
    elif command == "/llm" and len(parts) >= 2:
        if parts[1] == "list":
            from llm.registry import LLMRegistry
            reg = LLMRegistry()
            for name, info in reg.list_llms().items():
                status = "[green]✓[/green]" if info.get("available") else "[red]✗[/red]"
                console.print(f"  {status} {name} — {info.get('description','')}")
        elif parts[1] == "use" and len(parts) >= 3:
            await orchestrator.set_llm(parts[2])
            console.print(f"[green]Switched to {parts[2]}[/green]")
    elif command == "/mode" and len(parts) >= 2:
        await orchestrator.set_mode(parts[1])
        console.print(f"[green]Mode: {parts[1]}[/green]")
    elif command == "/status":
        console.print(f"LLM: [yellow]{orchestrator.active_llm}[/yellow]  Mode: [yellow]{orchestrator.active_mode}[/yellow]")
    elif command == "/key" and len(parts) >= 4 and parts[1] == "set":
        from core.auth import KeyVault
        vault = KeyVault()
        vault.set_key(parts[2], parts[3])
        console.print(f"[green]Key saved for {parts[2]}[/green]")

if __name__ == "__main__":
    app()
