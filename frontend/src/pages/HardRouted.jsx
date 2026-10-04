import { useState } from "react";
import RestorationShell from "../components/RestorationShell.jsx";
import { Bars, Card, Segmented } from "../components/ui.jsx";

export default function HardRouted() {
  const [routing, setRouting] = useState("predicted");
  const controls = (
    <Card title="Routing mode">
      <Segmented value={routing} onChange={setRouting} options={[["predicted", "Predicted (classifier)"], ["oracle", "Oracle (known label)"]]} />
      <p className="mt-2 text-xs text-slate-500">Oracle uses the corruption you selected to pick the expert; it is unavailable for “Already corrupted”.</p>
    </Card>);
  return (
    <RestorationShell title="Hard-Routed Restoration"
      subtitle="A classifier detects the corruption and sends the image to exactly one specialist (clean images bypass restoration)."
      endpoint="/restore/hard" extraControls={controls} extraForm={{ routing }}
      renderRouting={(r) => (
        <Card title="Classifier & routing">
          <div className="grid gap-6 md:grid-cols-2">
            <Bars data={r.routing.probabilities} />
            <div className="space-y-2 text-sm">
              <Row k="Predicted corruption" v={r.routing.predicted} />
              <Row k="Selected expert" v={r.routing.routed_to} strong />
              <Row k="Routing mode" v={r.routing.mode} />
              {r.routing.oracle_label && <Row k="True label" v={r.routing.oracle_label} />}
              {r.routing.classifier_correct != null &&
                <Row k="Classifier" v={r.routing.classifier_correct ? "correct ✓" : "wrong ✗"} bad={!r.routing.classifier_correct} />}
            </div>
          </div>
        </Card>)} />
  );
}
const Row = ({ k, v, strong, bad }) => (
  <div className="flex justify-between border-b border-slate-800 pb-1">
    <span className="text-slate-400">{k}</span>
    <span className={`${strong ? "font-semibold text-indigo-300" : "text-slate-200"} ${bad ? "text-red-400" : ""}`}>{v}</span>
  </div>);
