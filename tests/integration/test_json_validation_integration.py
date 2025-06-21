import pytest
import os
from sisu_bot.bot.utils import load_json_safe

def test_load_json_safe_valid(tmp_path):
    valid_json = tmp_path / "valid.json"
    valid_json.write_text('{"foo": "bar"}', encoding="utf-8")
    data = load_json_safe(valid_json, default={"fallback": 42})
    assert data["foo"] == "bar"

def test_load_json_safe_invalid(tmp_path):
    invalid_json = tmp_path / "invalid.json"
    invalid_json.write_text('{"foo": ', encoding="utf-8")  # битый json
    data = load_json_safe(invalid_json, default={"fallback": 42})
    assert data["fallback"] == 42

def test_load_json_safe_missing(tmp_path):
    missing_json = tmp_path / "missing.json"
    data = load_json_safe(missing_json, default={"fallback": 99})
    assert data["fallback"] == 99 