# StudyMateAI - MVP Technical & Product Specification

This specification defines the functional scope, configuration, constraints, and data schemas for the MVP version of StudyMateAI.

## 1. Product Capabilities & Boundaries

### 1.1 Academic Scope
The MVP explicitly supports:
- **Subjects**: Physics, Chemistry.
- **Entrance Exams**: KCET (Karnataka Common Entrance Test), NEET (National Eligibility cum Entrance Test).

*Note: Mathematics, Biology, English, and JEE are designed for future releases but are explicitly blocked in the MVP router and ingestion pipeline.*

### 1.2 User Capacity
- Optimized for **0–10 active concurrent users**.
- Single-instance backend hosting architecture.

### 1.3 Core Workflows
1. **Doubt Solving & Concept Explanation**: Accept a user query, retrieve relevant curriculum context using metadata-filtered RAG, and generate a clear response.
2. **Notes & Summary Generation**: Generate 5–10 bullet-point summaries or 10–15 bullet-point study notes grounded in source materials.
3. **Quiz Generation**: Generate exactly 5 multiple-choice questions (MCQs) complete with 4 options, the correct answer, and an explanation.
4. **Teacher Review & Academic Quality Evaluation**: Grade student quiz/subjective answers and check LLM responses for accuracy and guardrail safety.

---

## 2. API Schema and Data Models

### 2.1 Request Schema (Doubt / Quiz / Notes Query)
```json
{
  "year_of_study": "2nd_puc",
  "board_university": "karnataka_state_board",
  "subject": "physics",
  "prompt": "Explain Ray Optics refraction for NEET"
}
```

### 2.2 Response Schema (SME Response with Sources)
```json
{
  "text": "Refraction is the bending of light as it passes from one transparent medium to another...",
  "sources": [
    {
      "document_id": "8f2a1b3c-9d8e-7f6a-5b4c-3d2e1f0a9b8c",
      "chapter": "ray_optics",
      "page_number": 142
    }
  ],
  "agent_path": "orchestrator -> RAG -> PhysicsSME -> TeacherReviewAgent",
  "teacher_review": {
    "accuracy_score": 0.98,
    "curriculum_alignment_score": 1.0,
    "exam_alignment_score": 0.95,
    "response_quality_score": 0.96,
    "approved": true,
    "feedback": "Aligned with NEET scope and NCERT concepts."
  }
}
```

### 2.3 Quiz Response Schema
```json
{
  "questions": [
    {
      "question_id": 1,
      "question_text": "What is the relation between focal length and radius of curvature for a spherical mirror?",
      "options": {
        "A": "f = R",
        "B": "f = R/2",
        "C": "f = 2R",
        "D": "f = R/4"
      },
      "correct_answer": "B",
      "explanation": "For spherical mirrors of small aperture, the focal length is half of its radius of curvature."
    }
  ]
}
```

---

## 3. System Constraints & Cost Controls

| Parameter | MVP Constraint | Rationale |
| :--- | :--- | :--- |
| **Max Concurrent Users** | 10 | Standard serverless single container limits |
| **RAG Top-K Chunks** | 3 | Limits context size and keeps prompt token costs low |
| **Chunk Size** | 250–350 tokens | Ensures focused retrieval context |
| **Cloud Run Instances** | Min: 0, Max: 2 | Minimizes cold-standby charges and controls maximum cost |
| **Embedding Dimension** | 768 | Matches `text-embedding-004` dimensions |
| **Model Selection** | Vertex AI Gemini 1.5 Flash | Fast execution speed, high context size, cost-optimized |

---

## 4. UI Specification
The frontend must provide a simple, single-page form layout:
- **Inputs**:
  - `Year of Study`: Dropdown (`1st_puc`, `2nd_puc`, etc.)
  - `University / Board`: Dropdown (`karnataka_state_board`, `cbse`, etc.)
  - `Subject Selection`: Radio buttons (`Physics`, `Chemistry`)
  - `Exam Prep Focus`: Toggle dropdown (`Board`, `KCET`, `NEET`)
  - `Task Selection`: Tabs (`Ask Doubt`, `Generate Summary`, `Take Quiz`)
  - `Prompt Box`: Text area with character limit (10–500 characters)
