import streamlit as st
import bcrypt
from rag.retriever import retriever
from rag.llm import llm_model,PROMPT
from rag.cleaner import format_retrieved_docs
from rag.memory import format_chat_history
from userData.database import (
    register_user,
    login_user,
    save_message,
    load_chat,
    get_recent_context
)
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
from langchain_huggingface import HuggingFaceEmbeddings

embedding_model = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)
if not st.session_state.logged_in:

    st.title("🌿 AyurCare")

    username = st.text_input(
        "Username"
    )

    password = st.text_input(
        "Password",
        type="password"
    )

    col1,col2 = st.columns(2)
    with col1:

        if st.button("Login"):

            user_id = login_user(
                username,
                password
            )

            if user_id:

                st.session_state.logged_in = True

                st.session_state.user_id = user_id

                st.session_state.messages = load_chat(
                    user_id
                )

                st.rerun()

            else:

                st.error(
                    "Invalid credentials"
                )

    with col2:

        if st.button("Register"):

            success = register_user(
                username,
                password
            )

            if success:

                st.success(
                    "Registration successful"
                )

            else:

                st.error(
                    "Username already exists"
                )

    st.stop()
with st.sidebar:

    st.header("Chat")

    if st.button("Clear Chat"):

        st.session_state.messages = []

        st.rerun()
if "messages" not in st.session_state:
    st.session_state.messages = load_chat(
        st.session_state.user_id
    )
st.title("🌿 Ayurvedic AI Assistant")

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

query = st.chat_input(
    "Ask your question..."
)

if query:

    st.chat_message("user").markdown(query)

    st.session_state.messages.append({
        "role":"user",
        "content":query
    })
    save_message(
        st.session_state.user_id,
        "user",
        query
    )

    query_embedding = embedding_model.embed_query(query)

    retrieved_docs = retriever(query_embedding)

    cleaned_docs = format_retrieved_docs(
        retrieved_docs
    )

    recent_messages = get_recent_context(
        st.session_state.messages
    )

    history = format_chat_history(
        recent_messages
    )

    final_prompt = PROMPT.invoke({
        "chat_history": history,
        "context": cleaned_docs,
        "query": query
    })

    response = llm_model.invoke(
        final_prompt
    ).content
    save_message(
        st.session_state.user_id,
        "assistant",
        response
    )
    st.chat_message(
        "assistant"
    ).markdown(response)

    st.session_state.messages.append({
        "role":"assistant",
        "content":response
    })

with st.sidebar:
    if "username" in st.session_state:
        st.write(f"👋 Welcome, {st.session_state.username}")

    st.divider()

    if st.button("Logout"):

        st.session_state.clear()

        st.rerun()