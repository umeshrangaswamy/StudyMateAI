# Phase 6: Agent CLI Migration Report

## CLI Architecture & Entrypoints
Phase 6 introduces the StudyMateAI Agent Command Line Interface (CLI). This allows students, teachers, and admins to run model routing, quiz generation, grading, memory retrieval, and curriculum ingestion processes directly from the terminal.

To support simple invocation on Windows environments, a `studymate.bat` wrapper has been added to the root of the workspace to forward calls to the Python CLI.

---

## Commands & Usage

### 1. `studymate ask`
Ask a physics or chemistry question:
```bash
.\studymate.bat ask "Explain Ray Optics refraction" --subject physics
```

### 2. `studymate quiz`
Generate a new MCQ quiz on a topic:
```bash
.\studymate.bat quiz --subject chemistry --prompt "Chemical Bonding"
```

### 3. `studymate evaluate`
Evaluate student quiz answers:
```bash
.\studymate.bat evaluate '[{"id": 1, "question": "..."}]' '{"1": "A"}'
```

### 4. `studymate progress`
Retrieve consolidated student learning profile (scores, goals, weak topics):
```bash
.\studymate.bat progress --user_id "student_123"
```

### 5. `studymate ingest`
Ingest textbook PDFs or curriculum documents:
```bash
.\studymate.bat ingest "path/to/chemistry_ch1.pdf" --subject chemistry
```

---

## Files Created / Modified / Deleted

### Created
*   [apps/backend/cli.py](file:///c:/Users/Admin/Documents/myprojects/StudyMateAI/apps/backend/cli.py): Main Python CLI implementation containing all parser arguments and orchestrator runners.
*   [studymate.bat](file:///c:/Users/Admin/Documents/myprojects/StudyMateAI/studymate.bat): Windows batch file wrapper.
*   [tests/test_cli.py](file:///c:/Users/Admin/Documents/myprojects/StudyMateAI/tests/test_cli.py): CLI automated test cases.

### Deleted
*   [scripts/ingestion/ingest.py](file:///c:/Users/Admin/Documents/myprojects/StudyMateAI/scripts/ingestion/ingest.py): Redundant script superseded by `studymate ingest`.
