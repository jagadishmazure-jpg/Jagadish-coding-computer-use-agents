# ADR 0002: Enforce browser guards at the network layer

**Status:** accepted

**Context.** A planner can be fooled by page text, and a page can load sub-resources on its own.

**Decision.** All requests go through a Playwright route handler. It aborts off-allowlist hosts and refuses the submit target unless a one-shot approval is armed.

**Consequences.** The naive-planner scenario shows containment without relying on the planner. Adding a new state-changing endpoint means adding it to the gate.
