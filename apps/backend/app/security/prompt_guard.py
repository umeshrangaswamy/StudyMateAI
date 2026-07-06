import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class PromptGuard:
    """
    Rule-based Prompt Guard to detect and block obvious prompt injection attempts.
    Returns structured allowed/reason results. Does not use LLMs for MVP constraints.
    """
    def __init__(self):
        # Precise injection patterns requested to block
        self.blocked_phrases = [
            "ignore previous instructions",
            "reveal system prompt",
            "print hidden instructions",
            "show api keys",
            "override developer message",
            "act as unrestricted ai",
            "jailbreak",
            "system override",
            "disregard safety rules"
        ]

    def validate_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        Checks input prompt against injection patterns.
        Returns a structured output:
        {
          "allowed": bool,
          "reason": Optional[str]
        }
        """
        if not prompt or not prompt.strip():
            return {
                "allowed": False,
                "reason": "empty_prompt"
            }

        prompt_lower = prompt.lower().strip()

        # Iterate and verify keywords
        for pattern in self.blocked_phrases:
            if pattern in prompt_lower:
                logger.warning(f"Prompt Guard blocked query due to injection signature: '{pattern}'")
                return {
                    "allowed": False,
                    "reason": "prompt_injection_detected"
                }

        return {
            "allowed": True,
            "reason": None
        }
