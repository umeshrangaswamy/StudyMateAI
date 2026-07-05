from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class SourceModel(BaseModel):
    """
    Metadata representation of a curriculum grounding source.
    """
    title: str = Field(..., description="Name of the textbook or resource document")
    chapter: Optional[str] = Field(None, description="Chapter/lesson name within the document")
    page_number: Optional[int] = Field(None, description="Page number of the reference source")

class MetadataModel(BaseModel):
    """
    Orchestration and classification metadata for the response.
    """
    subject: str = Field(..., description="Detected academic subject")
    intent: str = Field(..., description="Detected query intent")
    exam: Optional[str] = Field(None, description="Detected entrance exam (neet/kcet)")
    confidence: float = Field(0.86, description="Routing/classification confidence value")

class TeacherReviewModel(BaseModel):
    """
    Quality verification results from the Evaluator Agent (Teacher Review).
    """
    accuracy_score: float = Field(..., description="Factual correctness verification score (0 to 1)")
    curriculum_alignment_score: float = Field(..., description="Curriculum alignment verification score (0 to 1)")
    exam_alignment_score: float = Field(..., description="Entrance exam alignment verification score (0 to 1)")
    response_quality_score: float = Field(..., description="Response quality and readability score (0 to 1)")
    approved: bool = Field(..., description="Review approval status")
    feedback: str = Field(..., description="Teacher quality review explanation")

class AskResponse(BaseModel):
    """
    Response model matching the StudyMateAI backend specifications.
    This schema defines the strict JSON layout returned to external API consumers.
    """
    answer: str = Field(..., description="The pedagogical answer, feedback, or concepts explanation")
    response_type: str = Field(..., description="Classification category (e.g. explanation, summary, quiz, evaluation)")
    sources: List[SourceModel] = Field(default=[], description="List of curriculum grounding sources")
    metadata: MetadataModel = Field(..., description="Request routing and agent decision metadata")
    teacher_review: Optional[TeacherReviewModel] = Field(None, description="Quality review assessment from Evaluator Agent")

class MCQQuestionModel(BaseModel):
    """
    Schema for a single multiple choice question.
    """
    id: int = Field(..., description="Unique identifier for the question")
    question: str = Field(..., description="The multiple choice question prompt")
    options: Dict[str, str] = Field(..., description="Four options mapped as A, B, C, D keys")
    correct_option: str = Field(..., description="The correct option key (e.g. A, B, C, or D)")
    explanation: str = Field(..., description="Detailed pedagogical explanation for the correct answer")

class EvaluationModel(BaseModel):
    """
    Detailed evaluation scoring and pedagogical feedback for student submissions.
    """
    score: int = Field(..., description="Obtained score / count of correct answers")
    max_score: int = Field(..., description="Maximum possible score")
    feedback: str = Field(..., description="Overall descriptive feedback for the attempt")
    missing_points: List[str] = Field(default=[], description="Important conceptual points or units omitted")
    revision_tip: str = Field(..., description="Recommended reading or focus areas to improve")

class OrchestratorResult(BaseModel):
    """
    Internal container holding full processing output, including intermediate 
    structures like MCQ lists or evaluations.
    """
    answer: str
    response_type: str
    sources: List[SourceModel]
    metadata: MetadataModel
    quiz_questions: Optional[List[MCQQuestionModel]] = None
    evaluation: Optional[EvaluationModel] = None
    teacher_review: Optional[TeacherReviewModel] = None
