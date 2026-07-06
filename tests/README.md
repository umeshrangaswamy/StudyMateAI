# StudyMateAI Backend Tests

This directory houses unit and integration tests for verification of FastAPI endpoint routing, helper services, and agent logic.

## 📂 Test Organization

- **`conftest.py`**: Shared test fixtures, mock services, and FastAPI test client configurations.
- **`tests/test_api.py`**: Verification of endpoints (`/health`, `/ready`, `/api/ask` and legacy backward-compatibility routes).
- **`tests/test_agents.py`**: Isolated verification of sub-agent and orchestrator logic.

## 🚀 Running Tests
```bash
# Activate your virtual environment first, then run:
pytest
```
