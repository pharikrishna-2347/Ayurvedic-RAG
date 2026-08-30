from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_text_splitters import RecursiveJsonSplitter
from langchain_core.documents import Document
import json
from torch.fx.passes import splitter_base

with open("ayurvedic_data_clean.json", "r") as f:
    data = json.load(f)
docs = []
for item in data:
    # Format a readable, structured string text for the embedding model to read
    # We include all keys to ensure the model understands the full context
    page_content = (
        f"Name: {item.get('name')}\n"
        f"Botanical Name: {item.get('botanical_name')}\n"
        f"Synonyms: {', '.join(item.get('synonyms', []))}\n"
        f"Condition: {item.get('condition')}\n"
        f"Remedy: {', '.join(item.get('remedy', []))}\n"
        f"Safety Precautions: {', '.join(item.get('safety_precautions', []))}\n"
        f"Keywords: {', '.join(item.get('search_keywords', []))}"
    )

    # Store critical tracking items (like ID) in metadata so you can filter later if needed
    metadata = {
        "id": item.get("id"),
        "condition": item.get("condition"),
        "name": item.get("name")
    }

    # Create the single document object
    doc = Document(page_content=page_content, metadata=metadata)
    docs.append(doc)

#print(f"Successfully processed {len(docs)} individual Ayurvedic documents.")

