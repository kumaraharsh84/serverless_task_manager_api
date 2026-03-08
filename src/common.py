import base64
import json
import logging
import os
from datetime import datetime, timezone
from typing import Any

ALLOWED_STATUS = {"todo", "in-progress", "done"}
ALLOWED_PRIORITY = {"low", "medium", "high"}

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def response(status_code: int, body: dict[str, Any]) -> dict[str, Any]:
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }


def parse_json_body(event: dict[str, Any]) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    try:
        return json.loads(event.get("body") or "{}"), None
    except json.JSONDecodeError:
        return None, response(400, {"message": "Invalid JSON payload"})


def validate_due_date(value: Any) -> bool:
    if value is None:
        return True
    if not isinstance(value, str):
        return False
    raw = value.strip()
    if not raw:
        return False
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    try:
        datetime.fromisoformat(raw)
        return True
    except ValueError:
        return False


def authorize(event: dict[str, Any]) -> dict[str, Any] | None:
    expected = os.environ.get("API_TOKEN", "").strip()
    if not expected:
        return None

    headers = event.get("headers") or {}
    supplied = headers.get("x-api-key") or headers.get("X-API-Key") or headers.get("authorization")
    if supplied != expected:
        return response(401, {"message": "Unauthorized"})
    return None


def parse_limit(query_params: dict[str, Any]) -> tuple[int | None, dict[str, Any] | None]:
    raw_limit = (query_params or {}).get("limit")
    if raw_limit is None:
        return 10, None
    try:
        limit = int(raw_limit)
    except (TypeError, ValueError):
        return None, response(400, {"message": "limit must be an integer"})
    if limit < 1 or limit > 50:
        return None, response(400, {"message": "limit must be between 1 and 50"})
    return limit, None


def encode_last_key(last_key: dict[str, Any] | None) -> str | None:
    if not last_key:
        return None
    raw = json.dumps(last_key).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("utf-8")


def decode_last_key(raw: str | None) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    if not raw:
        return None, None
    try:
        decoded = base64.urlsafe_b64decode(raw.encode("utf-8")).decode("utf-8")
        return json.loads(decoded), None
    except (ValueError, json.JSONDecodeError):
        return None, response(400, {"message": "Invalid lastKey"})
