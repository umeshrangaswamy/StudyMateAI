# StudyMateAI Shared package

The `shared` package contains standard Pydantic models, Firestore transaction interfaces, database schemas, and helper utilities common across different components of the StudyMateAI platform.

## 📦 Package Contents

- **`packages/shared/shared/models/`**:
  - Request schemas (`AskRequest` defining query, subject constraints, quiz questions, and student answers).
  - Response schemas (`AskResponse`, `OrchestratorResult`, `MCQQuestionModel`, `TeacherReviewModel`, `EvaluationModel`).
- **`packages/shared/shared/services/`**:
  - `FirestoreService`: Handles logging query transactions and updates user profile statistics for student progress reports.
- **`packages/shared/shared/utils/`**:
  - Centralized utilities including date parsers and configuration validation helpers.

## 🚀 Usage

Install in editable mode for backend and script access:
```bash
# Install package from the root directory
pip install -e packages/shared
```
