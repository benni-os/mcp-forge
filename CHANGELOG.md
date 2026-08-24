# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `mcp-forge validate <module:app>` validates registered tool input schemas and reports missing descriptions before deployment.

## [0.1.1] — 2026-08-01

### Changed
- `actions/setup-python` bumped from v5 to v7 in all CI jobs
- `actions/checkout` bumped from v4 to v7
- `codecov/codecov-action` bumped from v4 to v7
- `mypy` step now runs without `--ignore-missing-imports` — honours `strict = true` in `pyproject.toml`
- CI step order enforced: format check → lint → type check → tests → coverage upload

### Added
- Python 3.13 officially supported and added to CI matrix classifiers
- `Typing :: Typed` PyPI classifier (signals `py.typed` marker to type checkers)
- `ruff format --check` step added to CI before lint
- `CODECOV_TOKEN` env var wired to Codecov upload step
- `[tool.ruff.format]` block in `pyproject.toml` (double quotes, space indent)
- `[tool.ruff.lint.per-file-ignores]`: `F401` suppressed in `__init__.py`, `S101` in `tests/`
- `py.typed` explicitly listed in `[tool.hatch.build.targets.wheel]` include
- `mypy` extended with `warn_return_any`, `warn_unused_configs`, `show_error_codes`

### Fixed
- `httpx` dev dependency bumped to `>=0.28.1` (security + API compat)
- `pytest-asyncio` bumped to `>=1.4.0` (resolves deprecation warnings in async fixtures)
- `anyio` bumped to `>=4.14.2`
- `typer` bumped to `>=0.27.0`
- `pytest` bumped to `>=9.1.1`

## [0.1.0] — 2026-07-31

### Added
- `Forge` class with `@app.tool()` declarative decorator
- Auto JSON Schema generation from Python type hints (Pydantic v2)
- STDIO transport — MCP spec `2024-11-05`, Claude Desktop / Cursor / VS Code compatible
- HTTP transport — FastAPI REST (`GET /tools`, `POST /tools/{name}`, `GET /health`)
- SSE transport — Server-Sent Events for streaming
- `ForgeConfig` dataclass with full server configuration
- CLI: `mcp-forge new`, `mcp-forge run`, `mcp-forge list`
- Contrib routers: `memory`, `filesystem`, `web`
- `ForgeTestClient` with sync `.call()` and async `.acall()`
- Full test suite with pytest + pytest-asyncio
- GitHub Actions CI — Python 3.11 + 3.12, ruff, mypy, auto-publish

### Fixed
- STDIO transport: all logging redirected to stderr (stdout is MCP wire channel)
- STDIO transport: `notifications/initialized` handler added (MCP spec required)
- STDIO transport: replaced deprecated `get_event_loop()` with `get_running_loop()`
- `Forge.include()`: deep-copy prevents shared mutable state between instances
- `memory` contrib: scoped `_store` per router instance, not global module
- `schema.py`: guarded `get_type_hints()` with try/except for untyped params
- HTTP transport: `Body()` for proper FastAPI request validation
- Contrib `__init__`: lazy imports prevent `ImportError` without optional extras
- `ForgeTestClient`: `nest_asyncio` fallback for running event loops
