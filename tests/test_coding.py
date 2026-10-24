import pytest

from cuagents.coding.agent import evaluate, solve
from cuagents.coding.policy import candidates, function_lines
from cuagents.coding.sandbox import Sandbox, SandboxError
from cuagents.coding.tasks import TASKS

BY_ID = {t.task_id: t for t in TASKS}


@pytest.fixture(scope="module")
def trajectories():
    return {t.task_id: t for t in evaluate(TASKS)}


def test_task_set_size_is_swe_style_small():
    assert 10 <= len(TASKS) <= 15
    assert len({t.task_id for t in TASKS}) == len(TASKS)


@pytest.mark.parametrize("task", TASKS, ids=lambda t: t.task_id)
def test_every_task_starts_broken(task):
    s = Sandbox(task.files)
    try:
        assert not s.run_tests()[0]
    finally:
        s.close()


def test_resolved_count_is_stable(trajectories):
    assert sum(t.resolved for t in trajectories.values()) == 12


def test_multi_line_fixes_are_known_misses(trajectories):
    assert not trajectories["T10-missing-branch"].resolved
    assert not trajectories["T11-two-line-fix"].resolved


def test_overfit_caught_by_hidden_tests(trajectories):
    t = trajectories["T13-overfit-trap"]
    assert t.visible_pass and not t.hidden_pass and not t.resolved


def test_failed_attempts_are_reverted(trajectories):
    t = trajectories["T15-nested-call"]
    assert t.reverted == 1 and t.edits == 2 and t.resolved


def test_step_cap_enforced():
    t = solve(BY_ID["T15-nested-call"], max_steps=5)
    assert t.hit_cap and not t.resolved and t.steps <= 6


def test_sandbox_blocks_escape():
    s = Sandbox({"a.py": "x = 1\n"})
    try:
        with pytest.raises(SandboxError):
            s.read("../../etc/passwd")
        with pytest.raises(SandboxError):
            s.write("/tmp/evil.py", "x")
    finally:
        s.close()


def test_sandbox_tests_are_read_only():
    s = Sandbox({"a.py": "x = 1\n", "test_a.py": "def test_x():\n    pass\n"})
    try:
        with pytest.raises(SandboxError):
            s.write("test_a.py", "")
    finally:
        s.close()


def test_sandbox_no_new_files():
    s = Sandbox({"a.py": "x = 1\n"})
    try:
        with pytest.raises(SandboxError):
            s.write("conftest.py", "")
    finally:
        s.close()


def test_sandbox_scrubs_environment(monkeypatch):
    monkeypatch.setenv("FAKE_API_TOKEN", "should-not-leak")
    s = Sandbox({"test_env.py": "import os\n\n\ndef test_e():\n    assert 'FAKE_API_TOKEN' not in os.environ\n"})
    try:
        assert s.run_tests()[0]
    finally:
        s.close()


def test_sandbox_timeout():
    s = Sandbox({"test_slow.py": "import time\n\n\ndef test_s():\n    time.sleep(5)\n"})
    try:
        ok, out = s.run_tests(timeout=1)
        assert not ok and out == "TIMEOUT"
    finally:
        s.close()


def test_hidden_tests_never_left_in_sandbox():
    s = Sandbox(BY_ID["T02-wrong-operator"].files)
    try:
        s.run_tests(extra={"test_hidden.py": "def test_h():\n    pass\n"})
        assert "test_hidden.py" not in s.list_files()
    finally:
        s.close()


def test_function_lines_and_candidates_deterministic():
    src = "def f(a, b):\n    return max(a, max(b, 1))\n"
    assert function_lines(src, "f") == [1]
    c1, c2 = candidates(src, ["f"]), candidates(src, ["f"])
    assert c1 == c2 and len(c1) == 2  # max->min at each occurrence


def test_trajectory_records_plan(trajectories):
    assert trajectories["T02-wrong-operator"].plan[-1].startswith("fixed billing.py")
