import base64
import re
from typing import Any, Dict, Optional
from urllib.parse import urlencode

_CAMEL_BOUNDARY = re.compile(r"(?<!^)(?=[A-Z])")


def to_snake(key: str) -> str:
    return _CAMEL_BOUNDARY.sub("_", key).lower()


def normalize(obj: Any) -> Any:
    """Recursively convert response keys from camelCase to snake_case.

    The Eusend API returns camelCase for most resources but snake_case for a
    few (API keys, pagination cursors); this collapses both into snake_case so
    callers always use the same key style, e.g. ``email["created_at"]``.
    """
    if isinstance(obj, dict):
        return {to_snake(k): normalize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [normalize(v) for v in obj]
    return obj


def build_query(params: Optional[Dict[str, Any]]) -> str:
    if not params:
        return ""
    q: Dict[str, Any] = {}
    for key, value in params.items():
        if value is None:
            continue
        if isinstance(value, bool):
            value = "true" if value else "false"
        q[key] = value
    # doseq expands a list value into repeated params (``tag=a&tag=b``), which the
    # /emails tag filter uses to AND several filters. Scalars are unaffected.
    return "?" + urlencode(q, doseq=True) if q else ""


def _encode_attachment(att: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(att)
    content = out.get("content")
    if isinstance(content, (bytes, bytearray)):
        # Raw bytes are base64-encoded; a str is assumed to already be base64.
        out["content"] = base64.b64encode(bytes(content)).decode("ascii")
    return out


def prepare_email_payload(params: Dict[str, Any], allow_scheduling: bool = True) -> Dict[str, Any]:
    payload = dict(params)
    attachments = payload.get("attachments")
    if attachments:
        payload["attachments"] = [_encode_attachment(a) for a in attachments]
    if not allow_scheduling:
        # The batch endpoint rejects attachments and scheduling.
        payload.pop("attachments", None)
        payload.pop("scheduled_at", None)
    return payload
