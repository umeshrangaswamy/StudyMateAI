# Volume 2 – Multi-Agent Architecture Design
## StudyMateAI– Agentic AI Architecture (Version 1.0)

## 1. Purpose
This document defines the multi-agent architecture for StudyMateAI.

The architecture supports:
- Free Tier: 0–10 users, single runtime, low cost
- Enterprise: distributed multi-agent ecosystem, high scale, stronger governance

## 2. Core Agent Design Principle
Every request follows:
```text
Understand -> Retrieve -> Reason -> Generate -> Evaluate -> Respond
```

This ensures:
- Curriculum alignment
- Exam alignment
- Hallucination reduction
- Cost optimization
- Traceability

## 3. Agent Set – Design Scope
Full design includes:
1. Orchestrator Agent
2. Physics SME Agent
3. Chemistry SME Agent
4. Mathematics SME Agent
5. Biology SME Agent
6. English SME Agent
7. RAG Retrieval Agent
8. Internet Research Agent
9. Quiz Generator Agent
10. Evaluator Agent
11. Personalization Agent

## 4. Agent Set – Free Tier Implementation
Implemented in Free Tier:
1. Orchestrator Agent
2. Physics SME Agent
3. Chemistry SME Agent
4. RAG Agent
5. Quiz Generator Agent
6. Evaluator Agent
    - Academic Validation
    - Exam Validation
    - Quality Validation
    - Safety Validation
    - Student Assessment

Deferred:
- Mathematics SME
- Biology SME
- English SME
- Internet Research Agent
- Personalization Agent

## 5. Free Tier Logical Architecture
```text
Student
    |
Orchestrator
    |
RAG
    |
Physics SME / Chemistry SME
    |
Conditional Evaluator
    |
Response Composer
    |
Student
```

### Conditional Evaluator Execution

Under the Free Tier, the Evaluator Agent runs conditionally based on the intent, exam, and confidence of the query:
- **Mandatory Scenarios**: Quiz generation, Student answer evaluation.
- **Conditional Scenarios**: KCET queries, NEET queries, Lesson summaries, Quick notes, and Low confidence SME responses.

### Enterprise Behavior

In the Enterprise tier, the Evaluator Agent acts as the final teacher-review layer in the response pipeline and executes on every SME-generated response before it is sent to the student.


## 6. Enterprise Logical Architecture
```text
Student
  -> API Gateway
  -> Orchestrator Agent
      -> SME Agents
      -> RAG Agent
      -> Internet Research Agent
      -> Quiz Generator Agent
      -> Evaluator Agent
      -> Personalization Agent
  -> Response Composer
  -> Analytics + Monitoring
```

## 7. Orchestrator Agent
### Responsibilities
- Validate request
- Run prompt guard
- Detect subject
- Detect intent
- Detect exam name from prompt: KCET or NEET in free tier
- Route to correct workflow
- Route to Evaluator Agent for quality validation and teacher-review based on routing rules
- Assemble response
- Enforce scope restrictions

### Orchestrator Routing Rules
The Orchestrator Agent determines if the Evaluator Agent is required according to the following rules:
```text
IF intent = quiz_generation
    -> Evaluator Required

IF intent = answer_evaluation
    -> Evaluator Required

IF exam = KCET
    -> Evaluator Required

IF exam = NEET
    -> Evaluator Required

IF intent = lesson_summary
    -> Evaluator Required

IF intent = quick_notes
    -> Evaluator Required

IF confidence < threshold
    -> Evaluator Required
```

### Intents
- doubt_solving
- lesson_explanation
- lesson_summary
- quick_notes
- exam_preparation
- entrance_preparation
- quiz_generation
- answer_evaluation

### Output Contract
```json
{
  "subject": "physics",
  "intent": "entrance_preparation",
  "exam": "neet",
  "workflow": "rag_then_sme",
  "confidence": 0.85
}
```

## 8. Physics SME Agent
### Important Clarification
Physics SME is not only a doubt-answering agent. It must support:
- Physics query answering
- Lesson explanation
- Lesson summary
- Quick notes
- Board exam preparation
- KCET preparation
- NEET preparation
- Formula explanation
- Numerical guidance
- Graph/diagram explanation where useful

### Response Structure
1. Short heading
2. Simple explanation
3. Real-life example
4. Formula if applicable
5. KCET/NEET tip if exam is detected

## 9. Chemistry SME Agent
Chemistry SME supports:
- Chemistry query answering
- Lesson explanation
- Lesson summary
- Quick notes
- Board exam preparation
- KCET preparation
- NEET preparation
- Chemical reaction explanation
- Equation explanation
- Concept comparison

