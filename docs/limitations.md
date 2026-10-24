# Limitations and known failures

- **Scripted coding policy.** It searches single-token edits in a fixed order and cannot add branches or edit two
  lines. T10 and T11 are kept as misses. The search order suits these bug types, so its mean of 6 steps is not
  comparable to an LLM agent's trajectory.
- **Overfit T13** is kept as a test. The policy "fixes" it in a way that passes the visible test only.
- **Sandbox** isolation is process-level. Code under test runs as the same OS user and can open network sockets. A real deployment needs a container or VM with no network.
- **Mock vision** reads DOM boxes, so recognition errors from a real vision model are not modelled.
- **Template OCR** is matched to its own font. Its accuracy says nothing about real scans; only pixel noise is tested.
- **Injection markers** are regex-based and easy to paraphrase past. The guarantees come from the allowlist and the approval gate.
- **Small sets:** 15 tasks, 7 scenarios, and 80 invoice renders (20 invoices at 4 noise levels). These are regression checks.
