# Phase 5: Learning Memory Migration Report

## Memory Architecture
Phase 5 introduces a Firestore-backed student learning memory to persist progress, assessments, weak areas, and revision metrics. This ensures contextual personalization across sessions without introducing high-cost state engines.

---

## Data Schema & Storage Structures

### `quiz_scores` Collection
Each document logs a single quiz session attempt:
*   `user_id` (string): Student ID.
*   `subject` (string): physics or chemistry.
*   `score` (integer): Obtained score.
*   `max_score` (integer): Maximum score.
*   `topic` (string): Grounding chapter or query context.
*   `timestamp` (timestamp): Server record timestamp.

### `student_profiles` Collection
Maintains consolidated user status details:
*   `weak_topics` (map): Keyed by subject containing list of weak concepts.
*   `exam_goal` (string): Target exam focus (neet/kcet).
*   `target_score` (integer): Target score goal.

### `revision_history` Collection
Tracks student milestone progress:
*   `user_id` (string): Student ID.
*   `subject` (string): Subject.
*   `topic` (string): Topic studied/revised.
*   `details` (string): Summary context details.
*   `timestamp` (timestamp): Server timestamp.

---

## Progress Skill (`progress_skill.py`)
Provides the `get_progress_report` capability to fetch consolidated metrics, weak areas, and custom revision advice based on the student's history.

---

## Files Created / Modified

### Created
*   [app/services/memory_service.py](file:///c:/Users/Admin/Documents/myprojects/StudyMateAI/apps/backend/app/services/memory_service.py): Core service wrapping async Firestore client queries for scoring, goals, and weakness lists.
*   [adk/skills/progress_skill.py](file:///c:/Users/Admin/Documents/myprojects/StudyMateAI/apps/backend/adk/skills/progress_skill.py): Exposes progress profiles and revision suggestions.

### Modified
*   [adk/skills/__init__.py](file:///c:/Users/Admin/Documents/myprojects/StudyMateAI/apps/backend/adk/skills/__init__.py): Exposes `get_progress_report`.
