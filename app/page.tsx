import Navbar from "@/components/Navbar";
import Hero from "@/components/Hero";
import Architecture from "@/components/Architecture";
import Experience from "@/components/Experience";
import AISection from "@/components/AISection";
import Security from "@/components/Security";
import Contact from "@/components/Contact";

export default function Home() {
  return (
    <main className="min-h-screen bg-[#07111f] text-slate-100">
      <Navbar />
      <div className="lg:pl-[252px]">
        <div className="mx-auto max-w-[1500px] px-4 pb-16 sm:px-6 lg:px-8">
          <Hero />
          <AISection />
          <Architecture />
          <Experience />
          <Security />
          <Contact />
        </div>
      </div>
    </main>
  );
}
