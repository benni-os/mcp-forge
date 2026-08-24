"""Validation helpers for the ``mcp-forge validate`` command."""

from __future__ import annotations

from dataclasses import dataclass, field
from importlib import import_module
from typing import Any

from jsonschema import Draft7Validator, SchemaError

from mcp_forge.core.forge import Forge


@dataclass
class ValidationReport:
    """The errors and warnings found while inspecting a Forge application."""

    tool_count: int
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def validate_target(target: str) -> ValidationReport:
    """Import a ``module:attribute`` Forge target and validate its registered tools."""
    module_name, separator, attribute_name = target.partition(":")
    if not separator or not module_name or not attribute_name:
        raise ValueError("target must use the form module:attribute")

    try:
        module = import_module(module_name)
    except ImportError as error:
        raise ValueError(f"could not import module '{module_name}': {error}") from error

    app = getattr(module, attribute_name, None)
    if not isinstance(app, Forge):
        raise ValueError(f"'{target}' is not a Forge application")

    return validate_forge(app)


def validate_forge(app: Forge) -> ValidationReport:
    """Validate the MCP-facing fields for every tool registered on ``app``."""
    report = ValidationReport(tool_count=len(app._tools))

    for registered_name, tool in app._tools.items():
        _validate_tool(registered_name, tool, report)

    return report


def _validate_tool(name: str, tool: dict[str, Any], report: ValidationReport) -> None:
    display_name = tool.get("name", name)
    if not isinstance(display_name, str) or not display_name:
        report.errors.append(f"tool '{name}': name is required")
    if not isinstance(tool.get("description"), str) or not tool["description"].strip():
        report.warnings.append(f"tool '{name}': description missing (recommended)")

    schema = tool.get("schema")
    if not isinstance(schema, dict) or not isinstance(schema.get("input"), dict):
        report.errors.append(f"tool '{name}': inputSchema is required")
        return

    try:
        Draft7Validator.check_schema(schema["input"])
    except SchemaError as error:
        report.errors.append(f"tool '{name}': invalid inputSchema: {error.message}")
