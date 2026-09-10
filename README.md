# PortfolioPilot

**AI-Powered Architecture & Engineering Portfolio Platform**

PortfolioPilot is an AI-powered portfolio platform designed to demonstrate modern **software architecture, full-stack engineering, cloud-native development, and Generative AI/RAG capabilities**.

The platform combines a modern Next.js frontend with a FastAPI backend and an AI-powered Retrieval-Augmented Generation (RAG) pipeline that allows users to interact with portfolio and architecture knowledge through natural-language questions.

---

## Architecture

```text
                         ┌─────────────────────────┐
                         │      User / Browser      │
                         └────────────┬────────────┘
                                      │ HTTPS
                                      ▼
                         ┌─────────────────────────┐
                         │   Next.js 16 Frontend   │
                         │                         │
                         │ React / TypeScript      │
                         │ Portfolio UI            │
                         │ AI Portfolio Chat       │
                         └────────────┬────────────┘
                                      │ REST API
                                      ▼
                         ┌─────────────────────────┐
                         │     FastAPI Backend     │
                         │                         │
                         │ RAG Orchestration       │
                         │ Authorization            │
                         │ Retrieval               │
                         │ Reranking               │
                         └────────────┬────────────┘
                                      │
                         ┌────────────┴────────────┐
                         │                         │
                         ▼                         ▼
                ┌─────────────────┐      ┌─────────────────┐
                │   FAISS Vector  │      │ Gemini 3.6 Flash│
                │      Store      │      │      LLM        │
                └────────┬────────┘      └─────────────────┘
                         │
                         ▼
                ┌─────────────────────┐
                │ HuggingFace         │
                │ Embeddings          │
                │ all-MiniLM-L6-v2    │
                └─────────────────────┘
```

---

## AI / RAG Pipeline

PortfolioPilot implements a Retrieval-Augmented Generation pipeline:

```text
User Question
      │
      ▼
Question Embedding
      │
      ▼
FAISS Semantic Search
      │
      ▼
Initial Retrieval
      │
      ▼
Metadata Authorization
      │
      ▼
Lexical Reranking
      │
      ▼
Top Context Selection
      │
      ▼
Grounded Prompt
      │
      ▼
Gemini 3.6 Flash
      │
      ▼
AI Response + Retrieval Metadata
```

The RAG implementation is designed to keep responses grounded in the portfolio knowledge base rather than allowing the model to invent projects, technologies, responsibilities, or professional experience.

### Current RAG Components

| Component        | Technology                     |
| ---------------- | ------------------------------ |
| Frontend         | Next.js 16                     |
| UI               | React / TypeScript             |
| Backend          | Python / FastAPI               |
| RAG Framework    | LangChain                      |
| Vector Database  | FAISS                          |
| Embeddings       | HuggingFace `all-MiniLM-L6-v2` |
| LLM              | Google Gemini 3.6 Flash        |
| Document Format  | Markdown                       |
| Retrieval        | Semantic Search                |
| Reranking        | Lightweight Lexical Reranking  |
| API              | REST                           |
| Frontend Hosting | Vercel                         |
| Cloud Target     | Azure / Cloud-Native           |

---

## Features

### AI Portfolio Assistant

Users can ask natural-language questions about:

* Software architecture experience
* AI and Generative AI projects
* RAG implementations
* Cloud architecture
* Microservices
* .NET
* Python
* FastAPI
* Kubernetes
* CI/CD
* AWS / Azure
* Enterprise architecture
* Technical leadership

Example:

```text
Tell me about the RAG systems you have built.
```

The backend retrieves relevant portfolio knowledge and generates a grounded response.

---

## Technology Stack

### Frontend

* Next.js 16
* React
* TypeScript
* Tailwind CSS
* Next.js App Router

### Backend

* Python
* FastAPI
* Uvicorn
* LangChain
* REST APIs

### AI / Machine Learning

* Retrieval-Augmented Generation (RAG)
* Google Gemini
* HuggingFace Sentence Transformers
* Semantic Search
* Vector Embeddings
* FAISS
* Prompt Engineering
* Context Reranking
* Grounded Generation

### Cloud / DevOps

The architecture is designed for cloud-native deployment using:

* Azure
* Docker
* Kubernetes
* CI/CD
* Infrastructure as Code
* Serverless / scale-to-zero compute

---

# Getting Started

## Prerequisites

Install:

* Node.js 20+
* Python 3.14+
* Git

Verify:

```powershell
node --version
python --version
git --version
```

---

# Frontend Setup

Navigate to the project:

```powershell
cd C:\Projects\ai-architect-portfolio-v1
```

Install dependencies:

```powershell
npm install
```

Start the development server:

```powershell
npm run dev
```

Open:

```text
http://localhost:3000
```

---

# Backend Setup

Navigate to the backend:

```powershell
cd C:\Projects\ai-architect-portfolio-v1\backend
```

Create the Python virtual environment:

