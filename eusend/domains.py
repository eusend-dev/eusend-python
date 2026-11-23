from typing import Any, Dict, List, Optional

from eusend._compat import TypedDict

from eusend.models import Domain, DnsRecord, DomainInbound
from eusend.request import Request


class Domains:
    class CreateResponse(TypedDict):
        id: str
        name: str
        # Every record to publish, in presentation order. Prefer this over the
        # individual keys below — it is the only place the optional Return-Path
        # alignment records appear.
        records: list[DnsRecord]
        dkim: DnsRecord
        dmarc: DnsRecord

    class DomainListItem(TypedDict):
        id: str
        name: str
        status: str
        created_at: str

    class RemoveResponse(TypedDict):
        message: str
        # Scheduled emails from the domain, canceled because it can no longer send them.
        canceled_scheduled_emails: int

    @classmethod
    def create(cls, name: str) -> "Domains.CreateResponse":
        """Add a domain and return the DNS records to publish."""
        return Request[Domains.CreateResponse](
            path="/domains", params={"name": name}, verb="post"
        ).perform_with_content()

    @classmethod
    def list(cls) -> List["Domains.DomainListItem"]:
        return Request[List[Domains.DomainListItem]](path="/domains", verb="get").perform_with_content()

    @classmethod
    def get(cls, domain_id: str) -> Domain:
        return Request[Domain](path=f"/domains/{domain_id}", verb="get").perform_with_content()

    @classmethod
    def verify(cls, domain_id: str) -> None:
        """Trigger DNS verification after publishing the records."""
        Request(path=f"/domains/{domain_id}/verify", verb="post").perform()

    @classmethod
    def remove(cls, domain_id: str) -> "Domains.RemoveResponse":
        return Request[Domains.RemoveResponse](
            path=f"/domains/{domain_id}", verb="delete"
        ).perform_with_content()

    @classmethod
    def enable_inbound(cls, domain_id: str, subdomain: Optional[str] = None) -> DomainInbound:
        """Receive mail on a verified domain or a subdomain of it.

        ``subdomain`` is the labels below the domain, like ``"in"`` for ``in.example.com``.
        Leave it out to receive on the domain itself, only when nothing else handles its mail.
        Returns the MX record to publish; mail starts arriving once it resolves. Not
        available to test keys.
        """
        params: Dict[str, Any] = {} if subdomain is None else {"subdomain": subdomain}
        return Request[DomainInbound](
            path=f"/domains/{domain_id}/inbound", params=params, verb="put"
        ).perform_with_content()

    @classmethod
    def disable_inbound(cls, domain_id: str) -> None:
        """Stop receiving mail on the domain. Mail already received is kept."""
        Request(path=f"/domains/{domain_id}/inbound", verb="delete").perform()
