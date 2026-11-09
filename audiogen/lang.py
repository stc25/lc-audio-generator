"""The active language, switchable per request / per command.

The old single-language apps hard-wired one pack at import time. Here the
parser, gender guesser and generator all read `PACK`, a proxy that forwards to
whichever language is active in the current context. `use("es")` switches it
for the duration of a `with` block (and for threads started via `spawn`).
"""
from __future__ import annotations

import contextvars
import os
import threading
from contextlib import contextmanager

from .languages import AVAILABLE, load

_code: contextvars.ContextVar = contextvars.ContextVar(
    "audiogen_lang", default=os.environ.get("AUDIOGEN_LANG", "es"))


def current() -> str:
    return _code.get()


def pack(code: str | None = None):
    return load(code or current())


@contextmanager
def use(code: str):
    load(code)                       # validate early: raises ValueError
    tok = _code.set(load(code).CODE)
    try:
        yield
    finally:
        _code.reset(tok)


def spawn(fn, *a, **kw) -> threading.Thread:
    """Start a thread that keeps the caller's active language."""
    ctx = contextvars.copy_context()
    t = threading.Thread(target=lambda: ctx.run(fn, *a, **kw), daemon=True)
    t.start()
    return t


class _Proxy:
    def __getattr__(self, name):
        return getattr(load(current()), name)


PACK = _Proxy()
