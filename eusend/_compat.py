"""Typing-helper compatibility shim.

``NotRequired`` landed in the stdlib ``typing`` in Python 3.11; on 3.8–3.10 it
lives in ``typing_extensions``. Import these names from here so callers don't
need to care.
"""

import sys

if sys.version_info >= (3, 11):
    from typing import Literal, NotRequired, TypedDict
else:  # pragma: no cover
    from typing_extensions import Literal, NotRequired, TypedDict

__all__ = ["TypedDict", "NotRequired", "Literal"]
