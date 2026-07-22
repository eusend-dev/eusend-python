"""Response type definitions (TypedDicts) shared across resources.

Responses are plain dicts at runtime (with snake_case keys); these types exist
for editor/type-checker support. Access fields with ``resp["field"]``.
"""

from typing import Any, Dict, List

from eusend._compat import TypedDict

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
    test_mode: bool
    created_at: str


class DnsRecord(TypedDict):
    type: str
    name: str
    value: str


class Domain(TypedDict):
    id: str
    name: str
    dkim_public_key: str
    dkim_selector: str
    status: str
    created_at: str
    verified_at: str


class Contact(TypedDict):
    id: str
    audience_id: str
    email: str
    first_name: str
    last_name: str
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
    name: str
    status: str
    audience_id: str
    from_address: str
    subject: str
    html: str
    template_id: str
    template_variables: Dict[str, str]
    scheduled_at: str
    created_at: str
    updated_at: str
