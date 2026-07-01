"""Tests for Email integration."""

from __future__ import annotations

from unittest.mock import MagicMock, patch


class TestEmailHandlerInit:
    def test_init_defaults(self) -> None:
        from logly.integrations.email import EmailHandler

        handler = EmailHandler()
        assert handler.smtp_host == "localhost"
        assert handler.smtp_port == 25
        assert handler.from_addr == ""
        assert handler.to_addrs == []
        assert handler.username is None
        assert handler.password is None
        assert handler.use_tls is True
        assert handler.use_ssl is False
        assert handler.timeout == 30.0
        assert handler.subject_prefix == "[Logly]"

    def test_init_custom_params(self) -> None:
        from logly.integrations.email import EmailHandler

        handler = EmailHandler(
            "smtp.gmail.com",
            587,
            from_addr="a@b.com",
            to_addrs=["c@d.com"],
            username="user",
            password="pass",
            use_tls=False,
            use_ssl=True,
            timeout=10.0,
            subject_prefix="[Test]",
        )
        assert handler.smtp_host == "smtp.gmail.com"
        assert handler.smtp_port == 587
        assert handler.from_addr == "a@b.com"
        assert handler.to_addrs == ["c@d.com"]
        assert handler.use_tls is False
        assert handler.use_ssl is True
        assert handler.subject_prefix == "[Test]"


class TestEmailHandlerWrite:
    def test_write_missing_from_addr_noop(self) -> None:
        from logly.integrations.email import EmailHandler

        handler = EmailHandler(to_addrs=["recipient@test.com"])
        handler.write("msg")  # should not raise

    def test_write_missing_to_addrs_noop(self) -> None:
        from logly.integrations.email import EmailHandler

        handler = EmailHandler(from_addr="sender@test.com")
        handler.write("msg")  # should not raise

    def test_write_empty_addrs_noop(self) -> None:
        from logly.integrations.email import EmailHandler

        handler = EmailHandler()
        handler.write("msg")

    @patch("logly.integrations.email.smtplib.SMTP")
    def test_write_sends_email(self, MockSMTP: MagicMock) -> None:
        from logly.integrations.email import EmailHandler

        mock_server = MagicMock()
        MockSMTP.return_value = mock_server

        handler = EmailHandler(
            "smtp.test.com",
            587,
            from_addr="a@b.com",
            to_addrs=["c@d.com"],
            username="user",
            password="pass",
        )
        handler.write("hello email\n")

        MockSMTP.assert_called_once_with("smtp.test.com", 587, timeout=30.0)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("user", "pass")
        mock_server.sendmail.assert_called_once()
        mock_server.quit.assert_called_once()

    @patch("logly.integrations.email.smtplib.SMTP_SSL")
    def test_write_ssl_mode(self, MockSMTP_SSL: MagicMock) -> None:
        from logly.integrations.email import EmailHandler

        mock_server = MagicMock()
        MockSMTP_SSL.return_value = mock_server

        handler = EmailHandler(
            "smtp.test.com",
            465,
            from_addr="a@b.com",
            to_addrs=["c@d.com"],
            use_ssl=True,
        )
        handler.write("ssl msg\n")

        MockSMTP_SSL.assert_called_once()
        mock_server.quit.assert_called_once()

    @patch("logly.integrations.email.smtplib.SMTP")
    def test_write_exception_swallows(self, MockSMTP: MagicMock) -> None:
        from logly.integrations.email import EmailHandler

        MockSMTP.side_effect = ConnectionError("fail")

        handler = EmailHandler(
            from_addr="a@b.com",
            to_addrs=["c@d.com"],
        )
        handler.write("msg")
        # Should not raise


class TestEmailHandlerFlushClose:
    def test_flush_noop(self) -> None:
        from logly.integrations.email import EmailHandler

        handler = EmailHandler()
        handler.flush()

    def test_close_noop(self) -> None:
        from logly.integrations.email import EmailHandler

        handler = EmailHandler()
        handler.close()
