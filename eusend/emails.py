from typing import Any, Dict, List, Optional, Union, cast

from eusend._compat import NotRequired, TypedDict

from eusend._util import build_query, prepare_email_payload
from eusend.models import Email, EmailListItem
from eusend.request import Request

# `from` is a reserved keyword, declared via functional TypedDict syntax.
_SendParamsFrom = TypedDict("_SendParamsFrom", {"from": str})


class Attachment(TypedDict):
    filename: str
    content: NotRequired[Union[str, bytes]]
    path: NotRequired[str]
    content_type: NotRequired[str]
    content_id: NotRequired[str]


class _SendParamsDefault(_SendParamsFrom):
    to: Union[str, List[str]]
    subject: NotRequired[str]
    cc: NotRequired[Union[str, List[str]]]
    bcc: NotRequired[Union[str, List[str]]]
    reply_to: NotRequired[Union[str, List[str]]]
    html: NotRequired[str]
    text: NotRequired[str]
    template_id: NotRequired[str]
    variables: NotRequired[Dict[str, Any]]
    headers: NotRequired[Dict[str, str]]
    track_opens: NotRequired[bool]
    track_clicks: NotRequired[bool]
    attachments: NotRequired[List[Attachment]]
    scheduled_at: NotRequired[str]


# `from` again for the list filter.
_ListParamsFrom = TypedDict("_ListParamsFrom", {"from": NotRequired[str]})


class _ListParamsDefault(_ListParamsFrom):
    limit: NotRequired[int]
    cursor: NotRequired[str]
    status: NotRequired[str]
    to: NotRequired[str]


class Emails:
    class SendParams(_SendParamsDefault):
        pass

    class SendResponse(TypedDict):
        id: str

    class SendOptions(TypedDict):
        idempotency_key: NotRequired[str]

    class ListParams(_ListParamsDefault):
        pass

    class ListResponse(TypedDict):
        data: List[EmailListItem]
        next_cursor: Optional[str]

    class UpdateParams(TypedDict):
        id: str
        scheduled_at: str

    class UpdateResponse(TypedDict):
        id: str
        status: str
        scheduled_at: str

    class CancelResponse(TypedDict):
        id: str
        status: str

    @classmethod
    def send(cls, params: "Emails.SendParams", options: Optional["Emails.SendOptions"] = None) -> "Emails.SendResponse":
        """Send a single email. Pass ``options={"idempotency_key": ...}`` to make
        the send safe to retry without duplicating."""
        payload = prepare_email_payload(cast(Dict[str, Any], params))
        return Request[Emails.SendResponse](
            path="/emails",
            params=payload,
            verb="post",
            options=cast(Optional[Dict[str, Any]], options),
        ).perform_with_content()

    @classmethod
    def get(cls, email_id: str) -> Email:
        """Retrieve an email by ID, including its delivery events."""
        return Request[Email](path=f"/emails/{email_id}", verb="get").perform_with_content()

    @classmethod
    def list(cls, params: Optional["Emails.ListParams"] = None) -> "Emails.ListResponse":
        """List emails, most recent first. Filter by ``status``, ``from``, ``to``."""
        path = "/emails" + build_query(cast(Optional[Dict[str, Any]], params))
        return Request[Emails.ListResponse](path=path, verb="get").perform_with_content()

    @classmethod
    def update(cls, params: "Emails.UpdateParams") -> "Emails.UpdateResponse":
        """Reschedule a scheduled email. Fails once it has started sending."""
        return Request[Emails.UpdateResponse](
            path=f"/emails/{params['id']}",
            params={"scheduled_at": params["scheduled_at"]},
            verb="patch",
        ).perform_with_content()

    @classmethod
    def cancel(cls, email_id: str) -> "Emails.CancelResponse":
        """Cancel a scheduled email. Fails once it has started sending."""
        return Request[Emails.CancelResponse](
            path=f"/emails/{email_id}/cancel", verb="post"
        ).perform_with_content()
