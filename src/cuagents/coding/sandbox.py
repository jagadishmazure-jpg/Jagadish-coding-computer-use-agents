"""A throwaway workspace for one task. Tools are the only way the agent touches it.

Controls: every path must resolve inside the sandbox root; writes are limited to existing .py files that
are not tests (the agent may not edit the tests it is graded on); pytest runs in a subprocess with a
timeout, a scrubbed environment and no inherited secrets. This is process-level isolation for a lab, not a
security boundary against hostile code; see docs/threat-model.md.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SAFE_ENV_KEYS = ("PATH", "LANG", "LC_ALL", "SYSTEMROOT")


class SandboxError(Exception):
    pass


class Sandbox:
    def __init__(self, files: dict[str, str]) -> None:
        self.root = Path(tempfile.mkdtemp(prefix="cu-sbx-")).resolve()
        for name, text in files.items():
            self._resolve(name).write_text(text)
        self.log: list[dict] = []

    def _resolve(self, rel: str) -> Path:
        p = (self.root / rel).resolve()
        if p.parent != self.root and self.root not in p.parents:
            raise SandboxError("path outside sandbox")
        return p

    def list_files(self) -> list[str]:
        self.log.append({"tool": "list_files"})
        return sorted(p.name for p in self.root.iterdir() if p.suffix == ".py")

    def read(self, rel: str) -> str:
        self.log.append({"tool": "read", "path": rel})
        return self._resolve(rel).read_text()

    def write(self, rel: str, text: str) -> None:
        p = self._resolve(rel)
        if p.name.startswith("test_"):
            raise SandboxError("tests are read-only for the agent")
        if not p.exists() or p.suffix != ".py":
            raise SandboxError("only existing source files may be edited")
        self.log.append({"tool": "write", "path": rel})
        p.write_text(text)

    def run_tests(self, extra: dict[str, str] | None = None, timeout: int = 30) -> tuple[bool, str]:
        """Run pytest. `extra` lets the grader drop in hidden tests; the agent never calls it with extra."""
        tag = "hidden" if extra else "visible"
        target = self.root
        if extra:
            target = Path(tempfile.mkdtemp(prefix="cu-grade-")).resolve()
            for f in self.root.glob("*.py"):
                if not f.name.startswith("test_"):
                    shutil.copy(f, target / f.name)
            for name, text in extra.items():
                (target / name).write_text(text)
        env = {k: os.environ[k] for k in SAFE_ENV_KEYS if k in os.environ}
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        try:
            r = subprocess.run(  # noqa: S603 - fixed argv, no shell
                [sys.executable, "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider", "--tb=short", str(target)],
                cwd=target,
                env=env,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
            ok, out = r.returncode == 0, r.stdout[-4000:]
        except subprocess.TimeoutExpired:
            ok, out = False, "TIMEOUT"
        finally:
            if extra:
                shutil.rmtree(target, ignore_errors=True)
        if not extra:
            self.log.append({"tool": "run_tests", "ok": ok, "which": tag})
        return ok, out

    def close(self) -> None:
        shutil.rmtree(self.root, ignore_errors=True)
