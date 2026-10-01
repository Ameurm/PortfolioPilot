"use client";

import { ChangeEvent, FormEvent, useState } from "react";

type Source = {
  source: string;
  chunk_id: number;
  category: string;
  access_level: string;
};

type Message = {
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
};

type RagResponse = {
  answer: string;
  retrieval: {
    initial_k: number;
    retrieved: number;
  };
  authorization: {
    authorized: number;
    filtered: number;
  };
  reranking: {
    enabled: boolean;
    type: string;
    documents_reranked: number;
    production_upgrade: string;
  };
  context: {
    selected: number;
    max_context: number;
  };
  model: string;
  embedding_model: string;
  vector_store: string;
  sources: Source[];
};

const suggestions = [
  "How did you implement RAG?",
  "What is your AI architecture?",
  "How did you use .NET and microservices?",
  "How did you solve production AI problems?"
];

export default function PortfolioChat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Welcome to the AI Architect system. Ask about RAG, .NET, cloud, distributed systems, security or documented project experience."
    }
  ]);

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [ragData, setRagData] = useState<RagResponse | null>(null);

  const [resumeName, setResumeName] = useState<string | null>(null);
  const [resumeUploading, setResumeUploading] = useState(false);

  async function sendMessage(
    event?: FormEvent,
    selected?: string
  ): Promise<void> {
    event?.preventDefault();

    const message = (selected ?? input).trim();

    if (!message || loading) {
      return;
    }

    setMessages((current) => [
      ...current,
      {
        role: "user",
        content: message
      }
    ]);

    setInput("");
    setLoading(true);
    setRagData(null);

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          message
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data: RagResponse = await response.json();

      setRagData(data);

      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content: data.answer,
          sources: data.sources
        }
      ]);
    } catch (error) {
      console.error("PortfolioPilot chat error:", error);

      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content:
            "AI backend unavailable. Check that the FastAPI service is running and try again."
        }
      ]);
    } finally {
      setLoading(false);
    }
  }

  async function handleResumeSelect(
    event: ChangeEvent<HTMLInputElement>
  ): Promise<void> {
    const file = event.target.files?.[0];

    if (!file) {
      return;
    }

    const allowedTypes = [
      "application/pdf",
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ];

    const isAllowedType =
      allowedTypes.includes(file.type) ||
      file.name.toLowerCase().endsWith(".pdf") ||
      file.name.toLowerCase().endsWith(".docx");

    if (!isAllowedType) {
      alert("Please upload a PDF or DOCX resume.");
      event.target.value = "";
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      alert("Resume must be smaller than 10 MB.");
      event.target.value = "";
      return;
    }

    setResumeUploading(true);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch("/api/resume/upload", {
        method: "POST",
        body: formData
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(
          `Resume upload failed: HTTP ${response.status} ${errorText}`
        );
      }

      const data = await response.json();

      console.log("Resume upload response:", data);

      setResumeName(file.name);

      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content:
            `Resume "${file.name}" has been uploaded and indexed. ` +
            "You can now ask questions about your experience, skills, projects, architecture, or technologies in the resume."
        }
      ]);
    } catch (error) {
      console.error("Resume upload error:", error);

      alert(
        "Resume upload failed. Please verify that the backend resume upload endpoint is available."
      );
    } finally {
      setResumeUploading(false);
      event.target.value = "";
    }
  }

  function clearChat(): void {
    setMessages([
      {
        role: "assistant",
        content:
          "Session reset. Ask about architecture, AI systems, RAG, .NET, cloud or documented experience."
      }
    ]);

    setRagData(null);
    setInput("");
  }

  return (
    <div className="overflow-hidden rounded-xl border border-slate-800 bg-[#091525] shadow-2xl shadow-black/20">
      <div className="grid lg:grid-cols-[210px_1fr]">
        <aside className="border-b border-slate-800 bg-[#081321] p-4 lg:border-b-0 lg:border-r">
          <div className="flex items-center gap-2">
            <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-cyan-400/10 font-mono text-cyan-300">
              ✦
            </span>

            <div>
              <div className="text-xs font-bold text-white">
                ARCHITECT COPILOT
              </div>

              <div className="font-mono text-[8px] text-slate-600">
                SESSION / GROUNDED
              </div>
            </div>
          </div>

          <div className="mt-6 space-y-2">
            <Mini label="MODEL" value="GPT-OSS 120B · Groq" />
            <Mini label="VECTOR STORE" value="FAISS" />
            <Mini label="EMBEDDINGS" value="all-MiniLM-L6-v2" />
            <Mini label="API" value="FastAPI" />
          </div>

          <div className="mt-6">
            <div className="font-mono text-[8px] tracking-[.18em] text-slate-600">
              RESUME KNOWLEDGE
            </div>

            <label
              htmlFor="resume-upload"
              className="mt-2 flex cursor-pointer flex-col rounded-md border border-dashed border-slate-700 bg-slate-950/20 p-3 transition hover:border-cyan-400/30 hover:bg-cyan-400/[.03]"
            >
              <span className="text-[10px] font-semibold text-slate-400">
                {resumeUploading
                  ? "INDEXING RESUME..."
                  : resumeName
                    ? "✓ RESUME READY"
                    : "📄 UPLOAD RESUME"}
              </span>

              <span className="mt-1 break-all font-mono text-[7px] text-slate-600">
                {resumeName ?? "PDF or DOCX · MAX 10 MB"}
              </span>

              <input
                id="resume-upload"
                type="file"
                accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                onChange={handleResumeSelect}
                disabled={resumeUploading}
                className="hidden"
              />
            </label>

            {resumeName && !resumeUploading && (
              <div className="mt-2 font-mono text-[7px] leading-4 text-emerald-400/70">
                Resume indexed successfully. Ask the assistant about your
                experience or skills.
              </div>
            )}
          </div>

          <div className="mt-6">
            <div className="font-mono text-[8px] tracking-[.18em] text-slate-600">
              PIPELINE STATUS
            </div>

            <div className="mt-2 space-y-1.5">
              {[
                "Semantic Retrieval",
                "Authorization",
                "Reranking",
                "Grounded Context"
              ].map((item) => (
                <div
                  key={item}
                  className="flex items-center gap-2 text-[9px] text-slate-500"
                >
                  <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
                  {item}
                </div>
              ))}
            </div>
          </div>
        </aside>

        <section className="flex min-h-[580px] min-w-0 flex-col">
          <header className="flex items-center justify-between border-b border-slate-800 px-4 py-3 sm:px-5">
            <div>
              <div className="text-xs font-bold text-white">
                AI Architect Assistant
              </div>

              <div className="mt-1 flex items-center gap-2 font-mono text-[8px] text-emerald-300">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
                CONNECTED / GROUNDED RAG
              </div>
            </div>

            <button
              type="button"
              onClick={clearChat}
              className="rounded-md border border-slate-700 px-2.5 py-1.5 font-mono text-[8px] text-slate-500 hover:text-white"
            >
              NEW CHAT
            </button>
          </header>

          <div className="flex-1 overflow-y-auto p-4 sm:p-6">
            <div className="mx-auto max-w-3xl space-y-4">
              {messages.map((message, index) => (
                <div
                  key={index}
                  className={`flex gap-2 ${
                    message.role === "user"
                      ? "justify-end"
                      : "justify-start"
                  }`}
                >
                  {message.role === "assistant" && (
                    <span className="mt-1 flex h-6 w-6 shrink-0 items-center justify-center rounded-md bg-cyan-400/10 font-mono text-[10px] text-cyan-300">
                      AI
                    </span>
                  )}

                  <div
                    className={
                      message.role === "user"
                        ? "max-w-[82%] rounded-xl rounded-br-sm bg-cyan-400 px-3.5 py-3 text-xs leading-6 text-slate-950"
                        : "max-w-[88%] rounded-xl rounded-bl-sm border border-slate-800 bg-[#0d1a2b] px-4 py-3 text-xs leading-6 text-slate-300"
                    }
                  >
                    {message.role === "assistant" && (
                      <div className="mb-2 font-mono text-[8px] tracking-widest text-cyan-300">
                        ARCHITECT / RESPONSE
                      </div>
                    )}

                    <div className="whitespace-pre-line">
                      {message.content}
                    </div>

                    {message.sources && message.sources.length > 0 ? (
                      <div className="mt-4 border-t border-slate-800 pt-3">
                        <div className="mb-2 font-mono text-[8px] tracking-widest text-slate-600">
                          SOURCES
                        </div>

                        <div className="space-y-1">
                          {message.sources.map((source, sourceIndex) => (
                            <div
                              key={`${source.source}-${source.chunk_id}-${sourceIndex}`}
                              className="flex items-center gap-2 rounded-md border border-slate-800 bg-slate-950/30 px-2.5 py-2 font-mono text-[8px] text-slate-500"
                            >
                              <span className="text-cyan-400">◇</span>

                              <span className="truncate">
                                {source.source}
                              </span>

                              <span className="ml-auto shrink-0">
                                {source.category} · chunk {source.chunk_id}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    ) : null}
                  </div>
                </div>
              ))}

              {loading && (
                <div className="flex gap-2">
                  <span className="flex h-6 w-6 items-center justify-center rounded-md bg-cyan-400/10 font-mono text-[9px] text-cyan-300">
                    AI
                  </span>

                  <div className="rounded-xl border border-slate-800 bg-[#0d1a2b] px-4 py-3 font-mono text-[9px] text-slate-500">
                    <span className="mr-2 inline-block h-1.5 w-1.5 animate-pulse rounded-full bg-cyan-400" />
                    EXECUTING RAG PIPELINE...
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="border-t border-slate-800 px-4 py-3">
            <div className="mb-2 overflow-x-auto">
              <div className="flex min-w-max gap-1.5">
                {suggestions.map((question) => (
                  <button
                    key={question}
                    type="button"
                    disabled={loading}
                    onClick={() => sendMessage(undefined, question)}
                    className="rounded-full border border-slate-800 px-2.5 py-1.5 font-mono text-[8px] text-slate-500 hover:border-cyan-400/30 hover:text-cyan-300 disabled:opacity-40"
                  >
                    {question}
                  </button>
                ))}
              </div>
            </div>

            <form
              onSubmit={sendMessage}
              className="flex items-center gap-2 rounded-lg border border-slate-700 bg-slate-950/30 p-1.5 focus-within:border-cyan-400/30"
            >
              <input
                id="portfolio-question"
                value={input}
                onChange={(event) => setInput(event.target.value)}
                disabled={loading}
                placeholder="Ask about RAG, .NET, AWS, architecture..."
                className="min-w-0 flex-1 bg-transparent px-2.5 py-2 text-xs text-white outline-none placeholder:text-slate-600"
              />

              <button
                type="submit"
                disabled={loading || !input.trim()}
                className="rounded-md bg-cyan-400 px-3 py-2 font-mono text-[9px] font-bold text-slate-950 disabled:opacity-30"
              >
                SEND →
              </button>
            </form>

            <div className="mt-2 text-center font-mono text-[7px] text-slate-700">
              ANSWERS ARE GROUNDED IN THE PORTFOLIO KNOWLEDGE BASE
            </div>
          </div>
        </section>
      </div>

      {ragData ? <Trace data={ragData} /> : null}
    </div>
  );
}

function Mini({
  label,
  value
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="rounded-md border border-slate-800 bg-slate-950/20 p-2.5">
      <div className="font-mono text-[7px] tracking-widest text-slate-600">
        {label}
      </div>

      <div className="mt-1 truncate text-[9px] font-semibold text-slate-400">
        {value}
      </div>
    </div>
  );
}

function Trace({ data }: { data: RagResponse }) {
  const steps: [string, string][] = [
    ["QUERY EMBEDDING", data.embedding_model],
    ["SEMANTIC RETRIEVAL", `${data.retrieval.retrieved} candidates`],
    [
      "AUTHORIZATION",
      `${data.authorization.authorized} authorized / ${data.authorization.filtered} filtered`
    ],
    ["RERANKING", data.reranking.type],
    ["FINAL CONTEXT", `${data.context.selected} chunks`],
    ["LLM", data.model]
  ];

  return (
    <div className="border-t border-cyan-400/10 bg-[#07111f] p-4 sm:p-5">
      <div className="flex items-center justify-between">
        <div>
          <div className="font-mono text-[9px] font-bold tracking-[.18em] text-cyan-300">
            RAG EXECUTION
          </div>

          <div className="mt-1 text-[10px] text-slate-600">
            Latest request telemetry
          </div>
        </div>

        <span className="rounded-full border border-emerald-400/15 bg-emerald-400/[.05] px-2 py-1 font-mono text-[7px] font-bold text-emerald-300">
          GROUNDED
        </span>
      </div>

      <div className="mt-4 grid gap-2 sm:grid-cols-2 xl:grid-cols-6">
        {steps.map(([title, value], index) => (
          <div
            key={title}
            className="relative rounded-lg border border-slate-800 bg-[#0b1728] p-3"
          >
            <div className="font-mono text-[7px] text-cyan-400">
              0{index + 1}
            </div>

            <div className="mt-1 text-[9px] font-bold text-slate-300">
              {title}
            </div>

            <div
              className="mt-1 truncate font-mono text-[8px] text-slate-600"
              title={value}
            >
              {value}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
