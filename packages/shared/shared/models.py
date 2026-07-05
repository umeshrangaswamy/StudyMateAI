from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from uuid import UUID

# --- Pydantic Schemas for Database Sync and Validation ---

class DocumentBase(BaseModel):
    id: Optional[UUID] = None
    title: str = Field(..., description="Name of the curriculum textbook or note file")
    subject: str = Field(..., description="physics/chemistry")
    board: str = Field(..., description="karnataka_state_board/cbse")
    year: str = Field(..., description="1st_puc/2nd_puc")
    chapter: Optional[str] = None
    document_type: Optional[str] = None
    source: Optional[str] = None
    gcs_path: Optional[str] = None
    created_at: Optional[datetime] = None

class CurriculumChunkBase(BaseModel):
    id: Optional[UUID] = None
    document_id: UUID
    subject: str
    board: str
    year: str
    chapter: Optional[str] = None
    topic: Optional[str] = None
    exam: Optional[str] = None  # neet/kcet
    content: str
    page_number: Optional[int] = None
    created_at: Optional[datetime] = None

class ChunkEmbeddingBase(BaseModel):
    id: Optional[UUID] = None
    chunk_id: UUID
    embedding: List[float] = Field(..., description="Vector embedding list (768 dimensions for text-embedding-004)")
    created_at: Optional[datetime] = None

class StudentAssessmentBase(BaseModel):
    id: Optional[UUID] = None
    student_id: Optional[str] = None
    subject: str
    exam: Optional[str] = None
    score: float
    feedback: str
    created_at: Optional[datetime] = None
