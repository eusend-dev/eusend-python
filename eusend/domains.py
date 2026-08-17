from typing import List

from eusend._compat import TypedDict

from eusend.models import Domain, DnsRecord
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
        tracking_enabled: bool
        tracking_status: str
        created_at: str

    class TrackingResponse(TypedDict):
        id: str
        name: str
        tracking_enabled: bool
        tracking_status: str
        # Carries the tracking CNAME to publish when tracking was just enabled.
        records: list[DnsRecord]

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

    @classmethod
    def set_tracking(cls, domain_id: str, enabled: bool) -> "Domains.TrackingResponse":
        """Opt in or out of serving open/click tracking from track.<domain>.

        Enabling requires a verified domain and returns the CNAME to publish; tracked
        links keep using the platform host until the record resolves and the subdomain
        is confirmed serving. Disabling takes effect on the next message sent.
        """
        return Request[Domains.TrackingResponse](
            path=f"/domains/{domain_id}/tracking", params={"enabled": enabled}, verb="patch"
        ).perform_with_content()
