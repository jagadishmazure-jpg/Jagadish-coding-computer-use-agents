# ADR 0001: Scripted policies and mock vision instead of real models

**Status:** accepted

**Context.** CI must be free and deterministic. The point is the harness: sandbox, guards, grading and escalation.

**Decision.** The coding agent uses a deterministic repair search, the browser agent uses scripted planners, and the vision step derives boxes from the DOM.

**Consequences.** Every guard is tested on every push. None of the numbers describe an LLM's ability. A real-model path must be optional and reported separately.
