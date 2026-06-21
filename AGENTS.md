# AGENTS.md

Operating manual for AI coding agents working in this repository.

## About The Project

`telegram-webapp-auth` is a small Python package for validating Telegram Mini App `initData`.
It implements Telegram's bot-token HMAC validation and third-party Ed25519 validation flows, and returns typed dataclasses for users, chats, and init data.

- Runtime: Python `>=3.10,<4.0`.
- Package manager: Poetry.
- Runtime dependency surface: keep it lightweight; `cryptography` is the core dependency.
- Public API lives in `telegram_webapp_auth.auth`, `telegram_webapp_auth.data`, and `telegram_webapp_auth.errors`.
- Documentation is built with MkDocs Material and published to GitHub Pages.

## Golden Rules

1. Keep changes small and maintenance-focused. This project is in maintenance mode and accepts bug fixes.
2. Preserve compatibility with Python 3.10 unless the user explicitly changes the supported version range.
3. Treat Telegram authentication behavior as security-sensitive. Prefer exact Telegram documentation behavior over convenience shortcuts.
4. Use Poetry for dependency resolution and lockfile updates; do not hand-edit `poetry.lock`.
5. Everything in this repository is written in English.

## Project Layout

```text
telegram_webapp_auth/
  auth.py        validation algorithms and parsing/serialization helpers
  data.py        public dataclasses, chat enum, Telegram public keys
  errors.py      public exception hierarchy
tests/
  test_validate.py
  test_validate_third_party.py
docs/
  guide/         user documentation and examples
  references/    API reference pages generated through mkdocstrings
mkdocs.yml       MkDocs Material configuration
pyproject.toml   package metadata, dependency constraints, tool dependencies
Makefile         common local commands
```

## Daily Commands

```bash
poetry install --no-root
make test
make lint
make format
make black-lint
make mkdocs-serve
make benchmark
```

For narrow edits, prefer targeted commands first, for example:

```bash
poetry run pytest tests/test_validate.py
poetry run pytest tests/test_validate_third_party.py
poetry run mypy --config formatters-cfg.toml telegram_webapp_auth
poetry run flake8 --toml-config formatters-cfg.toml telegram_webapp_auth tests
```

Run `make test` and `make lint` before considering a behavior change complete when time permits.

## Python Conventions

- Keep code compatible with Python 3.10 through 3.14.
- Follow the existing style: dataclasses, explicit imports, `typing.Optional`, and double quotes.
- Use timezone-aware datetimes (`timezone.utc`) for auth-date logic.
- Keep parser and validation failures raising `InvalidInitDataError`; use `ExpiredInitDataError` only for expiry failures.
- Do not replace `hmac.compare_digest` with normal equality for hash comparison.
- Preserve unknown top-level init-data fields in `WebAppInitData.extra`.
- Avoid new abstractions unless they remove real complexity in the current files.

## Authentication Rules

- Bot-token validation is implemented through `generate_secret_key()` and `TelegramAuthenticator.validate()`.
- Third-party validation uses Telegram's test and production Ed25519 public keys from `data.py`.
- Query-string parsing must reject empty input, duplicate keys, empty keys, malformed query strings, invalid JSON objects, invalid integers, and invalid signatures.
- Changes to Telegram field handling should update both data models and tests.
- When changing public behavior, update docs under `docs/guide/` and API references under `docs/references/` if needed.

## Tests

- Tests use `pytest`.
- Coverage is collected for `telegram_webapp_auth`.
- Keep tests deterministic. Use fixed timestamps or `freezegun` for time-sensitive behavior.
- Add regression tests for every authentication, parsing, expiry, or serialization bug fix.
- Benchmark tests are separate and marked with `benchmark`; normal test runs exclude them.

## Documentation

- User-facing docs live under `docs/`.
- MkDocs config is in `mkdocs.yml`.
- Material icon tokens such as `:material-shield-check:` are supported through `pymdownx.emoji`.
- Keep README and docs aligned when installation, examples, public APIs, or supported Python versions change.
- Build locally with `make mkdocs-serve` for interactive docs work.

## Dependencies

- Respect `requires-python = ">=3.10,<4.0"`.
- When updating dependencies, choose versions that still support Python 3.10.
- Use `poetry update` for broad lockfile refreshes and `poetry update <package>` for scoped updates.
- Use `poetry lock` after changing dependency constraints.
- Do not add runtime dependencies unless the package imports them in production code.

## GitHub Actions

- Python checks run on pull requests for Python and dependency metadata changes.
- The CI matrix covers Python 3.10, 3.11, 3.12, 3.13, and 3.14 on Linux, macOS, and Windows.
- Workflow permissions should stay least-privilege.
- The Telegram docs update workflow uses `.github/actions/webchanges-action` and imports custom hooks with `webchanges --hooks`.
- `deduplicate_by_title` is custom hook behavior, not a valid upstream `webchanges` config key in `webchanges==3.36.1`; do not put it under `report.github_issue` unless upstream schema support is confirmed.

## Commit And PR Hygiene

- One logical change per commit.
- Target `dev` for normal pull requests.
- Use concise Conventional Commit messages such as `fix: validate duplicate init data keys` or `docs: clarify third-party validation`.
- Do not bump the package version unless explicitly asked.
- Call out security-sensitive authentication changes in the PR description.

## Things Not To Do

- Do not commit `.idea/`, `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`, `htmlcov/`, `coverage.xml`, `site/`, `dist/`, `build/`, or `*.egg-info/`.
- Do not commit local scratch files such as root-level `hooks.py` or downloaded tool binaries.
- Do not weaken validation to accept malformed Telegram init data for convenience.
- Do not change supported Python versions, package metadata, or CI matrix casually.
- Do not remove documentation examples when changing public behavior; update them instead.
