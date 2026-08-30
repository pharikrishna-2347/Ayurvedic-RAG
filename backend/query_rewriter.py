from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from rag.llm import llm_model

QUERY_REWRITE_PROMPT = PromptTemplate(
    template="""
You are a query rewriting assistant for an Ayurvedic RAG system.

Your task is to rewrite the user's latest question into a
self-contained search query that can be understood without
the previous conversation.

Use the conversation history to resolve references such as:

- it
- this
- that
- this remedy
- the above
- what about it
- explain it
- dosage?
- how should I take it?

Rules:

1. If the user's question is already self-contained,
   return it unchanged.
2. If it refers to something from the conversation(most recent),
   replace the reference with the actual subject.
3. Do NOT answer the question.
4. Do NOT add information that is not present in the conversation.
5. Return ONLY the rewritten search query.
6. Keep the query concise.
7. Return the query as a single string.

Conversation History:
{chat_history}

Latest User Question:
{query}

Rewritten Search Query:
""",
    input_variables=[
        "chat_history",
        "query"
    ]
)

# Create an explicit chain using LCEL
rewrite_chain = QUERY_REWRITE_PROMPT | llm_model | StrOutputParser()


def rewrite_query(query, chat_history):
    # StrOutputParser automatically extracts and cleans the string response
    rewritten_query = rewrite_chain.invoke({
        "chat_history": chat_history,
        "query": query
    })

    return rewritten_query.strip()