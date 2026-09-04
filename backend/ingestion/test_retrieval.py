from pathlib import Path

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


BASE_DIR = Path(__file__).resolve().parent.parent

VECTORSTORE_PATH = BASE_DIR / "vectorstore"


# ---------------------------------------------------------
# Load embedding model
# ---------------------------------------------------------

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


# ---------------------------------------------------------
# Load FAISS index
# ---------------------------------------------------------

vectorstore = FAISS.load_local(
    str(VECTORSTORE_PATH),
    embeddings,
    allow_dangerous_deserialization=True,
)


# ---------------------------------------------------------
# User question
# ---------------------------------------------------------

query = "How did you implement RAG?"


# ---------------------------------------------------------
# Retrieve relevant chunks
# ---------------------------------------------------------

results = vectorstore.similarity_search(
    query,
    k=3,
)


# ---------------------------------------------------------
# Display results
# ---------------------------------------------------------

print()
print("=" * 70)
print("USER QUESTION")
print("=" * 70)
print(query)

for index, document in enumerate(results, start=1):

    print()
    print("=" * 70)
    print(f"RETRIEVED CHUNK {index}")
    print("=" * 70)

    print(document.page_content)