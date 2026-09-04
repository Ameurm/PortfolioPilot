from pathlib import Path
from typing import Any

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_ollama import ChatOllama


# =========================================================
# Configuration
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
VECTORSTORE_PATH = BASE_DIR / "vectorstore"

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
OLLAMA_MODEL = "llama3.2"

INITIAL_RETRIEVAL_K = 10
FINAL_CONTEXT_K = 5


# =========================================================
# Embeddings
# =========================================================

print("Loading embedding model...")

embeddings = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL
)

print("Embedding model loaded.")


# =========================================================
# FAISS Vector Store
# =========================================================

print("Loading FAISS vector store...")

vectorstore = FAISS.load_local(
    str(VECTORSTORE_PATH),
    embeddings,
    allow_dangerous_deserialization=True,
)

print("FAISS vector store loaded.")


# =========================================================
# Retriever
# =========================================================

retriever = vectorstore.as_retriever(
    search_kwargs={
        "k": INITIAL_RETRIEVAL_K
    }
)


# =========================================================
# Ollama / Llama
# =========================================================

llm = ChatOllama(
    model=OLLAMA_MODEL,
    temperature=0,
)


# =========================================================
# Metadata Authorization
# =========================================================

def is_authorized(document) -> bool:
    """
    Portfolio demo authorization policy.

    Only public documents are currently allowed.

    Production authorization could evaluate:

    - tenant_id
    - user_id
    - department
    - role
    - document permissions
    - security policies
    """

    access_level = document.metadata.get(
        "access_level",
        "restricted"
    )

    return access_level == "public"


# =========================================================
# Lightweight Lexical Reranking
# =========================================================

def rerank_documents(question, documents):

    question_words = {
        word.lower().strip(".,?!:;()[]{}\"'")
        for word in question.split()
        if len(word) > 2
    }

    scored_documents = []

    for document in documents:

        content = document.page_content.lower()

        score = 0

        for word in question_words:

            if word in content:
                score += 1

        scored_documents.append(
            (score, document)
        )

    scored_documents.sort(
        key=lambda item: item[0],
        reverse=True
    )

    return [
        document
        for score, document in scored_documents
    ]


# =========================================================
# RAG Response
# =========================================================

