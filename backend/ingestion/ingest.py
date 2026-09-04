from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


# =========================================================
# 1. Paths
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DOCUMENT_PATH = (
    BASE_DIR
    / "documents"
    / "ai_architecture_knowledge.md"
)

VECTORSTORE_PATH = BASE_DIR / "vectorstore"


# =========================================================
# 2. Load Document
# =========================================================

text = DOCUMENT_PATH.read_text(
    encoding="utf-8"
)

print(f"Loaded document: {DOCUMENT_PATH}")
print(f"Characters: {len(text)}")


# =========================================================
# 3. Chunk Document
# =========================================================

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=150,
)

chunks = text_splitter.create_documents(
    [text]
)


# =========================================================
# 4. Add Metadata
# =========================================================

for index, chunk in enumerate(chunks, start=1):

    chunk.metadata = {
        "source": DOCUMENT_PATH.name,
        "document_type": "ai_architecture_knowledge",
        "chunk_id": index,
        "access_level": "public",
        "category": "architecture",
    }


print()
print(f"Created {len(chunks)} chunks")


# =========================================================
# 5. Load Embedding Model
# =========================================================

print()
print("Loading embedding model...")

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

print("Embedding model loaded.")


# =========================================================
# 6. Create FAISS Vector Store
# =========================================================

print()
print("Creating FAISS vector store...")

vectorstore = FAISS.from_documents(
    chunks,
    embeddings,
)

print("FAISS vector store created.")


# =========================================================
# 7. Save FAISS
# =========================================================

VECTORSTORE_PATH.mkdir(
    parents=True,
    exist_ok=True,
)

vectorstore.save_local(
    str(VECTORSTORE_PATH)
)

print()
print("=" * 70)
print("FAISS VECTOR STORE SAVED")
print("=" * 70)

print(f"Location: {VECTORSTORE_PATH}")


# =========================================================
# 8. Display Sample Metadata
# =========================================================

print()
print("=" * 70)
print("SAMPLE CHUNKS")
print("=" * 70)

for chunk in chunks[:5]:

    print()
    print(f"Chunk {chunk.metadata['chunk_id']}")
    print(f"Metadata: {chunk.metadata}")