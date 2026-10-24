# Interview points

- **Hidden tests matter:** one of 13 visible passes was an overfit. Only the hidden test caught it.
- **Know your agent's reach:** a single-edit policy cannot write new branches (T10, T11), and the table says so.
- **Revert on failure:** T14 and T15 needed a second candidate. Without the revert, the first bad edit would stack under the second.
- **Defense in depth for browsers:** even a planner that obeys injected text sent 0 off-allowlist requests and 0 unapproved submits, because the network route enforces both.
- **Default deny:** with no approver configured, nothing is submitted.
- **Escalation beats accuracy:** at 20% pixel noise, 19 of 20 invoices were escalated and 0 were wrongly auto-accepted. Accepting everything would have let 4 bad ones through.

<!-- BEGIN:coding -->
| metric | value |
| --- | --- |
| tasks | 15 |
| resolved (visible + hidden tests pass) | 12 / 15 (80.0%) |
| visible-only pass (overfit, caught by hidden tests) | 1 |
| mean steps | 6.0 |
| mean edits | 1.00 |
| mean test runs | 2.00 |
| step cap hits | 0 |
<!-- END:coding -->

Tests: <!-- BEGIN:tests -->73<!-- END:tests -->.
