"""Official Python SDK for the Eusend API — the EU-native transactional email platform.

Configure a module-level API key, then call the resource classes directly
(mirrors resend-python)::

    import eusend

    eusend.api_key = "eu_live_..."  # or set EUSEND_API_KEY

    email = eusend.Emails.send({
        "from": "Acme <you@yourdomain.com>",
        "to": "user@example.com",
        "subject": "Hello",
        "html": "<p>Hello world</p>",
    })
    print(email["id"])
"""

import os
from typing import Optional

# Module-level configuration, read at request time.
api_key: Optional[str] = os.environ.get("EUSEND_API_KEY")
api_url: str = os.environ.get("EUSEND_API_URL", "https://api.eusend.dev")

from eusend.version import get_version  # noqa: E402

# Resource classes are imported after the config above so `import eusend`
# inside the request layer sees an initialized module.
from eusend.emails import Emails  # noqa: E402
from eusend.batch import Batch  # noqa: E402
from eusend.domains import Domains  # noqa: E402
from eusend.api_keys import FULL_ACCESS, SENDING_ACCESS, ApiKeys  # noqa: E402
from eusend.audiences import Audiences  # noqa: E402
from eusend.templates import Templates  # noqa: E402
from eusend.webhooks import Webhooks  # noqa: E402
from eusend.broadcasts import Broadcasts  # noqa: E402
from eusend.suppressions import Suppressions  # noqa: E402

from eusend.exceptions import (  # noqa: E402
    ApplicationError,
    EusendError,
    InvalidApiKeyError,
    MissingApiKeyError,
    NoContentError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)

__version__ = get_version()

__all__ = [
    "api_key",
    "api_url",
    "Emails",
    "Batch",
    "Domains",
    "ApiKeys",
    "FULL_ACCESS",
    "SENDING_ACCESS",
    "Audiences",
    "Templates",
    "Webhooks",
    "Broadcasts",
    "Suppressions",
    "EusendError",
    "ApplicationError",
    "InvalidApiKeyError",
    "MissingApiKeyError",
    "NoContentError",
    "NotFoundError",
    "RateLimitError",
    "ValidationError",
    "__version__",
]