def answer_question(question: str) -> dict[str, Any]:

    print()
    print("=" * 70)
    print("QUESTION")
    print("=" * 70)

    print(question)

    # =====================================================
    # 1. Semantic Retrieval
    # =====================================================

    documents = retriever.invoke(question)

    retrieved_count = len(documents)

    print()
    print("=" * 70)
    print("RETRIEVED CANDIDATES")
    print("=" * 70)

    print(
        f"Candidates retrieved: {retrieved_count}"
    )

    for index, document in enumerate(
        documents,
        start=1
    ):

        print()
        print(f"--- CANDIDATE {index} ---")

        print(
            f"Metadata: {document.metadata}"
        )

    # =====================================================
    # 2. Metadata Authorization
    # =====================================================

    authorized_documents = [
        document
        for document in documents
        if is_authorized(document)
    ]

    authorized_count = len(
        authorized_documents
    )

    filtered_count = (
        retrieved_count -
        authorized_count
    )

    print()
    print("=" * 70)
    print("METADATA AUTHORIZATION")
    print("=" * 70)

    print(
        f"Authorized documents: "
        f"{authorized_count}"
    )

    print(
        f"Filtered documents: "
        f"{filtered_count}"
    )

    # =====================================================
    # 3. No Authorized Context
    # =====================================================

    if not authorized_documents:

        answer = (
            "The knowledge base does not contain "
            "authorized information to answer this question."
        )

        return {
            "answer": answer,
            "question": question,
            "retrieval": {
                "initial_k": INITIAL_RETRIEVAL_K,
                "retrieved": retrieved_count,
            },
            "authorization": {
                "authorized": 0,
                "filtered": filtered_count,
            },
            "reranking": {
                "enabled": True,
                "type": "lightweight_lexical",
                "production_upgrade": "cross_encoder",
            },
            "context": {
                "selected": 0,
            },
            "model": OLLAMA_MODEL,
            "embedding_model": EMBEDDING_MODEL,
            "vector_store": "FAISS",
            "sources": [],
        }

    # =====================================================
    # 4. Lightweight Lexical Reranking
    # =====================================================

    print()
    print("=" * 70)
    print("LIGHTWEIGHT LEXICAL RERANKING")
    print("=" * 70)

    reranked_documents = rerank_documents(
        question,
        authorized_documents
    )

    reranked_count = len(
        reranked_documents
    )

    print(
        f"Documents after reranking: "
        f"{reranked_count}"
    )

    # =====================================================
    # 5. Select Final Context
    # =====================================================

    final_documents = reranked_documents[
        :FINAL_CONTEXT_K
    ]

    final_context_count = len(
        final_documents
    )

    print()
    print("=" * 70)
    print("FINAL CONTEXT")
    print("=" * 70)

    print(
        f"Documents sent to Llama: "
        f"{final_context_count}"
    )

    for index, document in enumerate(
        final_documents,
        start=1
    ):

        print()
        print(f"--- SOURCE {index} ---")

        print(
            f"Metadata: {document.metadata}"
        )

        print()
        print(document.page_content)

    # =====================================================
    # 6. Build Context
    # =====================================================

    context_parts = []

    for index, document in enumerate(
        final_documents,
        start=1
    ):

        context_parts.append(
            f"""
[SOURCE {index}]

Source:
{document.metadata.get("source")}

Category:
{document.metadata.get("category")}

Access Level:
{document.metadata.get("access_level")}

Content:
{document.page_content}
"""
        )

    context = "\n\n".join(
        context_parts
    )

    # =====================================================
    # 7. Strict Grounded Prompt
    # =====================================================

    prompt = f"""
You are answering a question using a retrieved knowledge base.

You MUST answer the user's question using ONLY the information
contained in the SOURCE MATERIAL below.

You are NOT a general conversational assistant.

SOURCE MATERIAL
===============

{context}

END SOURCE MATERIAL
===================

USER QUESTION
=============

{question}

ANSWERING RULES
===============

1. Answer the USER QUESTION directly.
2. Use only facts supported by the SOURCE MATERIAL.
3. Do not use outside knowledge.
4. Do not invent technologies, projects, companies, responsibilities,
   metrics, or personal experience.
5. If the SOURCE MATERIAL contains the answer, explain it clearly
   and concisely.
6. If the SOURCE MATERIAL does not contain enough information,
   respond exactly with:

"The knowledge base does not contain enough information to answer
that accurately."

7. Do not ask the user to provide another question.
8. Do not say "Please go ahead and ask your question."
9. Do not describe yourself as an AI assistant.
10. Do not repeat the user's question.
11. Distinguish between technologies actually implemented and
    technologies listed only as production alternatives.
12. Keep the response professional and concise.

Now answer the USER QUESTION.

ANSWER:
"""

    # =====================================================
    # 8. Llama Generation
    # =====================================================

    print()
    print("=" * 70)
    print("CALLING LLAMA 3.2")
    print("=" * 70)

    response = llm.invoke(prompt)

    answer = response.content

    # =====================================================
    # 9. Build Source Metadata
    # =====================================================

    sources = []

    for document in final_documents:

        sources.append(
            {
                "source": document.metadata.get(
                    "source"
                ),
                "chunk_id": document.metadata.get(
                    "chunk_id"
                ),
                "category": document.metadata.get(
                    "category"
                ),
                "access_level": document.metadata.get(
                    "access_level"
                ),
            }
        )

    # =====================================================
    # 10. Final Result
    # =====================================================

    print()
    print("=" * 70)
    print("RAG ANSWER")
    print("=" * 70)

    print(answer)

    return {
        "answer": answer,
        "question": question,

        "retrieval": {
            "initial_k": INITIAL_RETRIEVAL_K,
            "retrieved": retrieved_count,
        },

        "authorization": {
            "authorized": authorized_count,
            "filtered": filtered_count,
        },

        "reranking": {
            "enabled": True,
            "type": "lightweight_lexical",
            "documents_reranked": reranked_count,
            "production_upgrade": "cross_encoder",
        },

        "context": {
            "selected": final_context_count,
            "max_context": FINAL_CONTEXT_K,
        },

        "model": OLLAMA_MODEL,

        "embedding_model": EMBEDDING_MODEL,

        "vector_store": "FAISS",

        "sources": sources,
    }