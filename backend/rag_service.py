from pathlib import Path
import re
from typing import Any

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI


BASE_DIR = Path(__file__).resolve().parent

VECTORSTORE_PATH = BASE_DIR / "vectorstore"
RESUME_VECTORSTORE_PATH = BASE_DIR / "resume_data" / "vectorstore"

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
LLM_MODEL = "gemini-3.6-flash"

INITIAL_RETRIEVAL_K = 10
FINAL_CONTEXT_K = 5


# ============================================================
# Embeddings
# ============================================================

print("Loading embedding model...")

embeddings = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL
)

print("Embedding model loaded.")


# ============================================================
# Portfolio Vector Store
# ============================================================

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


# ============================================================
# Resume Vector Store
# ============================================================

resume_vectorstore = None
resume_retriever = None

resume_index_file = RESUME_VECTORSTORE_PATH / "index.faiss"

if resume_index_file.exists():

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

else:

    print(
        "Resume FAISS vector store not found. "
        "Resume retrieval is disabled."
    )


# ============================================================
# LLM
# ============================================================

llm = ChatGoogleGenerativeAI(
    model=LLM_MODEL
)


# ============================================================
# Authorization
# ============================================================

def is_authorized(document) -> bool:

    access_level = document.metadata.get(
        "access_level",
        "restricted",
    )

    return access_level == "public"


# ============================================================
# Source Classification
# ============================================================

def classify_source(document) -> str:

    document_type = document.metadata.get(
        "document_type"
    )

    if document_type == "resume":
        return "resume"

    return "portfolio"


# ============================================================
# Text Normalization
# ============================================================

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


# ============================================================
# Personal Experience Detection
# ============================================================

def is_personal_experience_question(question: str) -> bool:

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
        "developed",
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


# ============================================================
# Hybrid Reranking
# ============================================================

def rerank_documents(
    question: str,
    documents: list,
) -> list:

    if not documents:
        return []

    normalized_question = normalize_text(question)

    question_tokens = set(
        tokenize(question)
    )

    personal_question = (
        is_personal_experience_question(question)
    )

    scored_documents = []

    for semantic_rank, document in enumerate(documents):

        content = normalize_text(
            document.page_content
        )

        source_type = classify_source(document)

        score = 0.0

        # ----------------------------------------------------
        # 1. Exact phrase match
        # ----------------------------------------------------

        if normalized_question in content:
            score += 20.0

        # ----------------------------------------------------
        # 2. Exact token matches
        # ----------------------------------------------------

        content_tokens = set(
            tokenize(document.page_content)
        )

        exact_matches = (
            question_tokens.intersection(
                content_tokens
            )
        )

        score += len(exact_matches) * 4.0

        # ----------------------------------------------------
        # 3. Strong technology / phrase matching
        #
        # Multi-word or technology terms receive extra weight.
        # This helps queries such as:
        #
        # "LangGraph and MCP"
        #
        # ----------------------------------------------------

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

        matched_technology_terms = 0

        for term in technology_terms:

            normalized_term = normalize_text(term)

            if not normalized_term:
                continue

            if normalized_term in content:

                # Exact technology match gets substantial weight.
                if " " in normalized_term:
                    score += 8.0
                else:
                    score += 7.0

                matched_technology_terms += 1

        # ----------------------------------------------------
        # 4. Personal experience boost
        #
        # When the visitor asks about Javier's experience,
        # resume evidence should outrank generic architecture
        # knowledge when both are relevant.
        # ----------------------------------------------------

        if personal_question and source_type == "resume":

            score += 12.0

        # ----------------------------------------------------
        # 5. Resume chunk with multiple requested terms
        #
        # A resume chunk mentioning both LangGraph and MCP
        # should strongly outrank a chunk mentioning only one.
        # ----------------------------------------------------

        if source_type == "resume":

            requested_technology_matches = 0

            for token in question_tokens:

                if token in {
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
                }:

                    if token in content_tokens:
                        requested_technology_matches += 1

            score += (
                requested_technology_matches * 6.0
            )

        # ----------------------------------------------------
        # 6. Semantic retrieval rank bonus
        #
        # Preserve some of the original FAISS semantic ranking
        # so that lexical matching doesn't completely dominate.
        # ----------------------------------------------------

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

    # Highest score first.
    #
    # Semantic rank is used as the tie breaker so we don't lose
    # the original FAISS relevance signal.
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


# ============================================================
# Context Selection
# ============================================================

