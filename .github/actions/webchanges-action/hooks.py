"""Custom reporters and filters for webchanges utility."""

import json
import logging
import re
import typing
from datetime import datetime
from datetime import timezone
from http import HTTPStatus
from typing import TypedDict

from webchanges.filters import FilterBase
from webchanges.reporters import MarkdownReporter

logger = logging.getLogger(__name__)


def _patch_webchanges_config_schema() -> None:
    """Patch webchanges github_issue schema at runtime to accept custom dedupe option."""
    try:
        from webchanges import storage
        from webchanges.storage import _config as webchanges_config
    except Exception as exc:  # pragma: no cover - import issues should not break the action
        logger.debug("Cannot import webchanges config schema module: %s", exc)
        return

    config = getattr(webchanges_config, "_ConfigReportGithubIssue", None)
    if config is None:
        return

    annotations = getattr(config, "__annotations__", None)
    if not isinstance(annotations, dict):
        return

    annotations["deduplicate_by_title"] = bool

    required_keys = getattr(config, "__required_keys__", frozenset())
    optional_keys = getattr(config, "__optional_keys__", frozenset())

    if isinstance(required_keys, frozenset):
        required_keys = set(required_keys)
    elif isinstance(required_keys, (set, list, tuple)):
        required_keys = set(required_keys)
    else:
        required_keys = set()

    if isinstance(optional_keys, frozenset):
        optional_keys = set(optional_keys)
    elif isinstance(optional_keys, (set, list, tuple)):
        optional_keys = set(optional_keys)
    else:
        optional_keys = set()

    required_keys.discard("deduplicate_by_title")
    optional_keys.add("deduplicate_by_title")
    config.__required_keys__ = frozenset(required_keys)
    config.__optional_keys__ = frozenset(optional_keys)

    if hasattr(storage, "_config") and isinstance(webchanges_config.DEFAULT_CONFIG, dict):
        github_issue_defaults = webchanges_config.DEFAULT_CONFIG.get("report", {}).get("github_issue")
        if isinstance(github_issue_defaults, dict):
            github_issue_defaults.setdefault("deduplicate_by_title", False)


_patch_webchanges_config_schema()


