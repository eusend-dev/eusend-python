from typing import Any, Dict

from eusend._util import normalize


class ResponseDict(dict):
    """A dict response with the HTTP response headers attached at ``.headers``."""

    headers: Dict[str, str]


def to_response(data: Any, headers: Dict[str, str]) -> Any:
    """Normalize response keys to snake_case; wrap dicts so ``resp["id"]`` works."""
    data = normalize(data)
    if isinstance(data, dict):
        resp = ResponseDict(data)
        resp.headers = headers
        return resp
    return data
