from pathlib import Path
import os
import re
from typing import Any

from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq

load_dotenv()


BASE_DIR = Path(__file__).resolve().parent

VECTORSTORE_PATH = BASE_DIR / "vectorstore"
RESUME_VECTORSTORE_PATH = BASE_DIR / "resume_data" / "vectorstore"

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
LLM_MODEL = "openai/gpt-oss-120b"

INITIAL_RETRIEVAL_K = 10
FINAL_CONTEXT_K = 5


print("Loading embedding model...")

embeddings = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL
)

print("Embedding model loaded.")


print("Loading portfolio FAISS vector store...")

vectorstore = FAISS.load_local(
    str(VECTORSTORE_PATH),
    embeddings,
    allow_dangerous_deserialization=True,
)

print("Portfolio FAISS vector store loaded.")

portfolio_retriever = vectorstore.as_retriever(
    search_kwargs={"k": INITIAL_RETRIEVAL_K}
)


# ---------------------------------------------------------
# Resume vector store
# ---------------------------------------------------------

resume_vectorstore = None
resume_retriever = None


def reload_resume_retriever() -> bool:
    global resume_vectorstore
    global resume_retriever

    resume_index_file = RESUME_VECTORSTORE_PATH / "index.faiss"

    if not resume_index_file.exists():
        resume_vectorstore = None
        resume_retriever = None

        print(
            "Resume FAISS vector store not found. "
            "Resume retrieval is disabled."
        )

        return False

    try:
        print("Loading resume FAISS vector store...")

        resume_vectorstore = FAISS.load_local(
            str(RESUME_VECTORSTORE_PATH),
            embeddings,
            allow_dangerous_deserialization=True,
        )

        resume_retriever = resume_vectorstore.as_retriever(
            search_kwargs={"k": INITIAL_RETRIEVAL_K}
        )

        print("Resume FAISS vector store loaded.")

        return True

    except Exception as exc:

        resume_vectorstore = None
        resume_retriever = None

        print(
            f"Failed to load resume FAISS vector store: {exc}"
        )

        return False


reload_resume_retriever()


# ---------------------------------------------------------
# Gemini
# ---------------------------------------------------------

# ---------------------------------------------------------
# Gemini
# ---------------------------------------------------------

# ---------------------------------------------------------
# Groq
# ---------------------------------------------------------

llm = ChatGroq(
    model=LLM_MODEL,
    groq_api_key=os.getenv("GROQ_API_KEY"),
    temperature=0,
)


# ---------------------------------------------------------
# Security / authorization
# ---------------------------------------------------------

def is_authorized(document) -> bool:

    access_level = document.metadata.get(
        "access_level",
        "restricted",
    )

    return access_level == "public"


# ---------------------------------------------------------
# Source classification
# ---------------------------------------------------------

def classify_source(document) -> str:

    document_type = document.metadata.get(
        "document_type"
    )

    if document_type == "resume":
        return "resume"

    return "portfolio"


# ---------------------------------------------------------
# Text normalization
# ---------------------------------------------------------

def normalize_text(text: str) -> str:

    text = text.lower()

    text = re.sub(
        r"[^a-z0-9+#./-]+",
        " ",
        text,
    )

    return re.sub(
        r"\s+",
        " ",
        text,
    ).strip()


def tokenize(text: str) -> list[str]:

    normalized = normalize_text(text)

    return [
        token
        for token in normalized.split()
        if len(token) > 2
    ]


# ---------------------------------------------------------
# Personal experience detection
# ---------------------------------------------------------

def is_personal_experience_question(
    question: str,
) -> bool:

    normalized = normalize_text(question)

    personal_terms = [
        "experience",
        "worked",
        "work",
        "built",
        "developed",
        "designed",
        "implemented",
        "architected",
        "used",
        "skills",
        "background",
        "resume",
        "career",
        "project",
        "projects",
        "javier",
        "candidate",
        "professional",
    ]

    return any(
        term in normalized
        for term in personal_terms
    )


# ---------------------------------------------------------
# Hybrid reranking
# ---------------------------------------------------------

