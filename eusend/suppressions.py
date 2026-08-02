from typing import Any, Dict, List, Optional, Union, cast

from eusend._compat import NotRequired, TypedDict

from eusend._util import build_query
from eusend.request import Request


class Suppressions:
    """The addresses your organization will not send to.

    Hard bounces and spam complaints are added automatically; these methods cover the
    addresses you manage yourself. Suppression applies to live sending only — a
    test-mode key can read the list but not modify it.
    """

    class SuppressionEntry(TypedDict):
        id: str
        email: str
        reason: str
        created_at: str

    class CreateParams(TypedDict):
        email: str
        # Defaults to "manual". An add never overwrites the reason an address is
        # already suppressed for.
        reason: NotRequired[str]

    class ImportItem(TypedDict):
        email: str
        reason: NotRequired[str]

    class ListParams(TypedDict):
        # Matches addresses containing this substring. Pass a domain ("@acme.com") to
        # see every suppressed address there.
        email: NotRequired[str]
        reason: NotRequired[str]
        limit: NotRequired[int]
        cursor: NotRequired[str]

    class ListResponse(TypedDict):
        data: List["Suppressions.SuppressionEntry"]
        next_cursor: Optional[str]

    class ImportResponse(TypedDict):
        #: Entries written.
        count: int
        #: Entries that were already on the list.
        already_suppressed: int
        #: Repeated addresses in the payload, collapsed before the write.
        duplicates: int

    class RemoveResponse(TypedDict):
        deleted: int

    @classmethod
    def list(cls, params: Optional["Suppressions.ListParams"] = None) -> "Suppressions.ListResponse":
        """A page of suppressed addresses, newest first."""
        query = build_query(cast(Optional[Dict[str, Any]], params))
        return Request[Suppressions.ListResponse](
            path=f"/suppressions{query}", verb="get"
        ).perform_with_content()

    @classmethod
    def create(cls, params: "Suppressions.CreateParams") -> "Suppressions.SuppressionEntry":
        """Suppress an address.

        If it is already suppressed the existing entry is returned unchanged — a manual
        add never rewrites a real bounce or complaint.
        """
        return Request[Suppressions.SuppressionEntry](
            path="/suppressions", params=cast(Dict[str, Any], params), verb="post"
        ).perform_with_content()

    @classmethod
    def import_list(
        cls, emails: List[Union[str, "Suppressions.ImportItem"]]
    ) -> "Suppressions.ImportResponse":
        """Add up to 1,000 addresses in one call.

        For carrying a suppression list over from another provider before your first
        send. Items may be bare address strings or dicts with a ``reason``.

        Named ``import_list`` because ``import`` is a Python keyword.
        """
        return Request[Suppressions.ImportResponse](
            path="/suppressions/batch",
            params={"emails": cast(List[Any], emails)},
            verb="post",
        ).perform_with_content()

    @classmethod
    def remove(cls, id_or_email: str) -> "Suppressions.RemoveResponse":
        """Un-suppress by entry id or by address, making the address sendable again.

        Removing addresses that hard-bounced or complained is what damages a sender's
        reputation when done in bulk — remove an entry when the address was fixed or the
        complaint was a mistake, not to retry a failing list.
        """
        from urllib.parse import quote

        return Request[Suppressions.RemoveResponse](
            path=f"/suppressions/{quote(id_or_email, safe='')}", verb="delete"
        ).perform_with_content()

    @classmethod
    def export(cls) -> bytes:
        """The whole list as CSV (``email,reason,created_at``), for backup or migration."""
        return Request(path="/suppressions/export", verb="get").perform_raw(accept="text/csv")
