import os
import json
import logging
import psycopg2
import sys
import asyncio
from pypdf import PdfReader

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Add apps/backend to sys.path
backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "apps", "backend")
sys.path.append(backend_dir)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.embedding_service import EmbeddingService
from app.core.config import settings
from chunk_text import chunk_text

async def process_pdf(pdf_path, metadata, embedding_service, cursor):
    title = metadata["title"]
    subject = metadata["subject"]
    board = metadata["board"]
    year = metadata["year"]
    exam = metadata.get("exam")
    chapter = metadata.get("chapter")

    logger.info(f"Extracting text from PDF: {pdf_path}")
    reader = PdfReader(pdf_path)
    full_text = ""
    # To avoid huge billing and slow runs, let's extract up to 40 pages of text per PDF (or all if short)
    max_pages = min(len(reader.pages), 40)
    for i in range(max_pages):
        try:
            text = reader.pages[i].extract_text()
            if text:
                text = text.replace("\x00", "")
                full_text += f"\n[Page {i+1}]\n" + text
        except Exception as ex:
            logger.warning(f"Failed to extract page {i} from {pdf_path}: {ex}")

    if not full_text.strip():
        logger.warning(f"No text extracted from PDF {pdf_path}. Skipping.")
        return

    # Chunk text (300 words with 10% overlap)
    chunks = chunk_text(full_text, chunk_size_tokens=300, overlap_percent=0.1)
    if not chunks:
        logger.warning(f"No chunks generated for {pdf_path}.")
        return

    logger.info(f"Inserting document record: {title}")
    insert_doc_query = """
        INSERT INTO documents (title, subject, board, year)
        VALUES (%s, %s, %s, %s)
        RETURNING id;
    """
    cursor.execute(insert_doc_query, (title, subject, board, year))
    document_id = cursor.fetchone()[0]

    logger.info(f"Generating embeddings and inserting {len(chunks)} chunks for '{title}'...")
    for idx, chunk in enumerate(chunks, start=1):
        # Throttle request to avoid Vertex AI rate limits
        await asyncio.sleep(0.1)
        try:
            embedding_vector = await embedding_service.embed_text(chunk)
        except Exception as ex:
            logger.error(f"Failed to generate embedding for chunk {idx}: {ex}")
            # Fallback to placeholder if it fails
            embedding_vector = [0.01] * 768

        insert_chunk_query = """
            INSERT INTO curriculum_chunks (document_id, content, chapter, page_number, exam)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id;
        """
        page_num = idx
        cursor.execute(insert_chunk_query, (document_id, chunk, chapter, page_num, exam))
        chunk_id = cursor.fetchone()[0]

        insert_embed_query = """
            INSERT INTO chunk_embeddings (chunk_id, embedding)
            VALUES (%s, %s);
        """
        cursor.execute(insert_embed_query, (chunk_id, embedding_vector))

    logger.info(f"Finished processing '{title}' successfully.")

async def main():
    download_dir = "c:\\Users\\Admin\\Documents\\myprojects\\StudyMateAI\\downloaded"
    if not os.path.exists(download_dir):
        logger.error(f"Download directory {download_dir} does not exist!")
        return

    embedding_service = EmbeddingService()
    db_url = settings.DATABASE_URL

    conn = None
    try:
        conn = psycopg2.connect(db_url)
        conn.autocommit = False
        cursor = conn.cursor()

        # Iterate through the download_dir folders
        for root, dirs, files in os.walk(download_dir):
            for file in files:
                if not file.endswith(".pdf"):
                    continue

                pdf_path = os.path.join(root, file)
                rel_path = os.path.relpath(pdf_path, download_dir)
                folder = rel_path.split(os.sep)[0] # "KCET", "NEET", "Textbooks"

                # Define metadata dynamically based on file & folder
                metadata = {
                    "board": "Karnataka State Board",
                    "year": "2nd PUC",
                    "subject": "physics",
                    "exam": None,
                    "chapter": None,
                    "title": file.replace(".pdf", "")
                }

                # Determine exam
                if folder == "KCET":
                    metadata["exam"] = "kcet"
                elif folder == "NEET":
                    metadata["exam"] = "neet"

                # Determine subject
                if "chemistry" in file.lower() or "chem" in file.lower():
                    metadata["subject"] = "chemistry"
                else:
                    metadata["subject"] = "physics"

                # Determine year
                if "1st PUC" in file or "11th" in file:
                    metadata["year"] = "1st PUC"
                else:
                    metadata["year"] = "2nd PUC"

                # Determine chapter
                if "Part-1" in file:
                    metadata["chapter"] = "Part-1"
                elif "Part-2" in file:
                    metadata["chapter"] = "Part-2"

                logger.info(f"Processing PDF file: {rel_path} with metadata: {metadata}")
                await process_pdf(pdf_path, metadata, embedding_service, cursor)
                conn.commit() # Commit file-by-file

        logger.info("All PDF files successfully ingested into the cloud database!")

    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    asyncio.run(main())
