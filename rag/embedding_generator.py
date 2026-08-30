"""
from langchain_huggingface import HuggingFaceEmbeddings

embedding_model = HuggingFaceEmbeddings(model_name = 'BAAI/bge-m3')

chunks_embeddings = embedding_model.embed_documents(chunks)

print(len(chunks_embeddings))
"""

from sentence_transformers import SentenceTransformer

# 1. Load a compact, highly efficient model locally
# (This downloads once, then runs completely offline)
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# 2. Your list of 130 text chunks
from rag.text_splitter import docs
text_chunks = [chunk.page_content for chunk in docs]

# 3. Generate embeddings efficiently in batches
print(f"Processing {len(text_chunks)} chunks locally...")
embeddings = embedding_model.encode(
    text_chunks,
    batch_size=32,      # Processes 32 chunks at a time to optimize memory
    show_progress_bar=True,
    convert_to_numpy=True
)

# 4. Verify the output shape
# Expected output for all-MiniLM-L6-v2: (130, 384)
print("Finished!")
#print("Embeddings matrix shape:", embeddings.shape)

