"""Coding agent loop: read the repo, plan, edit, run pytest, retry, under a hard step cap."""

from __future__ import annotations

from dataclasses import dataclass, field

from .policy import called_functions, candidates
from .sandbox import Sandbox
from .tasks import BugTask


@dataclass
class Trajectory:
    task_id: str
    steps: int = 0
    reads: int = 0
    edits: int = 0
    test_runs: int = 0
    reverted: int = 0
    visible_pass: bool = False
    hidden_pass: bool = False
    hit_cap: bool = False
    plan: list[str] = field(default_factory=list)

    @property
    def resolved(self) -> bool:
        return self.visible_pass and self.hidden_pass


def solve(task: BugTask, max_steps: int = 40) -> Trajectory:
    tr = Trajectory(task.task_id)
    sbx = Sandbox(task.files)

    def step() -> bool:
        tr.steps += 1
        if tr.steps > max_steps:
            tr.hit_cap = True
            return False
        return True

    try:
        step()
        files = sbx.list_files()
        src_files = [f for f in files if not f.startswith("test_")]
        test_files = [f for f in files if f.startswith("test_")]
        step()
        ok, out = sbx.run_tests()
        tr.test_runs += 1
        tr.plan.append(f"baseline tests: {'pass' if ok else 'fail'}")
        if ok:
            tr.visible_pass = True
        else:
            tests_src = ""
            for f in test_files:
                if not step():
                    break
                tests_src += sbx.read(f)
                tr.reads += 1
            fns = called_functions(out, tests_src)
            tr.plan.append(f"suspect functions: {', '.join(fns)}")
            for target in src_files:
                if tr.hit_cap or not step():
                    break
                original = sbx.read(target)
                tr.reads += 1
                for line_no, patched in candidates(original, fns):
                    if not step():
                        break
                    sbx.write(target, patched)
                    tr.edits += 1
                    if not step():
                        break
                    ok, out = sbx.run_tests()
                    tr.test_runs += 1
                    if ok:
                        tr.plan.append(f"fixed {target} line {line_no + 1}")
                        tr.visible_pass = True
                        break
                    sbx.write(target, original)  # revert a failed attempt before trying the next
                    tr.reverted += 1
                if tr.visible_pass:
                    break
        if tr.visible_pass:
            tr.hidden_pass, _ = sbx.run_tests(extra={"test_hidden.py": task.hidden_tests})
    finally:
        sbx.close()
    return tr


def evaluate(tasks: list[BugTask], max_steps: int = 40) -> list[Trajectory]:
    return [solve(t, max_steps) for t in tasks]
