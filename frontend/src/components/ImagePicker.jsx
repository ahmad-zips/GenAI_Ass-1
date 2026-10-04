import { useEffect, useRef, useState } from "react";
import { Button, Card } from "./ui.jsx";

export default function ImagePicker({ file, onFile, webcam = false, label = "Input image" }) {
  const [url, setUrl] = useState(null);
  const [samples, setSamples] = useState([]);
  const [cam, setCam] = useState(false);
  const [camErr, setCamErr] = useState("");
  const videoRef = useRef(null);
  const streamRef = useRef(null);

  useEffect(() => {
    if (!file) { setUrl(null); return; }
    const u = URL.createObjectURL(file); setUrl(u);
    return () => URL.revokeObjectURL(u);
  }, [file]);

  useEffect(() => {
    fetch("/samples/manifest.json").then((r) => r.json()).then((m) => Array.isArray(m) && setSamples(m)).catch(() => {});
  }, []);

  const stopCam = () => { streamRef.current?.getTracks().forEach((t) => t.stop()); streamRef.current = null; setCam(false); };
  useEffect(() => () => streamRef.current?.getTracks().forEach((t) => t.stop()), []);

  const startCam = async () => {
    setCamErr("");
    try {
      streamRef.current = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "user" } });
      setCam(true);
    } catch { setCamErr("Camera unavailable or permission denied."); }
  };
  useEffect(() => { if (cam && videoRef.current) videoRef.current.srcObject = streamRef.current; }, [cam]);

  const capture = () => {
    const v = videoRef.current; if (!v?.videoWidth) return;
    const c = document.createElement("canvas"); c.width = v.videoWidth; c.height = v.videoHeight;
    c.getContext("2d").drawImage(v, 0, 0);
    c.toBlob((b) => { onFile(new File([b], "webcam.png", { type: "image/png" })); stopCam(); }, "image/png");
  };

  const loadSample = async (name) => {
    const b = await (await fetch(`/samples/${name}`)).blob();
    onFile(new File([b], name, { type: b.type || "image/jpeg" }));
  };

  const onDrop = (e) => { e.preventDefault(); const f = e.dataTransfer.files?.[0]; if (f) onFile(f); };

  return (
    <Card title={label}>
      {cam ? (
        <div className="space-y-2">
          <video ref={videoRef} autoPlay playsInline muted className="w-full rounded-xl bg-black" />
          <div className="flex gap-2"><Button onClick={capture}>Capture</Button><Button variant="ghost" onClick={stopCam}>Cancel</Button></div>
        </div>
      ) : (
        <label onDragOver={(e) => e.preventDefault()} onDrop={onDrop}
          className="flex aspect-video cursor-pointer items-center justify-center overflow-hidden rounded-xl border-2 border-dashed border-slate-700 bg-slate-950 text-sm text-slate-500 hover:border-indigo-400">
          {url ? <img src={url} alt="input" className="h-full w-full object-contain" /> : "Drop an image here or click to upload"}
          <input type="file" accept="image/jpeg,image/png,image/webp" className="hidden"
                 onChange={(e) => e.target.files?.[0] && onFile(e.target.files[0])} />
        </label>
      )}
      {webcam && !cam && <Button variant="ghost" className="mt-3" onClick={startCam}>Use webcam</Button>}
      {camErr && <p className="mt-2 text-xs text-red-400">{camErr}</p>}
      {samples.length > 0 && (
        <div className="mt-3 flex flex-wrap gap-2">
          {samples.map((s) => (
            <button key={s} onClick={() => loadSample(s)} className="h-12 w-12 overflow-hidden rounded-lg border border-slate-700 hover:border-indigo-400">
              <img src={`/samples/${s}`} alt={s} className="h-full w-full object-cover" />
            </button>))}
        </div>)}
    </Card>
  );
}
