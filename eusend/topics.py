from typing import Any, Dict, List, Optional, cast

from eusend._compat import NotRequired, TypedDict

from eusend.request import Request


class Topic(TypedDict):
    """A named category of email a contact can subscribe to and leave independently."""

    id: str
    name: str
    description: Optional[str]
    #: ``"opt_in"`` or ``"opt_out"``. Fixed at creation.
    default_subscription: str
    #: ``"public"`` or ``"private"``.
    visibility: str
    #: Explicit opt-ins only. Returned by ``create`` and ``list``, not by ``get``.
    subscriber_count: NotRequired[int]
    created_at: str
    updated_at: str


class Topics:
    """Subscription topics -- the kinds of email a contact can choose between.

    Scope a broadcast to a topic with ``topic_id`` and it reaches only the contacts who
    want that kind of mail, so an unsubscribe becomes a preference change rather than
    losing the contact entirely.
    """

    class CreateParams(TypedDict):
        """Fields for a new topic.

        ``name`` is at most 50 characters and unique within the organization. It is what
        the recipient reads on the unsubscribe page.

        ``default_subscription`` is ``"opt_in"`` (everyone receives it until they leave) or
        ``"opt_out"`` (nobody receives it until they join). It CANNOT be changed afterwards:
        flipping an opt-out topic to opt-in would start mailing every contact who never
        asked for it, and nothing stored says which of them would have agreed.

        ``visibility`` is ``"private"`` (the default) or ``"public"`` -- whether the topic
        is listed on the unsubscribe page to a contact who is not already opted in.
        """

        name: str
        default_subscription: str
        description: NotRequired[Optional[str]]
        visibility: NotRequired[str]

    class UpdateParams(TypedDict):
        """The mutable fields. ``default_subscription`` is absent deliberately."""

        name: NotRequired[str]
        description: NotRequired[Optional[str]]
        visibility: NotRequired[str]

    class DeleteResponse(TypedDict):
        id: str
        deleted: bool

    class SubscriptionResponse(TypedDict):
        topic_id: str
        contact_id: str
        subscribed: bool

    class ClearSubscriptionResponse(TypedDict):
        topic_id: str
        contact_id: str
        deleted: bool

    @classmethod
    def create(cls, params: "Topics.CreateParams") -> Topic:
        return Request[Topic](
            path="/topics",
            params=cast(Dict[str, Any], params),
            verb="post",
        ).perform_with_content()

    @classmethod
    def list(cls) -> List[Topic]:
        """Every topic the organization has defined, ordered by name.

        Unpaginated -- the list is capped at 100 entries and every caller wants all of it.
        """
        resp = Request[Dict[str, Any]](path="/topics", verb="get").perform_with_content()
        return cast(List[Topic], resp["data"])

    @classmethod
    def get(cls, topic_id: str) -> Topic:
        return Request[Topic](
            path=f"/topics/{topic_id}", verb="get"
        ).perform_with_content()

    @classmethod
    def update(cls, topic_id: str, params: "Topics.UpdateParams") -> Topic:
        return Request[Topic](
            path=f"/topics/{topic_id}",
            params=cast(Dict[str, Any], params),
            verb="patch",
        ).perform_with_content()

    @classmethod
    def remove(cls, topic_id: str) -> "Topics.DeleteResponse":
        """Delete the topic and every stored preference for it.

        A draft or scheduled broadcast scoped to the topic widens back to its whole
        audience; broadcasts already sent keep their recipient records.
        """
        return Request[Topics.DeleteResponse](
            path=f"/topics/{topic_id}", verb="delete"
        ).perform_with_content()

    @classmethod
    def subscribe(
        cls, topic_id: str, contact_id: str, subscribed: bool = True
    ) -> "Topics.SubscriptionResponse":
        """Record an explicit preference for one contact."""
        return Request[Topics.SubscriptionResponse](
            path=f"/topics/{topic_id}/contacts/{contact_id}",
            params={"subscribed": subscribed},
            verb="put",
        ).perform_with_content()

    @classmethod
    def clear_subscription(
        cls, topic_id: str, contact_id: str
    ) -> "Topics.ClearSubscriptionResponse":
        """Forget the contact's choice so they fall back to the topic's default.

        Different from ``subscribe(..., False)``, which records "no thanks": on an opt-in
        topic, clearing means the contact starts receiving it again.
        """
        return Request[Topics.ClearSubscriptionResponse](
            path=f"/topics/{topic_id}/contacts/{contact_id}", verb="delete"
        ).perform_with_content()
