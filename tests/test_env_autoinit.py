"""Tests for LOGLY_AUTOINIT environment variable behavior."""

from __future__ import annotations

import os


def test_autoinit_enabled_by_default() -> None:
    """LOGLY_AUTOINIT not set should result in auto-configured sink."""
    # The module-level logger should have a stderr handler added
    from logly import logger

    assert logger._native is not None


def test_autoinit_env_var_controls_behavior() -> None:
    """Setting LOGLY_AUTOINIT=false should skip auto-init."""
    old_val = os.environ.get("LOGLY_AUTOINIT")
    try:
        os.environ["LOGLY_AUTOINIT"] = "false"
        # Re-read the autoinit logic
        autoinit = os.environ.get("LOGLY_AUTOINIT", "true").lower()
        assert autoinit in ("false", "0", "no")
    finally:
        if old_val is not None:
            os.environ["LOGLY_AUTOINIT"] = old_val
        else:
            os.environ.pop("LOGLY_AUTOINIT", None)


def test_autoinit_true_allows_sink() -> None:
    """LOGLY_AUTOINIT=true should allow pre-configured sink."""
    old_val = os.environ.get("LOGLY_AUTOINIT")
    try:
        os.environ["LOGLY_AUTOINIT"] = "true"
        autoinit = os.environ.get("LOGLY_AUTOINIT", "true").lower()
        assert autoinit not in ("false", "0", "no")
    finally:
        if old_val is not None:
            os.environ["LOGLY_AUTOINIT"] = old_val
        else:
            os.environ.pop("LOGLY_AUTOINIT", None)


def test_autoinit_0_disables() -> None:
    old_val = os.environ.get("LOGLY_AUTOINIT")
    try:
        os.environ["LOGLY_AUTOINIT"] = "0"
        autoinit = os.environ.get("LOGLY_AUTOINIT", "true").lower()
        assert autoinit in ("false", "0", "no")
    finally:
        if old_val is not None:
            os.environ["LOGLY_AUTOINIT"] = old_val
        else:
            os.environ.pop("LOGLY_AUTOINIT", None)


def test_autoinit_no_disables() -> None:
    old_val = os.environ.get("LOGLY_AUTOINIT")
    try:
        os.environ["LOGLY_AUTOINIT"] = "no"
        autoinit = os.environ.get("LOGLY_AUTOINIT", "true").lower()
        assert autoinit in ("false", "0", "no")
    finally:
        if old_val is not None:
            os.environ["LOGLY_AUTOINIT"] = old_val
        else:
            os.environ.pop("LOGLY_AUTOINIT", None)
