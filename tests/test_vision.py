import pytest

from cuagents.vision.agent import benchmark, extract, truth
from cuagents.vision.font import GLYPHS
from cuagents.vision.invoices import VENDORS, make_invoice, render
from cuagents.vision.ocr import _BITS, read_cell


@pytest.fixture(scope="module")
def rows():
    return benchmark()


def test_glyphs_are_distinct_and_cover_vendors():
    assert len({g for g in GLYPHS.values()}) == len(GLYPHS)
    for v in VENDORS:
        assert set(v) <= set(GLYPHS)


def test_clean_cell_reads_with_full_confidence():
    ch, conf = read_cell(_BITS["8"])
    assert ch == "8" and conf == 1.0


def test_clean_invoice_extracts_exactly():
    inv = make_invoice(0)
    d = extract(render(inv))
    assert d.route == "auto" and d.fields == truth(inv)


def test_bad_math_escalated_even_when_clean():
    inv = make_invoice(9, corrupt_total=True)
    d = extract(render(inv))
    assert d.route == "human" and "subtotal + tax != total" in d.reasons


def test_heavy_noise_escalates_with_low_confidence():
    d = extract(render(make_invoice(1), noise=0.25, seed=1))
    assert d.route == "human" and any("confidence" in r or "unreadable" in r for r in d.reasons)


def test_zero_wrong_auto_accepts_at_every_noise_level(rows):
    assert all(r["wrong_auto"] == 0 for r in rows)


def test_gate_prevents_errors_that_would_pass_without_it(rows):
    assert sum(r["wrong_if_no_gate"] for r in rows) > 0


def test_escalation_rises_with_noise(rows):
    hum = [r["human"] for r in rows]
    assert hum == sorted(hum) and hum[-1] > hum[0]


def test_all_bad_math_caught(rows):
    assert all(r["bad_math_caught"] == r["bad_math_total"] for r in rows)


def test_rendering_is_deterministic():
    a = render(make_invoice(3), noise=0.1, seed=3).tobytes()
    b = render(make_invoice(3), noise=0.1, seed=3).tobytes()
    assert a == b


def test_invalid_date_escalated(monkeypatch):
    from cuagents.vision import invoices

    inv = invoices.Invoice("INV-12345", "2026-02-30", "BIRCHLINE SUPPLY", "10.00", "0.80", "10.80")
    d = extract(render(inv))
    assert "date: not a calendar date" in d.reasons
