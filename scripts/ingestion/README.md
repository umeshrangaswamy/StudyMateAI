# StudyMateAI Ingestion Pipeline

This ingestion pipeline parses curriculum documents, slices them into uniform chunks, generates vector embeddings using Google's `text-embedding-004` model, and loads them into a PostgreSQL database with `pgvector` HNSW indexes enabled.

## 📂 Core Ingestion Files

- **`extract_text.py`**: Utility to read raw txt file textbooks and notes.
- **`chunk_text.py`**: Splits text into chunks of approximately 300 words with a 10% (30-word) overlap offset to maintain structural context.
- **`embed_and_load.py`**: Main orchestrator script that validates metadata schemas, skips unsupported subjects (MVP limits), generates 768-dimensional float embedding coordinates, and runs transactional SQL inserts.
- **`metadata_schema.json`**: JSON schema defining validation properties for document descriptors.

## 📂 Directory Structure

Save raw textbook files in the following path before running ingestion:
```text
content/
  physics/
    ray-optics.txt
    ray-optics.metadata.json
  chemistry/
    chemical-bonding.txt
    chemical-bonding.metadata.json
```

## 🚀 Running Ingestion

To launch the ingestion pipeline:
```bash
python scripts/ingestion/embed_and_load.py
```
If the PostgreSQL database is not running locally, the pipeline logs simulated insertion metrics and continues successfully, allowing easy test runs and mock verification.
