# Running

```bash
python -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"
python -m playwright install chromium        # on CI: --with-deps
ruff check . && ruff format --check .
pytest -q
python scripts/count_tests.py
cuagents demo
python scripts/render_docs.py --check
python scripts/check_brands.py
```

Pinned versions: playwright 1.64.1, pillow 13.0.0, pytest 8.4.2, ruff 0.14.1.

**Optional real models:** not written. A real-model coding policy or a vision model would plug in behind the same
interfaces (`candidates`-style proposals; `look()` returning boxes). It would be skipped in CI and reported separately.

**Originality:** `python scripts/overlap_check.py <reference.txt>` checks for 8-word overlaps. References are never committed.
