---
name: project-pull-request
description: Use when creating, updating, or reviewing a telegram-webapp-auth GitHub Pull Request. Defines dev-targeted branch flow, maintenance-mode constraints, assignee defaults, Conventional-style titles, required PR template sections, test evidence, security notes, and post-create reporting rules.
---

# Project Pull Request

Use this skill for `telegram-webapp-auth` Pull Request work. The repository's
`.github/PULL_REQUEST_TEMPLATE.md` is the required PR body format; do not
replace it with a second template.

## Preconditions

- Inspect `git status`, current branch, upstream tracking, and diff before
  creating or updating a PR.
- Use `dev` as the base branch unless the user explicitly gives another base.
- For release promotion, use `master` as the base branch and `dev` as the head branch.
- Do not open a PR from `dev`, `master`, or a release branch except for the explicit `dev` to `master` release promotion PR.
- This project is in maintenance mode. Keep PRs focused on bug fixes,
  dependency updates, CI fixes, documentation corrections, or security fixes.
- Push the current feature branch to `origin` before creating the PR.
- Create PRs ready for review by default. Use draft only when the user
  explicitly asks for a draft PR.

## Assignee

- Assign the PR to the authenticated GitHub user by default. Resolve the login
  with `gh api user --jq .login` or the equivalent GitHub connector identity.
- For this repository, the expected default assignee is `swimmwatch` unless the
  user explicitly requests another assignee.
- If the assignee cannot be resolved or GitHub rejects it, report the blocker
  and leave the PR otherwise complete.

## Title

- Use a concise Conventional-style title, such as
  `fix: reject duplicate init data keys`, `docs: clarify third-party validation`,
  or `ci: fix Telegram docs update workflow`.
- Use imperative or present-tense wording after the conventional prefix.
- Make the title describe the main user-visible or maintenance change, not a
  test result or implementation detail.

## Body

Fill every section from `.github/PULL_REQUEST_TEMPLATE.md`:

- `Description`: explain what changed and why in 2-4 concrete bullets or short
  paragraphs.
- `Related Issue`: link the open issue when one exists. If there is no issue,
  state that clearly instead of leaving placeholder text.
- `Motivation and Context`: describe the bug, CI failure, dependency need, or
  documentation gap being addressed.
- `How Has This Been Tested (if appropriate)?`: list exact commands and
  outcomes. If relevant checks were skipped, state why.
- `Screenshots (if appropriate)`: include only for rendered documentation or UI
  changes; otherwise mark as not applicable.

Do not leave HTML comments or placeholder text in the submitted PR body.

## Test Evidence

Choose evidence based on the change:

- Auth/parser/model changes: run targeted `pytest`, then `make test` when
  feasible.
- Type or style changes: run `make lint` or the relevant `mypy`, `flake8`, and
  `black --check` commands.
- Documentation changes: run `poetry run mkdocs build` or `make mkdocs-serve`
  when visual review is needed.
- Dependency changes: run `poetry update <package>` or `poetry update`, then
  report the package changes and any tests run.
- Workflow changes: run `make actionlint` if Docker is available, or state why
  local action linting was not run.

## Security Notes

Call out security-sensitive areas explicitly when relevant:

- Telegram init data parsing, HMAC validation, Ed25519 validation, expiry
  checks, and unknown-field handling.
- GitHub Actions permissions, `GITHUB_TOKEN`, `PYPI_TOKEN`, Codecov token, and
  docs-update issue creation.
- Runtime dependency changes, especially `cryptography`.

## Create Or Update

- Prefer the available GitHub app or connector. Use `gh` when connector support
  is unavailable or insufficient.
- If a PR already exists for the branch, update its title/body instead of
  creating a duplicate.
- After creating or updating the PR, report the PR URL, base/head branches,
  title, assignee, whether it is draft or ready for review, and any skipped
  checks.
