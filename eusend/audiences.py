from typing import Any, Dict, List, Optional, cast

from eusend._compat import NotRequired, TypedDict

from eusend._util import build_query
from eusend.models import Contact
from eusend.request import Request


class Audiences:
    class Audience(TypedDict):
        id: str
        name: str
        organization_id: str
        created_at: str
        updated_at: str

    class AudienceListItem(TypedDict):
        id: str
        name: str
        created_at: str
        contact_count: int

    class CreateContactParams(TypedDict):
        email: str
        first_name: NotRequired[str]
        last_name: NotRequired[str]

    class UpdateContactParams(TypedDict):
        first_name: NotRequired[str]
        last_name: NotRequired[str]
        unsubscribed: NotRequired[bool]

    class ListContactsParams(TypedDict):
        limit: NotRequired[int]
        cursor: NotRequired[str]
        search: NotRequired[str]
        subscribed: NotRequired[bool]

    class ListContactsResponse(TypedDict):
        data: List[Contact]
        next_cursor: Optional[str]

    class BatchCreateContactsResponse(TypedDict):
        count: int

    # --- Audiences ---------------------------------------------------------

    @classmethod
    def create(cls, name: str) -> "Audiences.Audience":
        return Request[Audiences.Audience](
            path="/audiences", params={"name": name}, verb="post"
        ).perform_with_content()

    @classmethod
    def list(cls) -> List["Audiences.AudienceListItem"]:
        resp = Request[Dict[str, Any]](path="/audiences", verb="get").perform_with_content()
        return cast(List["Audiences.AudienceListItem"], resp["data"])

    @classmethod
    def remove(cls, audience_id: str) -> None:
        Request(path=f"/audiences/{audience_id}", verb="delete").perform()

    # --- Contacts (nested under an audience) -------------------------------

    @classmethod
    def create_contact(cls, audience_id: str, params: "Audiences.CreateContactParams") -> Contact:
        """Add a contact to an audience, upserting on email."""
        return Request[Contact](
            path=f"/audiences/{audience_id}/contacts",
            params=cast(Dict[str, Any], params),
            verb="post",
        ).perform_with_content()

    @classmethod
    def batch_create_contacts(
        cls, audience_id: str, contacts: List["Audiences.CreateContactParams"]
    ) -> "Audiences.BatchCreateContactsResponse":
        """Upsert up to 1,000 contacts; returns the number written."""
        return Request[Audiences.BatchCreateContactsResponse](
            path=f"/audiences/{audience_id}/contacts/batch",
            params={"contacts": cast(List[Any], contacts)},
            verb="post",
        ).perform_with_content()

    @classmethod
    def list_contacts(
        cls, audience_id: str, params: Optional["Audiences.ListContactsParams"] = None
    ) -> "Audiences.ListContactsResponse":
        path = f"/audiences/{audience_id}/contacts" + build_query(cast(Optional[Dict[str, Any]], params))
        return Request[Audiences.ListContactsResponse](path=path, verb="get").perform_with_content()

    @classmethod
    def get_contact(cls, audience_id: str, contact_id: str) -> Contact:
        return Request[Contact](
            path=f"/audiences/{audience_id}/contacts/{contact_id}", verb="get"
        ).perform_with_content()

    @classmethod
    def update_contact(
        cls, audience_id: str, contact_id: str, params: "Audiences.UpdateContactParams"
    ) -> Contact:
        return Request[Contact](
            path=f"/audiences/{audience_id}/contacts/{contact_id}",
            params=cast(Dict[str, Any], params),
            verb="patch",
        ).perform_with_content()

    @classmethod
    def remove_contact(cls, audience_id: str, contact_id: str) -> None:
        Request(path=f"/audiences/{audience_id}/contacts/{contact_id}", verb="delete").perform()
