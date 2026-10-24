# Implementation guide

1. **Keep the harness, swap the model.** A real coding model replaces `policy.candidates` with proposed patches. Keep
   the sandbox, step cap, revert-on-fail and hidden-test grading unchanged.
2. **Grade on tests the agent cannot see.** Without hidden tests, T13-style overfits count as wins.
3. **Run the sandbox in a container** with no network, a read-only root and CPU/memory limits. The temp-dir jail here is the minimum.
4. **Enforce browser policy at the network layer,** not just in the planner. Route every request, abort off-allowlist hosts, and gate state-changing requests on a one-shot human approval.
5. **Take parameters from the goal, never from the page.** Amounts, recipients and URLs must come from the trusted task, and the approver should see them.
6. **Escalate documents on any doubt:** confidence below threshold, a failed cross-field check or an unparseable field. Track wrong auto-accepts as the headline metric and gate it at 0.
7. **Mask PII** in every log path, exceptions included.
