from typing import Any, Dict, List, cast

from eusend._compat import NotRequired, TypedDict

from eusend._util import prepare_email_payload
from eusend.emails import Emails
from eusend.request import Request


class Batch:
    class BatchItemResult(TypedDict):
        id: NotRequired[str]
        error: NotRequired[str]
        code: NotRequired[str]

    class SendResponse(TypedDict):
        data: List["Batch.BatchItemResult"]

    @classmethod
    def send(cls, params: List[Emails.SendParams]) -> "Batch.SendResponse":
        """Send up to 100 emails in one request.

        Attachments and scheduling are not supported on the batch endpoint and
        are stripped from each item — send those individually via ``Emails.send``.
        The result maps positionally to the input: queued items carry ``id``,
        rejected items carry ``error`` and ``code``.
        """
        payload = [
            prepare_email_payload(cast(Dict[str, Any], p), allow_scheduling=False) for p in params
        ]
        return Request[Batch.SendResponse](
            path="/emails/batch",
            params=cast(List[Any], payload),
            verb="post",
        ).perform_with_content()
