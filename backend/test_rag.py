from rag import *

# -----------------------------------
# READ PDF
# -----------------------------------

text = read_pdf("Aadharsh Experian Resume.pdf")

print("\nPDF READ SUCCESSFULLY\n")

# -----------------------------------
# CREATE CHUNKS
# -----------------------------------

chunks = chunk_text(text)

print(f"TOTAL CHUNKS: {len(chunks)}")

# -----------------------------------
# CREATE VECTOR STORE
# -----------------------------------

index = create_vector_store(chunks)

print("\nVECTOR STORE CREATED\n")

# -----------------------------------
# USER QUESTION
# -----------------------------------

query = "What technical skills does he have?"

# -----------------------------------
# SEARCH RELEVANT CHUNKS
# -----------------------------------

results = search_chunks(
    query,
    chunks,
    index
)

print("\nRELEVANT CHUNKS FOUND\n")

# -----------------------------------
# GENERATE FINAL ANSWER
# -----------------------------------

answer = generate_answer(
    query,
    results
)

print("\nFINAL ANSWER:\n")

print(answer)