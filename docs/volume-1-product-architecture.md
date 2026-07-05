# Volume 1 – Product Architecture, Educational AI Boundaries & UI Workflow Design
## StudyMateAI– Spec Driven Architecture (Version 1.0)

## 1. Purpose
StudyMateAIis an AI-powered Study Mentor platform designed to assist school, PUC, undergraduate, and entrance-exam students with curriculum-aligned learning support.

The platform acts as an experienced teacher by:
- Explaining concepts in simple language
- Providing real-life examples
- Solving doubts
- Generating summaries and notes
- Assisting with entrance exam preparation
- Conducting self-assessments and quizzes
- Remaining strictly within selected academic scope

## 2. Scope
### Design Scope
Subjects:
- Physics
- Chemistry
- Mathematics
- Biology
- English

Entrance Exams:
- KCET
- NEET
- JEE

### Phase 1 Implementation Scope
Subjects:
- Physics
- Chemistry

Entrance Exams:
- KCET
- NEET

## 3. Core Product Principles
### 3.1 Curriculum First
Every response must prioritize:
- Year of Study
- University / Board
- Subject
- Exam scope if mentioned in the prompt

### 3.2 Scope Constrained
The AI must not drift outside the selected academic context. If a query is outside the scope, it should politely redirect the student.

### 3.3 Teacher-Like Responses
Responses must be:
- Simple
- Crisp
- Accurate
- Context-aware
- Easy to remember
- Exam-oriented where relevant

Avoid:
- Research-style answers
- Long essays
- Unsupported claims
- Overly short unhelpful replies

### 3.4 Progressive Learning Pattern
Preferred answer pattern:
1. Simple explanation
2. Real-life example
3. Formula / diagram / table where useful
4. Exam relevance if KCET or NEET is detected

## 4. Target Users
### School Students
Needs: concept understanding, quick notes, homework support.

### PUC Students
Needs: board exams, KCET preparation, NEET preparation.

### Undergraduate Students
Needs: semester preparation and university syllabus support.

## 5. Educational AI Boundaries
### Allowed
- Physics, Chemistry, Mathematics, Biology, English
- KCET, NEET, JEE preparation
- Lesson explanation
- Doubt solving
- Revision notes
- Quiz generation
- Formula explanation
- Exam preparation
- Study guidance

### Restricted
- Political debate
- Medical diagnosis
- Legal advice
- Financial advice
- Harmful activity
- Out-of-curriculum advanced topics unless explicitly relevant
- Prompt injection or system prompt extraction requests

## 6. Response Length Rules
- Definition: 50–100 words
- Concept explanation: 100–200 words
- Numerical problem: stepwise solution
- Summary: 5–10 bullets
- Quick notes: 10–15 bullets
- Quiz: 5 questions by default in free tier

## 7. Free Tier Product Scope
User base: 0–10 active students.

Supported:
- Doubt solving
- Lesson explanation
- Lesson summary
- Quick notes
- Quiz generation
- Evaluator feedback
- KCET support
- NEET support
- Physics and Chemistry only

Not included initially:
- Authentication dashboard
- Parent dashboard
- Teacher dashboard
- Personalization engine
- Redis cache
- GKE
- Apigee
- Cloud Armor

## 8. Production / Enterprise Scope
Additional capabilities:
- Personalized study plans
- Weakness identification
- Progress analytics
- Teacher dashboard
- Parent dashboard
- Multi-language support
- Advanced content moderation
- Internet research agent
- Additional subjects and exams

## 9. Free Tier UI Specification
Fields:
1. Year of Study dropdown
2. University / Board dropdown
3. Subject dropdown
4. Prompt text area
5. Submit button
6. Response panel

Important decision:
The student prompt is where the user mentions lesson name, chapter name, exam name, or entrance exam name. These are not separate UI fields in the free-tier version.

Example prompts:
- Explain Ray Optics for NEET
- Summarize Thermodynamics
- Generate KCET quiz on Atomic Structure
- What is Chemical Bonding?

## 10. Free Tier UI Layout
```text
+------------------------------------------------+
|                  StudyMateAI               |
+------------------------------------------------+
| Year of Study       [Dropdown]                 |
| University / Board  [Dropdown]                 |
| Subject             [Dropdown]                 |
|                                                |
| Ask Your Question                              |
| [Large Text Box]                               |
|                                                |
| [Submit]                                       |
|                                                |
| Response Panel                                 |
| - Text                                         |
| - Tables                                       |
| - Equations                                    |
| - Quiz                                         |
| - Mermaid diagrams                             |
+------------------------------------------------+
```

## 11. User Journey – Free Tier
```text
Student
  -> Select Year
  -> Select University / Board
  -> Select Subject
  -> Enter prompt
  -> Submit
  -> Backend Orchestrator
  -> RAG + SME / Quiz / Evaluator
  -> Response displayed
```

## 12. User Journey – Enterprise
```text
Student
  -> Authenticated profile
  -> Context-aware prompt
  -> API Gateway
  -> Orchestrator
  -> RAG / SME / Evaluator / Personalization
  -> Response composer
  -> Analytics update
```

## 13. Product Workflow – Free Tier
```text
Frontend UI
  -> Cloud Run Backend
  -> Orchestrator Agent
  -> RAG Agent
  -> Physics SME or Chemistry SME
  -> Quiz Generator or Evaluator when required
  -> Response Panel
```

## 14. Product Workflow – Enterprise
```text
Frontend / Mobile App
  -> Cloud Armor
  -> Apigee
  -> Orchestrator Service
  -> Distributed Agent Services
  -> RAG + Evaluation + Personalization
  -> Observability + Analytics
```

## 15. Locked Product Decisions
- Design includes Physics, Chemistry, Mathematics, Biology, English.
- Free tier implements Physics and Chemistry only.
- Design includes KCET, NEET, JEE.
- Free tier implements KCET and NEET only.
- UI remains minimal in free tier.
- Prompt field captures lesson, chapter, exam, entrance exam, and question intent.