class GitHubIssueReporter(MarkdownReporter):
    """Reporter that submits reports as issues to a GitHub repository."""

    __kind__ = "github_issue"

    config: TypedDict(
        "_ConfigReportGithubIssue",
        {
            "enabled": bool,
            "token": str,
            "owner": str,
            "repo": str,
            "title": typing.Optional[str],
            "labels": list[str],
            "format_dt": typing.Optional[str],
            "format_content": typing.Optional[str],
            "assignees": typing.Optional[typing.Sequence[str]],
            "type": typing.Optional[str],
            "milestone": typing.Optional[str],
            "deduplicate_by_title": typing.Optional[bool],
        },
    )

    _ISSUES_API_URL = "https://api.github.com/repos/{owner}/{repo}/issues"
    _ISSUE_API_URL = "https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}"
    _CONTENT_LIMIT = 65536  # GitHub issue body limit

    def _headers(self) -> dict[str, str]:
        """Return GitHub API headers."""
        return {
            "Authorization": f"Bearer {self.config['token']}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def _request(self, method: str, url: str, **kwargs: typing.Any):
        """Perform an HTTP request with the client provided by webchanges."""
        request = getattr(self.http_client, method.lower())
        return request(url, **kwargs)

    @staticmethod
    def _response_json(response: typing.Any) -> typing.Any:
        """Return decoded JSON when possible."""
        try:
            return response.json()
        except ValueError:
            return response.text

    @classmethod
    def _raise_for_response(cls, action: str, response: typing.Any, expected: set[HTTPStatus]) -> None:
        """Raise a useful error for unexpected GitHub API responses."""
        if response.status_code in expected:
            return

        response_body = cls._response_json(response)
        response_text = json.dumps(response_body, indent=2) if not isinstance(response_body, str) else response_body
        raise RuntimeError(f"Failed to {action}: {response_text}")

    @staticmethod
    def _next_link(link_header: str | None) -> str | None:
        """Extract the next pagination link from a GitHub Link header."""
        if not link_header:
            return None

        for part in link_header.split(","):
            url_part, _, rel_part = part.partition(";")
            if 'rel="next"' in rel_part:
                return url_part.strip()[1:-1]

        return None

    def _format_title(self) -> str:
        """Format the title of the issue."""
        now = datetime.now(tz=timezone.utc)
        format_dt = self.config.get("format_dt", "%Y-%m-%d %H:%M:%S")

        title = self.config.get("title")
        if not title:
            title = "WebChanges report"
        else:
            dt = now.strftime(format_dt)
            title = title.format(dt=dt)

        return title

    def _format_text(self, content: str) -> str:
        """Format the content of the issue."""
        format_content = self.config.get("format_content")
        content = content[: self._CONTENT_LIMIT]
        if format_content:
            placeholder = "{content}"
            max_content_length = self._CONTENT_LIMIT - (len(format_content) - len(placeholder))
            content = content[:max_content_length]
            content = format_content.format(content=content)

        return content

    def _find_open_issue_by_title(self, title: str) -> int | None:
        """Find an open issue with exactly the same title."""
        url = self._ISSUES_API_URL.format(owner=self.config["owner"], repo=self.config["repo"])
        params: dict[str, typing.Any] | None = {"state": "open", "per_page": 100}

        while url:
            response = self._request("get", url, headers=self._headers(), params=params)
            self._raise_for_response("list issues", response, {HTTPStatus.OK})

            for issue in self._response_json(response):
                if issue.get("pull_request"):
                    continue
                if issue.get("title") == title:
                    return typing.cast(int, issue["number"])

            url = self._next_link(response.headers.get("link"))
            params = None

        return None

    def _issue_data(self, title: str, content: str) -> dict[str, typing.Any]:
        """Build issue data for GitHub API requests."""
        issue_data: dict[str, typing.Any] = {
            "title": title,
            "body": content,
            "labels": self.config.get("labels", []),
        }

        assignees = self.config.get("assignees", [])
        if assignees:
            issue_data["assignees"] = assignees

        type_ = self.config.get("type")
        if type_:
            issue_data["type"] = type_

        milestone = self.config.get("milestone")
        if milestone:
            issue_data["milestone"] = milestone

        return issue_data

    def _create_issue(self, title: str, content: str) -> None:
        """Create an issue on GitHub."""
        url = self._ISSUES_API_URL.format(owner=self.config["owner"], repo=self.config["repo"])
        response = self._request("post", url, headers=self._headers(), json=self._issue_data(title, content))
        self._raise_for_response("create issue", response, {HTTPStatus.CREATED})
        logger.info("Issue created successfully.")

    def _update_issue(self, issue_number: int, content: str) -> None:
        """Update an existing GitHub issue body."""
        url = self._ISSUE_API_URL.format(
            owner=self.config["owner"],
            repo=self.config["repo"],
            issue_number=issue_number,
        )
        response = self._request("patch", url, headers=self._headers(), json={"body": content})
        self._raise_for_response("update issue", response, {HTTPStatus.OK})
        logger.info("Issue #%s updated successfully.", issue_number)

    def _create_or_update_issue(self, content: str) -> None:
        """Create a GitHub issue or update an existing same-title issue."""
        title = self._format_title()
        content = self._format_text(content)

        if self.config.get("deduplicate_by_title", False):
            issue_number = self._find_open_issue_by_title(title)
            if issue_number is not None:
                self._update_issue(issue_number, content)
                return

        self._create_issue(title, content)

    def submit(
        self,
        max_length: int | None = None,
        **kwargs: typing.Any,
    ) -> typing.Iterator[str]:
        """Submit the report to GitHub as an issue."""
        lines = list(super().submit(max_length, **kwargs))
        content = "\n".join(lines)
        if not content:
            logger.info("No content to submit.")
            return iter(())

        logger.info("Submitting issue to GitHub...")
        self._create_or_update_issue(content)

        return iter(lines)


def get_lines_between(
    lines: typing.Sequence[str],
    start_pattern: str | None = None,
    end_pattern: str | None = None,
) -> typing.Generator[str, None, None]:
    """Yield lines between start and end patterns."""
    started = False
    for line in lines:
        if not started:
            if start_pattern and re.search(start_pattern, line):
                started = True
            continue
        if end_pattern and re.search(end_pattern, line):
            break

        yield line


class BetweenLinesFilter(FilterBase):
    """Filter to extract lines between two patterns."""

    __kind__ = "between"

    __supported_subfilters__ = {
        "start": "Pattern to match the start line.",
        "end": "Pattern to match the end line.",
    }

    __default_subfilter__ = "indent"

    @staticmethod
    def filter(
        data: str | bytes,
        mime_type: str,
        subfilter: dict[str, typing.Any],
    ) -> tuple[str | bytes, str]:
        """Filter lines between start and end patterns."""
        start_pattern = subfilter.get("start")
        end_pattern = subfilter.get("end")

        is_bytes = isinstance(data, bytes)
        if is_bytes:
            data = data.decode("utf-8")

        lines = data.splitlines(keepends=True)
        filtered_lines = get_lines_between(lines, start_pattern, end_pattern)
        filtered_data = "".join(filtered_lines)

        return (
            filtered_data.encode("utf-8") if is_bytes else filtered_data,
            mime_type,
        )
