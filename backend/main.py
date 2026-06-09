from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime

from rag import (
    read_pdf,
    chunk_text,
    create_vector_store,
    search_chunks,
    generate_answer
)

import os

# -----------------------------------
# LOAD ENV VARIABLES
# -----------------------------------

load_dotenv()

# -----------------------------------
# FASTAPI APP
# -----------------------------------

app = FastAPI()

# -----------------------------------
# ENABLE CORS
# -----------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------
# CREATE UPLOAD FOLDER
# -----------------------------------

UPLOAD_FOLDER = "uploaded_pdfs"

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

# -----------------------------------
# GROQ CLIENT
# -----------------------------------

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# -----------------------------------
# MONGODB CONNECTION
# -----------------------------------

mongo_client = MongoClient(
    os.getenv("MONGO_URI")
)

print(
    mongo_client.list_database_names()
)

# Database
db = mongo_client["chatbot_db"]

# Collection
chat_collection = db["messages"]

# -----------------------------------
# GLOBAL RAG STORAGE
# -----------------------------------

stored_chunks = []

stored_index = None

uploaded_pdf_name = None

# -----------------------------------
# REQUEST MODEL
# -----------------------------------

class ChatRequest(BaseModel):

    message: str

# -----------------------------------
# HOME ROUTE
# -----------------------------------

@app.get("/")
def home():

    return {
        "message": "RAG PDF Chatbot Backend Running"
    }

# -----------------------------------
# PDF UPLOAD ENDPOINT
# -----------------------------------

@app.post("/upload-pdf")
async def upload_pdf(
    file: UploadFile = File(...)
):

    global stored_chunks
    global stored_index
    global uploaded_pdf_name

    try:

        # -----------------------------------
        # VALIDATE FILE
        # -----------------------------------

        if not file.filename.endswith(".pdf"):

            return {
                "error": "Only PDF files allowed"
            }

        # -----------------------------------
        # SAVE PDF
        # -----------------------------------

        pdf_path = os.path.join(
            UPLOAD_FOLDER,
            file.filename
        )

        with open(pdf_path, "wb") as f:

            content = await file.read()

            f.write(content)

        print(
            f"\nPDF SAVED: {pdf_path}"
        )

        # -----------------------------------
        # PROCESS PDF
        # -----------------------------------

        text = read_pdf(pdf_path)

        stored_chunks = chunk_text(text)

        stored_index = create_vector_store(
            stored_chunks
        )

        uploaded_pdf_name = file.filename

        print(
            "\nRAG PIPELINE READY\n"
        )

        # -----------------------------------
        # RESPONSE
        # -----------------------------------

        return {

            "message":
                "PDF uploaded successfully",

            "pdf_name":
                uploaded_pdf_name,

            "total_chunks":
                len(stored_chunks)
        }

    except Exception as e:

        print(
            "\nUPLOAD ERROR:\n",
            str(e)
        )

        return {
            "error": str(e)
        }

# -----------------------------------
# CHAT ENDPOINT
# -----------------------------------

@app.post("/chat")
async def chat(request: ChatRequest):

    global stored_chunks
    global stored_index
    global uploaded_pdf_name

    try:

        # -----------------------------------
        # USER MESSAGE
        # -----------------------------------

        user_message = request.message

        print(
            f"\nUSER: {user_message}"
        )

        # -----------------------------------
        # RAG MODE
        # -----------------------------------

        if stored_index is not None:

            print(
                "\nUSING RAG MODE\n"
            )

            # Semantic retrieval
            results = search_chunks(

                user_message,

                stored_chunks,

                stored_index
            )

            # Generate grounded answer
            ai_reply = generate_answer(

                user_message,

                results
            )

        # -----------------------------------
        # NORMAL CHAT MODE
        # -----------------------------------

        else:

            print(
                "\nUSING NORMAL CHAT MODE\n"
            )

            response = client.chat.completions.create(

                model="llama-3.3-70b-versatile",

                messages=[

                    {
                        "role": "system",

                        "content":
                            "You are a helpful AI assistant."
                    },

                    {
                        "role": "user",

                        "content": user_message
                    }
                ]
            )

            ai_reply = (
                response
                .choices[0]
                .message
                .content
            )

        # -----------------------------------
        # SAVE CHAT TO MONGODB
        # -----------------------------------

        chat_collection.insert_one({

            "user_message":
                user_message,

            "ai_response":
                ai_reply,

            "pdf_used":
                uploaded_pdf_name,

            "created_at":
                datetime.utcnow()
        })

        print(
            "\nCHAT SAVED TO MONGODB\n"
        )

        # -----------------------------------
        # RETURN RESPONSE
        # -----------------------------------

        return {

            "response": ai_reply,

            "pdf_used":
                uploaded_pdf_name
        }

    except Exception as e:

        print(
            "\nCHAT ERROR:\n",
            str(e)
        )

        return {
            "error": str(e)
        }