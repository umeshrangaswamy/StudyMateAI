# Architecture Decision Record (ADR) - 002: Agent Framework & Architecture

## Status
Approved

## Context
To move beyond monolithic API scripts, the agent orchestration must be modular, stateful, and capable of sequential tool execution, while maintaining zero latency overhead and strict cost boundaries.

## Decision
We adopt the **Google Agent Development Kit (ADK)** framework for agent definition and coordination:
- **Hierarchical Design**: A master `RootAgent` acts as a deterministic dispatcher, orchestrating task flow to specialized sub-agents (`RAGAgent`, `PhysicsSMEAgent`, `ChemistrySMEAgent`, `QuizAgent`, `EvaluatorAgent`).
- **Cost Gating**: Routing is determined by deterministic rules (e.g. keywords, intent classifiers) rather than auto-agent negotiation to eliminate unnecessary LLM reasoning calls.
- **State Management**: Session variables (such as query metadata and retrieved chunks) are persisted and shared in the ADK Session state object.
- **Factory Pattern**: All agents are instantiated via factory functions rather than module-level singletons to prevent runtime conflicts.

## Consequences
- **Pros**: Extensible agent structure, clean integration with Google's agent ecosystem, and strict execution trace visibility.
- **Cons**: Introducing ADK requires adapting local unit tests to mock runner and session layers.
