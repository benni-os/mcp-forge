"""Tests for the ``mcp-forge validate`` command."""

from __future__ import annotations

import sys
from types import ModuleType

from typer.testing import CliRunner

from mcp_forge import Forge
from mcp_forge.cli.main import app

runner = CliRunner()


def register_target(monkeypatch, forge: Forge) -> str:
    module_name = "validate_test_target"
    module = ModuleType(module_name)
    module.app = forge
    monkeypatch.setitem(sys.modules, module_name, module)
    return f"{module_name}:app"


def test_validate_reports_valid_forge(monkeypatch) -> None:
    forge = Forge(name="validate-test")

    @forge.tool(description="Add two integers")
    def add(first: int, second: int) -> int:
        return first + second

    result = runner.invoke(app, ["validate", register_target(monkeypatch, forge)])

    assert result.exit_code == 0
    assert "tools: 1 registered" in result.output
    assert "schemas: all valid JSON Schema draft-07" in result.output


def test_validate_warns_for_missing_description(monkeypatch) -> None:
    forge = Forge(name="validate-test")

    @forge.tool()
    def search(query: str) -> str:
        return query

    result = runner.invoke(app, ["validate", register_target(monkeypatch, forge)])

    assert result.exit_code == 0
    assert "tool 'search': description missing" in result.output


def test_validate_rejects_invalid_schema(monkeypatch) -> None:
    forge = Forge(name="validate-test")

    @forge.tool(description="Broken schema")
    def broken() -> str:
        return "broken"

    forge._tools["broken"]["schema"]["input"] = {"type": "not-a-json-schema-type"}
    result = runner.invoke(app, ["validate", register_target(monkeypatch, forge)])

    assert result.exit_code == 1
    assert "tool 'broken': invalid inputSchema" in result.output


def test_validate_requires_module_attribute_target() -> None:
    result = runner.invoke(app, ["validate", "server.py"])

    assert result.exit_code == 1
    assert "target must use the form module:attribute" in result.output
