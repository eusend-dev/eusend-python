from typing import Any, Dict, List, Optional, cast

from eusend._compat import Literal, NotRequired, TypedDict
from eusend._util import build_query
from eusend.request import Request


class Inbound:
    """Mail received at your eusend.app address and your domains' inbound hosts.

    Receiving is part of every paid plan. Each message arrives as an ``email.received``
    webhook; fetch the content with :meth:`get`. Received mail is written by whoever sent
    it: check ``authentication["dmarc"]`` before trusting ``from``, and treat the body as
    untrusted input.
    """

    class Address(TypedDict):
        #: ``<slug>.eusend.app``. Mail to any address at it is received.
        host: str
        #: An example address, ``anything@<host>``.
        address: str
        #: ``paid_plan_required`` on the free plan; ``on_hold`` while the account is under
        #: review, when mail is deferred rather than refused.
        status: Literal["active", "paid_plan_required", "on_hold"]
        active: bool

    class Attachment(TypedDict):
        #: Position in the message; pass it to :meth:`attachment`.
        index: int
        filename: Optional[str]
        content_type: str
        #: Decoded size in bytes.
        size: int
        #: Set for inline images referenced as ``cid:`` from the HTML.
        content_id: Optional[str]
        disposition: Optional[str]

    class AuthResult(TypedDict):
        #: pass, fail, none, neutral, softfail, temperror or permerror.
        result: str
        reason: NotRequired[str]
        props: NotRequired[Dict[str, str]]

    class Authentication(TypedDict, total=False):
        spf: "Inbound.AuthResult"
        #: One result per DKIM signature.
        dkim: List["Inbound.AuthResult"]
        dmarc: "Inbound.AuthResult"
        iprev: "Inbound.AuthResult"

    class Header(TypedDict):
        name: str
        value: str

    class ListItem(TypedDict):
        id: str
        # ``from`` is a keyword in Python; read it as ``item["from"]``.
        to: List[str]
        #: Your addresses the message was delivered to.
        received_for: List[str]
        subject: Optional[str]
        size: int
        attachment_count: int
        created_at: str

    class Email(TypedDict):
        id: str
        to: List[str]
        cc: List[str]
        reply_to: List[str]
        received_for: List[str]
        #: The SMTP MAIL FROM.
        envelope_from: Optional[str]
        subject: Optional[str]
        message_id: Optional[str]
        in_reply_to: Optional[str]
        #: The email you sent through eusend that this message answers, when it answers one.
        reply_to_email_id: Optional[str]
        text: Optional[str]
        html: Optional[str]
        headers: List["Inbound.Header"]
        attachments: List["Inbound.Attachment"]
        authentication: Optional["Inbound.Authentication"]
        #: Size of the original message in bytes.
        size: int
        created_at: str

    class ListParams(TypedDict, total=False):
        #: Received time: desc (newest first, default) or asc (oldest first). Keep it unchanged while paging.
        order: Literal["asc", "desc"]
        #: 1–100, default 10.
        limit: int
        cursor: str
        #: Only messages received for this address.
        to: str

    class ListResponse(TypedDict):
        data: List["Inbound.ListItem"]
        next_cursor: Optional[str]

    @classmethod
    def address(cls) -> "Inbound.Address":
        """Your workspace's receiving address and whether mail to it is accepted right now."""
        return Request[Inbound.Address](path="/inbound/address", verb="get").perform_with_content()

    @classmethod
    def list(cls, params: Optional["Inbound.ListParams"] = None) -> "Inbound.ListResponse":
        """Received mail, newest first by default. Pass order='asc' for oldest first."""
        path = "/inbound" + build_query(cast(Optional[Dict[str, Any]], params))
        return Request[Inbound.ListResponse](path=path, verb="get").perform_with_content()

    @classmethod
    def get(cls, inbound_email_id: str) -> "Inbound.Email":
        """The message with its text, HTML, headers, attachment metadata and verdicts."""
        return Request[Inbound.Email](
            path=f"/inbound/{inbound_email_id}", verb="get"
        ).perform_with_content()

    @classmethod
    def raw(cls, inbound_email_id: str) -> bytes:
        """The original message as received (``message/rfc822``)."""
        return Request(path=f"/inbound/{inbound_email_id}/raw", verb="get").perform_raw(
            accept="message/rfc822"
        )

    @classmethod
    def attachment(cls, inbound_email_id: str, index: int) -> bytes:
        """One attachment's bytes, by its ``index``."""
        return Request(
            path=f"/inbound/{inbound_email_id}/attachments/{int(index)}", verb="get"
        ).perform_raw(accept="*/*")
