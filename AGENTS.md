# Repository Guidelines

## Project Structure & Module Organization
- agents/: YAML specs by domain (engineering, data, ops, product, _templates)
- adapters/: Code generators (claude, langgraph)
- templates/: Jinja2 templates for generated artifacts
- schemas/: JSON Schemas for validation
- scripts/: CLI, renderer, validator
- tests/: Pytest suite for CLI, adapters, validation

## Build, Test, and Development Commands
- Install (dev): `pip install -e ".[dev]"`
- Pre-commit: `pre-commit install` then `pre-commit run -a`
- Validate specs: `agents validate` or `agents validate agents/engineering/security-auditor.yaml`
- Render (Claude): `agents render claude --install`
- Render (LangGraph): `agents render langgraph`
- List agents: `agents list-agents --domain engineering`
- New agent: `agents init-agent my-agent --domain custom --name "My Agent"`
- Tests + coverage: `pytest` (HTML report in `htmlcov/`)

## Coding Style & Naming Conventions
- Python: Black + Ruff (line length 88, Python 3.11). Run `ruff --fix` and `ruff format`.
- YAML: 2-space indent; yamllint config in `.yamllint.yml`.
- Agent IDs: kebab-case, regex `^[a-z0-9][a-z0-9-]*[a-z0-9]$` (e.g., `security-auditor`).
- Tool IDs: snake_case (e.g., `code_scanner`).
- Place agent files under `agents/<domain>/<agent-id>.yaml`.

## Testing Guidelines
- Framework: Pytest with coverage for `scripts/` and `adapters/` (see `pyproject.toml`).
- Test patterns: files `tests/test_*.py`, classes `Test*`, functions `test_*`.
- Minimum expectation: keep coverage high for touched areas; run locally before PR.
- Validate schemas in tests when adding new spec fields.

## Commit & Pull Request Guidelines
- Commits: Conventional Commits (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`). Example: `feat: add LangGraph app generator`.
- PR checklist:
  - `pre-commit run -a`, `pytest`, `agents validate` all pass
  - Clear description and linked issue
  - Include example output paths (e.g., `adapters/claude/<agent>.md`) and screenshots/logs when relevant
  - No secrets or credentials; follow `docs/SECURITY.md`

## Security & Configuration Tips
- Never commit secrets; hooks run Bandit, YAML/JSON checks, and secret scans.
- Use `constraints.pii_policy` in specs (`allow`, `mask`, `forbid_raw_pii`).
- See `docs/SECURITY.md` and `docs/STYLEGUIDE.md` for deeper guidance.

