"""Mock vision: takes a real PNG screenshot, validates it, and returns element detections.

Honest note: detections come from the DOM's bounding boxes (via the environment), not from recognising
pixels. That keeps the loop deterministic and free while exercising the same contract a vision model
would have: screenshot in, labelled boxes with coordinates out. Every text field is marked untrusted.
"""

from __future__ import annotations

from .env import check_png
from .guards import wrap_untrusted


def look(screenshot: bytes, dom_detections: list[dict]) -> dict:
    w, h = check_png(screenshot)
    elements = []
    for d in dom_detections:
        if 0 <= d["x"] <= w and 0 <= d["y"] <= h:
            elements.append(d | {"text": wrap_untrusted(d["text"])})
    markers = sorted({m for e in elements for m in e["text"]["injection_markers"]})
    return {"size": (w, h), "elements": elements, "injection_markers": markers}
