from typing import List

from eusend._compat import TypedDict

from eusend.models import Domain, DnsRecord
from eusend.request import Request


class Domains:
    class CreateResponse(TypedDict):
        id: str
        name: str
        dkim: DnsRecord
        spf: DnsRecord
        dmarc: DnsRecord

    class DomainListItem(TypedDict):
        id: str
        name: str
        status: str
        created_at: str

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
    def remove(cls, domain_id: str) -> None:
        Request(path=f"/domains/{domain_id}", verb="delete").perform()
