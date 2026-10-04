import { useEffect, useState } from "react";
import { apiGet } from "./api.js";
import Universal from "./pages/Universal.jsx";
import HardRouted from "./pages/HardRouted.jsx";
import SoftMoE from "./pages/SoftMoE.jsx";
import FaceToSketch from "./pages/FaceToSketch.jsx";

const TABS = [
  ["universal", "Universal Restoration", "Task 1", Universal],
  ["hard", "Hard-Routed Restoration", "Task 2", HardRouted],
  ["soft", "Soft Mixture-of-Experts", "Task 3", SoftMoE],
  ["sketch", "Face-to-Sketch Generator", "Task 4", FaceToSketch],
];

function SystemStatus() {
  const [h, setH] = useState(null);
  const [down, setDown] = useState(false);
  useEffect(() => {
    const poll = () => apiGet("/health").then((x) => { setH(x); setDown(false); }).catch(() => setDown(true));
    poll(); const id = setInterval(poll, 10000); return () => clearInterval(id);
  }, []);
  return (
    <div className="mt-6 rounded-xl border border-slate-800 bg-slate-900/60 p-3 text-xs">
      <div className="mb-2 flex items-center gap-2 font-medium text-slate-300">
        <span className={`h-2 w-2 rounded-full ${down ? "bg-red-500" : "bg-emerald-400"}`} />
        {down ? "Backend offline" : "Backend online"}
      </div>
      {h && (<>
        <div className="mb-2 text-slate-500">ONNX Runtime {h.onnxruntime} · {h.providers[0]} · {h.models_ready}/{h.models_total} models</div>
        <ul className="space-y-0.5">
          {Object.entries(h.models).map(([k, m]) => (
            <li key={k} className="flex justify-between text-slate-400">
              <span>{k}</span><span className={m.available ? "text-emerald-400" : "text-red-400"}>{m.available ? `${m.size_mb} MB` : "missing"}</span>
            </li>))}
        </ul></>)}
    </div>);
}

export default function App() {
  const [tab, setTab] = useState("universal");
  const Page = TABS.find((t) => t[0] === tab)[3];
  return (
    <div className="min-h-screen bg-slate-950 text-slate-200 lg:flex">
      <aside className="border-b border-slate-800 p-4 lg:min-h-screen lg:w-72 lg:shrink-0 lg:border-b-0 lg:border-r">
        <h1 className="mb-4 text-lg font-semibold text-white">GenAI Studio</h1>
        <nav className="flex gap-2 overflow-x-auto lg:flex-col">
          {TABS.map(([id, label, task]) => (
            <button key={id} onClick={() => setTab(id)}
              className={`whitespace-nowrap rounded-xl px-3 py-2 text-left text-sm transition ${tab === id ? "bg-indigo-500 text-white" : "text-slate-300 hover:bg-slate-800"}`}>
              <span className="block text-[10px] uppercase tracking-wider opacity-70">{task}</span>{label}
            </button>))}
        </nav>
        <div className="hidden lg:block"><SystemStatus /></div>
      </aside>
      <main className="flex-1 p-4 md:p-8"><Page key={tab} /></main>
    </div>);
}
