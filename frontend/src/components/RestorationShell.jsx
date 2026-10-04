import { useState } from "react";
import { apiPost, buildRestoreForm } from "../api.js";
import ImagePicker from "./ImagePicker.jsx";
import CorruptionControls, { defaultControls } from "./CorruptionControls.jsx";
import { Button, Card, ErrorBox, ImageCard, Stat } from "./ui.jsx";

// Shared layout for the three restoration workspaces (universal / hard-routed / soft-MoE).
export default function RestorationShell({ title, subtitle, endpoint, extraControls = null, extraForm = {}, renderRouting }) {
  const [file, setFile] = useState(null);
  const [ctl, setCtl] = useState(defaultControls);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  const [res, setRes] = useState(null);

  const run = async () => {
    setBusy(true); setErr("");
    try { setRes(await apiPost(endpoint, buildRestoreForm(file, ctl, extraForm))); }
    catch (e) { setErr(e.message); setRes(null); }
    finally { setBusy(false); }
  };

  const m = res?.metrics, t = res?.timing;
  return (
    <div className="space-y-6">
      <header><h2 className="text-2xl font-semibold text-slate-100">{title}</h2><p className="text-sm text-slate-400">{subtitle}</p></header>
      <div className="grid gap-6 xl:grid-cols-[360px_1fr]">
        <div className="space-y-4">
          <ImagePicker file={file} onFile={(f) => { setFile(f); setRes(null); }} />
          <CorruptionControls value={ctl} onChange={setCtl} />
          {extraControls}
          <Button className="w-full" disabled={!file || busy} onClick={run}>{busy ? "Running…" : "Restore"}</Button>
          <ErrorBox msg={err} />
        </div>

        <div className="space-y-4">
          {!res ? (
            <Card><p className="py-16 text-center text-sm text-slate-500">Upload an image, choose a corruption and press Restore.</p></Card>
          ) : (<>
            <Card title="Results">
              <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
                <ImageCard title="Original (target)" src={res.images.original} />
                <ImageCard title="Model input" src={res.images.input} />
                <ImageCard title="Restored" src={res.images.restored} filename={`restored_${res.workspace}.png`} />
                <ImageCard title="Absolute error map" src={res.images.error_map} />
              </div>
              <p className="mt-3 text-[11px] text-slate-500">Error map reference: {m.error_map_reference}. Brighter = larger error.</p>
            </Card>
            {renderRouting?.(res)}
            <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
              <Stat label="Inference time" value={`${t.inference_ms} ms`} hint={t.classifier_ms != null ? `clf ${t.classifier_ms} + expert ${t.expert_ms}` : "ONNX Runtime · CPU"} />
              {m.psnr_restored != null && <Stat label="PSNR restored" value={`${m.psnr_restored} dB`} hint={`input ${m.psnr_input} dB`} />}
              {m.mae_restored != null && <Stat label="MAE restored" value={m.mae_restored} hint={`input ${m.mae_input}`} />}
            </div>
            <Card title="Applied corruption settings">
              <pre className="overflow-x-auto text-xs text-slate-300">{JSON.stringify(res.settings, null, 2)}</pre>
            </Card>
          </>)}
        </div>
      </div>
    </div>
  );
}
