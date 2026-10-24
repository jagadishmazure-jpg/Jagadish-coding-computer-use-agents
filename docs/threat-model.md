# Threat model

## STRIDE

| threat | surface | mitigation | residual |
| --- | --- | --- | --- |
| Spoofing | page text posing as system instructions | untrusted wrapper; planner ignores page instructions | a real LLM planner can still be persuaded; containment relies on the gates below |
| Tampering | agent edits tests or files outside the task | read-only tests, path jail, no new files | code under test can still do anything the OS user can |
| Repudiation | what did the agent do? | trajectory records (plan, edits, runs); per-step action log, PII-masked | logs are in memory only |
| Information disclosure | navigation or a sub-resource to an attacker host; env secrets | request-level allowlist; scrubbed env | DNS/network from test code is not blocked |
| Denial of service | infinite loops, hanging tests | step caps, subprocess timeout | - |
| Elevation of privilege | submit without consent | default-deny approver plus network one-shot | the approver policy is code; a careless human approver is out of scope |

## OWASP Top 10 for LLM applications

| item | where | control |
| --- | --- | --- |
| LLM01 Prompt injection | ticket text | wrapper, markers, goal-only parameters, allowlist, approval |
| LLM02 Sensitive information disclosure | logs | masking filter |
| LLM05 Improper output handling | agent edits code that is then executed | sandbox, hidden-test grading |
| LLM06 Excessive agency | submit, navigate | approval gate, allowlist |
| LLM10 Unbounded consumption | loops | step caps, timeouts |
