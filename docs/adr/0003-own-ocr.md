# ADR 0003: A small template OCR over generated invoices

**Status:** accepted

**Context.** An external OCR engine's output varies by version and platform, which would make CI numbers flaky.

**Decision.** Render with a 5x7 bitmap font and read back by template matching, with per-character confidence.

**Consequences.** Results are exactly reproducible. Accuracy is not a real-world claim, which is why the metric that matters is wrong auto-accepts under noise.
