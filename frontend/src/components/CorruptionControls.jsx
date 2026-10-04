import { Card, Segmented } from "./ui.jsx";

export const defaultControls = {
  corruption: "salt_pepper", severity: "medium", seed: "",
  sp_prob: 0.08, blur_kernel: 5, blur_sigma: 1.5, occ_n: 2, occ_area: 0.2,
};

const Slider = ({ label, value, min, max, step, onChange, fmt = (v) => v }) => (
  <label className="block text-xs text-slate-400">
    <div className="mb-1 flex justify-between"><span>{label}</span><span className="text-slate-200">{fmt(value)}</span></div>
    <input type="range" min={min} max={max} step={step} value={value} onChange={(e) => onChange(Number(e.target.value))} className="w-full accent-indigo-400" />
  </label>
);

export default function CorruptionControls({ value, onChange }) {
  const set = (patch) => onChange({ ...value, ...patch });
  const applies = value.corruption !== "none" && value.corruption !== "already_corrupted";
  return (
    <Card title="Corruption">
      <div className="space-y-3">
        <Segmented value={value.corruption} onChange={(v) => set({ corruption: v })} options={[
          ["none", "Clean"], ["salt_pepper", "Salt & pepper"], ["blur", "Gaussian blur"], ["occlusion", "Occlusion"], ["already_corrupted", "Already corrupted"]]} />
        {value.corruption === "already_corrupted" && (
          <p className="text-xs text-slate-500">The uploaded image is used as-is (no ground truth, so the error map compares output to input).</p>)}
        {applies && (<>
          <Segmented value={value.severity} onChange={(v) => set({ severity: v })}
            options={[["low", "Low"], ["medium", "Medium"], ["high", "High"], ["custom", "Custom"]]} />
          {value.severity === "custom" && (
            <div className="space-y-3 rounded-xl bg-slate-800/40 p-3">
              {value.corruption === "salt_pepper" && <Slider label="Noise probability" min={0.01} max={0.3} step={0.01} value={value.sp_prob} onChange={(v) => set({ sp_prob: v })} />}
              {value.corruption === "blur" && (<>
                <Slider label="Kernel size" min={3} max={15} step={2} value={value.blur_kernel} onChange={(v) => set({ blur_kernel: v })} />
                <Slider label="Sigma" min={0.3} max={4} step={0.1} value={value.blur_sigma} onChange={(v) => set({ blur_sigma: v })} /></>)}
              {value.corruption === "occlusion" && (<>
                <Slider label="Rectangles" min={1} max={3} step={1} value={value.occ_n} onChange={(v) => set({ occ_n: v })} />
                <Slider label="Area covered" min={0.05} max={0.5} step={0.01} value={value.occ_area} onChange={(v) => set({ occ_area: v })} fmt={(v) => `${Math.round(v * 100)}%`} /></>)}
            </div>)}
          <label className="flex items-center gap-2 text-xs text-slate-400">Seed
            <input type="number" placeholder="random" value={value.seed} onChange={(e) => set({ seed: e.target.value })}
              className="w-28 rounded-lg border border-slate-700 bg-slate-950 px-2 py-1 text-slate-200" />
          </label>
        </>)}
      </div>
    </Card>
  );
}
