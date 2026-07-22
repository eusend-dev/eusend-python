from typing import Any, Dict, List, Optional, cast

from eusend._compat import NotRequired, TypedDict

from eusend.models import Broadcast
from eusend.request import Request

# `from` is a reserved keyword, declared via functional TypedDict syntax.
_BroadcastFrom = TypedDict("_BroadcastFrom", {"from": str})
_BroadcastFromOpt = TypedDict("_BroadcastFromOpt", {"from": NotRequired[str]})


class Broadcasts:
    class CreateParams(_BroadcastFrom):
        name: str
        audience_id: str
        subject: str
        html: NotRequired[str]
        template_id: NotRequired[str]
        template_variables: NotRequired[Dict[str, str]]

    class UpdateParams(_BroadcastFromOpt):
        name: NotRequired[str]
        audience_id: NotRequired[str]
        subject: NotRequired[str]
        html: NotRequired[str]
        template_id: NotRequired[str]
        template_variables: NotRequired[Dict[str, str]]
        scheduled_at: NotRequired[str]

    class SendParams(TypedDict):
        scheduled_at: NotRequired[str]

    class SendResponse(TypedDict):
        id: str
        status: str
        scheduled_at: Optional[str]

    class BroadcastListItem(TypedDict):
        id: str
        name: str
        status: str
        audience_id: str
        from_address: str
        subject: str
        recipient_count: Optional[int]
        sent_count: Optional[int]
        scheduled_at: Optional[str]
        created_at: str
        audience_name: Optional[str]

    @classmethod
    def create(cls, params: "Broadcasts.CreateParams") -> Broadcast:
        return Request[Broadcast](
            path="/broadcasts", params=cast(Dict[str, Any], params), verb="post"
        ).perform_with_content()

    @classmethod
    def list(cls) -> List["Broadcasts.BroadcastListItem"]:
        resp = Request[Dict[str, Any]](path="/broadcasts", verb="get").perform_with_content()
        return cast(List["Broadcasts.BroadcastListItem"], resp["data"])

    @classmethod
    def get(cls, broadcast_id: str) -> Broadcast:
        """Get a broadcast including delivery stats."""
        return Request[Broadcast](path=f"/broadcasts/{broadcast_id}", verb="get").perform_with_content()

    @classmethod
    def update(cls, broadcast_id: str, params: "Broadcasts.UpdateParams") -> Broadcast:
        return Request[Broadcast](
            path=f"/broadcasts/{broadcast_id}", params=cast(Dict[str, Any], params), verb="patch"
        ).perform_with_content()

    @classmethod
    def send(
        cls, broadcast_id: str, params: Optional["Broadcasts.SendParams"] = None
    ) -> "Broadcasts.SendResponse":
        """Send a broadcast now, or schedule it with ``{"scheduled_at": ...}``.
        Calling send on a paused broadcast resumes it from where it stopped."""
        return Request[Broadcasts.SendResponse](
            path=f"/broadcasts/{broadcast_id}/send",
            params=cast(Dict[str, Any], params or {}),
            verb="post",
        ).perform_with_content()

    @classmethod
    def cancel(cls, broadcast_id: str) -> Broadcast:
        return Request[Broadcast](
            path=f"/broadcasts/{broadcast_id}/cancel", verb="post"
        ).perform_with_content()

    @classmethod
    def remove(cls, broadcast_id: str) -> None:
        Request(path=f"/broadcasts/{broadcast_id}", verb="delete").perform()
