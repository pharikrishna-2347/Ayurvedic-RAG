from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from embedding_generator import text_chunks,docs
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
"""
vector_store = Chroma(
    embedding_function=embedding_model,
    persist_directory='./chromaDB',
    collection_name='ayurvedic'
)
vector_store.add_documents(
    documents=docs
)

"""