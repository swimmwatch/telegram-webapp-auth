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


class GitHubIssueReporter(MarkdownReporter):
    """Reporter that submits issues to a GitHub repository."""

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
        },
    )

    _API_URL = "https://api.github.com/repos/{owner}/{repo}/issues"
    _CONTENT_LIMIT = 65536  # GitHub issue body limit

    def _format_title(self) -> str:
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
        format_content = self.config.get("format_content", None)
        if format_content:
            return format_content.format(content=content)
        return content

    def _create_issue(self, content: str):
        url = self._API_URL.format(owner=self.config["owner"], repo=self.config["repo"])
        headers = {"Authorization": f"token {self.config['token']}", "Accept": "application/vnd.github.v3+json"}

        title = self._format_title()
        content = self._format_text(content)
        issue_data = {"title": title, "body": content, "labels": self.config.get("labels", [])}
        response = self.post_client(url, headers=headers, json=issue_data)

        if response.status_code == HTTPStatus.CREATED:
            logger.info("Issue created successfully.")
        else:
            json_object = json.loads(response.text)
            json_formatted_str = json.dumps(json_object, indent=2)
            raise RuntimeError(f"Failed to create issue: {json_formatted_str}")

    def submit(
        self,
        max_length: int | None = None,
        **kwargs: typing.Any,
    ) -> typing.Iterator[str]:
        """Submit the report as a GitHub issue."""
        lines = super().submit(max_length, **kwargs)
        content = "\n".join(lines)
        if not content:
            logger.info("No content to submit.")
            return

        if len(content) > self._CONTENT_LIMIT:
            logger.warning("Content exceeds GitHub's issue body limit (65536 characters). Truncating content.")
            content = content[: self._CONTENT_LIMIT]

        logger.info("Submitting issue to GitHub...")
        self._create_issue(content)

        return lines


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

        lines = data.splitlines(keepends=True)
        filtered_lines = get_lines_between(lines, start_pattern, end_pattern)

        return (
            "\n".join(filtered_lines),
            mime_type,
        )
