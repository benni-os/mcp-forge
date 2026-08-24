"""mcp-forge CLI — new, run, validate, build, list."""

import subprocess
import sys
from pathlib import Path

from mcp_forge.cli.validator import validate_target

try:
    import typer
except ImportError as error:
    raise SystemExit("mcp-forge CLI requires typer. Run: pip install mcp-forge[cli]") from error

app = typer.Typer(
    name="mcp-forge",
    help="⚡ The FastAPI-style framework for building MCP servers.",
    add_completion=False,
)


@app.command()
def new(name: str = typer.Argument(..., help="Project name")) -> None:
    """Scaffold a new mcp-forge project."""
    project_dir = Path(name)
    if project_dir.exists():
        typer.echo(f"❌ Directory '{name}' already exists.", err=True)
        raise typer.Exit(1)

    project_dir.mkdir()
    (project_dir / "server.py").write_text(
        f'from mcp_forge import Forge\n\napp = Forge(name="{name}")\n\n\n'
        '@app.tool(description="Example tool")\n'
        "def hello(name: str) -> str:\n"
        '    return f"Hello, {name}!"\n\n\n'
        'if __name__ == "__main__":\n'
        "    app.run()\n"
    )
    (project_dir / "mcp-forge.toml").write_text(
        f'[server]\nname = "{name}"\nversion = "0.1.0"\ntransport = "stdio"\n'
    )
    (project_dir / "requirements.txt").write_text("mcp-forge\n")
    typer.echo(f"✅ Created project '{name}'")
    typer.echo(f"   cd {name} && mcp-forge run")


@app.command()
def run(
    file: str = typer.Argument("server.py", help="Entry point file"),
    transport: str = typer.Option(None, "--transport", "-t", help="Transport: stdio, http, sse"),
    port: int = typer.Option(None, "--port", "-p", help="Port (HTTP/SSE only)"),
    reload: bool = typer.Option(False, "--reload", help="Enable hot reload"),
) -> None:
    """Run the MCP server."""
    cmd = [sys.executable, file]
    if transport:
        cmd += ["--transport", transport]
    if port:
        cmd += ["--port", str(port)]
    if reload:
        cmd.append("--reload")
    subprocess.run(cmd, check=True)


@app.command()
def validate(
    target: str = typer.Argument(..., help="Forge application target in module:attribute form"),
) -> None:
    """Validate registered tools without starting a transport."""
    try:
        report = validate_target(target)
    except ValueError as error:
        typer.echo(f"❌ {error}", err=True)
        raise typer.Exit(1) from error

    for message in report.errors:
        typer.echo(f"❌ {message}", err=True)
    for message in report.warnings:
        typer.echo(f"⚠️  {message}")

    if report.errors:
        raise typer.Exit(1)

    typer.echo(f"✅ tools: {report.tool_count} registered")
    typer.echo("✅ schemas: all valid JSON Schema draft-07")


@app.command(name="list")
def list_tools(file: str = typer.Argument("server.py", help="Entry point file")) -> None:
    """List all registered tools in the server."""
    typer.echo(f"📋 Tools in {file}:")
    typer.echo("   (run the server and call GET /tools for full schema)")


if __name__ == "__main__":
    app()
