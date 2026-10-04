import RestorationShell from "../components/RestorationShell.jsx";
import { Bars, Card } from "../components/ui.jsx";

export default function SoftMoE() {
  return (
    <RestorationShell title="Soft Mixture-of-Experts Restoration"
      subtitle="A jointly trained gate assigns a continuous weight to the identity branch and every expert; the output is their weighted sum."
      endpoint="/restore/soft"
      renderRouting={(r) => (
        <Card title="Gate weights" right={<span className="text-xs text-slate-400">dominant: <b className="text-indigo-300">{r.routing.dominant}</b></span>}>
          <div className="grid gap-6 md:grid-cols-2">
            <Bars data={r.routing.weights} />
            <div className="space-y-3 text-xs text-slate-400">
              <p>Normalised entropy: <b className="text-slate-200">{r.routing.normalized_entropy}</b> (0 = a single expert, 1 = uniform).</p>
              <div className="flex h-8 overflow-hidden rounded-lg">
                {Object.entries(r.routing.weights).map(([k, v], i) => (
                  <div key={k} title={`${k}: ${(v * 100).toFixed(1)}%`} style={{ width: `${v * 100}%` }}
                    className={["bg-slate-500", "bg-rose-400", "bg-sky-400", "bg-amber-400"][i]} />))}
              </div>
              <p>Contribution strip: slate = clean, rose = salt & pepper, blue = blur, amber = occlusion.</p>
            </div>
          </div>
        </Card>)} />
  );
}
