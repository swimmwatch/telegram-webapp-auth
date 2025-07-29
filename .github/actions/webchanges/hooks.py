import json
import logging
import typing
from datetime import datetime
from datetime import timezone
from http import HTTPStatus
from typing import TypedDict

from webchanges.reporters import MarkdownReporter

logger = logging.getLogger(__name__)


class GitHubIssueReporter(MarkdownReporter):
    __kind__ = 'github_issue'

    config: TypedDict(
        '_ConfigReportGithubIssue',
        {
            'enabled': bool,
            'token': str,
            'owner': str,
            'repo': str,
            'title': typing.Optional[str],
            'labels': list[str],
            'format_dt': typing.Optional[str],
        },
    )

    _API_URL = 'https://api.github.com/repos/{owner}/{repo}/issues'

    def _format_title(self) -> str:
        now = datetime.now(tz=timezone.utc)
        format_dt = self.config.get('format_dt', '%Y-%m-%d %H:%M:%S')

        title = self.config.get('title')
        if not title:
            title = "WebChanges report"
        else:
            dt = now.strftime(format_dt)
            title = title.format(dt=dt)

        return title

    def _post_request(self, content: str):
        url = self._API_URL.format(
            owner=self.config['owner'],
            repo=self.config['repo']
        )
        headers = {
            "Authorization": f"token {self.config['token']}",
            "Accept": "application/vnd.github.v3+json"
        }

        title = self._format_title()
        issue_data = {
            "title": title,
            "body": content,
            "labels": self.config.get('labels', [])
        }
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
        lines = super().submit(max_length, **kwargs)
        content = '\n'.join(lines)
        # if not content:
        #     logger.info("No content to submit.")
        #     return

        logger.info("Submitting issue to GitHub...")
        self._post_request(content)

        return lines
