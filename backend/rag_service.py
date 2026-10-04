from pathlib import Path
import os
import re
from typing import Any

from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq

from resume_service import get_resume_retriever


load_dotenv()


BASE_DIR = Path(__file__).resolve().parent

VECTORSTORE_PATH = BASE_DIR / "vectorstore"

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
LLM_PROVIDER = "groq"
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
    search_kwargs={
        "k": INITIAL_RETRIEVAL_K
    }
)


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
# Query intent classification
# ---------------------------------------------------------

def classify_query_intent(question: str) -> str:
    """
    Classifies the question so retrieval can prioritize
    the appropriate knowledge source.

    Returns:
        PERSONAL_EXPERIENCE
        PERSONAL_SKILLS
        PROJECT_ARCHITECTURE
        TECHNICAL_ARCHITECTURE
        GENERAL
    """

    normalized = normalize_text(question)

    personal_terms = {
        "my experience",
        "my background",
        "my career",
        "my resume",
        "my skills",
        "my projects",
        "what have i built",
        "what have i developed",
        "what have i designed",
        "what have i implemented",
        "what did i build",
        "what did i develop",
        "what did i design",
        "what did i implement",
        "have i used",
        "did i use",
        "years of experience",
        "professional experience",
        "experience building",
        "experience with",
        "experience developing",
        "experience designing",
        "experience implementing",
    }

    project_architecture_terms = {
        "architecture used in",
        "architecture of",
        "architecture for",
        "architecture behind",
        "how does my application",
        "how does my portfolio",
        "how does portfolio",
        "how does the application",
        "how is the application",
        "how is portfolio",
        "implementation used in",
        "implementation of",
        "rag architecture",
        "rag pipeline used",
        "pipeline used in",
    }

    personal_skill_terms = {
        "what technologies do i know",
        "what technologies and skills do i have",
        "what skills and technologies do i have",
        "what technologies do i have",
        "what technologies do i have",
        "what are my technologies",
        "what skills do i have",
        "what is my tech stack",
        "what is my technology stack",
        "which technologies have i used",
        "which tools have i used",
    }

    technical_architecture_terms = {
        "how does rag work",
        "how does rag retrieval work",
        "how does rag retrieval and reranking work",
        "how does retrieval and reranking work",
        "how do retrieval and reranking work",
        "explain retrieval and reranking",
        "how does rag architecture work",
        "explain rag",
        "explain the rag architecture",
        "explain the rag pipeline",
        "how does retrieval work",
        "how does semantic search work",
        "how does vector search work",
        "how does reranking work",
        "how does the retrieval pipeline work",
    }

    if any(
        term in normalized
        for term in personal_terms
    ):
        return "PERSONAL_EXPERIENCE"

    if any(
        term in normalized
        for term in personal_skill_terms
    ):
        return "PERSONAL_SKILLS"

    if any(
        term in normalized
        for term in project_architecture_terms
    ):
        return "PROJECT_ARCHITECTURE"

    if any(
        term in normalized
        for term in technical_architecture_terms
    ):
        return "TECHNICAL_ARCHITECTURE"

    return "GENERAL"


# ---------------------------------------------------------
# Backward-compatible personal question detection
# ---------------------------------------------------------

def is_personal_experience_question(
    question: str,
) -> bool:

    intent = classify_query_intent(question)

    return intent in {
        "PERSONAL_EXPERIENCE",
        "PERSONAL_SKILLS",
    }


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

    query_intent = classify_query_intent(question)

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

        # Intent-based source priority
        if query_intent in {
            "PERSONAL_EXPERIENCE",
            "PERSONAL_SKILLS",
        }:
            if source_type == "resume":
                score += 12.0

        elif query_intent in {
            "PROJECT_ARCHITECTURE",
            "TECHNICAL_ARCHITECTURE",
        }:
            if source_type == "portfolio":
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

    intent = classify_query_intent(question)

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

    # -----------------------------------------------------
    # Personal experience
    # -----------------------------------------------------

    if intent == "PERSONAL_EXPERIENCE":

        primary = resume_documents
        secondary = portfolio_documents

    # -----------------------------------------------------
    # Personal skills
    # -----------------------------------------------------

    elif intent == "PERSONAL_SKILLS":

        primary = resume_documents
        secondary = portfolio_documents

    # -----------------------------------------------------
    # Project architecture
    # -----------------------------------------------------

    elif intent == "PROJECT_ARCHITECTURE":

        primary = portfolio_documents
        secondary = resume_documents

    # -----------------------------------------------------
    # Technical architecture
    # -----------------------------------------------------

    elif intent == "TECHNICAL_ARCHITECTURE":

        primary = portfolio_documents
        secondary = resume_documents

    # -----------------------------------------------------
    # General question
    # -----------------------------------------------------

    else:

        # Preserve the hybrid reranking order for
        # questions that do not clearly belong to
        # one knowledge domain.

        return documents[:max_documents]

    selected = []

    # Primary knowledge source gets first priority.
    for document in primary:

        if len(selected) >= max_documents:
            break

        selected.append(document)

    # Secondary source fills remaining context.
    for document in secondary:

        if len(selected) >= max_documents:
            break

        if document not in selected:
            selected.append(document)

    return selected[:max_documents]


