import json
import logging

from app.core.logging import JSONFormatter


def test_request_middleware_logs_structured_fields(client, caplog):
    with caplog.at_level(logging.INFO, logger="app.requests"):
        response = client.get("/health")

    assert response.status_code == 200

    records = [r for r in caplog.records if r.name == "app.requests"]
    assert len(records) == 1

    record = records[0]
    assert record.method == "GET"
    assert record.path == "/health"
    assert record.status_code == 200
    assert isinstance(record.duration_ms, float)


def test_json_formatter_produces_valid_json_with_extra_fields():
    record = logging.LogRecord(
        name="app.requests",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="request handled",
        args=(),
        exc_info=None,
    )
    record.method = "GET"
    record.status_code = 200

    formatted = JSONFormatter().format(record)
    payload = json.loads(formatted)

    assert payload["message"] == "request handled"
    assert payload["method"] == "GET"
    assert payload["status_code"] == 200
