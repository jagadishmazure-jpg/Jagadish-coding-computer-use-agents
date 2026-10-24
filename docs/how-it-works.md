# How it works, step by step

## Coding agent
1. `Sandbox(task.files)` copies the task into a fresh temp directory.
2. Steps 1-2: list files, then run the visible tests to get a baseline failure.
3. Read the test files and collect the names they import from the module. Those are the suspect functions.
4. Read each source file and generate candidates: for each line of each suspect function, every repair pattern at
   every occurrence, in a fixed order, with duplicates removed.
5. For each candidate: write it (one step), run pytest (one step), stop on a pass, otherwise restore the original (reverted += 1).
6. Every action counts against `max_steps` (default 40). At the cap, the run stops with `hit_cap`.
7. If the visible tests pass, the grader copies the source into a separate directory with the hidden tests and runs them.
   `resolved` means both suites pass.

## Computer-use loop
1. `Env` launches headless Chromium and routes every request through `_route`.
2. Off-allowlist hosts are aborted and recorded. `refund.html`, the form's target, is refused unless `Approval.consume()` returns True.
3. Each step: `screenshot()` returns PNG bytes, then `look()` validates them and attaches DOM boxes, with all text wrapped untrusted and markers listed.
4. The planner returns one action: `click`, `click_type`, `goto`, `submit`, `done` or `stop`.
5. `submit` calls `Approval.ask(summary)`. A no ends the run with "waiting for a human". A yes arms one network pass, and the click goes through.
6. `done` checks the confirmation page shows the goal amount.

## Invoice agent
1. `make_invoice(i)` makes a fictional invoice; every tenth one gets a total that does not add up.
2. `render()` draws it at 3x scale and flips pixels with seeded noise.
3. `read()` majority-votes each 3x3 block back to a 5x7 cell, finds the nearest glyph by Hamming distance and scores
   its confidence from the distance and the margin to the runner-up.
4. `extract()` regex-parses six fields, checks arithmetic and date, applies the 0.80 threshold, and routes to `auto` or `human` with reasons.