def rerank_documents(
    question: str,
    documents: list,
) -> list:

    if not documents:
        return []

    normalized_question = normalize_text(
        question
    )

    question_tokens = set(
        tokenize(question)
    )

    personal_question = (
        is_personal_experience_question(
            question
        )
    )

    scored_documents = []

    for semantic_rank, document in enumerate(
        documents
    ):

        content = normalize_text(
            document.page_content
        )

        source_type = classify_source(
            document
        )

        score = 0.0

        # Exact phrase match
        if normalized_question in content:
            score += 20.0

        # Token matching
        content_tokens = set(
            tokenize(document.page_content)
        )

        exact_matches = (
            question_tokens.intersection(
                content_tokens
            )
        )

        score += len(exact_matches) * 4.0

        # Technology matching
        technology_terms = [
            "langgraph",
            "langchain",
            "mcp",
            "model context protocol",
            "rag",
            "fastapi",
            "python",
            "dotnet",
            ".net",
            "asp.net",
            "react",
            "angular",
            "azure",
            "aws",
            "gcp",
            "kafka",
            "faiss",
            "pinecone",
            "openai",
            "gemini",
            "claude",
            "llm",
            "multi-agent",
            "agentic",
            "microservices",
            "cosmos db",
            "sql server",
            "kubernetes",
            "aks",
            "eks",
            "terraform",
        ]

        for term in technology_terms:

            normalized_term = normalize_text(
                term
            )

            if not normalized_term:
                continue

            if normalized_term in content:

                if " " in normalized_term:
                    score += 8.0
                else:
                    score += 7.0

        # Resume priority for personal questions
        if (
            personal_question
            and source_type == "resume"
        ):
            score += 12.0

        # Requested technology matching
        if source_type == "resume":

            requested_technology_terms = {
                "langgraph",
                "langchain",
                "mcp",
                "rag",
                "fastapi",
                "python",
                "react",
                "angular",
                "azure",
                "aws",
                "gcp",
                "kafka",
                "faiss",
                "pinecone",
                "openai",
                "gemini",
                "claude",
                "llm",
            }

            requested_matches = 0

            for token in question_tokens:

                if token in requested_technology_terms:

                    if token in content_tokens:
                        requested_matches += 1

            score += requested_matches * 6.0

        # Small semantic-rank bonus
        semantic_bonus = max(
            0.0,
            5.0 - (semantic_rank * 0.35),
        )

        score += semantic_bonus

        scored_documents.append(
            (
                score,
                semantic_rank,
                document,
            )
        )

    scored_documents.sort(
        key=lambda item: (
            item[0],
            -item[1],
        ),
        reverse=True,
    )

    return [
        document
        for score, semantic_rank, document
        in scored_documents
    ]


# ---------------------------------------------------------
# Context selection
# ---------------------------------------------------------

def select_context_documents(
    question: str,
    documents: list,
    max_documents: int = FINAL_CONTEXT_K,
) -> list:

    if not documents:
        return []

    personal_question = (
        is_personal_experience_question(
            question
        )
    )

    if personal_question:

        resume_documents = [
            document
            for document in documents
            if classify_source(document)
            == "resume"
        ]

        selected = []

        # Prioritize resume evidence
        for document in resume_documents[:3]:

            selected.append(document)

        # Fill remaining context
        for document in documents:

            if len(selected) >= max_documents:
                break

            if document not in selected:
                selected.append(document)

        return selected[:max_documents]

    return documents[:max_documents]


# ---------------------------------------------------------
# Main RAG function
# ---------------------------------------------------------

