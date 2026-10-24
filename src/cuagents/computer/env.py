"""Headless browser environment. Serves the local app under a fake host and enforces the guards at the
network layer. The agent only gets screenshots plus mock-vision detections, and acts by coordinates."""

from __future__ import annotations

import io
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlparse

from PIL import Image
from playwright.sync_api import Route, sync_playwright

from .guards import Allowlist, Approval

APP = Path(__file__).parent / "app"
HOST = "desk.example.test"
TYPES = {".html": "text/html", ".gif": "image/gif"}

DETECT_JS = """
() => [...document.querySelectorAll('h1,p,a,button,input,label,.msg')].map(e => {
  const r = e.getBoundingClientRect();
  return {tag: e.tagName.toLowerCase(), id: e.id || '', text: (e.innerText || e.value || '').trim().slice(0, 400),
          x: r.x + r.width / 2, y: r.y + r.height / 2, w: r.width, h: r.height,
          kind: e.tagName === 'BUTTON' && e.type === 'submit' ? 'submit' : (e.tagName === 'INPUT' ? 'field' : 'text')};
}).filter(d => d.w > 0 && d.h > 0)
"""


@dataclass
class Env:
    allow: Allowlist = field(default_factory=lambda: Allowlist(frozenset({HOST})))
    approval: Approval = field(default_factory=Approval)
    blocked: list[str] = field(default_factory=list)
    submits_sent: list[str] = field(default_factory=list)

    def __enter__(self) -> Env:
        self._pw = sync_playwright().start()
        self._browser = self._pw.chromium.launch(headless=True)
        self._ctx = self._browser.new_context(viewport={"width": 820, "height": 640}, java_script_enabled=True)
        self._ctx.route("**/*", self._route)
        self.page = self._ctx.new_page()
        return self

    def __exit__(self, *exc: object) -> None:
        self._ctx.close()
        self._browser.close()
        self._pw.stop()

    def _route(self, route: Route) -> None:
        url = route.request.url
        if not self.allow.allows(url):
            self.blocked.append(urlparse(url).hostname or url)
            route.abort("blockedbyclient")
            return
        path = urlparse(url).path.lstrip("/") or "inbox.html"
        if path == "refund.html":
            # The form's request: refuse unless a human approved this one submit.
            if not self.approval.consume():
                self.blocked.append("unapproved-submit")
                route.abort("blockedbyclient")
                return
            self.submits_sent.append(url)
        f = (APP / path).resolve()
        if f.parent != APP.resolve() or not f.exists():
            route.fulfill(status=404, body="not found")
            return
        route.fulfill(status=200, body=f.read_bytes(), content_type=TYPES.get(f.suffix, "text/plain"))

    # --- what the agent can do ------------------------------------------------------------------
    def goto(self, url: str) -> bool:
        if not self.allow.allows(url):
            self.blocked.append(urlparse(url).hostname or url)
            return False
        self.page.goto(url, wait_until="load")
        return True

    def screenshot(self) -> bytes:
        return self.page.screenshot(type="png")

    def detections(self) -> list[dict]:
        return self.page.evaluate(DETECT_JS)

    def click(self, x: float, y: float) -> None:
        self.page.mouse.click(x, y)
        self._settle()

    def _settle(self) -> None:
        # A click may or may not start a navigation. Give it a moment to start, then wait for load.
        self.page.wait_for_timeout(150)
        self.page.wait_for_load_state("load")

    def type_text(self, text: str) -> None:
        self.page.keyboard.press("Control+A")
        self.page.keyboard.type(text)

    def url(self) -> str:
        return self.page.url


def check_png(data: bytes) -> tuple[int, int]:
    """The mock vision step still takes a real screenshot and validates it before 'looking'."""
    if not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("not a PNG screenshot")
    with Image.open(io.BytesIO(data)) as im:
        return im.size
