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
        # Omit to use the organization default; False always wins over it.
        track_opens: NotRequired[bool]
        track_clicks: NotRequired[bool]

    class UpdateParams(_BroadcastFromOpt):
        name: NotRequired[str]
        audience_id: NotRequired[str]
        subject: NotRequired[str]
        html: NotRequired[str]
        template_id: NotRequired[str]
        template_variables: NotRequired[Dict[str, str]]
        scheduled_at: NotRequired[str]
        # Omit to leave the broadcast's current setting unchanged.
        track_opens: NotRequired[bool]
        track_clicks: NotRequired[bool]

    class SendParams(TypedDict):
        scheduled_at: NotRequired[str]

    class SendResponse(TypedDict):
        id: str
        status: str
        scheduled_at: Optional[str]

    class TestParams(TypedDict):
        # Up to 5 addresses, each on a domain verified on your account. A test send
        # delivers real mail without the paid-plan gate that ``send`` carries, so it is
        # restricted to inboxes you have already proved you control; anything else
        # returns DOMAIN_NOT_VERIFIED.
        to: List[str]

    class TestResponse(TypedDict):
        id: str
        # The addresses actually mailed, lowercased and de-duplicated.
        sent_to: List[str]
        # One email id per recipient, for looking the delivery up in the logs.
        email_ids: List[str]

    class BroadcastListItem(TypedDict):
        id: str
        name: str
        status: str
        audience_id: Optional[str]
        from_address: str
        subject: str
        recipient_count: Optional[int]
        sent_count: Optional[int]
        scheduled_at: Optional[str]
        started_at: Optional[str]
        completed_at: Optional[str]
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
    def test(cls, broadcast_id: str, params: "Broadcasts.TestParams") -> "Broadcasts.TestResponse":
        """Send a copy to your own verified addresses before the campaign goes out.

        The real message through the real sending path, so it shows what a recipient will
        see. Unlike ``send`` this works on every plan including Free. It costs daily and
        monthly quota like any other send, and does not move the broadcast's status.

        Requires a LIVE api key -- "test" here means a dress rehearsal, not a sandbox, so
        an ``eu_test_`` key is refused because the mail really is delivered.
        """
        return Request[Broadcasts.TestResponse](
            path=f"/broadcasts/{broadcast_id}/test",
            params=cast(Dict[str, Any], params),
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
