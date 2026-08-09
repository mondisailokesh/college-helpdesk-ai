import os
import shutil
import chromadb

from sentence_transformers import SentenceTransformer

# --------------------------------------------
# Settings
# --------------------------------------------

DB_PATH = "college_db"
COLLECTION_NAME = "college_helpdesk"
KNOWLEDGE_FOLDER = "knowledge"

CHUNK_SIZE = 300          # characters
CHUNK_OVERLAP = 60        # characters

# --------------------------------------------
# Delete old database
# --------------------------------------------

if os.path.exists(DB_PATH):
    shutil.rmtree(DB_PATH)
    print("Old database deleted.")

# --------------------------------------------
# Create ChromaDB
# --------------------------------------------

client = chromadb.PersistentClient(path=DB_PATH)

collection = client.get_or_create_collection(
    name=COLLECTION_NAME
)

# --------------------------------------------
# Load embedding model
# --------------------------------------------

print("Loading embedding model...")

model = SentenceTransformer("all-MiniLM-L6-v2")

# --------------------------------------------
# Text Cleaner
# --------------------------------------------

def clean_text(text):

    text = text.replace("\r", "")
    text = text.replace("\t", " ")

    while "\n\n\n" in text:
        text = text.replace("\n\n\n", "\n\n")

    while "  " in text:
        text = text.replace("  ", " ")

    return text.strip()

# --------------------------------------------
# Chunking
# --------------------------------------------

def split_into_chunks(text):

    text = clean_text(text)

    chunks = []

    start = 0

    while start < len(text):

        end = start + CHUNK_SIZE

        chunk = text[start:end].strip()

        if len(chunk) > 20:
            chunks.append(chunk)

        start += CHUNK_SIZE - CHUNK_OVERLAP

    return chunks

# --------------------------------------------
# Build Database
# --------------------------------------------

doc_id = 0

total_chunks = 0

print("\nBuilding knowledge base...\n")

for filename in sorted(os.listdir(KNOWLEDGE_FOLDER)):

    if not filename.endswith(".md"):
        continue

    filepath = os.path.join(KNOWLEDGE_FOLDER, filename)

    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()

    chunks = split_into_chunks(text)

    print(f"{filename:25} -> {len(chunks)} chunks")

    for chunk in chunks:

        embedding = model.encode(chunk).tolist()

        collection.add(
            ids=[str(doc_id)],
            documents=[chunk],
            metadatas=[{"source": filename}],
            embeddings=[embedding]
        )

        doc_id += 1
        total_chunks += 1

print("\n======================================")
print("Knowledge Base Built Successfully")
print("======================================")
print(f"Files processed : {doc_id}")
print(f"Chunks created  : {total_chunks}")
print(f"Database folder : {DB_PATH}")