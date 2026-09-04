const links = [
  ["overview", "Overview"],
  ["experience", "Experience"],
  ["architecture", "Architecture"],
  ["ai", "AI / RAG"],
  ["security", "Security"],
  ["contact", "Contact"],
];

export default function Navbar() {
  return (
    <>
      {/* Desktop Navigation */}
      <aside className="fixed inset-y-0 left-0 z-40 hidden w-[252px] border-r border-slate-800/70 bg-[#07111f]/95 px-5 py-6 backdrop-blur-xl lg:block">

        {/* Brand */}
        <a href="#overview" className="flex items-center gap-3">
          <span className="flex h-10 w-10 items-center justify-center rounded-xl border border-cyan-400/20 bg-cyan-400/10 font-mono text-xs font-bold text-cyan-300">
            AM
          </span>

          <div>
            <div className="text-sm font-bold text-white">
              AI ARCHITECT
            </div>

            <div className="font-mono text-[9px] tracking-[.2em] text-slate-500">
              PORTFOLIO.OS
            </div>
          </div>
        </a>

        {/* Navigation Label */}
        <div className="mb-3 mt-10 px-2 font-mono text-[9px] font-bold tracking-[.2em] text-slate-600">
          SYSTEM NAVIGATION
        </div>

        {/* Navigation */}
        <nav className="space-y-1">
          {links.map(([id, label], i) => (
            <a
              key={id}
              href={`#${id}`}
              className="group flex items-center gap-3 rounded-lg px-3 py-2.5 text-xs text-slate-400 transition hover:bg-white/[.04] hover:text-cyan-300"
            >
              <span className="w-5 font-mono text-[9px] text-slate-600 group-hover:text-cyan-400">
                {String(i + 1).padStart(2, "0")}
              </span>

              {label}
            </a>
          ))}
        </nav>

        {/* System Status */}
        <div className="absolute bottom-6 left-5 right-5 rounded-xl border border-emerald-400/10 bg-emerald-400/[.04] p-3">
          <div className="flex items-center gap-2 text-[10px] font-semibold text-emerald-300">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 shadow-[0_0_10px_#34d399]" />

            AI SYSTEM ONLINE
          </div>

          <div className="mt-2 font-mono text-[9px] text-slate-600">
            AI / RAG / AGENTS / CLOUD
          </div>

          <div className="mt-1 font-mono text-[8px] text-slate-700">
            LANGGRAPH · FASTAPI · .NET · K8S
          </div>
        </div>
      </aside>

      {/* Mobile Navigation */}
      <header className="sticky top-0 z-30 border-b border-slate-800/70 bg-[#07111f]/90 px-4 py-3 backdrop-blur-xl lg:hidden">

        <div className="flex items-center justify-between">
          <a
            href="#overview"
            className="font-mono text-xs font-bold text-cyan-300"
          >
            AM / AI ARCHITECT
          </a>

          <a
            href="#contact"
            className="rounded-lg bg-cyan-400 px-3 py-2 text-[10px] font-bold text-slate-950"
          >
            CONTACT
          </a>
        </div>

        <nav className="mt-3 flex gap-4 overflow-x-auto pb-1 font-mono text-[9px] text-slate-500">
          {links.map(([id, label]) => (
            <a
              key={id}
              href={`#${id}`}
              className="shrink-0 hover:text-cyan-300"
            >
              {label}
            </a>
          ))}
        </nav>
      </header>
    </>
  );
}