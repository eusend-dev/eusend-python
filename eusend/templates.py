from typing import Any, Dict, List, cast

from eusend._compat import NotRequired, TypedDict

from eusend.models import Template
from eusend.request import Request


class Templates:
    class CreateParams(TypedDict):
        name: str
        subject: str
        html: str

    class UpdateParams(TypedDict):
        name: NotRequired[str]
        subject: NotRequired[str]
        html: NotRequired[str]

    class TemplateListItem(TypedDict):
        id: str
        name: str
        subject: str
        created_at: str
        updated_at: str

    @classmethod
    def create(cls, params: "Templates.CreateParams") -> Template:
        """Create a template. Use ``{{variable}}`` placeholders; values are
        HTML-escaped at send time."""
        return Request[Template](
            path="/templates", params=cast(Dict[str, Any], params), verb="post"
        ).perform_with_content()

    @classmethod
    def list(cls) -> List["Templates.TemplateListItem"]:
        resp = Request[Dict[str, Any]](path="/templates", verb="get").perform_with_content()
        return cast(List["Templates.TemplateListItem"], resp["data"])

    @classmethod
    def get(cls, template_id: str) -> Template:
        return Request[Template](path=f"/templates/{template_id}", verb="get").perform_with_content()

    @classmethod
    def update(cls, template_id: str, params: "Templates.UpdateParams") -> Template:
        return Request[Template](
            path=f"/templates/{template_id}", params=cast(Dict[str, Any], params), verb="patch"
        ).perform_with_content()

    @classmethod
    def remove(cls, template_id: str) -> None:
        Request(path=f"/templates/{template_id}", verb="delete").perform()
