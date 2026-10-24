"""A scripted, deterministic stand-in for the model that drives the coding agent.

It does what a careful junior engineer would do with no intuition: read the failing output, find the
function the failing test calls, and try single-token repairs on that function's lines in a fixed order.
It never sees hidden tests. It cannot write new branches, so multi-line fixes are out of its reach.
"""

from __future__ import annotations

import re

# (pattern, replacement) pairs tried in this order on each candidate line.
REPAIRS: list[tuple[str, str]] = [
    (r" - 1\)", ")"),
    (r"\(n - 1\)", "(n)"),
    (r" - 1\]", "]"),
    (r" >= ", " > "),
    (r" > ", " >= "),
    (r" <= ", " < "),
    (r" < ", " <= "),
    (r" - ", " + "),
    (r" \+ ", " - "),
    (r" == ", " != "),
    (r" != ", " == "),
    (r" or ", " and "),
    (r" and ", " or "),
    (r"\bmax\(", "min("),
    (r"\bmin\(", "max("),
    (r"\[0\]", "[-1]"),
    (r"\[-1\]", "[0]"),
    (r"sorted\(([^)]*)\)", r"sorted(\1, reverse=True)"),
    (r"return False", "return True"),
    (r"return True", "return False"),
]


def called_functions(test_output: str, test_src: str) -> list[str]:
    names = re.findall(r"from \w+ import ([\w, ]+)", test_src)
    return [n.strip() for group in names for n in group.split(",")]


def function_lines(src: str, name: str) -> list[int]:
    lines = src.splitlines()
    out, inside = [], False
    for i, line in enumerate(lines):
        if line.startswith(f"def {name}("):
            inside = True
            continue
        if inside:
            if line and not line.startswith((" ", "\t")):
                break
            if line.strip():
                out.append(i)
    return out


def candidates(src: str, fn_names: list[str]) -> list[tuple[int, str]]:
    """Every single-edit candidate as (line index, new source), in deterministic order."""
    lines = src.splitlines()
    out: list[tuple[int, str]] = []
    for name in fn_names:
        for i in function_lines(src, name):
            seen: set[str] = set()
            for pat, rep in REPAIRS:
                # try the repair at each occurrence on the line, left to right
                for m in re.finditer(pat, lines[i]):
                    new_line = lines[i][: m.start()] + m.expand(rep) + lines[i][m.end() :]
                    if new_line != lines[i] and new_line not in seen:
                        seen.add(new_line)
                        patched = lines[:i] + [new_line] + lines[i + 1 :]
                        out.append((i, "\n".join(patched) + "\n"))
    return out
