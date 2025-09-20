import chromadb
from chromadb.utils import embedding_functions
from sqlalchemy import create_engine, text
import os
import sys

# Add the project root to the path to allow imports from `app`
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.core.config import DATABASE_URL

# --- Configuration ---
CHROMA_DATA_PATH = "chroma_db"
COLLECTION_NAME = "job_descriptions"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

def main():
    print("--- Starting Vector DB Population Script ---")

    # 1. Initialize ChromaDB Client (Persistent)
    client = chromadb.PersistentClient(path=CHROMA_DATA_PATH)
    print(f"ChromaDB client initialized. Data will be stored in: ./{CHROMA_DATA_PATH}")

    # 2. Setup Embedding Function
    # This will download the model automatically on the first run
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBEDDING_MODEL_NAME
    )
    print(f"Embedding model '{EMBEDDING_MODEL_NAME}' loaded.")

    # 3. Create or Get Chroma Collection
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=sentence_transformer_ef,
        metadata={"hnsw:space": "cosine"} # Using cosine distance for similarity
    )
    print(f"Collection '{COLLECTION_NAME}' accessed.")

    # 4. Connect to PostgreSQL and Fetch Data
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as connection:
            query = text("SELECT job_id, job_title, job_description FROM jobplacement_RAG.job_listings WHERE job_description IS NOT NULL")
            result = connection.execute(query).fetchall()
            if not result:
                print("No job listings found in the database. Exiting.")
                return
            print(f"Fetched {len(result)} job listings from PostgreSQL.")
    except Exception as e:
        print(f"Error connecting to PostgreSQL: {e}")
        return

    # 5. Prepare data for ChromaDB
    documents = []
    metadatas = []
    ids = []

    for row in result:
        job_id, job_title, job_description = row
        # Combine title and description for richer context
        content = f"Job Title: {job_title}\nDescription: {job_description}"
        documents.append(content)
        metadatas.append({"job_id": job_id, "job_title": job_title})
        ids.append(str(job_id)) # Chroma requires string IDs

    # 6. Add data to ChromaDB Collection
    # `add` will update existing documents if the ID already exists.
    if documents:
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        print(f"Successfully added/updated {len(documents)} documents in ChromaDB.")
    else:
        print("No new documents to add.")

    print("--- Vector DB Population Complete ---")

if __name__ == "__main__":
    main()