import os

# Base directory paths mapping to packages/prompts
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_prompt(filename: str) -> str:
    """
    Loads prompt instructions from markdown files, automatically stripping 
    top metadata frontmatter boundaries.
    """
    filepath = os.path.join(BASE_DIR, filename)
    if not os.path.exists(filepath):
        # Fallback to local package directory if needed
        local_filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        if os.path.exists(local_filepath):
            filepath = local_filepath
        else:
            raise FileNotFoundError(f"Prompt file '{filename}' was not found at {filepath}")

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Automatically parse and strip YAML frontmatter if present
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            content = parts[2].strip()

    return content

# Backward compatibility direct prompt loader variables
ORCHESTRATOR_SYSTEM_PROMPT = load_prompt("global_system.md")
PHYSICS_SME_SYSTEM_PROMPT = load_prompt("physics_sme.md")
CHEMISTRY_SME_SYSTEM_PROMPT = load_prompt("chemistry_sme.md")
QUIZ_GENERATOR_SYSTEM_PROMPT = load_prompt("quiz_generator.md")
EVALUATOR_SYSTEM_PROMPT = load_prompt("evaluator.md")
EVALUATOR_REVIEW_SYSTEM_PROMPT = load_prompt("evaluator_review.md")
RAG_AGENT_SYSTEM_PROMPT = load_prompt("rag_agent.md")
