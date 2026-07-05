from pydantic import BaseModel, Field, field_validator, AliasChoices
from typing import Optional, Dict, List, Any

class AskRequest(BaseModel):
    """
    Request model for StudyMateAI backend queries.
    Enforces validation constraints including empty string prevention,
    free-tier subject filtering, and maximum query lengths.
    Supports optional quiz evaluation parameters.
    """
    year: str = Field(
        ..., 
        description="Year of study / Grade level (e.g. 2nd PUC, class 11)",
        example="2nd PUC"
    )
    board: str = Field(
        ..., 
        description="Educational Board / University (e.g. Karnataka State Board, CBSE)",
        example="Karnataka State Board"
    )
    subject: str = Field(
        ..., 
        description="Academic subject (physics or chemistry only for Free Tier)",
        example="Physics"
    )
    query: str = Field(
        ..., 
        description="The student question, prompt topic, or exam focus",
        example="Explain Ray Optics for NEET"
    )
    
    # Optional parameters for self-assessment checks and backward compatibility
    student_answers: Optional[Dict[str, str]] = Field(
        None,
        description="Key-value pairs of question IDs and answers for evaluation",
        example={"1": "A", "2": "C"}
    )
    quiz_questions: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Optional list of quiz questions being evaluated",
    )

    @field_validator("year", "board", "query", mode="before")
    @classmethod
    def validate_non_empty(cls, value: Any, info) -> str:
        """Ensures text inputs are not empty or solely whitespace."""
        if not isinstance(value, str):
            raise ValueError(f"Field '{info.field_name}' must be a string value.")
        cleaned = value.strip()
        if not cleaned:
            raise ValueError(f"Field '{info.field_name}' must not be empty.")
        return cleaned

    @field_validator("subject")
    @classmethod
    def validate_free_tier_subject(cls, value: str) -> str:
        """Enforces that only Physics and Chemistry subjects are permitted in the Free Tier."""
        cleaned_subj = value.strip().lower()
        if cleaned_subj not in ["physics", "chemistry"]:
            raise ValueError(
                f"Subject '{value}' is not supported in the Free Tier. "
                "Only 'Physics' and 'Chemistry' are currently implemented."
            )
        return value.strip()

    @field_validator("query")
    @classmethod
    def validate_query_constraints(cls, value: str) -> str:
        """Controls maximum token output cost rules by restricting input query lengths."""
        max_query_length = 1000
        if len(value) > max_query_length:
            raise ValueError(
                f"Query exceeds the maximum allowable length of {max_query_length} characters."
            )
        return value

    class Config:
        json_schema_extra = {
            "example": {
                "year": "2nd PUC",
                "board": "Karnataka State Board",
                "subject": "Physics",
                "query": "Explain Ray Optics for NEET"
            }
        }
