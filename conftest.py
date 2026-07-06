"""Root conftest.py – adds apps/backend to sys.path so that
both `app.*` and `adk.*` imports resolve during pytest execution."""
import sys
import os

# Ensure apps/backend is on sys.path for all test modules
_backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "apps", "backend"))
if _backend_path not in sys.path:
    sys.path.insert(0, _backend_path)
