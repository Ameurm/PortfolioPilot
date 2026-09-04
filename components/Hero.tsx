function Metric({
  value,
  label,
}: {
  value: string;
  label: string;
}) {
  return (
    <div className="panel rounded-xl p-4">
      <div className="font-mono text-2xl font-bold text-white">
        {value}
      </div>
      <div className="mt-1 text-[10px] uppercase tracking-wider text-slate-500">
        {label}
      </div>
    </div>
  );
}

const capabilities = [
  ".NET / C#",
  "Python / FastAPI",
  "AI / GenAI / RAG",
  "AWS / Azure",
  "Kubernetes",
  "Microservices",
  "Event-Driven",
  "API Architecture",
];

export default function Hero() {
  return (
    <section
      id="overview"
      className="dashboard-grid scanline relative scroll-mt-20 overflow-hidden rounded-b-2xl border-x border-b border-slate-800/70 px-5 py-10 sm:px-8 lg:py-16"
    >
      {/* Ambient AI glow */}
      <div className="pointer-events-none absolute -right-40 -top-40 h-96 w-96 rounded-full bg-cyan-400/10 blur-3xl" />
      <div className="pointer-events-none absolute -bottom-40 left-1/3 h-80 w-80 rounded-full bg-violet-500/5 blur-3xl" />

      <div className="relative grid gap-12 xl:grid-cols-[1fr_430px] xl:items-end">

        {/* Main Hero */}
        <div>
          {/* Status */}
          <div className="mb-6 flex flex-wrap items-center gap-3 font-mono text-[9px] uppercase tracking-[.18em]">
            <span className="rounded-full border border-emerald-400/20 bg-emerald-400/[.06] px-3 py-1.5 text-emerald-300">
              <span className="mr-1.5">●</span>
              Available for architecture roles
            </span>

            <span className="text-slate-600">
              SYSTEM ID: AM-ARCH-01
            </span>
          </div>

          {/* Eyebrow */}
          <p className="font-mono text-[10px] font-bold tracking-[.25em] text-cyan-300">
            PRINCIPAL SOFTWARE ARCHITECT · AI ENGINEER
          </p>

          {/* Headline */}
          <h1 className="mt-4 max-w-5xl text-4xl font-bold leading-tight tracking-tight text-white sm:text-6xl lg:text-7xl">
            Designing enterprise systems with{" "}
            <span className="text-cyan-300">
              AI at the core.
            </span>
          </h1>

          {/* Description */}
          <p className="mt-7 max-w-3xl text-sm leading-7 text-slate-400 sm:text-base">
            Ameur Mezaache — 18+ years engineering enterprise applications,
            distributed systems, cloud platforms, APIs, microservices and
            production-oriented AI solutions.
          </p>

          {/* Capability Tags */}
          <div className="mt-8 flex max-w-4xl flex-wrap gap-2">
            {capabilities.map((capability) => (
              <span
                key={capability}
                className="rounded-md border border-slate-700 bg-slate-900/50 px-2.5 py-1.5 font-mono text-[10px] text-slate-400 transition hover:border-cyan-400/30 hover:text-cyan-300"
              >
                {capability}
              </span>
            ))}
          </div>

          {/* Actions */}
          <div className="mt-9 flex flex-wrap gap-3">
            <a
              href="#ai"
              className="rounded-lg bg-cyan-400 px-5 py-3 text-xs font-bold text-slate-950 shadow-[0_0_25px_rgba(34,211,238,.12)] transition hover:bg-cyan-300"
            >
              Launch AI Assistant →
            </a>

            <a
              href="#architecture"
              className="rounded-lg border border-slate-700 px-5 py-3 text-xs font-semibold text-slate-300 transition hover:border-cyan-400/30 hover:bg-white/[.03] hover:text-cyan-300"
            >
              View Architecture
            </a>

            <a
              href="#experience"
              className="rounded-lg border border-slate-800 px-5 py-3 text-xs font-semibold text-slate-500 transition hover:border-slate-700 hover:text-slate-300"
            >
              Experience
            </a>
          </div>
        </div>

        {/* Architecture Metrics */}
        <div className="grid grid-cols-3 gap-2">
          <Metric value="18+" label="Years" />
          <Metric value="AI" label="GenAI / RAG" />
          <Metric value=".NET" label="Enterprise" />

          <div className="panel col-span-3 rounded-xl p-4">
            <div className="flex items-center justify-between">
              <span className="font-mono text-[9px] uppercase tracking-[.2em] text-slate-500">
                Architecture Focus
              </span>

              <span className="font-mono text-[9px] text-emerald-300">
                ONLINE
              </span>
            </div>

            <div className="mt-3 grid grid-cols-2 gap-2">
              {[
                "Cloud Native",
                "Distributed Systems",
                "Agentic AI",
                "Enterprise APIs",
                "RAG Platforms",
                "DevSecOps",
              ].map((item) => (
                <div
                  key={item}
                  className="rounded-md border border-slate-800 bg-slate-950/40 px-3 py-2 font-mono text-[9px] text-slate-500"
                >
                  {item}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}