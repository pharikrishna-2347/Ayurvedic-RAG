#print("Enter your query here !")
from langchain_huggingface import HuggingFaceEmbeddings
from retriever import *
from llm import *
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
#from vector_store import vector_store
from cleaner import format_retrieved_docs
from memory import format_chat_history

chat_memory = []

while True:

    query = input("Enter your query here ! ")

    if query.lower() == "exit":
        break

    query_embedding = embedding_model.embed_query(query)

    retrieved_docs = retriever(query_embedding)

    cleaned_retrieved_docs = format_retrieved_docs(retrieved_docs)

    history = format_chat_history(chat_memory)

    final_prompt = PROMPT.invoke({
        "chat_history": history,
        "context": cleaned_retrieved_docs,
        "query": query
    })

    response = llm_model.invoke(final_prompt).content

    print(response)

    chat_memory.append({
        "role": "user",
        "content": query
    })

    chat_memory.append({
        "role": "assistant",
        "content": response
    })