from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
# 1. Initialize the same embedding model used to create the database
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# 2. Open a direct connection to your existing database files
vector_store = Chroma(
    persist_directory=str(BASE_DIR / "chromaDB"),
    embedding_function=embedding_model,
    collection_name='ayurvedic'
)

def retriever(query_embedding):
    return vector_store.similarity_search_by_vector(query_embedding,k=5)

