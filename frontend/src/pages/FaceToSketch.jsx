import { useState } from "react";
import { apiPost } from "../api.js";
import ImagePicker from "../components/ImagePicker.jsx";
import { Button, Card, ErrorBox, ImageCard, Segmented, Stat } from "../components/ui.jsx";

export default function FaceToSketch() {
  const [file, setFile] = useState(null);
  const [style, setStyle] = useState(1);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  const [res, setRes] = useState(null);       // single result
  const [all, setAll] = useState(null);       // all three styles

  const call = (s) => { const f = new FormData(); f.append("file", file); f.append("style", s); return apiPost("/sketch", f); };
  const run = async (compare) => {
    setBusy(true); setErr("");
    try {
      if (compare) { setAll(await Promise.all([1, 2, 3].map(call))); setRes(null); }
      else { setRes(await call(style)); setAll(null); }
    } catch (e) { setErr(e.message); } finally { setBusy(false); }
  };

  return (
    <div className="space-y-6">
      <header><h2 className="text-2xl font-semibold text-slate-100">Face-to-Sketch Generator</h2>
        <p className="text-sm text-slate-400">A style-conditioned U-Net (conditional GAN generator) turns a face photo into a sketch in one of three artist styles.</p></header>
      <div className="grid gap-6 xl:grid-cols-[360px_1fr]">
        <div className="space-y-4">
          <ImagePicker file={file} onFile={(f) => { setFile(f); setRes(null); setAll(null); }} webcam label="Face photo" />
          <Card title="Sketch style">
            <Segmented value={style} onChange={setStyle} options={[[1, "Style 1"], [2, "Style 2"], [3, "Style 3"]]} />
          </Card>
          <div className="flex gap-2">
            <Button className="flex-1" disabled={!file || busy} onClick={() => run(false)}>{busy ? "Generating…" : "Generate"}</Button>
            <Button variant="ghost" disabled={!file || busy} onClick={() => run(true)}>All styles</Button>
          </div>
          <ErrorBox msg={err} />
        </div>
        <div className="space-y-4">
          {!res && !all && <Card><p className="py-16 text-center text-sm text-slate-500">Upload or capture a face photo, pick a style and press Generate.</p></Card>}
          {res && (<>
            <Card title={`Result — Style ${res.style}`}>
              <div className="grid grid-cols-2 gap-4">
                <ImageCard title="Original photograph" src={res.images.original} />
                <ImageCard title="Generated sketch" src={res.images.sketch} filename={`sketch_style${res.style}.png`} />
              </div>
            </Card>
            <Stat label="Inference time" value={`${res.timing.inference_ms} ms`} hint="ONNX Runtime · CPU" />
          </>)}
          {all && (
            <Card title="Style comparison">
              <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
                <ImageCard title="Original" src={all[0].images.original} />
                {all.map((r) => <ImageCard key={r.style} title={`Style ${r.style} · ${r.timing.inference_ms} ms`} src={r.images.sketch} filename={`sketch_style${r.style}.png`} />)}
              </div>
            </Card>)}
        </div>
      </div>
    </div>
  );
}
