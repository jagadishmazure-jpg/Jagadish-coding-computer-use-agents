"""Invoice extraction agent: OCR -> parse -> validate -> auto-accept or escalate to a human.

A document is auto-accepted only if every required field parses, its weakest character is above the
confidence threshold, and the arithmetic checks (subtotal + tax == total, a real calendar date).
Anything else goes to the human queue with the reasons. Wrong auto-accepts are the metric that matters.
"""

from __future__ import annotations

import datetime as dt
import re
from dataclasses import dataclass, field

from .invoices import Invoice, make_invoice, render
from .ocr import read

FIELDS = {
    "vendor": re.compile(r"^VENDOR: ([A-Z ]+)$"),
    "number": re.compile(r"^INVOICE NO: (INV-\d{5})$"),
    "date": re.compile(r"^DATE: (\d{4}-\d{2}-\d{2})$"),
    "subtotal": re.compile(r"^SUBTOTAL: (\d+\.\d{2})$"),
    "tax": re.compile(r"^TAX: (\d+\.\d{2})$"),
    "total": re.compile(r"^TOTAL: (\d+\.\d{2})$"),
}
THRESHOLD = 0.80


@dataclass
class Decision:
    fields: dict[str, str | None]
    min_conf: float
    route: str  # "auto" or "human"
    reasons: list[str] = field(default_factory=list)


def extract(img, threshold: float = THRESHOLD) -> Decision:
    lines = read(img, n_lines=6, cols=26)
    fields: dict[str, str | None] = {}
    reasons: list[str] = []
    for (name, pat), line in zip(FIELDS.items(), lines, strict=True):
        m = pat.match(line.text)
        fields[name] = m.group(1) if m else None
        if not m:
            reasons.append(f"{name}: unreadable")
    min_conf = min(line.min_conf for line in lines)
    if min_conf < threshold:
        reasons.append(f"low confidence {min_conf:.2f} < {threshold:.2f}")
    if all(fields[k] for k in ("subtotal", "tax", "total")):
        s, t, tot = (round(float(fields[k]) * 100) for k in ("subtotal", "tax", "total"))
        if s + t != tot:
            reasons.append("subtotal + tax != total")
    if fields.get("date"):
        try:
            dt.date.fromisoformat(fields["date"])
        except ValueError:
            reasons.append("date: not a calendar date")
    return Decision(fields, round(min_conf, 4), "human" if reasons else "auto", reasons)


def truth(inv: Invoice) -> dict[str, str]:
    return {k: getattr(inv, k) for k in FIELDS}


NOISE_LEVELS = (0.0, 0.05, 0.12, 0.20)


def benchmark(n: int = 20, threshold: float = THRESHOLD) -> list[dict]:
    rows = []
    for noise in NOISE_LEVELS:
        auto = human = wrong_auto = caught_bad_math = field_ok = field_n = wrong_no_gate = 0
        for i in range(n):
            bad_math = i % 10 == 9  # 1 in 10 documents does not add up
            inv = make_invoice(i, corrupt_total=bad_math)
            d = extract(render(inv, noise=noise, seed=i), threshold)
            t = truth(inv)
            correct = d.fields == t
            wrong_no_gate += (not correct) or bad_math
            if d.route == "auto":
                auto += 1
                wrong_auto += (not correct) or bad_math
                field_ok += sum(d.fields[k] == t[k] for k in t)
                field_n += len(t)
            else:
                human += 1
                caught_bad_math += bad_math and "subtotal + tax != total" in d.reasons
        rows.append(
            {
                "noise": noise,
                "n": n,
                "auto": auto,
                "human": human,
                "wrong_auto": wrong_auto,
                "wrong_if_no_gate": wrong_no_gate,
                "auto_field_acc": field_ok / field_n if field_n else None,
                "bad_math_caught": caught_bad_math,
                "bad_math_total": n // 10,
            }
        )
    return rows
