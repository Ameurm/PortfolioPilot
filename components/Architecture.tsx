const systems = [
 { id:"01", title:"Enterprise Platform", tag:"CLOUD / DISTRIBUTED", desc:"Secure, resilient application platforms built around APIs, microservices, events, containers and cloud infrastructure.", flow:["Web / Mobile","API Gateway","Services","Event Bus","Data","Cloud"], tech:[".NET","C#","Kafka","RabbitMQ","Docker","Kubernetes","AWS","Azure"] },
 { id:"02", title:"RAG Intelligence", tag:"GENERATIVE AI", desc:"Document-to-answer pipelines that retrieve authoritative enterprise context before generating grounded responses.", flow:["Documents","Ingestion","Chunks","Embeddings","FAISS","Rerank","LLM"], tech:["Python","FastAPI","LangChain","FAISS","HuggingFace","Ollama","Llama 3.2"] },
 { id:"03", title:"Agentic Workflows", tag:"AI ENGINEERING", desc:"Controlled AI workflows with explicit tools, validation, guardrails and human escalation boundaries.", flow:["Request","Orchestrator","Agent","Tools","Validation","Response"], tech:["LangGraph","Tool Calling","Guardrails","MCP","Human-in-loop"] },
];
export default function Architecture() {
 return <section id="architecture" className="scroll-mt-20 py-16">
  <SectionHead eyebrow="ARCHITECTURE" title="Systems designed as products." text="Architecture is the connective tissue between business requirements, software, data, AI and infrastructure." />
  <div className="space-y-3">{systems.map(s => <article key={s.id} className="panel panel-hover rounded-xl p-5 sm:p-6">
   <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
    <div className="max-w-md"><div className="font-mono text-[9px] text-cyan-300">{s.id} / {s.tag}</div><h3 className="mt-2 text-lg font-bold text-white">{s.title}</h3><p className="mt-2 text-xs leading-6 text-slate-400">{s.desc}</p></div>
    <div className="min-w-0 flex-1 lg:max-w-3xl"><div className="overflow-x-auto"><div className="flex min-w-max items-center gap-1">{s.flow.map((x,i)=><div key={x} className="flex items-center gap-1"><span className="rounded-md border border-slate-700 bg-slate-900/70 px-2.5 py-2 font-mono text-[9px] text-slate-300">{x}</span>{i<s.flow.length-1&&<span className="text-cyan-500/60">→</span>}</div>)}</div></div><div className="mt-4 flex flex-wrap gap-1.5">{s.tech.map(t=><span key={t} className="rounded border border-slate-800 bg-slate-950/40 px-2 py-1 font-mono text-[9px] text-slate-500">{t}</span>)}</div></div>
   </div>
  </article>)}</div>
 </section>
}
function SectionHead({eyebrow,title,text}:{eyebrow:string;title:string;text:string}) { return <div className="mb-7"><div className="font-mono text-[9px] font-bold tracking-[.22em] text-cyan-300">{eyebrow}</div><h2 className="mt-2 text-2xl font-bold text-white sm:text-3xl">{title}</h2><p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">{text}</p></div>; }
