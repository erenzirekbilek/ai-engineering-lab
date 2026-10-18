"""Log yazicinin JSONL urettigini ve hata durumunda sessizce gectigini dogrular."""

import json

from tools import logging_utils


def test_log_event_writes_one_json_line(tmp_path, monkeypatch):
    log_file = tmp_path / "usage.jsonl"
    monkeypatch.setattr(logging_utils, "LOGS_DIR", tmp_path)
    monkeypatch.setattr(logging_utils, "USAGE_LOG", log_file)

    logging_utils.log_event("chat.ok", model="gpt-4o-mini", input_tokens=12)

    record = json.loads(log_file.read_text(encoding="utf-8").strip())
    assert record["event"] == "chat.ok"
    assert record["model"] == "gpt-4o-mini"
    assert record["input_tokens"] == 12
    assert "ts" in record


def test_log_event_appends_without_overwriting(tmp_path, monkeypatch):
    log_file = tmp_path / "usage.jsonl"
    monkeypatch.setattr(logging_utils, "LOGS_DIR", tmp_path)
    monkeypatch.setattr(logging_utils, "USAGE_LOG", log_file)

    logging_utils.log_event("chat.ok", i=1)
    logging_utils.log_event("chat.error", i=2)

    events = logging_utils.read_events()
    assert [e["event"] for e in events] == ["chat.ok", "chat.error"]


def test_log_event_never_raises_when_target_is_unwritable(tmp_path, monkeypatch):
    # USAGE_LOG bir klasore isaret ederse open() IsADirectoryError (OSError) atar.
    blocked = tmp_path / "bir_klasor"
    blocked.mkdir()
    monkeypatch.setattr(logging_utils, "LOGS_DIR", tmp_path)
    monkeypatch.setattr(logging_utils, "USAGE_LOG", blocked)

    logging_utils.log_event("chat.error", kind="auth")  # patlamamali


def test_read_events_on_missing_file_is_empty(tmp_path, monkeypatch):
    monkeypatch.setattr(logging_utils, "USAGE_LOG", tmp_path / "yok.jsonl")
    assert logging_utils.read_events() == []
