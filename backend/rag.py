from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from groq import Groq
from dotenv import load_dotenv
import faiss
import numpy as np
import os

load_dotenv()
# -----------------------------------
# LOAD EMBEDDING MODEL
# -----------------------------------

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

# -----------------------------------
# LOAD GROQ CLIENT
# -----------------------------------

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# -----------------------------------
# READ PDF
# -----------------------------------

def read_pdf(file_path):

    reader = PdfReader(file_path)

    text = ""

    for page in reader.pages:

        extracted = page.extract_text()

        if extracted:
            text += extracted

    return text

# -----------------------------------
# CHUNK TEXT
# -----------------------------------

def chunk_text(text, chunk_size=500):

    chunks = []

    for i in range(0, len(text), chunk_size):

        chunk = text[i:i + chunk_size]

        chunks.append(chunk)

    return chunks

# -----------------------------------
# CREATE VECTOR STORE
# -----------------------------------

def create_vector_store(chunks):

    embeddings = model.encode(chunks)

    embeddings = np.array(
        embeddings,
        dtype=np.float32
    )

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatL2(dimension)

    index.add(embeddings)

    return index

# -----------------------------------
# SEARCH CHUNKS
# -----------------------------------

def search_chunks(query, chunks, index):

    query_embedding = model.encode([query])

    query_embedding = np.array(
        query_embedding,
        dtype=np.float32
    )

    distances, indices = index.search(
        query_embedding,
        k=3
    )

    results = []

    for i in indices[0]:

        results.append(chunks[i])

    return results

# -----------------------------------
# GENERATE FINAL ANSWER
# -----------------------------------

def generate_answer(query, chunks):

    context = "\n\n".join(chunks)

    prompt = f"""
    You are a helpful AI assistant.

    Answer the question ONLY using
    the provided context.

    If the answer is not found in
    the context, say:

    "Answer not found in document."

    -------------------------
    CONTEXT:
    -------------------------

    {context}

    -------------------------
    QUESTION:
    -------------------------

    {query}
    """

    response = client.chat.completions.create(

        model="llama-3.3-70b-versatile",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.3
    )

    return response.choices[0].message.content

# -----------------------------------
# MAIN FUNCTION
# -----------------------------------

if __name__ == "__main__":

    # -----------------------------
    # LOAD PDF
    # -----------------------------

    pdf_path = "sample.pdf"

    print("\nREADING PDF...\n")

    text = read_pdf(pdf_path)

    print("PDF READ SUCCESSFULLY\n")

    # -----------------------------
    # CHUNK TEXT
    # -----------------------------

    chunks = chunk_text(text)

    print(f"TOTAL CHUNKS: {len(chunks)}\n")

    # -----------------------------
    # CREATE VECTOR STORE
    # -----------------------------

    print("CREATING VECTOR STORE...\n")

    index = create_vector_store(chunks)

    print("VECTOR STORE CREATED\n")

    # -----------------------------
    # CHAT LOOP
    # -----------------------------

    while True:

        query = input("\nAsk Question (or type exit): ")

        if query.lower() == "exit":
            break

        # -------------------------
        # SEARCH RELEVANT CHUNKS
        # -------------------------

        results = search_chunks(
            query,
            chunks,
            index
        )

        print("\nRELEVANT CHUNKS FOUND\n")

        # -------------------------
        # GENERATE ANSWER
        # -------------------------

        answer = generate_answer(
            query,
            results
        )

        print("\nANSWER:\n")

        print(answer)