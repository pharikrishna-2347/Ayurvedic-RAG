from fastapi import FastAPI
from pydantic import BaseModel

from langchain_huggingface import HuggingFaceEmbeddings

from rag.retriever import retriever
from rag.cleaner import format_retrieved_docs
from rag.llm import llm_model,PROMPT

from backend.database import Base, engine
from backend.models import User, Message

Base.metadata.create_all(bind=engine)

from sqlalchemy.orm import Session
from fastapi import Depends

from backend.database import get_db
from backend.crud import create_google_user, get_user_by_google_id,save_message,get_chat,get_recent_messages

import os

from dotenv import load_dotenv

from starlette.middleware.sessions import SessionMiddleware

load_dotenv()

from fastapi import Request

from backend.oauth import oauth
from backend.query_rewriter import rewrite_query

app = FastAPI(
    title = "Ayuredic RAG API",
    description = "Backend API for Ayurvedic RAG Assistant",
    version = "1.0.0"
)

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET")
)

@app.get("/")
def basic():
    return {
        "message : Basic API Created successfully!"
    }

#Embedding model
embedding_model = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)

#Helper function 
def format_database_history(messages):

    history = ""

    for message in messages:

        if message.role == "user":
            role = "User"

        else:
            role = "Assistant"

        history += f"{role}: {message.content}\n"

    return history  

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
def chat(request: ChatRequest,
    http_request: Request,
    db: Session = Depends(get_db)
    ):
    
    #1. Checking authentication
    user_id = http_request.session.get(
        "user_id"
    )

    if user_id is None:
        return {
            "error" : "Not authenticated"
        }

    #2. Get user query    
    query = request.message

    #3. Get Last 10 messages
    recent_messages = get_recent_messages(
        db=db,
        user_id=user_id,
        limit=20
    )
    #print("RECENT MSGS",recent_messages)

    history = format_database_history(recent_messages)
    print("HISTORY IS ", history)

    search_query = rewrite_query(
    query=query,
    chat_history=history
    )
    print("MODIFIED QUERY IS : ", search_query)
    #4. Save user message
    save_message(
        db = db,
        user_id=user_id,
        role="user",
        content=query
    )

    

    #6. RAG retrieval
    query_embedding = embedding_model.embed_query(search_query)
    retrieved_docs = retriever(query_embedding)
    cleaned_retrieved_docs = format_retrieved_docs(retrieved_docs)



    #7. Prompt
    final_prompt = PROMPT.invoke({
        "chat_history" : history,
        "context" : cleaned_retrieved_docs,
        "query" : query
    })

    #8. Generate Response
    response = llm_model.invoke(final_prompt).content

    #9. Save AI response
    save_message(
        db = db,
        user_id=user_id,
        role="assistant",
        content=response
    )

    #10. Return response
    return {
        "answer" : response
    }


@app.get("/chat/history")
def chat_history(
    http_request: Request,
    db: Session = Depends(get_db)
    ):
    user_id = http_request.session.get(
        "user_id"
    )

    if user_id is None:
        return {
            "error" : "Noy authenticated"
        }
    messages = get_chat(
        db = db,
        user_id = user_id
    )    
    return {
        "messages" : [
            {
                "id" : message.id,
                "role" : message.role,
                "content" : message.content,
                "created_at" : message.created_at
            }
            for message in messages
        ]
    }




@app.post("/test-user")
def test_user(
    username: str,
    db: Session = Depends(get_db)
):

    existing_user = get_user_by_username(
        db,
        username
    )

    if existing_user:

        return {
            "message": "User already exists",
            "user_id": existing_user.id
        }

    user = create_user(
        db,
        username
    )

    return {
        "message": "User created",
        "user_id": user.id
    }


@app.post("/test-message")
def test_message(
    user_id: int,
    content: str,
    db: Session = Depends(get_db)
):

    message = save_message(
        db,
        user_id,
        "user",
        content
    )

    return {
        "message_id": message.id,
        "content": message.content
    }    


@app.get("/test-chat/{user_id}")
def test_chat(
    user_id: int,
    db: Session = Depends(get_db)
):

    messages = get_chat(
        db,
        user_id
    )

    return [
        {
            "role": message.role,
            "content": message.content
        }
        for message in messages
    ]    


@app.get("/auth/google")
async def google_login(request: Request):

    google = oauth.create_client("google")

    redirect_uri = request.url_for(
        "google_callback"
    )

    return await google.authorize_redirect(
        request,
        redirect_uri
    )

@app.get(
    "/auth/google/callback",
    name="google_callback"
)
async def google_callback(
    request: Request,
    db: Session = Depends(get_db)
):

    google = oauth.create_client("google")

    token = await google.authorize_access_token(
        request
    )

    userinfo = token["userinfo"]

    google_id = userinfo["sub"]
    email = userinfo.get("email")
    name = userinfo.get("name")
    picture = userinfo.get("picture")

    # Check whether user already exists
    user = get_user_by_google_id(
        db,
        google_id
    )

    # If first login, create the user
    if user is None:

        user = create_google_user(
            db=db,
            google_id=google_id,
            email=email,
            name=name,
            profile_picture=picture
        )

    # Store user ID in session
    request.session["user_id"] = user.id

    return {
        "message": "Login successful",
        "user_id": user.id,
        "email": user.email,
        "name": user.name
    }


@app.get("/auth/me")
def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
):

    user_id = request.session.get(
        "user_id"
    )

    if user_id is None:

        return {
            "authenticated": False
        }

    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if user is None:

        request.session.clear()

        return {
            "authenticated": False
        }

    return {
        "authenticated": True,
        "user_id": user.id,
        "email": user.email,
        "name": user.name,
        "profile_picture": user.profile_picture
    }

@app.post("/auth/logout")
def logout(request: Request):

    request.session.clear()

    return {
        "message": "Logged out successfully"
    }        

  