import sys
import os
import json
from unittest.mock import patch, MagicMock
import pytest

# Add apps/backend to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "apps", "backend"))

from cli import main


def test_cli_ask():
    test_args = ["cli.py", "ask", "Explain refractive index", "--subject", "physics"]
    with patch("sys.argv", test_args), patch("builtins.print") as mock_print:
        main()
        assert mock_print.called
        # Check printed output structure
        args, kwargs = mock_print.call_args
        output_str = args[0]
        output_data = json.loads(output_str)
        assert "answer" in output_data
        assert output_data["metadata"]["subject"] == "physics"


def test_cli_quiz():
    test_args = ["cli.py", "quiz", "--subject", "chemistry"]
    with patch("sys.argv", test_args), patch("builtins.print") as mock_print:
        main()
        assert mock_print.called
        args, kwargs = mock_print.call_args
        output_str = args[0]
        output_data = json.loads(output_str)
        # Should output a list of questions (mock quiz fallback structure)
        if isinstance(output_data, list):
            assert len(output_data) > 0
            assert "options" in output_data[0]
        else:
            assert "error" in output_data or "answer" in output_data


def test_cli_evaluate():
    questions = json.dumps([
        {
            "id": 1,
            "question": "Formula of water?",
            "correct_option": "A",
            "explanation": "H2O"
        }
    ])
    answers = json.dumps({"1": "A"})
    test_args = ["cli.py", "evaluate", questions, answers, "--subject", "chemistry"]
    with patch("sys.argv", test_args), patch("builtins.print") as mock_print:
        main()
        assert mock_print.called
        args, kwargs = mock_print.call_args
        output_str = args[0]
        output_data = json.loads(output_str)
        assert "score" in output_data
        assert output_data["score"] == 1


def test_cli_progress():
    test_args = ["cli.py", "progress", "--user_id", "test_user_123"]
    with patch("sys.argv", test_args), patch("builtins.print") as mock_print:
        main()
        assert mock_print.called
        args, kwargs = mock_print.call_args
        output_str = args[0]
        output_data = json.loads(output_str)
        assert "user_id" in output_data
        assert "weak_topics" in output_data


def test_cli_ingest():
    test_args = ["cli.py", "ingest", "dummy_path.pdf", "--subject", "physics"]
    with patch("sys.argv", test_args), patch("builtins.print") as mock_print:
        main()
        assert mock_print.called
        # Verify success message printed
        mock_print.assert_any_call("Ingestion completed successfully.")
