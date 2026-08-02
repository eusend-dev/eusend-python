import json
import urllib.error
import urllib.request
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union, cast

from eusend._compat import Literal

import eusend
from eusend._response import to_response
from eusend.exceptions import (
    ApplicationError,
    MissingApiKeyError,
    NoContentError,
    raise_for_code_and_type,
)
from eusend.version import get_version

RequestVerb = Literal["get", "post", "patch", "delete"]
T = TypeVar("T")

ParamsType = Union[Dict[str, Any], List[Any]]

DEFAULT_TIMEOUT = 30.0


class Request(Generic[T]):
    """A single HTTP request to the Eusend API.

    Configuration (``eusend.api_key``, ``eusend.api_url``) is read at call time
    from the module, mirroring resend-python.
    """

    def __init__(
        self,
        path: str,
        params: Optional[ParamsType] = None,
        verb: RequestVerb = "get",
        options: Optional[Dict[str, Any]] = None,
    ):
        self.path = path
        self.params = params
        self.verb = verb
        self.options = options or {}

    def perform(self) -> Optional[T]:
        if not eusend.api_key:
            raise MissingApiKeyError()

        url = f"{eusend.api_url}{self.path}"
        data = json.dumps(self.params).encode("utf-8") if self.params is not None else None

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {eusend.api_key}",
            "User-Agent": f"eusend-python:{get_version()}",
        }
        if self.verb == "post" and self.options.get("idempotency_key"):
            headers["Idempotency-Key"] = str(self.options["idempotency_key"])

        req = urllib.request.Request(url, data=data, method=self.verb.upper(), headers=headers)

        try:
            with urllib.request.urlopen(req, timeout=DEFAULT_TIMEOUT) as resp:
                raw = resp.read()
                if resp.status == 204 or not raw:
                    return None
                return cast(T, to_response(json.loads(raw), dict(resp.headers)))
        except urllib.error.HTTPError as exc:
            raw = exc.read()
            message = "Request failed"
            code = "INTERNAL_ERROR"
            try:
                payload = json.loads(raw)
                message = payload.get("error") or message
                code = payload.get("code") or code
            except (ValueError, AttributeError):
                pass
            raise_for_code_and_type(
                code=code,
                message=message,
                status_code=exc.code,
                headers=dict(exc.headers or {}),
            )
        except urllib.error.URLError as exc:
            raise ApplicationError(
                message=f"Network request failed: {exc.reason}",
                code="application_error",
            ) from None

    def perform_with_content(self) -> T:
        resp = self.perform()
        if resp is None:
            raise NoContentError()
        return resp

    def perform_raw(self, accept: str = "application/json") -> bytes:
        """Return the raw response body, undecoded.

        For the endpoints that answer with something other than JSON — the suppression
        list export is CSV — where ``perform``'s ``json.loads`` would reject a perfectly
        good response. Errors are still JSON, and are raised the same way.
        """
        if not eusend.api_key:
            raise MissingApiKeyError()

        headers = {
            "Accept": accept,
            "Authorization": f"Bearer {eusend.api_key}",
            "User-Agent": f"eusend-python:{get_version()}",
        }
        req = urllib.request.Request(
            f"{eusend.api_url}{self.path}", method=self.verb.upper(), headers=headers
        )

        try:
            with urllib.request.urlopen(req, timeout=DEFAULT_TIMEOUT) as resp:
                return cast(bytes, resp.read())
        except urllib.error.HTTPError as exc:
            raw = exc.read()
            message = "Request failed"
            code = "INTERNAL_ERROR"
            try:
                payload = json.loads(raw)
                message = payload.get("error") or message
                code = payload.get("code") or code
            except (ValueError, AttributeError):
                pass
            raise_for_code_and_type(
                code=code,
                message=message,
                status_code=exc.code,
                headers=dict(exc.headers or {}),
            )
            raise  # unreachable — raise_for_code_and_type always raises
        except urllib.error.URLError as exc:
            raise ApplicationError(
                message=f"Network request failed: {exc.reason}",
                code="application_error",
            ) from None
