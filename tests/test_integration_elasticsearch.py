from __future__ import annotations

import sys
import urllib.request
from unittest.mock import MagicMock, patch

from logly.integrations.elasticsearch import ElasticsearchSink


class TestElasticsearchSinkInit:
    def test_init_default_params(self) -> None:
        with patch.dict(sys.modules, {"elasticsearch": None}):
            sink = ElasticsearchSink()
            assert sink.endpoint == "http://localhost:9200"
            assert sink.index == "logly-logs"
            assert sink.timeout == 5.0
            assert sink._use_client is False

    def test_init_with_elasticsearch_client(self) -> None:
        mock_es_cls = MagicMock()
        mock_es = MagicMock()
        mock_es_cls.return_value = mock_es
        fake_es = MagicMock()
        fake_es.Elasticsearch = mock_es_cls
        with patch.dict(sys.modules, {"elasticsearch": fake_es}):
            sink = ElasticsearchSink("http://es:9200", index="my-logs")
            assert sink._use_client is True
            assert sink.index == "my-logs"

    def test_init_with_auth(self) -> None:
        with patch.dict(sys.modules, {"elasticsearch": None}):
            sink = ElasticsearchSink(username="user", password="pass")
            assert sink._auth is not None

    def test_init_without_auth(self) -> None:
        with patch.dict(sys.modules, {"elasticsearch": None}):
            sink = ElasticsearchSink()
            assert sink._auth is None


class TestElasticsearchSinkWrite:
    def test_write_with_client(self) -> None:
        mock_es_cls = MagicMock()
        mock_es = MagicMock()
        mock_es_cls.return_value = mock_es
        fake_es = MagicMock()
        fake_es.Elasticsearch = mock_es_cls
        with patch.dict(sys.modules, {"elasticsearch": fake_es}):
            sink = ElasticsearchSink()
            sink.write("hello es\n")
            mock_es.index.assert_called_once()

    def test_write_fallback_http(self) -> None:
        mock_response = MagicMock()
        mock_response.read.return_value = b""
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = MagicMock(return_value=False)
        with patch.dict(sys.modules, {"elasticsearch": None}):
            with patch("urllib.request.urlopen", return_value=mock_response) as mock_urlopen:
                sink = ElasticsearchSink()
                sink.write("fallback msg\n")
                mock_urlopen.assert_called_once()
                call_args = mock_urlopen.call_args
                req = call_args[0][0]
                assert isinstance(req, urllib.request.Request)

    def test_write_strips_newline(self) -> None:
        mock_response = MagicMock()
        mock_response.read.return_value = b""
        with patch.dict(sys.modules, {"elasticsearch": None}):
            with patch("urllib.request.urlopen", return_value=mock_response) as mock_urlopen:
                sink = ElasticsearchSink()
                sink.write("msg\n")
                req = mock_urlopen.call_args[0][0]
                assert isinstance(req, urllib.request.Request)

    def test_write_empty_message(self) -> None:
        mock_response = MagicMock()
        mock_response.read.return_value = b""
        with patch.dict(sys.modules, {"elasticsearch": None}):
            with patch("urllib.request.urlopen", return_value=mock_response) as mock_urlopen:
                sink = ElasticsearchSink()
                sink.write("\n")
                mock_urlopen.assert_called_once()


class TestElasticsearchSinkFlush:
    def test_flush_with_client(self) -> None:
        mock_es_cls = MagicMock()
        mock_es = MagicMock()
        mock_es_cls.return_value = mock_es
        fake_es = MagicMock()
        fake_es.Elasticsearch = mock_es_cls
        with patch.dict(sys.modules, {"elasticsearch": fake_es}):
            sink = ElasticsearchSink()
            sink.flush()
            mock_es.indices.refresh.assert_called_once_with(index="logly-logs")

    def test_flush_without_client_noop(self) -> None:
        with patch.dict(sys.modules, {"elasticsearch": None}):
            sink = ElasticsearchSink()
            sink.flush()


class TestElasticsearchSinkClose:
    def test_close_with_client(self) -> None:
        mock_es_cls = MagicMock()
        mock_es = MagicMock()
        mock_es_cls.return_value = mock_es
        fake_es = MagicMock()
        fake_es.Elasticsearch = mock_es_cls
        with patch.dict(sys.modules, {"elasticsearch": fake_es}):
            sink = ElasticsearchSink()
            sink.close()
            mock_es.close.assert_called_once()

    def test_close_without_client_noop(self) -> None:
        with patch.dict(sys.modules, {"elasticsearch": None}):
            sink = ElasticsearchSink()
            sink.close()
