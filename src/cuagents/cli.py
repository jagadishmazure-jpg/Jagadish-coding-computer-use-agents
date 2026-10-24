"""`cuagents demo` runs all three agents and prints the results tables."""

from __future__ import annotations

import sys

from .coding.agent import evaluate
from .coding.tasks import TASKS


def coding_md(trs) -> tuple[str, str]:
    n = len(trs)
    resolved = sum(t.resolved for t in trs)
    vis = sum(t.visible_pass for t in trs)
    rows = [
        "| task | resolved | visible tests | hidden tests | steps | edits | test runs | reverted |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for t in trs:
        rows.append(
            f"| {t.task_id} | {'yes' if t.resolved else 'no'} | {'pass' if t.visible_pass else 'fail'} | "
            f"{'pass' if t.hidden_pass else ('fail' if t.visible_pass else '-')} | {t.steps} | {t.edits} | {t.test_runs} | {t.reverted} |"
        )
    summary = [
        "| metric | value |",
        "| --- | --- |",
        f"| tasks | {n} |",
        f"| resolved (visible + hidden tests pass) | {resolved} / {n} ({resolved / n:.1%}) |",
        f"| visible-only pass (overfit, caught by hidden tests) | {vis - resolved} |",
        f"| mean steps | {sum(t.steps for t in trs) / n:.1f} |",
        f"| mean edits | {sum(t.edits for t in trs) / n:.2f} |",
        f"| mean test runs | {sum(t.test_runs for t in trs) / n:.2f} |",
        f"| step cap hits | {sum(t.hit_cap for t in trs)} |",
    ]
    return "\n".join(summary), "\n".join(rows)


def computer_md(runs) -> str:
    rows = [
        "| scenario | goal reached | steps | approvals asked | submits sent | blocked requests | injection markers | stop reason |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for r in runs:
        rows.append(
            f"| {r.scenario} | {'yes' if r.ok else 'no'} | {r.steps} | {len(r.approvals_asked)} | {len(r.submits_sent)} | "
            f"{', '.join(r.blocked) or '-'} | {len(r.injection_markers)} | {r.stop_reason} |"
        )
    return "\n".join(rows)


def vision_md(rows) -> str:
    out = [
        "| pixel noise | docs | auto-accepted | escalated | wrong auto-accepts | wrong if no gate | auto field accuracy | bad-math docs caught |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for r in rows:
        acc = "-" if r["auto_field_acc"] is None else f"{r['auto_field_acc']:.1%}"
        out.append(
            f"| {r['noise']:.0%} | {r['n']} | {r['auto']} | {r['human']} | {r['wrong_auto']} | {r['wrong_if_no_gate']} | {acc} | "
            f"{r['bad_math_caught']} / {r['bad_math_total']} |"
        )
    return "\n".join(out)


def all_blocks() -> dict[str, str]:
    from .computer.loop import scenarios
    from .vision.agent import benchmark

    s, t = coding_md(evaluate(TASKS))
    return {"coding": s, "coding_tasks": t, "computer": computer_md(scenarios()), "vision": vision_md(benchmark())}


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if not argv or argv[0] != "demo":
        print("usage: cuagents demo")
        return 2
    b = all_blocks()
    print("## Coding agent\n\n" + b["coding"] + "\n\n" + b["coding_tasks"])
    print("\n## Computer-use loop\n\n" + b["computer"])
    print("\n## Invoice vision agent\n\n" + b["vision"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
