import logging
from typing import List, Dict, Any, Optional
from app.services.embedding_service import EmbeddingService
from app.services.vector_store import VectorStore

logger = logging.getLogger(__name__)

class RAGAgent:
    """
    RAG Agent responsible for orchestration of context retrieval:
    1. Generates dense query embeddings.
    2. Dynamically detects context chapters.
    3. Searches the pgvector database.
    4. Formats and compresses context for downstream SME consumption.
    """
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()
        logger.info("RAGAgent initialized with downstream services.")

    async def retrieve(
        self, 
        query: str, 
        subject: str, 
        board: str, 
        year: str, 
        exam: Optional[str] = None, 
        top_k: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Retrieves curriculum chunks from the vector database, formats the grounding context, 
        and extracts structured source references.
        """
        logger.info(
            f"RAGAgent: Retrieving context for query on subject={subject}, board={board}"
        )

        from app.core.config import settings
        limit_k = top_k if top_k is not None else settings.MAX_RAG_CHUNKS
        limit_k = min(limit_k, settings.MAX_RAG_CHUNKS)

        # 1. Generate text embedding
        query_embedding = await self.embedding_service.embed_text(query)

        # 2. Dynamically check/detect chapter based on keywords
        chapter = self._detect_chapter(query, subject)

        # 3. Retrieve chunks with metadata filters
        chunks = await self.vector_store.search_chunks(
            embedding=query_embedding,
            subject=subject.lower().strip(),
            board=board,
            year=year,
            exam=exam,
            chapter=chapter,
            limit=limit_k
        )

        # 4. Formulate compressed context text and sources
        if not chunks:
            logger.info("RAGAgent: No grounding chunks retrieved from database.")
            return {
                "chunks": [],
                "context_str": "",
                "sources": [],
                "status": "empty"
            }

        # Format context string as a single, compressed text block for the SME prompt
        context_lines = []
        sources = []
        for c in chunks:
            title = c.get("title", "Curriculum Document")
            chap = c.get("chapter", "N/A")
            page = c.get("page_number", "N/A")
            content = c.get("content", "")
            
            context_lines.append(
                f"Source: {title} (Chapter: {chap}, Page: {page})\n"
                f"Content: {content}\n"
            )
            
            # Extract unique source mappings
            sources.append({
                "title": title,
                "chapter": chap,
                "page_number": page
            })

        context_str = "\n".join(context_lines)
        logger.info(f"RAGAgent: Successfully formatted {len(chunks)} chunks.")

        return {
            "chunks": chunks,
            "context_str": context_str,
            "sources": sources,
            "status": "success"
        }

    def _detect_chapter(self, query: str, subject: str) -> Optional[str]:
        """
        Identifies textbook chapter volume boundaries ("Part-1" or "Part-2") based on query keywords.
        This matches the actual chapter metadata values in the database.
        """
        query_lower = query.lower()
        subj_lower = subject.lower().strip()

        if subj_lower == "physics":
            # Part-1 chapters: Electric Charges, Potential, Current, Moving Charges, Magnetism, Induction, AC
            if any(w in query_lower for w in ["charge", "coulomb", "field", "potential", "capacit", "current", "electric", "ohm", "resistance", "volt"]):
                return "Part-1"
            # Part-2 chapters: Optics, Wave, Dual Nature, Atoms, Nuclei, Semiconductors
            elif any(w in query_lower for w in ["optic", "lens", "mirror", "refraction", "light", "wave", "atom", "nucle", "semiconductor"]):
                return "Part-2"
        elif subj_lower == "chemistry":
            # Part-1 chapters: Solutions, Electrochemistry, Kinetics, d/f Block, Coordination
            if any(w in query_lower for w in ["solut", "electro", "kinetic", "coordinat", "bonding", "hybrid"]):
                return "Part-1"
            # Part-2 chapters: Haloalkanes, Alcohols, Aldehydes, Amines, Biomolecules
            elif any(w in query_lower for w in ["alcohol", "ether", "aldehyde", "ketone", "amine", "biomolecule"]):
                return "Part-2"
        
        return None
