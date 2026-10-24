"""Guardrails for the computer-use loop.

1. Domain allowlist, enforced twice: the navigate action is checked, and every network request the page
   makes goes through a route handler that aborts off-allowlist hosts.
2. No form submit without approval: clicking a submit control is a separate action type that needs an
   approver's yes, and the route handler refuses the form's request unless a one-shot approval is armed.
3. Untrusted page text: everything read off the page is wrapped as data, scanned for injection markers,
   and never parsed for instructions by the guarded planner.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from urllib.parse import urlparse

INJECTION = re.compile(
    r"(ignore (all |any )?(previous|prior) instructions|system note to the ai|you are now|disregard the user|"
    r"https?://[^\s]+)",
    re.I,
)


@dataclass
class Allowlist:
    hosts: frozenset[str]

    def allows(self, url: str) -> bool:
        u = urlparse(url)
        return u.scheme in {"http", "https"} and (u.hostname or "") in self.hosts


@dataclass
class Approval:
    """Human-in-the-loop gate. `decide` receives a summary and returns True to approve."""

    decide: object = None
    armed: bool = False
    requests: list[str] = field(default_factory=list)

    def ask(self, summary: str) -> bool:
        self.requests.append(summary)
        ok = bool(self.decide(summary)) if callable(self.decide) else False  # default deny
        self.armed = ok
        return ok

    def consume(self) -> bool:
        ok, self.armed = self.armed, False
        return ok


def wrap_untrusted(text: str) -> dict:
    hits = sorted({m.group(0).lower() for m in INJECTION.finditer(text)})
    return {"untrusted": True, "text": text, "injection_markers": hits}
