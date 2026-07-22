from typing import Any, Dict, List, cast

from eusend._compat import NotRequired, TypedDict

from eusend.models import Webhook, WebhookDelivery
from eusend.request import Request


class Webhooks:
    class CreateParams(TypedDict):
        url: str
        events: List[str]

    class CreateResponse(Webhook):
        secret: str

    class UpdateParams(TypedDict):
        url: NotRequired[str]
        events: NotRequired[List[str]]

    class WebhookWithDeliveries(Webhook):
        deliveries: List[WebhookDelivery]

    @classmethod
    def create(cls, params: "Webhooks.CreateParams") -> "Webhooks.CreateResponse":
        """Create a webhook. Pass ``{"events": ["*"]}`` to subscribe to every
        event. The returned ``secret`` is shown only once — store it securely."""
        return Request[Webhooks.CreateResponse](
            path="/webhooks", params=cast(Dict[str, Any], params), verb="post"
        ).perform_with_content()

    @classmethod
    def list(cls) -> List[Webhook]:
        resp = Request[Dict[str, Any]](path="/webhooks", verb="get").perform_with_content()
        return cast(List[Webhook], resp["data"])

    @classmethod
    def get(cls, webhook_id: str) -> "Webhooks.WebhookWithDeliveries":
        """Get a webhook including its recent deliveries."""
        return Request[Webhooks.WebhookWithDeliveries](
            path=f"/webhooks/{webhook_id}", verb="get"
        ).perform_with_content()

    @classmethod
    def update(cls, webhook_id: str, params: "Webhooks.UpdateParams") -> Webhook:
        return Request[Webhook](
            path=f"/webhooks/{webhook_id}", params=cast(Dict[str, Any], params), verb="patch"
        ).perform_with_content()

    @classmethod
    def remove(cls, webhook_id: str) -> None:
        Request(path=f"/webhooks/{webhook_id}", verb="delete").perform()
