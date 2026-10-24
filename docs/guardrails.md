# Guardrails

| risk | control | test |
| --- | --- | --- |
| Agent writes outside its workspace | resolved path must be inside the sandbox root | `test_sandbox_blocks_escape` |
| Agent edits the tests it is graded on | `test_*` files are read-only; no new files | `test_sandbox_tests_are_read_only`, `test_sandbox_no_new_files` |
| Secrets leak into code under test | pytest runs with a scrubbed environment | `test_sandbox_scrubs_environment` |
| Hanging test | subprocess timeout | `test_sandbox_timeout` |
| Overfitting to visible tests | hidden tests graded separately and removed afterwards | `test_overfit_caught_by_hidden_tests`, `test_hidden_tests_never_left_in_sandbox` |
| Runaway loop | step caps in both agents | `test_step_cap_enforced` |
| Exfiltration by navigation or sub-resource | allowlist on `goto` and on every request | `test_goto_off_allowlist_refused`, `test_tracking_pixel_blocked_at_network`, `test_allowlist` |
| Unapproved form submit | approval action (default deny) plus network-level one-shot gate | `test_direct_click_on_submit_without_approval_is_blocked_at_network`, `test_approval_is_one_shot` |
| Prompt injection in page text | text wrapped untrusted, markers flagged, amount taken from goal | `test_injection_detected_and_ignored_by_guarded_planner`, `test_naive_planner_is_contained` |
| Wrong document auto-accepted | confidence threshold plus arithmetic and date checks | `test_zero_wrong_auto_accepts_at_every_noise_level` |
| PII in logs or errors | masking filter on the logger | `test_logger_masks` |
