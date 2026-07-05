import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

class VectorStore:
    """
    Service wrapper for interacting with Cloud SQL PostgreSQL + pgvector database.
    Performs metadata-filtered vector searches using text-embedding-004 vectors.
    """
    def __init__(self):
        self.db_url = settings.DATABASE_URL
        # Parse database host identifier for safe logging
        host_info = "localhost"
        if "@" in self.db_url:
            host_info = self.db_url.split("@")[-1].split("/")[0]
        logger.info(f"VectorStore initialized with target database host: {host_info}")

    async def search_chunks(
        self, 
        embedding: List[float], 
        subject: str, 
        board: str, 
        year: str, 
        exam: Optional[str] = None, 
        chapter: Optional[str] = None,
        limit: int = 3  # Matches top_k requirements
    ) -> List[Dict[str, Any]]:
        """
        Executes a metadata-filtered vector similarity search against pgvector database.
        Enforces filtering before distance computation. Falls back to mock data if DB is offline.
        """
        # Validate critical filtering constraints to prevent global database scans
        if not subject or not subject.strip():
            raise ValueError("Subject filter is required to prevent unindexed global table scans.")
        if not board or not board.strip():
            raise ValueError("Board filter is required to prevent unindexed global table scans.")
        if not year or not year.strip():
            raise ValueError("Year filter is required to prevent unindexed global table scans.")

        logger.info(
            f"Searching vector database. Filters applied: subject={subject}, "
            f"board={board}, year={year}, exam={exam or 'none'}, chapter={chapter or 'none'}, limit={limit}"
        )

        conn = None
        try:
            # Connect to PostgreSQL with a 3-second connection timeout to fail fast
            conn = psycopg2.connect(self.db_url, connect_timeout=3)
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            # Build query dynamically to apply metadata filters first
            query = """
                SELECT 
                    c.content, 
                    d.title, 
                    c.chapter, 
                    c.page_number,
                    c.chapter as topic,
                    (e.embedding <=> %s::vector) AS distance
                FROM chunk_embeddings e
                JOIN curriculum_chunks c ON e.chunk_id = c.id
                JOIN documents d ON c.document_id = d.id
                WHERE d.subject = %s AND d.board = %s AND d.year = %s
            """
            
            params = [embedding, subject, board, year]

            if exam:
                query += " AND (c.exam = %s OR c.exam IS NULL)"
                params.append(exam)
                
            if chapter:
                query += " AND c.chapter = %s"
                params.append(chapter)

            # Cosine similarity sorting and limit bounds
            query += """
                ORDER BY distance ASC
                LIMIT %s
            """
            params.append(limit)

            cursor.execute(query, params)
            results = cursor.fetchall()
            
            # Format outputs
            formatted_results = []
            for row in results:
                formatted_results.append({
                    "content": row["content"],
                    "title": row["title"],
                    "chapter": row["chapter"],
                    "topic": row["topic"] or row["chapter"],
                    "page_number": row["page_number"],
                    "distance": float(row["distance"])
                })

            cursor.close()
            logger.info(f"Vector search returned {len(formatted_results)} chunks from database.")
            return formatted_results

        except psycopg2.OperationalError as e:
            # Fall back gracefully to mock chunks for development environments if DB is unavailable
            logger.warning(
                f"VectorStore database connection refused or offline. "
                f"Falling back to curriculum mock grounding data. Detail: {str(e)}"
            )
            return self._get_mock_fallback_chunks(subject, board, year, exam, chapter, limit)
            
        except Exception as e:
            logger.error(f"VectorStore query execution failed: {str(e)}")
            raise e
            
        finally:
            if conn:
                conn.close()

    def _get_mock_fallback_chunks(
        self, 
        subject: str, 
        board: str, 
        year: str, 
        exam: Optional[str], 
        chapter: Optional[str], 
        limit: int
    ) -> List[Dict[str, Any]]:
        """
        Returns mock chunks for local sandboxed testing that conform to exact data structures.
        """
        mock_chunks = [
            {
                "content": f"Curriculum ground truth explaining properties of '{subject.capitalize()}' aligned to {board} ({year}).",
                "title": f"NCERT Class 12 {subject.capitalize()} Textbook",
                "chapter": chapter or ("Ray Optics" if subject.lower() == "physics" else "Chemical Bonding"),
                "topic": chapter or ("Ray Optics" if subject.lower() == "physics" else "Chemical Bonding"),
                "page_number": 104,
                "distance": 0.12
            },
            {
                "content": f"Revision guidelines and previous {exam.upper() if exam else 'KCET/NEET'} study pattern overview for {subject}.",
                "title": f"NEET and KCET Academic Study Pack for {subject.capitalize()}",
                "chapter": chapter or ("Thermodynamics" if subject.lower() == "physics" else "Atomic Structure"),
                "topic": chapter or ("Thermodynamics" if subject.lower() == "physics" else "Atomic Structure"),
                "page_number": 12,
                "distance": 0.25
            }
        ]
        return mock_chunks[:limit]