# ---------------------------------------------------------
# Main RAG function
# ---------------------------------------------------------

def answer_question(
    question: str,
    session_id: str,
) -> dict[str, Any]:

    question = question.strip()

    if not question:

        return {
            "answer": (
                "Please provide a question about "
                "the candidate's experience, skills, "
                "or projects."
            ),
            "question": question,
            "query_intent": "GENERAL",
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
                "query_intent": "GENERAL",
                "documents_reranked": 0,
            },
            "context": {
                "selected": 0,
                "max_context": FINAL_CONTEXT_K,
            },
            "provider": LLM_PROVIDER,
            "model": LLM_MODEL,
            "embedding_model": EMBEDDING_MODEL,
            "vector_store": "FAISS",
            "sources": [],
        }

    query_intent = classify_query_intent(question)

    # -----------------------------------------------------
    # Portfolio retrieval
    # -----------------------------------------------------

    portfolio_documents = (
        portfolio_retriever.invoke(
            question
        )
    )

    # -----------------------------------------------------
    # Session-specific resume retrieval
    # -----------------------------------------------------

    resume_documents = []

    resume_retriever = (
        get_resume_retriever(
            session_id
        )
    )

    if resume_retriever is not None:

        resume_documents = (
            resume_retriever.invoke(
                question
            )
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
You are the AI assistant for a professional software
architect portfolio.

Answer the user's question using ONLY the provided
source material.

USER QUESTION:
{question}

QUERY INTENT:
{query_intent}

SOURCE MATERIAL:
{context}

RULES:

1. Answer the question directly.

2. Use only facts explicitly supported by the source
material.

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
documented in the candidate's experience and technologies
mentioned only as possible alternatives or architectural
concepts.

12. When the source type is "resume", treat it as
authoritative evidence for the candidate's documented
professional experience, skills, projects, education,
and career history.

13. When the source type is "portfolio", treat it as
project architecture and technical knowledge documented
in the portfolio.

14. When a session-specific resume is present, NEVER use
a person's name, identity, employer history, education,
or personal background from another portfolio document
to identify the candidate.

15. Do not combine unrelated claims merely because they
appear in different documents.

16. Keep the answer concise but useful.

17. When the question asks about the candidate's personal
experience, prioritize the session-specific resume.

18. If multiple resume sections support the same
technology, synthesize them into one accurate answer.

19. Do not infer that knowing a technology means the
candidate used it professionally unless the source
explicitly supports that.

20. Never introduce a candidate name unless that name
appears in the authoritative session-specific resume
source material.

21. When the query intent is PROJECT_ARCHITECTURE,
prioritize the portfolio source as the authoritative
source for the application's documented architecture.

22. When the query intent is TECHNICAL_ARCHITECTURE,
prioritize portfolio architecture documentation while
using resume material only when it directly supports
the technical answer.
"""

    # -----------------------------------------------------
    # Groq
    # -----------------------------------------------------

    response = llm.invoke(
        prompt
    )

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
        "query_intent": query_intent,

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
            "query_intent": query_intent,
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

        "provider": LLM_PROVIDER,
        "model": LLM_MODEL,
        "embedding_model": EMBEDDING_MODEL,
        "vector_store": "FAISS",

        "session_id": session_id,

        "sources": sources,
    }