def answer_question(
    question: str,
) -> dict[str, Any]:

    question = question.strip()

    if not question:

        return {
            "answer": (
                "Please provide a question about "
                "Javier's experience, skills, or projects."
            ),
            "question": question,
            "retrieval": {
                "initial_k": INITIAL_RETRIEVAL_K,
                "portfolio_retrieved": 0,
                "resume_retrieved": 0,
                "retrieved": 0,
            },
            "authorization": {
                "authorized": 0,
                "filtered": 0,
            },
            "reranking": {
                "enabled": True,
                "type": "hybrid_exact_semantic",
                "documents_reranked": 0,
            },
            "context": {
                "selected": 0,
                "max_context": FINAL_CONTEXT_K,
            },
            "model": LLM_MODEL,
            "embedding_model": EMBEDDING_MODEL,
            "vector_store": "FAISS",
            "sources": [],
        }

    # -----------------------------------------------------
    # Portfolio retrieval
    # -----------------------------------------------------

    portfolio_documents = (
        portfolio_retriever.invoke(question)
    )

    # -----------------------------------------------------
    # Resume retrieval
    # -----------------------------------------------------

    resume_documents = []

    if resume_retriever is not None:

        resume_documents = (
            resume_retriever.invoke(question)
        )

    # -----------------------------------------------------
    # Combine sources
    # -----------------------------------------------------

    all_documents = (
        portfolio_documents
        + resume_documents
    )

    # -----------------------------------------------------
    # Authorization filter
    # -----------------------------------------------------

    authorized_documents = [
        document
        for document in all_documents
        if is_authorized(document)
    ]

    filtered_count = (
        len(all_documents)
        - len(authorized_documents)
    )

    # -----------------------------------------------------
    # Reranking
    # -----------------------------------------------------

    reranked_documents = rerank_documents(
        question,
        authorized_documents,
    )

    # -----------------------------------------------------
    # Context selection
    # -----------------------------------------------------

    selected_documents = (
        select_context_documents(
            question,
            reranked_documents,
            FINAL_CONTEXT_K,
        )
    )

    # -----------------------------------------------------
    # Build context
    # -----------------------------------------------------

    context_blocks = []

    for index, document in enumerate(
        selected_documents,
        start=1,
    ):

        source_type = classify_source(
            document
        )

        source = document.metadata.get(
            "source",
            "unknown",
        )

        category = document.metadata.get(
            "category",
            "unknown",
        )

        access_level = document.metadata.get(
            "access_level",
            "unknown",
        )

        context_blocks.append(
            f"""
SOURCE {index}

Source Type: {source_type}
Source: {source}
Category: {category}
Access Level: {access_level}

Content:
{document.page_content}
""".strip()
        )

    context = "\n\n".join(
        context_blocks
    )

    # -----------------------------------------------------
    # LLM prompt
    # -----------------------------------------------------

    prompt = f"""
You are the AI assistant for Javier's professional portfolio.

Answer the user's question using ONLY the provided source material.

USER QUESTION:
{question}

SOURCE MATERIAL:
{context}

RULES:

1. Answer the question directly.

2. Use only facts explicitly supported by the source material.

3. Do not use outside knowledge.

4. Never invent technologies, projects, companies,
responsibilities, certifications, education, metrics,
achievements, or years of experience.

5. If the source material supports the answer,
explain it clearly and concisely.

6. If the source material does not contain enough
evidence, respond exactly with:

The knowledge base does not contain enough information to answer that accurately.

7. Do not ask the user to provide more information.

8. Do not mention that you are an AI assistant.

9. Do not repeat the user's question unnecessarily.

10. Do not speculate.

11. Clearly distinguish between technologies actually
documented in Javier's experience and technologies
mentioned only as possible alternatives or architectural
concepts.

12. When the source type is "resume", treat it as
documented professional experience, skills, projects,
and career history.

13. When the source type is "portfolio", treat it as
project architecture and technical knowledge documented
in the portfolio.

14. Do not combine unrelated claims merely because they
appear in different documents.

15. Keep the answer concise but useful.

16. When the question asks about Javier's personal
experience, prioritize evidence from the resume.

17. If multiple resume sections support the same
technology, synthesize them into one accurate answer.

18. Do not infer that knowing a technology means Javier
used it professionally unless the source explicitly
supports that.
"""

    # -----------------------------------------------------
    # Gemini
    # -----------------------------------------------------

    response = llm.invoke(prompt)

    answer = response.content

    if not isinstance(answer, str):

        if isinstance(answer, list):

            answer = " ".join(
                str(item)
                for item in answer
            )

        else:

            answer = str(answer)

    # -----------------------------------------------------
    # Sources
    # -----------------------------------------------------

    sources = []

    for document in selected_documents:

        document_type = document.metadata.get(
            "document_type",
            "unknown",
        )

        source_type = classify_source(
            document
        )

        sources.append(
            {
                "source": document.metadata.get(
                    "source",
                    "unknown",
                ),
                "chunk_id": document.metadata.get(
                    "chunk_id",
                    "unknown",
                ),
                "category": document.metadata.get(
                    "category",
                    "unknown",
                ),
                "document_type": document_type,
                "source_type": source_type,
                "access_level": document.metadata.get(
                    "access_level",
                    "unknown",
                ),
            }
        )

    # -----------------------------------------------------
    # Response
    # -----------------------------------------------------

    return {
        "answer": answer,
        "question": question,

        "retrieval": {
            "initial_k": INITIAL_RETRIEVAL_K,
            "portfolio_retrieved": len(
                portfolio_documents
            ),
            "resume_retrieved": len(
                resume_documents
            ),
            "retrieved": len(
                all_documents
            ),
        },

        "authorization": {
            "authorized": len(
                authorized_documents
            ),
            "filtered": filtered_count,
        },

        "reranking": {
            "enabled": True,
            "type": "hybrid_exact_semantic",
            "documents_reranked": len(
                authorized_documents
            ),
            "production_upgrade": "cross_encoder",
        },

        "context": {
            "selected": len(
                selected_documents
            ),
            "max_context": FINAL_CONTEXT_K,
        },

        "model": LLM_MODEL,
        "embedding_model": EMBEDDING_MODEL,
        "vector_store": "FAISS",

        "sources": sources,
    }
