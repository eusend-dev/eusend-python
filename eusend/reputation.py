from typing import Optional

from eusend._compat import Literal, TypedDict

from eusend.request import Request


class Reputation:
    """Your organization's sending reputation, as the sending limits judge it.

    Not available to sending-only keys. The API caches the answer for up to 30 seconds.
    """

    class Bounce(TypedDict):
        #: Raw rate over the judged window.
        rate: float
        #: The 95% confidence lower bound compared against the lines; 0 without enough evidence.
        judged_rate: float
        counted: int
        #: Bounces about eusend's sending infrastructure rather than the address.
        not_counted: int
        recipients: int
        window: Optional[Literal["7d", "30d"]]
        limited_at: float
        paused_at: float

    class Complaint(TypedDict):
        rate: float
        complaints: int
        limited_at: float
        paused_at: float

    class Next(TypedDict):
        state: Literal["limited", "paused"]
        #: None when no realistic run of bounces would reach it.
        bounces: Optional[int]

    class Verdict(TypedDict):
        #: "warning": high raw bounce rate, not yet past the line on the evidence.
        #: "limited": the daily ceiling is halved. "paused": sending is suspended.
        state: Literal["healthy", "warning", "limited", "paused"]
        #: False until at least 100 recipients have a delivery result.
        measured: bool
        bounce: "Reputation.Bounce"
        complaint: "Reputation.Complaint"
        #: None when the account is paused.
        next: Optional["Reputation.Next"]

    @classmethod
    def get(cls) -> "Reputation.Verdict":
        """The verdict the auto-suspend and the daily ceiling act on."""
        return Request[Reputation.Verdict](path="/reputation", verb="get").perform_with_content()