### Response Structure
1. Short heading
2. Concept
3. Explanation
4. Chemical example/equation if required
5. Exam tip if KCET/NEET is detected

## 10. RAG Agent
### Responsibilities
- Accept query and metadata
- Generate query embedding
- Apply metadata filters
- Perform pgvector similarity search
- Return top-k chunks
- Compress context
- Provide source metadata

### Retrieval Rule
Never search the full knowledge base without metadata filtering.

## 11. Quiz Generator Agent
### Responsibilities
- Generate MCQs
- Generate short answer questions
- Generate KCET-style questions
- Generate NEET-style questions
- Provide answers and short explanations

### Free Tier Default
- 5 questions
- MCQ format
- 4 options
- Correct answer
- Explanation

## 12. Evaluator Agent
The Evaluator Agent acts as the final **Teacher Review Agent** and **Academic Quality Agent**.

### Responsibilities

#### Academic Validation
Checks:
- Accuracy (factual correctness)
- Curriculum Alignment
- Subject Alignment
- Topic/Chapter Alignment
- Completeness (answer completeness)

#### Exam Alignment Validation
Checks:
- KCET Relevance (when KCET is detected)
- NEET Relevance (when NEET is detected)
- Exam Readiness
- Important Concepts Coverage (important exam-oriented points included)

#### Response Quality Validation
Checks:
- Answer Length (detect overly long or short responses)
- Readability (crisp and understandable answers)
- Teacher-like Explanation
- Real-life Examples (ensure included when appropriate)
- Clarity

#### Guardrail Validation
Checks:
- Prompt Leakage detection
- Instruction Leakage detection
- Unsafe Content detection
- Out-of-Scope Content detection

#### Student Assessment
Evaluates:
- MCQs (quiz answers)
- Subjective Answers
- Written Explanations
- Practice Tests (suggest revision topics and feedback)

### Output Contracts

#### 1. Student Assessment Output Contract
Returned when grading student attempts:
```json
{
  "score": 8,
  "max_score": 10,
  "feedback": "Good answer but missing one key point.",
  "missing_points": ["Mention formula", "Add unit"],
  "revision_tip": "Revise lens formula and sign convention."
}
```

#### 2. Teacher Review / Quality Validation Output Contract
Returned when reviewing generated SME responses or quizzes:
```json
{
  "accuracy_score": 0.95,
  "curriculum_alignment_score": 0.98,
  "exam_alignment_score": 0.92,
  "response_quality_score": 0.94,
  "approved": true,
  "feedback": "Response is aligned with NEET requirements and curriculum scope."
}
```

## 13. Internet Research Agent
Enterprise only.

Trigger conditions:
- Local RAG confidence is low
- Syllabus update needed
- Recent exam pattern update needed

Trusted domains:
- nta.ac.in
- ncert.nic.in
- cetonline.karnataka.gov.in
- ugc.gov.in
- gov.in domains

## 14. Personalization Agent
Enterprise only.

Responsibilities:
- Track weak topics
- Generate revision schedules
- Recommend quizzes
- Build learning profile
- Generate exam readiness reports

## 15. Free Tier Agent Deployment
All agents run in one Cloud Run backend service.

```text
Cloud Run: study-buddy-api
  -> Orchestrator
  -> Physics SME
  -> Chemistry SME
  -> RAG
  -> Quiz Generator
  -> Evaluator
```

## 16. Enterprise Agent Deployment
Agents may be split into services:
- orchestrator-service
- rag-service
- academic-sme-service
- quiz-service
- evaluator-service
- personalization-service

## 17. Agent Workflow Patterns
### Doubt Solving
```text
Orchestrator -> RAG -> SME -> Response
```

### Lesson Summary
```text
Orchestrator -> RAG -> SME Summary -> Response
```

### Entrance Preparation
```text
Orchestrator -> RAG -> SME with KCET/NEET mode -> Response
```

### Quiz Generation
```text
Orchestrator -> RAG -> Quiz Generator -> Response
```

### Evaluation
```text
Orchestrator -> Evaluator -> Response
```

## 18. Locked Agent Decisions
- No separate Exam Agent in free tier.
- Physics SME and Chemistry SME handle exam and entrance preparation.
- Quiz Generator only generates assessments.
- Evaluator Agent acts as a Teacher Review & Academic Quality layer, performing quality validation and safety checks, as well as student assessments.
- RAG only retrieves context.
- Orchestrator routes, validates, and manages conditional evaluation flow.
