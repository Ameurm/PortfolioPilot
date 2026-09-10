from pathlib import Path

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

DOCUMENT_PATH = BASE_DIR / "documents" / "ai_architecture_knowledge.md"
VECTORSTORE_PATH = BASE_DIR / "vectorstore"


# ---------------------------------------------------------
# Load document
# ---------------------------------------------------------

print("Loading knowledge document...")

text = DOCUMENT_PATH.read_text(encoding="utf-8")

print(f"Document: {DOCUMENT_PATH}")
print(f"Characters: {len(text)}")


# ---------------------------------------------------------
# Chunk document
# ---------------------------------------------------------

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=150,
)

chunks = text_splitter.create_documents([text])

for i, chunk in enumerate(chunks):
    chunk.metadata["source"] = DOCUMENT_PATH.name
    chunk.metadata["document_type"] = "ai_architecture_knowledge"
    chunk.metadata["chunk_id"] = i
    chunk.metadata["access_level"] = "public"
    chunk.metadata["category"] = "architecture"
print(f"Created {len(chunks)} chunks")


# ---------------------------------------------------------
# Create local embeddings
# ---------------------------------------------------------

print("Loading local embedding model...")

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

print("Embedding model loaded")


# ---------------------------------------------------------
# Create FAISS vector store
# ---------------------------------------------------------

print("Creating FAISS vector store...")

vectorstore = FAISS.from_documents(
    chunks,
    embeddings,
)


# ---------------------------------------------------------
# Save vector store
# ---------------------------------------------------------

VECTORSTORE_PATH.mkdir(parents=True, exist_ok=True)

vectorstore.save_local(str(VECTORSTORE_PATH))

print()
print("======================================")
print("VECTOR STORE CREATED SUCCESSFULLY")
print("======================================")
print(f"Location: {VECTORSTORE_PATH}")
print(f"Chunks indexed: {len(chunks)}")




