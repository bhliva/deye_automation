import pytest
from unittest.mock import patch
from config import _require, DEYE_HOST


def test_require_raises_for_missing_key():
    with patch("config.os.getenv", return_value=None):
        with pytest.raises(RuntimeError, match="Missing required env var: SOME_KEY"):
            _require("SOME_KEY")


def test_require_raises_for_empty_string():
    with patch("config.os.getenv", return_value=""):
        with pytest.raises(RuntimeError, match="Missing required env var: SOME_KEY"):
            _require("SOME_KEY")


def test_require_returns_value():
    with patch("config.os.getenv", return_value="the_value"):
        assert _require("SOME_KEY") == "the_value"


def test_deye_host_defaults_to_eu1():
    assert DEYE_HOST == "https://eu1-developer.deyecloud.com"
