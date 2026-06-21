---
name: project-release
description: Use when preparing, publishing, verifying, or recovering a telegram-webapp-auth release. Requires a confirmed SemVer tag such as v3.1.1, guides Poetry version metadata, PR flow, GitHub Release creation, PyPI publishing, MkDocs deployment, and post-release verification.
---

# Project Release

Use this skill only for `telegram-webapp-auth` release work. Require a
confirmed target version such as `v3.1.1`, and decide whether it is stable or
prerelease before preparing, publishing, or recovering a release. If the user
has not provided a target version, propose one from changes since the previous
release and ask the user to confirm it or choose a different tag before release
execution.

Release tags use Semantic Versioning 2.0.0 with the repository's `v` prefix,
for example `v3.1.1` or `v3.2.0-rc.1`. The pinned specification URL is
`https://semver.org/spec/v2.0.0.html`.

## Choosing The Target Version

- If the user provides a target tag, validate it before changing files.
- If no target tag is provided, fetch tags and inspect changes since the
  previous release tag:

```bash
git fetch origin --tags --prune
git describe --tags --abbrev=0
git log --oneline <previous-tag>..HEAD
```

- Inspect merged PR titles, dependency updates, CI changes, docs changes, and
  public API changes.
- Propose the next tag using Semantic Versioning 2.0.0:
  - `MAJOR` for backward-incompatible public API, exception, data model, or
    validation behavior changes;
  - `MINOR` for backward-compatible public API additions;
  - `PATCH` for backward-compatible fixes, dependency updates, docs, CI, or
    packaging-only changes.
- Present the proposed tag and short rationale, then ask the user to confirm it
  or choose another tag. Do not edit version metadata until the tag is
  confirmed.

## Preconditions

- Start from a clean worktree; do not overwrite unrelated user changes.
- Fetch latest refs and branch from current `dev` unless the user explicitly
  gives another base.
- Confirm no existing Git tag or GitHub Release already uses the target version.
- Before confirming the release tag, open and scan
  `https://semver.org/spec/v2.0.0.html`, then validate that the requested tag
  is the `v`-prefixed form of a SemVer 2.0.0 version.
- Before committing, open and scan
  `https://www.conventionalcommits.org/en/v1.0.0/`.

## Version Preparation

Update version metadata for the exact target version without the `v` prefix:

- `pyproject.toml` `[project].version`
- package metadata references in documentation only when they intentionally
  show the current release version

Then refresh lock metadata if Poetry reports it is needed:

```bash
poetry lock
```

Do not bump the package version outside release preparation.

## Validation

Before opening or merging the release PR, run the relevant local checks:

```bash
poetry install --no-root
make lint
make test
poetry build
poetry run mkdocs build
```

For workflow changes, also run:

```bash
make actionlint
```

If a check fails, fix the smallest release-relevant cause and rerun the
relevant command. If a check cannot be run locally, record the reason in the PR
body and final status.

## PR And Release Flow

- Commit release preparation as `chore(release): prepare vX.Y.Z`.
- For release PR creation or updates, also read and follow
  `.agents/skills/project-pull-request/SKILL.md`.
- Open the release preparation PR to `dev`.
- Include validation commands and outcomes in the PR body.
- Call out security-sensitive release workflow changes, especially `PYPI_TOKEN`,
  GitHub Release permissions, package publishing, and docs deployment.
- Wait for required PR checks to pass before merging the release preparation PR.
- After `dev` contains the release preparation commit, open a promotion PR from
  `dev` to `master`.
- Wait for required checks on the `dev` to `master` promotion PR before merging it.
- Create the GitHub Release only after the release commit is on `master`.
- Create a GitHub Release with:
  - tag `vX.Y.Z`;
  - target `master`, `origin/master`, or the exact `master` merge commit SHA;
  - title `vX.Y.Z`;
  - notes summarizing user-visible fixes, dependency updates, docs, and any
    security-relevant changes.
- Mark prerelease versions as GitHub prereleases.

Do not create a GitHub Release from a commit that exists only on `dev`; the
release tag must be reachable from `master`.

Creating a GitHub Release triggers:

- `.github/workflows/release.yml`, which builds and publishes the package to
  PyPI with Poetry and `PYPI_TOKEN`;
- `.github/workflows/docs.yml`, which rebuilds coverage docs and deploys MkDocs
  to GitHub Pages.

## Post-Release Verification

Watch the release and docs workflows until they complete. Then verify:

```bash
python3 -m pip index versions telegram-webapp-auth
python3 -m pip download --no-deps telegram-webapp-auth==X.Y.Z -d /tmp/telegram-webapp-auth-release-check
```

Also confirm:

- GitHub Release exists with the expected tag and target.
- The release tag is reachable from `origin/master`.
- The release tag tree matches `origin/master` unless a later non-release
  commit intentionally changed `master`.
- PyPI shows `telegram-webapp-auth` version `X.Y.Z`.
- Published metadata still advertises Python `>=3.10,<4.0`.
- Documentation at `https://swimmwatch.github.io/telegram-webapp-auth/` renders
  correctly after the docs workflow completes.

## Recovery

- If PyPI publishing fails because `PYPI_TOKEN` is missing or invalid, update
  the secret and rerun the failed release job.
- If a release artifact is already published to PyPI, do not delete and reuse
  the same version for code defects. Prepare a follow-up patch release.
- Rerun failed jobs only after confirming the failure is transient or caused by
  fixed external configuration.
- Keep release recovery notes in the final status report, including GitHub
  Release, PyPI, and docs deployment state.
