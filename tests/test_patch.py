"""Tests for record patching."""

from __future__ import annotations

from typing import Any

from logly import logger


class TestPatch:
    """Tests for patch() record mutation."""

    def test_patch_modifies_record(self) -> None:
        """Patcher should be able to modify record fields."""
        messages = []

        def capture(msg: str) -> None:
            messages.append(msg)

        def add_env(record: dict[str, Any]) -> None:
            record["extra"]["env"] = "test"

        patched = logger.patch(add_env)
        sink_id = patched.add(capture, format="{extra[env]} | {message}")
        patched.info("patched message")
        patched.remove(sink_id)
        assert len(messages) >= 1
        assert "test" in messages[0]

    def test_patch_multiple_patchers(self) -> None:
        """Multiple patchers should all be applied."""
        messages = []

        def capture(msg: str) -> None:
            messages.append(msg)

        def add_a(record: dict[str, Any]) -> None:
            record["extra"]["a"] = "1"

        def add_b(record: dict[str, Any]) -> None:
            record["extra"]["b"] = "2"

        patched = logger.patch(add_a).patch(add_b)
        sink_id = patched.add(
            capture,
            format="{extra[a]}:{extra[b]} | {message}",
        )
        patched.info("multi-patch")
        patched.remove(sink_id)
        assert len(messages) >= 1
        assert "1:2" in messages[0]

    def test_patch_does_not_mutate_parent(self) -> None:
        """Patching a clone should not affect the parent logger."""
        messages_parent = []

        def capture_parent(msg: str) -> None:
            messages_parent.append(msg)

        def add_field(record: dict[str, Any]) -> None:
            record["extra"]["patched"] = "yes"

        sink_id = logger.add(capture_parent, format="{message}")
        patched = logger.patch(add_field)
        patched.info("patched")

        logger.remove(sink_id)

        assert any("patched" in m for m in messages_parent)
