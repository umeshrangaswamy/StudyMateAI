# Kaggle Capstone Roadmap - StudyMateAI

This document defines the phases, timelines, and milestones for transforming StudyMateAI into a Kaggle Capstone project, validating multi-agent systems against academic benchmarks.

## 1. Roadmap Overview

```text
+------------------------+      +------------------------+      +------------------------+
|   Phase 0: Baseline    | ---> |  Phase 1: Validation   | ---> |   Phase 2: Release     |
|   Stable Architecture  |      |  Kaggle Dataset Ground |      |  Leaderboard Launch    |
|   Term Alignment       |      |  Automated Evaluator   |      |  Final Submission      |
+------------------------+      +------------------------+      +------------------------+
```

---

## 2. Phase Breakdown

### Phase 0: Architecture Stabilization (Current)
* **Goal**: Establish a clean, documented baseline and unify terminology.
* **Milestones**:
  - Replace all "Free Tier" instances with "MVP" to align with commercial readiness.
  - Create Specification, Architecture Vision, and ADRs.
  - Re-architect the Evaluator Agent into the **Teacher Review Agent** to explicitly capture the dual role of automated grading and safety/quality oversight.
  - Formulate future integration strategies for ADK and MCP.

### Phase 1: Dataset Grounding and Validation (Weeks 1-4)
* **Goal**: Ground the RAG system and SMEs in high-quality Kaggle datasets and academic test benchmarks.
* **Activities**:
  - Integrate public Kaggle question-answer datasets (e.g., MCQ datasets for Physics/Chemistry, KCET and NEET past papers).
  - Implement a programmatic evaluation script using the Teacher Review Agent.
  - Validate retrieval relevance (Hit Rate @ 3, Mean Reciprocal Rank) and response safety.

### Phase 2: Capstone Package Release & Submissions (Weeks 5-8)
* **Goal**: Package StudyMateAI as an open-source Kaggle Capstone repository and document outcomes.
* **Activities**:
  - Export structured evaluation reports detailing latency, cost (token usage), and accuracy metrics.
  - Deploy final frontend/backend configurations on Firebase and Cloud Run.
  - Prepare a submission Jupyter notebook detailing agent trace logging and performance against benchmark sets.
