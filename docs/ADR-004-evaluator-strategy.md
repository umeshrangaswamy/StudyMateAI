# Architecture Decision Record (ADR) - 004: Evaluator and Response Review Gating

## Status
Approved

## Context
Student-facing educational outputs must be high-quality, free from hallucinated facts, aligned with the target entrance exam format, and safe from jailbreaks or system prompt exposure.

## Decision
We implement a gated response verification system powered by the **Teacher Review Agent** (formerly the Evaluator Agent):
- **Post-generation Quality Check**: For high-stake intents (summaries, study notes) or low-confidence classification queries, the system routes the generated SME response to the Teacher Review Agent before returning it to the user.
- **Scoring Metrics**: The agent assigns scores (0.0 to 1.0) for accuracy, curriculum alignment, exam alignment, and quality.
- **Safety Gate**: If the response fails the approval gate (approved = False), the orchestrator intercepts the output and replaces it with a helpful revision alert, preventing toxic or hallucinated outputs from reaching the student.

## Consequences
- **Pros**: Double-gated safety and accuracy, preventing low-quality generated responses from reaching students.
- **Cons**: Adds a secondary LLM call latency penalty for reviewed queries.
