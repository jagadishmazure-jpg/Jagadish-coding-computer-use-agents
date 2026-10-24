"""Two scripted planners that map (goal, vision output) to one action.

`GuardedPlanner` matches only goal-derived targets (ticket id, fixed control labels) and takes the refund
amount from the goal, never from page text. `NaivePlanner` models an agent that obeys instructions found
on the page; it exists to prove the guards hold even when the planner is fooled.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Goal:
    ticket: str
    amount: str
    reason: str = "damaged parcel"


def _find(elements: list[dict], pred) -> dict | None:
    return next((e for e in elements if pred(e)), None)


class GuardedPlanner:
    def next_action(self, goal: Goal, seen: dict, url: str, memory: dict) -> dict:
        els = seen["elements"]
        if "refund.html" in url:
            done = _find(els, lambda e: e["id"] == "done")
            detail = _find(els, lambda e: e["id"] == "detail")
            amount_ok = bool(detail) and detail["text"]["text"] == f"Amount: {goal.amount}"
            return {"type": "done", "ok": bool(done) and amount_ok}
        if "ticket.html" in url:
            if not memory.get("amount_set"):
                f = _find(els, lambda e: e["kind"] == "field" and e["id"] == "amount")
                return (
                    {"type": "click_type", "x": f["x"], "y": f["y"], "text": goal.amount, "mark": "amount_set"} if f else _stop()
                )
            if not memory.get("reason_set"):
                f = _find(els, lambda e: e["kind"] == "field" and e["id"] == "reason")
                return (
                    {"type": "click_type", "x": f["x"], "y": f["y"], "text": goal.reason, "mark": "reason_set"} if f else _stop()
                )
            b = _find(els, lambda e: e["kind"] == "submit")
            if b:
                return {"type": "submit", "x": b["x"], "y": b["y"], "summary": f"refund {goal.amount} on {goal.ticket}"}
            return _stop()
        link = _find(els, lambda e: e["tag"] == "a" and e["text"]["text"].startswith(goal.ticket + " "))
        return {"type": "click", "x": link["x"], "y": link["y"]} if link else _stop()


class NaivePlanner(GuardedPlanner):
    """Follows instructions in page text: uses an amount it reads there and visits URLs it is told to."""

    def next_action(self, goal: Goal, seen: dict, url: str, memory: dict) -> dict:
        page_text = " ".join(e["text"]["text"] for e in seen["elements"])
        m_url = re.search(r"go to (https?://\S+?)(?:\s|$)", page_text)
        if m_url and not memory.get("visited_injected"):
            memory["visited_injected"] = True
            return {"type": "goto", "url": m_url.group(1)}
        m_amt = re.search(r"refund (\d+\.\d\d)", page_text)
        if m_amt:
            goal = Goal(goal.ticket, m_amt.group(1), goal.reason)
        return super().next_action(goal, seen, url, memory)


def _stop() -> dict:
    return {"type": "stop", "reason": "expected control not found"}
