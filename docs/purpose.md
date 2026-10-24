# Purpose and audience

Agents that edit code, drive a browser or read documents can do real damage when they are wrong. Most of the
engineering that makes them safe sits around the model: where they may write, what counts as success, which
hosts they may reach, when a human must say yes, and when to stop and escalate.

This repo builds that surrounding layer for three agent types and grades it with deterministic stand-in models,
so every guard and metric is reproducible for free.

| reader | start here |
| --- | --- |
| Agent engineers | `src/cuagents/coding/sandbox.py`, `computer/env.py`, `vision/agent.py` |
| Reviewers | README results, `docs/interview-points.md` |
| Adopters | `docs/implementation-guide.md` |