def select_context_documents(
    question: str,
    documents: list,
    max_documents: int = FINAL_CONTEXT_K,
) -> list:

    if not documents:
        return []

    personal_question = (
        is_personal_experience_question(question)
    )

    # For personal-experience questions, prefer resume evidence.
    if personal_question:

        resume_documents = [
            document
            for document in documents
            if classify_source(document) == "resume"
        ]

        portfolio_documents = [
            document
            for document in documents
            if classify_source(document) == "portfolio"
        ]

        selected = []

        # Prefer up to 3 highly relevant resume chunks.
        for document in resume_documents[:3]:
            selected.append(document)

        # Fill remaining context slots from the globally
        # reranked list while avoiding duplicates.
        for document in documents:

            if len(selected) >= max_documents:
                break

            if document not in selected:
                selected.append(document)

        return selected[:max_documents]

    return documents[:max_documents]


# ============================================================
# Answer Question
# ============================================================

def answer_question(question: str) -> dict[str, Any]:

    question = question.strip()

    if not question:

        return {
            "answer": (
                "Please provide a question about Javier's "
                "experience, skills, or projects."
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

    # --------------------------------------------------------
    # Portfolio retrieval
    # --------------------------------------------------------

    portfolio_documents = (
        portfolio_retriever.invoke(question)
    )

    # --------------------------------------------------------
    # Resume retrieval
    # --------------------------------------------------------

    resume_documents = []

    if resume_retriever is not None:

        resume_documents = (
            resume_retriever.invoke(question)
        )

    # --------------------------------------------------------
    # Combine retrieval results
    # --------------------------------------------------------

    all_documents = (
        portfolio_documents
        + resume_documents
    )

    # --------------------------------------------------------
    # Authorization
    # --------------------------------------------------------

    authorized_documents = [
        document
        for document in all_documents
        if is_authorized(document)
    ]

    filtered_count = (
        len(all_documents)
        - len(authorized_documents)
    )

    # --------------------------------------------------------
    # Hybrid reranking
    # --------------------------------------------------------

    reranked_documents = rerank_documents(
        question,
        authorized_documents,
    )

    # --------------------------------------------------------
    # Final context selection
    # --------------------------------------------------------

    selected_documents = select_context_documents(
        question,
        reranked_documents,
        FINAL_CONTEXT_K,
    )

    # --------------------------------------------------------
    # Build grounded context
    # --------------------------------------------------------

    context_blocks = []

    for index, document in enumerate(
        selected_documents,
        start=1,
    ):

        source_type = classify_source(document)

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

    # --------------------------------------------------------
    # Grounded prompt
    # --------------------------------------------------------

    prompt = f"""
You are the AI assistant for Javier's professional portfolio.

Answer the user's question using ONLY the provided source
material.

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

5. If the source material supports the answer, explain it
   clearly and concisely.

6. If the source material does not contain enough evidence,
   respond exactly with:

   The knowledge base does not contain enough information to answer that accurately.

7. Do not ask the user to provide more information.

8. Do not mention that you are an AI assistant.

9. Do not repeat the user's question unnecessarily.

10. Do not speculate.

11. Clearly distinguish between technologies actually documented
    in Javier's experience and technologies mentioned only as
    possible alternatives or architectural concepts.

12. When the source type is "resume", treat it as documented
    professional experience, skills, projects, and career history.

13. When the source type is "portfolio", treat it as project
    architecture and technical knowledge documented in the portfolio.

14. Do not combine unrelated claims merely because they appear
    in different documents.

15. Keep the answer concise but useful.

16. When the question asks about Javier's personal experience,
    prioritize evidence from the resume.

17. If multiple resume sections support the same technology,
    synthesize them into one accurate answer rather than
    repeating the same statement.

18. Do not infer that knowing a technology means Javier used it
    professionally unless the source explicitly supports that.
"""

    # --------------------------------------------------------
    # LLM invocation
    # --------------------------------------------------------

    response = llm.invoke(prompt)

    answer = response.content

    # Gemini/LangChain can occasionally return structured content.
    if not isinstance(answer, str):

        if isinstance(answer, list):

            answer = " ".join(
                str(item)
                for item in answer
            )

        else:

            answer = str(answer)

    # --------------------------------------------------------
    # Source metadata
    # --------------------------------------------------------

    sources = []

    for document in selected_documents:

        document_type = document.metadata.get(
            "document_type",
            "unknown",
        )

        source_type = classify_source(document)

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