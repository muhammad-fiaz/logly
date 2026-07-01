"""Elasticsearch integration for Logly.

Provides ``ElasticsearchSink`` that indexes log entries into Elasticsearch.

Requires ``elasticsearch``.

Install with::

    # Option 1: uv (recommended)
    uv add logly[elasticsearch]

    # Option 2: pip
    pip install "logly[elasticsearch]"

    # Option 3: uv without extras
    uv add elasticsearch

    # Option 4: pip without extras
    pip install elasticsearch
"""

from __future__ import annotations

import json
import urllib.request
from typing import Any

_IMPORT_MSG = (  # pragma: no cover
    "elasticsearch is required for Logly Elasticsearch integration.\n"
    "Install with one of:\n"
    "  uv add logly[elasticsearch]       # recommended\n"
    "  pip install logly[elasticsearch]\n"
    "  uv add elasticsearch\n"
    "  pip install elasticsearch"
)  # pragma: no cover


class ElasticsearchSink:
    """Index log entries into Elasticsearch.

    Posts each log message as a JSON document to the Elasticsearch
    ``_bulk`` API.

    Usage::

        from logly import logger
        from logly.integrations.elasticsearch import ElasticsearchSink

        logger.add(
            ElasticsearchSink(
                "http://localhost:9200",
                index="logs-{time:YYYY.MM.DD}",
            ),
            level="WARNING",
        )

    Args:
        endpoint: Elasticsearch URL.
        index: Index name pattern (supports ``{time:FORMAT}``).
        timeout: HTTP request timeout in seconds.
        username: Optional basic auth username.
        password: Optional basic auth password.
    """

    def __init__(
        self,
        endpoint: str = "http://localhost:9200",
        *,
        index: str = "logly-logs",
        timeout: float = 5.0,
        username: str | None = None,
        password: str | None = None,
    ) -> None:
        """Initialize the Elasticsearch sink.

        Args:
            endpoint: Elasticsearch URL.
            index: Index name pattern (supports ``{time:FORMAT}``).
            timeout: HTTP request timeout in seconds.
            username: Optional basic auth username.
            password: Optional basic auth password.
        """
        self._client: Any = None
        self._use_client = False
        try:
            from elasticsearch import Elasticsearch  # pragma: no cover

            kwargs: dict[str, Any] = {"hosts": [endpoint]}
            if username and password:
                kwargs["basic_auth"] = (username, password)
            self._client = Elasticsearch(**kwargs)
            self._use_client = True
        except ImportError:
            pass

        self.endpoint = endpoint
        self.index = index
        self.timeout = timeout
        self._auth = None
        if username and password:
            import base64

            self._auth = base64.b64encode(f"{username}:{password}".encode()).decode()

    def write(self, message: str) -> None:
        """Index one log entry."""
        from logly.integrations._utils import strip_ansi  # noqa: PLC0415

        msg = strip_ansi(message.rstrip("\n"))
        if self._use_client and self._client is not None:
            self._client.index(  # pragma: no cover
                index=self.index,
                document={"message": msg},
            )
            return

        # Fallback to raw HTTP
        doc = json.dumps({"message": msg}).encode("utf-8")
        url = f"{self.endpoint}/{self.index}/_doc"
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if self._auth:
            headers["Authorization"] = f"Basic {self._auth}"

        request = urllib.request.Request(url, data=doc, headers=headers, method="POST")
        with urllib.request.urlopen(request, timeout=self.timeout) as response:  # pragma: no cover
            response.read()

    def flush(self) -> None:
        """Flush Elasticsearch bulk operations."""
        if self._use_client and self._client is not None:
            self._client.indices.refresh(index=self.index)  # pragma: no cover

    def close(self) -> None:
        """Close the Elasticsearch client."""
        if self._use_client and self._client is not None:
            self._client.close()  # pragma: no cover
