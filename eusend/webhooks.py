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
        enabled: NotRequired[bool]
        """``False`` pauses the endpoint; ``True`` re-enables a paused or auto-disabled one."""

    class TestResponse(TypedDict):
        id: str

    class SecretResponse(TypedDict):
        secret: str

    class WebhookWithDeliveries(Webhook):
        deliveries: List[WebhookDelivery]

    @classmethod
    def create(cls, params: "Webhooks.CreateParams") -> "Webhooks.CreateResponse":
        """Create a webhook. Events are ``email.sent``, ``email.delivered``,
        ``email.bounced``, ``email.complained``, ``email.opened``, ``email.clicked``,
        ``email.failed``, ``email.suppressed`` and ``email.received``; pass
        ``{"events": ["*"]}`` to subscribe
        to every event. Store the returned ``secret`` securely; ``get_secret`` reads it again."""
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
    def test(cls, webhook_id: str) -> "Webhooks.TestResponse":
        """Send one signed ``webhook.test`` event to the endpoint. Works on a disabled
        endpoint, so a fix can be confirmed before enabling it again."""
        return Request[Webhooks.TestResponse](
            path=f"/webhooks/{webhook_id}/test", verb="post"
        ).perform_with_content()

    @classmethod
    def get_secret(cls, webhook_id: str) -> "Webhooks.SecretResponse":
        """The endpoint's current signing secret."""
        return Request[Webhooks.SecretResponse](
            path=f"/webhooks/{webhook_id}/secret", verb="get"
        ).perform_with_content()

    @classmethod
    def rotate_secret(cls, webhook_id: str) -> "Webhooks.CreateResponse":
        """Replace the signing secret and return the webhook with the new one. Takes effect
        immediately — the previous secret stops verifying."""
        return Request[Webhooks.CreateResponse](
            path=f"/webhooks/{webhook_id}/rotate-secret", verb="post"
        ).perform_with_content()

    @classmethod
    def remove(cls, webhook_id: str) -> None:
        Request(path=f"/webhooks/{webhook_id}", verb="delete").perform()
