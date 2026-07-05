import logging
from typing import List, Dict, Any, Optional
from app.services.vertex_ai_service import VertexAIService
from prompts import CHEMISTRY_SME_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

class ChemistrySMEAgent:
    """
    SME Agent specializing in Chemistry curriculum, board exams,
    and entrance exams (KCET/NEET). Supports concept comparison,
    chemical equations, reaction mechanisms, and summaries.
    """
    def __init__(self):
        self.vertex_service = VertexAIService()
        logger.info("ChemistrySMEAgent initialized.")

    async def generate_response(
        self, 
        prompt: str, 
        intent: str, 
        exam: Optional[str], 
        context: List[Dict[str, Any]]
    ) -> str:
        """
        Generates structured Chemistry pedagogical explanations based on RAG context.
        Adheres strictly to the requested response style constraints.
        """
        logger.info(f"Chemistry SME generating response for intent={intent}, exam={exam}")

        # Check for insufficient context
        prompt_lower = prompt.lower().strip()
        unrelated_domains = [
            "history", "geography", "civics", "political", "social studies",
            "biology", "zoology", "botany", "literature", "poetry", "shakespeare"
        ]
        
        is_insufficient = False
        if not context:
            is_insufficient = True
        elif any(domain in prompt_lower for domain in unrelated_domains):
            is_insufficient = True

        if is_insufficient:
            logger.info("RAG context is insufficient or query is out-of-scope for Chemistry SME.")
            return "I cannot answer this query. The curriculum knowledge base does not contain enough context for this topic."

        # Construct system grounding context based on RAG chunks
        context_str = "\n".join([
            f"Source: {c.get('source_title', 'NCERT Textbook')} (Chapter: {c.get('chapter', 'N/A')}, Page: {c.get('page_number', 'N/A')})\nContent: {c.get('content')}"
            for c in context
        ])

        # Load system instruction template from prompt file package
        system_instruction = CHEMISTRY_SME_SYSTEM_PROMPT.format(
            intent=intent,
            exam=exam or 'Board Exams',
            context_str=context_str
        )

        # Call model service to generate response
        response_text = await self.vertex_service.generate_text(system_instruction, prompt)
        return response_text
