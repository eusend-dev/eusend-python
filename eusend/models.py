"""Response type definitions (TypedDicts) shared across resources.

Responses are plain dicts at runtime (with snake_case keys); these types exist
for editor/type-checker support. Access fields with ``resp["field"]``.
"""

from typing import Any, Dict, List, Optional

from eusend._compat import NotRequired, TypedDict

# `from` is a reserved keyword, so it is declared via functional TypedDict syntax.
_EmailFrom = TypedDict("_EmailFrom", {"from": str})


class EmailEvent(TypedDict):
    id: str
    type: str
    metadata: Dict[str, Any]
    created_at: str


class Email(_EmailFrom):
    id: str
    to: List[str]
    cc: List[str]
    bcc: List[str]
    reply_to: List[str]
    subject: str
    html: str
    text: str
    status: str
    # Always a dict, ``{}`` when the send carried no tags.
    tags: Dict[str, str]
    test_mode: bool
    template_id: str
    scheduled_at: str
    created_at: str
    events: List[EmailEvent]


class EmailListItem(_EmailFrom):
    id: str
    to: List[str]
    subject: str
    status: str
    tags: Dict[str, str]
    test_mode: bool
    created_at: str


class DnsRecord(TypedDict, total=False):
    type: str
    name: str
    value: str
    priority: int  # MX records only
    purpose: str  # authentication | policy | alignment
    description: str


class DomainVerification(TypedDict):
    """Whether a verification chain is polling DNS for the domain right now."""

    running: bool
    started_at: str


class DomainDnsProvider(TypedDict):
    """The DNS host serving the zone, recognised from its nameservers."""

    id: str
    label: str
    #: Path to the guide for this panel on eusend.dev, or None where there is none.
    guide: str


class DomainDiagnostic(TypedDict):
    """What the last unmatched DNS check found, when it found a mistake.

    ``code`` is the mistake: ``doubled_domain`` (the record sits under the domain
    twice, because the control panel appends it to whatever you type),
    ``truncated_key`` (the value was cut at the 255-character limit for a single DNS
    string instead of being split into two), ``foreign_key`` (a DKIM key we did not
    issue is published at the selector), ``quoted_value``, ``multiple_records``,
    ``cname_at_selector``. New codes may be added, so treat an unknown one as generic.
    """

    code: str
    #: The name the record was actually found at, for ``doubled_domain``.
    found_at: str
    #: How much of the key is published, and how much there is, for ``truncated_key``.
    published_chars: int
    expected_chars: int
    #: Where the CNAME points, for ``cname_at_selector``.
    target: str
    provider: DomainDnsProvider


class Domain(TypedDict):
    id: str
    name: str
    dkim_public_key: str
    dkim_selector: str
    status: str
    created_at: str
    verified_at: str
    verification: DomainVerification
    #: None while nothing is wrong beyond the records not having propagated yet.
    diagnostic: DomainDiagnostic


class Contact(TypedDict):
    id: str
    audience_id: str
    email: str
    first_name: str
    last_name: str
    #: Custom properties, available as ``{{key}}`` in a broadcast body.
    properties: Dict[str, str]
    status: str
    unsubscribed_at: str
    created_at: str
    updated_at: str


class Template(TypedDict):
    id: str
    name: str
    subject: str
    html: str
    react_source: str
    created_at: str
    updated_at: str


class WebhookDelivery(TypedDict):
    id: str
    webhook_id: str
    email_id: str
    event_type: str
    payload: Dict[str, Any]
    status: str
    response_status: int
    attempts: int
    created_at: str
    last_attempt_at: str


class Webhook(TypedDict):
    id: str
    url: str
    events: List[str]
    created_at: str


class Broadcast(TypedDict):
    id: str
    organization_id: str
    name: str
    status: str
    audience_id: Optional[str]
    from_address: str
    reply_to: Optional[str]
    subject: str
    html: Optional[str]
    react_source: Optional[str]
    editor_json: Optional[Dict[str, Any]]
    template_id: Optional[str]
    template_variables: Optional[Dict[str, str]]
    track_opens: bool
    track_clicks: bool
    held_reason: Optional[str]
    scheduled_at: Optional[str]
    started_at: Optional[str]
    completed_at: Optional[str]
    recipient_count: int
    sent_count: int
    created_at: str
    updated_at: str
    # Present on GET /broadcasts/:id only.
    stats: NotRequired[Dict[str, int]]
