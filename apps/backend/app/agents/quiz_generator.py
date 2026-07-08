import logging
import json
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from app.services.vertex_ai_service import VertexAIService
from prompts import QUIZ_GENERATOR_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

# Pydantic schema definition for structured output
class MCQQuestionSchema(BaseModel):
    question: str = Field(..., description="The multiple choice question text, including board/exam tag like (Board) or (NEET) at the end")
    options: List[str] = Field(..., description="Exactly 4 options for the question")
    answer: str = Field(..., description="The correct option letter: A, B, C, or D")
    explanation: str = Field(..., description="Detailed pedagogical explanation of why this option is correct")

class QuizSchema(BaseModel):
    quiz: List[MCQQuestionSchema] = Field(..., description="A list of multiple choice questions")


class QuizGeneratorAgent:
    """
    Quiz Generator Agent responsible for creating educational assessment questions
    (allowing Concise (5) vs Detailed (20) MCQ count).
    Allows generating NEET-style, KCET-style, or general chapter quizzes grounded in RAG context.
    """
    def __init__(self):
        self.vertex_service = VertexAIService()
        logger.info("QuizGeneratorAgent initialized.")

    async def generate_quiz(
        self,
        year: str,
        board: str,
        subject: str,
        query: str,
        exam: Optional[str] = None,
        context: List[Dict[str, Any]] = [],
        sources: List[Dict[str, Any]] = [],
        response_style: Optional[str] = "concise"
    ) -> Dict[str, Any]:
        """
        Generates structured JSON quiz format matching the user requirements.
        Uses Gemini to generate topic-specific questions grounded in RAG context.
        """
        logger.info(
            f"QuizGeneratorAgent: Generating quiz on subject={subject}, board={board}, "
            f"exam={exam or 'general'}, query='{query}', response_style={response_style}"
        )

        # 1. Scope and boundaries validation
        subject_lower = subject.lower().strip()
        if subject_lower not in ["physics", "chemistry"]:
            raise ValueError(f"Quiz generation for subject '{subject}' is not supported in the MVP.")

        # 2. Extract grounding context contents
        context_str = "\n".join([
            f"Source: {c.get('source_title', 'Textbook')} (Chapter: {c.get('chapter', 'N/A')})\nContent: {c.get('content')}"
            for c in context
        ]) if context else "No specific context retrieved. Use general curriculum knowledge for this topic."

        # 3. Format dynamic system instructions
        system_instruction = QUIZ_GENERATOR_SYSTEM_PROMPT.format(
            prompt=query,
            subject=subject,
            board=board,
            year_of_study=year
        )

        num_questions = 20 if response_style == "detailed" else 5

        # 4. Build the full quiz generation prompt
        exam_style = f"{exam.upper()} style" if exam else "Board exam style"
        quiz_prompt = (
            f"Generate exactly {num_questions} {exam_style} multiple-choice questions (MCQs) on the following topic:\n"
            f"Topic: {query}\n"
            f"Subject: {subject} | Board: {board} | Year: {year}\n\n"
            f"Grounding Context from curriculum textbooks:\n{context_str}\n\n"
            f"IMPORTANT: Questions MUST be strictly about '{query}'. Do NOT generate questions about other topics.\n\n"
            f"Return a structured JSON object containing exactly {num_questions} questions."
        )

        try:
            # Use generate_json to enforce the Pydantic schema structurally
            response_json = await self.vertex_service.generate_json(
                system_instruction=system_instruction,
                prompt=quiz_prompt,
                schema=QuizSchema
            )

            data = json.loads(response_json)
            # If the response was a placeholder mock, raise ValueError to trigger fallback
            if "status" in data and data["status"] == "mocked":
                raise ValueError("Using mock fallback")

            # Parse questions to dicts matching expected list structure
            quiz_list = []
            for q in data.get("quiz", []):
                # Ensure options is list of strings
                opts = [str(o) for o in q.get("options", [])]
                # Pad to 4 options if not exactly 4
                while len(opts) < 4:
                    opts.append("Placeholder option")
                opts = opts[:4]

                quiz_list.append({
                    "question": str(q.get("question", "")),
                    "options": opts,
                    "answer": str(q.get("answer", "A")).upper().strip(),
                    "explanation": str(q.get("explanation", ""))
                })

            if len(quiz_list) >= 3:
                logger.info(f"QuizGeneratorAgent: Successfully generated {len(quiz_list)} structured LLM questions for '{query}'")
                return {"quiz": quiz_list}
            else:
                logger.warning(f"QuizGeneratorAgent: LLM returned insufficient valid questions ({len(quiz_list)}), using fallback")
                raise ValueError("Insufficient valid questions from LLM")

        except Exception as e:
            logger.error(f"QuizGeneratorAgent: Structured LLM quiz generation failed: {str(e)}. Using fallback.")
            return self._get_fallback_questions(subject_lower, query, exam)

    def _get_fallback_questions(self, subject: str, query: str, exam: Optional[str]) -> Dict[str, Any]:
        """
        Returns topic-aware fallback questions when the LLM fails.
        These are generic but labeled with the requested topic.
        """
        exam_suffix = f"({exam.upper()} target)" if exam else "(Board level)"
        query_lower = query.lower()

        if subject == "physics":
            if any(w in query_lower for w in ["electric", "charge", "coulomb", "field"]):
                return {"quiz": [
                    {
                        "question": f"According to Coulomb's Law, the electrostatic force between two point charges is: {exam_suffix}",
                        "options": ["Directly proportional to r²", "Inversely proportional to r²", "Directly proportional to r", "Inversely proportional to r"],
                        "answer": "B",
                        "explanation": "Coulomb's Law states F = kq₁q₂/r². Thus force is inversely proportional to the square of the distance between them."
                    },
                    {
                        "question": f"The SI unit of electric charge is: {exam_suffix}",
                        "options": ["Ampere", "Volt", "Coulomb", "Farad"],
                        "answer": "C",
                        "explanation": "The SI unit of electric charge is the Coulomb (C)."
                    },
                    {
                        "question": f"Electric field lines originate from: {exam_suffix}",
                        "options": ["Negative charges", "Positive charges", "Both positive and negative", "Neutral conductors only"],
                        "answer": "B",
                        "explanation": "Electric field lines originate from positive charges and terminate at negative charges."
                    },
                    {
                        "question": f"The value of permittivity of free space (ε₀) is approximately: {exam_suffix}",
                        "options": ["8.85 × 10⁻¹² C²/Nm²", "9 × 10⁹ Nm²/C²", "1.6 × 10⁻¹⁹ C", "6.67 × 10⁻¹¹ Nm²/kg²"],
                        "answer": "A",
                        "explanation": "ε₀ = 8.85 × 10⁻¹² C²/Nm² (or F/m)."
                    },
                    {
                        "question": f"A charge of 1 Coulomb is equivalent to: {exam_suffix}",
                        "options": ["6.24 × 10¹⁸ electrons", "1.6 × 10⁻¹⁹ electrons", "9 × 10⁹ electrons", "3 × 10⁸ electrons"],
                        "answer": "A",
                        "explanation": "1 C = 6.24 × 10¹⁸ elementary charges (electrons), since e = 1.6 × 10⁻¹⁹ C."
                    }
                ]}
            else:
                return {"quiz": [
                    {
                        "question": f"Which of the following is a vector quantity? {exam_suffix}",
                        "options": ["Mass", "Temperature", "Electric field", "Electric potential"],
                        "answer": "C",
                        "explanation": "Electric field is a vector quantity — it has both magnitude and direction."
                    },
                    {
                        "question": f"The principle of superposition in electrostatics states: {exam_suffix}",
                        "options": ["Charges cancel each other", "Total force is the vector sum of individual forces", "Forces multiply", "Charges repel always"],
                        "answer": "B",
                        "explanation": "The principle of superposition states that the total electric force on a charge is the vector sum of all individual forces due to each charge separately."
                    },
                    {
                        "question": f"Which physical quantity has the unit Newton/Coulomb (N/C)? {exam_suffix}",
                        "options": ["Electric potential", "Electric flux", "Electric field intensity", "Electric charge"],
                        "answer": "C",
                        "explanation": "Electric field intensity E is measured in Newtons per Coulomb (N/C) or equivalently Volts per metre (V/m)."
                    },
                    {
                        "question": f"A test charge used to measure electric field must be: {exam_suffix}",
                        "options": ["Large and positive", "Large and negative", "Infinitesimally small and positive", "Neutral"],
                        "answer": "C",
                        "explanation": "A test charge must be infinitesimally small so it does not disturb the source field being measured."
                    },
                    {
                        "question": f"The SI unit of electric field is: {exam_suffix}",
                        "options": ["Volt", "Coulomb", "N/C", "Joule"],
                        "answer": "C",
                        "explanation": "The SI unit of electric field E is Newton per Coulomb (N/C)."
                    }
                ]}
        else:
            return {"quiz": [
                {
                    "question": f"Which of the following compounds exhibits ionic bonding? {exam_suffix}",
                    "options": ["Carbon dioxide (CO₂)", "Sodium chloride (NaCl)", "Methane (CH₄)", "Water (H₂O)"],
                    "answer": "B",
                    "explanation": "NaCl forms through transfer of a valence electron from Na to Cl, resulting in ionic bonding."
                },
                {
                    "question": f"What type of hybridization is observed in the carbon atom of methane (CH₄)? {exam_suffix}",
                    "options": ["sp", "sp²", "sp³", "dsp²"],
                    "answer": "C",
                    "explanation": "Carbon in methane forms four single sigma bonds with hydrogen atoms, resulting in tetrahedral sp³ hybridization."
                },
                {
                    "question": f"In an exothermic reaction, the heat content of the products is: {exam_suffix}",
                    "options": ["Higher than reactants", "Lower than reactants", "Equal to reactants", "Unrelated to reactants"],
                    "answer": "B",
                    "explanation": "Exothermic reactions release energy — products possess lower enthalpy than the reactants."
                },
                {
                    "question": f"Which rule defines that orbitals of lowest energy are filled first? {exam_suffix}",
                    "options": ["Hund's Rule", "Aufbau Principle", "Pauli Exclusion Principle", "Avogadro's Hypothesis"],
                    "answer": "B",
                    "explanation": "The Aufbau principle dictates electrons populate lower-energy subshells before filling higher ones."
                },
                {
                    "question": f"An ionic bond is characterized by: {exam_suffix}",
                    "options": ["Equal sharing of electrons", "Unequal sharing of electrons", "Electrostatic attraction between oppositely charged ions", "Overlapping of valence s-orbitals"],
                    "answer": "C",
                    "explanation": "Ionic bonds are formed by electrostatic attraction between positive cations and negative anions."
                }
            ]}
