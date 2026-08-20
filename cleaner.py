def format_retrieved_docs(retrieved_docs):
    """
    Extracts page content from LangChain documents and formats them
    into a clean, numbered string for an LLM prompt.
    """
    cleaned_chunks = []

    for i, doc in enumerate(retrieved_docs, 1):
        # Extract the raw page content string
        content = doc.page_content

        # Format it cleanly with a header
        formatted_chunk = f"--- Ayurvedic Source #{i} ---\n{content.strip()}"
        cleaned_chunks.append(formatted_chunk)

    # Join all chunks with double newlines
    return "\n\n".join(cleaned_chunks)
