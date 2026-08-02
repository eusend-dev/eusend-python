from typing import Any, Dict, List, Optional

from eusend._compat import NotRequired, TypedDict

from eusend.request import Request

#: A key with access to every resource.
FULL_ACCESS = "full_access"
#: A key limited to sending email (and rescheduling or canceling a scheduled send).
SENDING_ACCESS = "sending_access"


class ApiKeys:
    class CreateParams(TypedDict):
        name: str
        test_mode: NotRequired[bool]
        permission: NotRequired[str]
        domain_id: NotRequired[str]

    class CreateResponse(TypedDict):
        id: str
        name: str
        key: str
        prefix: str
        test_mode: bool
        permission: str
        domain_id: Optional[str]
        domain_name: Optional[str]
        created_at: str

    class ApiKey(TypedDict):
        id: str
        name: str
        prefix: str
        test_mode: bool
        permission: str
        domain_id: Optional[str]
        domain_name: Optional[str]
        created_at: str
        last_used_at: str

    @classmethod
    def create(cls, params: "ApiKeys.CreateParams") -> "ApiKeys.CreateResponse":
        """Create an API key. The full ``key`` is returned only once.

        Pass ``{"test_mode": True}`` for a sandbox key — its sends are accepted
        and tracked but never delivered.

        ``permission`` defaults to ``FULL_ACCESS``. Pass ``SENDING_ACCESS`` for a
        key that can only send, optionally with ``domain_id`` to pin it to one
        sending domain (``domain_id`` is rejected on a full-access key).
        """
        body: Dict[str, Any] = {
            "name": params["name"],
            "test_mode": params.get("test_mode", False),
            "permission": params.get("permission", FULL_ACCESS),
        }
        domain_id = params.get("domain_id")
        if domain_id is not None:
            body["domain_id"] = domain_id
        return Request[ApiKeys.CreateResponse](
            path="/api-keys", params=body, verb="post"
        ).perform_with_content()

    @classmethod
    def list(cls) -> List["ApiKeys.ApiKey"]:
        return Request[List[ApiKeys.ApiKey]](path="/api-keys", verb="get").perform_with_content()

    @classmethod
    def remove(cls, api_key_id: str) -> None:
        Request(path=f"/api-keys/{api_key_id}", verb="delete").perform()
