import sys
import os
import logging
import psycopg2

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Add parent directory to sys.path to resolve backend app imports
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_dir)

from app.core.config import settings

def run_database_migrations():
    """
    Reads migration SQL files in numerical order and executes them inside a 
    PostgreSQL database transaction.
    """
    db_url = settings.DATABASE_URL
    logger.info(f"Database URL retrieved: {db_url.split('@')[-1] if '@' in db_url else 'localhost'}")

    migration_files = [
        "001_extensions.sql",
        "002_documents.sql",
        "003_chunks.sql",
        "004_embeddings.sql",
        "005_assessments.sql"
    ]

    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    conn = None
    try:
        logger.info("Connecting to PostgreSQL database...")
        conn = psycopg2.connect(db_url)
        conn.autocommit = False # Run migrations inside transaction blocks
        cursor = conn.cursor()

        for filename in migration_files:
            filepath = os.path.join(current_dir, filename)
            logger.info(f"Applying migration file: '{filename}'...")
            
            with open(filepath, "r", encoding="utf-8") as f:
                sql_script = f.read()
                
            cursor.execute(sql_script)
            logger.info(f"Successfully executed '{filename}'.")

        # Commit all tables and indexes successfully
        conn.commit()
        logger.info("All PostgreSQL + pgvector migrations applied successfully!")
        cursor.close()
        
    except psycopg2.OperationalError as e:
        logger.warning(
            f"Could not connect to PostgreSQL database (OperationalError). "
            f"This is expected during offline local testing if PostgreSQL is not active. "
            f"Detail: {str(e)}"
        )
        if conn:
            conn.rollback()
    except Exception as e:
        logger.error(f"Migration execution failed. Rolling back changes. Error: {str(e)}")
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    run_database_migrations()