```powershell
py -3.14 -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

---

# Environment Variables

PortfolioPilot uses environment variables for AI services.

For local development, configure the Gemini API key:

```powershell
$env:GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
```

Never commit API keys to Git.

The project should use environment variables or a secure cloud secret-management solution for production credentials.

---

# Start the Backend

From the `backend` directory:

```powershell
python -m uvicorn main:app --reload --port 8000
```

The API will be available at:

```text
http://127.0.0.1:8000
```

FastAPI documentation:

```text
http://127.0.0.1:8000/docs
```

---

# Test the AI API

Example PowerShell request:

```powershell
Invoke-RestMethod `
  -Uri http://127.0.0.1:8000/chat `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"message":"Tell me about where RAG was used"}'
```

The API returns the AI response together with retrieval metadata such as:

```text
question
retrieval
authorization
reranking
context
model
embedding_model
vector_store
sources
```

---

# Production Architecture

The intended production architecture separates the frontend and backend:

```text
                         Internet
                            │
                            ▼
                ┌─────────────────────┐
                │       Vercel        │
                │    Next.js App      │
                └──────────┬──────────┘
                           │ HTTPS
                           ▼
                ┌─────────────────────┐
                │   FastAPI Backend   │
                │ Azure Container Apps│
                └──────────┬──────────┘
                           │
             ┌─────────────┼─────────────┐
             │             │             │
             ▼             ▼             ▼
          Vector DB       Gemini       Secrets
          / Search         API        Management
```

The backend is designed to run using containerized, usage-based infrastructure rather than requiring a continuously running virtual machine.

---

# Environment Configuration

The frontend reads the backend URL from:

```text
NEXT_PUBLIC_API_URL
```

Local development:

```text
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

Production:

```text
NEXT_PUBLIC_API_URL=https://YOUR-BACKEND-DOMAIN
```

---

# Project Structure

```text
PortfolioPilot/
│
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   └── ...
│
├── components/
│   ├── PortfolioChat.tsx
│   ├── Security.tsx
│   └── ...
│
├── backend/
│   ├── documents/
│   │   └── ai_architecture_knowledge.md
│   │
│   ├── rag_service.py
│   ├── main.py
│   ├── requirements.txt
│   └── ...
│
├── public/
│
├── package.json
├── tsconfig.json
├── next.config.ts
└── README.md
```

---

# Security

PortfolioPilot follows several security principles:

* API keys are stored in environment variables.
* Secrets are never committed to Git.
* Backend authorization filters retrieved documents.
* AI responses are grounded in authorized portfolio content.
* Production deployment should use managed secrets.
* HTTPS should be enforced in production.
* CORS should be restricted to trusted frontend origins.
* API rate limiting should be enabled for production.
* Authentication and tenant isolation will be required for the commercial SaaS version.

---

# Current Development Status

### Completed

* Next.js frontend
* Portfolio UI
* AI Portfolio Chat
* FastAPI backend
* RAG pipeline
* FAISS vector search
* HuggingFace embeddings
* Gemini integration
* Grounded AI responses
* Retrieval metadata
* Vercel frontend deployment
* Azure resource group

### In Progress

* Production backend deployment
* Production API configuration
* CORS configuration
* Vector index deployment
* Cloud secrets
* End-to-end production testing

---

# Commercial SaaS Roadmap

PortfolioPilot is being designed so the current portfolio application can evolve into a commercial AI platform.

### Phase 1 — Portfolio AI

* AI portfolio assistant
* RAG knowledge base
* Architecture showcase
* AI project demonstrations

### Phase 2 — Multi-Tenant Platform

* User registration
* Authentication
* Tenant isolation
* Private knowledge bases
* Document uploads
* Per-tenant vector indexes

### Phase 3 — Enterprise AI

* Multiple LLM providers
* AWS Bedrock
* Azure OpenAI
* Google Gemini
* Agentic AI workflows
* Advanced RAG
* Hybrid search
* Reranking
* MCP integration
* Observability
* Audit logging

### Phase 4 — SaaS

* Subscription plans
* Usage metering
* Billing
* API quotas
* Organization management
* Enterprise security
* Role-Based Access Control (RBAC)
* Admin dashboard

---

# Future Architecture

The long-term platform architecture is planned around:

```text
                    PortfolioPilot SaaS
                           │
            ┌──────────────┼──────────────┐
            │              │              │
            ▼              ▼              ▼
       Web Application   AI Gateway    Admin Portal
            │              │              │
            └──────────────┼──────────────┘
                           ▼
                    Agentic AI Layer
                           │
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
           RAG          AI Agents      MCP Tools
             │             │             │
             └─────────────┼─────────────┘
                           ▼
                     Data Platform
                           │
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
        Vector DB       SQL/NoSQL      Object Storage
```

---

# Development Philosophy

PortfolioPilot demonstrates practical implementation of:

* Clean Architecture
* Cloud-Native Architecture
* Microservices
* API-First Development
* Retrieval-Augmented Generation
* Agentic AI
* Secure AI Engineering
* Infrastructure as Code
* CI/CD
* Observability
* Multi-Tenant SaaS Architecture

The goal is not simply to demonstrate an AI chatbot, but to demonstrate how AI capabilities can be incorporated into a **production-oriented enterprise architecture**.

---

# License

This project is currently maintained as a personal portfolio and engineering demonstration.

Commercial licensing and SaaS terms will be defined as the platform evolves.
