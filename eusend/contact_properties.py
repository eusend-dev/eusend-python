from typing import Any, Dict, List, Optional, cast

from eusend._compat import NotRequired, TypedDict

from eusend.models import ContactProperty
from eusend.request import Request


class ContactProperties:
    """The organization's declared custom contact properties.

    These are the schema behind the ``properties`` bag each contact carries. Declaring a
    property is optional: one arriving on a contact write that has never been declared
    registers itself as a ``string``, so an existing integration needs no changes.
    Declaring up front is what buys a type check and a fallback value.
    """

    class CreateParams(TypedDict):
        """Fields for a new property.

        ``key`` is lowercase letters, digits and underscores, starting with a letter (at
        most 40 characters). ``email``, ``name``, ``first_name``, ``last_name`` and
        ``full_name`` are built in and cannot be declared.

        ``type`` is ``"string"`` (the default) or ``"number"``. Values are carried and
        rendered as strings either way -- ``"number"`` buys a write-time check, not
        arithmetic or locale formatting.

        ``fallback_value`` must match ``type``. It is substituted into ``{{key}}`` for
        contacts that carry no value of their own.
        """

        key: str
        type: NotRequired[str]
        fallback_value: NotRequired[Optional[str]]

    class UpdateParams(TypedDict):
        """The fallback, which is the only mutable field.

        ``key`` and ``type`` are fixed at creation: a rename would have to rewrite every
        contact AND every broadcast body spelling ``{{old_key}}``, so changing either is a
        delete and a create.
        """

        fallback_value: Optional[str]

    class DeleteResponse(TypedDict):
        deleted: bool
        #: How many contacts had the key stripped from them.
        contacts_updated: int

    @classmethod
    def create(cls, params: "ContactProperties.CreateParams") -> ContactProperty:
        return Request[ContactProperty](
            path="/contact-properties",
            params=cast(Dict[str, Any], params),
            verb="post",
        ).perform_with_content()

    @classmethod
    def list(cls) -> List[ContactProperty]:
        """Every property the organization has defined.

        Unpaginated -- the registry is capped at 100 entries, and a variable picker wants
        all of them.
        """
        resp = Request[Dict[str, Any]](
            path="/contact-properties", verb="get"
        ).perform_with_content()
        return cast(List[ContactProperty], resp["data"])

    @classmethod
    def get(cls, property_id: str) -> ContactProperty:
        return Request[ContactProperty](
            path=f"/contact-properties/{property_id}", verb="get"
        ).perform_with_content()

    @classmethod
    def update(
        cls, property_id: str, params: "ContactProperties.UpdateParams"
    ) -> ContactProperty:
        return Request[ContactProperty](
            path=f"/contact-properties/{property_id}",
            params=cast(Dict[str, Any], params),
            verb="patch",
        ).perform_with_content()

    @classmethod
    def remove(cls, property_id: str) -> "ContactProperties.DeleteResponse":
        """Delete the definition AND strip the key from every contact in the org.

        Destructive and not undoable. Leaving the values in place was the alternative, and
        a worse one: the property would keep rendering in broadcasts, and the next contact
        write carrying that key would register it again.
        """
        return Request[ContactProperties.DeleteResponse](
            path=f"/contact-properties/{property_id}", verb="delete"
        ).perform_with_content()
