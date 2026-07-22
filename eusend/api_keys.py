from typing import List

from eusend._compat import NotRequired, TypedDict

from eusend.request import Request


class ApiKeys:
    class CreateParams(TypedDict):
        name: str
        test_mode: NotRequired[bool]

    class CreateResponse(TypedDict):
        id: str
        name: str
        key: str
        prefix: str
        test_mode: bool
        created_at: str

    class ApiKey(TypedDict):
        id: str
        name: str
        prefix: str
        test_mode: bool
        created_at: str
        last_used_at: str

    @classmethod
    def create(cls, params: "ApiKeys.CreateParams") -> "ApiKeys.CreateResponse":
        """Create an API key. The full ``key`` is returned only once.

        Pass ``{"test_mode": True}`` for a sandbox key — its sends are accepted
        and tracked but never delivered.
        """
        body = {"name": params["name"], "test_mode": params.get("test_mode", False)}
        return Request[ApiKeys.CreateResponse](
            path="/api-keys", params=body, verb="post"
        ).perform_with_content()

    @classmethod
    def list(cls) -> List["ApiKeys.ApiKey"]:
        return Request[List[ApiKeys.ApiKey]](path="/api-keys", verb="get").perform_with_content()

    @classmethod
    def remove(cls, api_key_id: str) -> None:
        Request(path=f"/api-keys/{api_key_id}", verb="delete").perform()
