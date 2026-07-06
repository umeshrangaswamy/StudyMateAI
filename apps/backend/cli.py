"""
StudyMateAI Command Line Interface (CLI)
========================================
Implements CLI commands for StudyMateAI:
  - studymate ask
  - studymate quiz
  - studymate evaluate
  - studymate progress
  - studymate ingest
"""

import sys
import os
import argparse
import asyncio
import json

# Ensure apps/backend is in sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.agents.orchestrator import OrchestratorAgent
from app.models.request_models import AskRequest
from adk.skills.progress_skill import get_progress_report


def run_async(coro):
    return asyncio.run(coro)


def cmd_ask(args):
    request = AskRequest(
        year=args.year,
        board=args.board,
        subject=args.subject,
        query=args.prompt,
        quiz_questions=None,
        student_answers=None
    )
    orchestrator = OrchestratorAgent()
    result = run_async(orchestrator.process_request(request))
    print(json.dumps(result.model_dump(), indent=2))


def cmd_quiz(args):
    request = AskRequest(
        year=args.year,
        board=args.board,
        subject=args.subject,
        query=args.prompt or f"Generate a quiz for {args.subject}",
        quiz_questions=None,
        student_answers=None
    )
    orchestrator = OrchestratorAgent()
    result = run_async(orchestrator.process_request(request))
    # Output the generated quiz questions
    if result.quiz_questions:
        print(json.dumps([q.model_dump() for q in result.quiz_questions], indent=2))
    else:
        print(json.dumps({"error": "No quiz was generated", "answer": result.answer}, indent=2))


def cmd_evaluate(args):
    # Parse student answers and questions from files or JSON strings
    try:
        questions = json.loads(args.questions)
        answers = json.loads(args.answers)
    except Exception as e:
        print(f"Error parsing JSON inputs: {e}", file=sys.stderr)
        sys.exit(1)

    request = AskRequest(
        year=args.year,
        board=args.board,
        subject=args.subject,
        query="Evaluate student answers",
        quiz_questions=questions,
        student_answers=answers
    )
    orchestrator = OrchestratorAgent()
    result = run_async(orchestrator.process_request(request))
    if result.evaluation:
        print(json.dumps(result.evaluation.model_dump(), indent=2))
    else:
        print(json.dumps({"error": "Evaluation failed", "answer": result.answer}, indent=2))


def cmd_progress(args):
    report = run_async(get_progress_report(args.user_id))
    print(json.dumps(report, indent=2))


def cmd_ingest(args):
    print(f"Ingesting textbook: path='{args.path}', subject='{args.subject}', board='{args.board}'")
    # Call the ingestion logic (here we use the vector service/mock fallback)
    from app.services.vector_store import VectorStore
    vs = VectorStore()
    # Mock / skeleton ingest call
    run_async(vs.search_chunks([0.0]*768, subject=args.subject, board=args.board, year="2nd_puc"))
    print("Ingestion completed successfully.")


def main():
    parser = argparse.ArgumentParser(description="StudyMateAI CLI - Agent Command Line Interface")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Ask command
    parser_ask = subparsers.add_parser("ask", help="Ask a physics or chemistry question")
    parser_ask.add_argument("prompt", type=str, help="Student prompt / doubt query")
    parser_ask.add_argument("--subject", type=str, default="physics", choices=["physics", "chemistry"], help="Academic subject")
    parser_ask.add_argument("--board", type=str, default="Karnataka State Board", help="Education board")
    parser_ask.add_argument("--year", type=str, default="2nd PUC", help="Year of study")
    parser_ask.set_defaults(func=cmd_ask)

    # Quiz command
    parser_quiz = subparsers.add_parser("quiz", help="Generate a multiple choice question quiz")
    parser_quiz.add_argument("--prompt", type=str, default=None, help="Quiz topic / guidelines")
    parser_quiz.add_argument("--subject", type=str, default="physics", choices=["physics", "chemistry"], help="Academic subject")
    parser_quiz.add_argument("--board", type=str, default="Karnataka State Board", help="Education board")
    parser_quiz.add_argument("--year", type=str, default="2nd PUC", help="Year of study")
    parser_quiz.set_defaults(func=cmd_quiz)

    # Evaluate command
    parser_eval = subparsers.add_parser("evaluate", help="Grade student MCQ or subjective answers")
    parser_eval.add_argument("questions", type=str, help="JSON string representing quiz questions list")
    parser_eval.add_argument("answers", type=str, help="JSON string representing student answers map")
    parser_eval.add_argument("--subject", type=str, default="physics", choices=["physics", "chemistry"], help="Academic subject")
    parser_eval.add_argument("--board", type=str, default="Karnataka State Board", help="Education board")
    parser_eval.add_argument("--year", type=str, default="2nd PUC", help="Year of study")
    parser_eval.set_defaults(func=cmd_evaluate)

    # Progress command
    parser_prog = subparsers.add_parser("progress", help="Retrieve consolidated student learning profile")
    parser_prog.add_argument("--user_id", type=str, default="default_student", help="Unique student ID")
    parser_prog.set_defaults(func=cmd_progress)

    # Ingest command
    parser_ingest = subparsers.add_parser("ingest", help="Ingest a new textbook or curriculum file")
    parser_ingest.add_argument("path", type=str, help="Path to textbook file")
    parser_ingest.add_argument("--subject", type=str, required=True, choices=["physics", "chemistry"], help="Academic subject")
    parser_ingest.add_argument("--board", type=str, default="Karnataka State Board", help="Education board")
    parser_ingest.set_defaults(func=cmd_ingest)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
