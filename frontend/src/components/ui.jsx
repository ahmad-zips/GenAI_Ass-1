import { downloadDataUri } from "../api.js";

export const Card = ({ title, children, right, className = "" }) => (
  <section className={`rounded-2xl border border-slate-800 bg-slate-900/60 p-4 ${className}`}>
    {(title || right) && (
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-sm font-semibold tracking-wide text-slate-300">{title}</h3>{right}
      </div>
    )}
    {children}
  </section>
);

export const Button = ({ children, variant = "primary", className = "", ...p }) => (
  <button
    {...p}
    className={`rounded-xl px-4 py-2 text-sm font-medium transition disabled:cursor-not-allowed disabled:opacity-40 ${
      variant === "primary" ? "bg-indigo-500 text-white hover:bg-indigo-400"
      : "border border-slate-700 text-slate-200 hover:bg-slate-800"} ${className}`}
  >{children}</button>
);

export const Segmented = ({ value, options, onChange }) => (
  <div className="flex flex-wrap gap-1 rounded-xl bg-slate-800/70 p-1">
    {options.map(([v, label]) => (
      <button key={v} onClick={() => onChange(v)}
        className={`rounded-lg px-3 py-1.5 text-xs font-medium transition ${
          value === v ? "bg-indigo-500 text-white" : "text-slate-300 hover:bg-slate-700"}`}>{label}</button>
    ))}
  </div>
);

export const Stat = ({ label, value, hint }) => (
  <div className="rounded-xl bg-slate-800/60 px-3 py-2">
    <div className="text-[11px] uppercase tracking-wider text-slate-400">{label}</div>
    <div className="text-lg font-semibold text-slate-100">{value}</div>
    {hint && <div className="text-[11px] text-slate-500">{hint}</div>}
  </div>
);

export const ImageCard = ({ title, src, filename }) => (
  <figure className="space-y-2">
    <div className="aspect-square overflow-hidden rounded-xl border border-slate-800 bg-slate-950">
      {src ? <img src={src} alt={title} className="pixel h-full w-full object-contain" />
           : <div className="flex h-full items-center justify-center text-xs text-slate-600">not available</div>}
    </div>
    <figcaption className="flex items-center justify-between text-xs text-slate-400">
      <span>{title}</span>
      {src && filename && <button className="text-indigo-300 hover:underline" onClick={() => downloadDataUri(src, filename)}>Download</button>}
    </figcaption>
  </figure>
);

// Horizontal bars for probabilities / routing weights. The largest entry is highlighted.
export const Bars = ({ data }) => {
  const entries = Object.entries(data);
  const max = Math.max(...entries.map(([, v]) => v));
  return (
    <div className="space-y-2">
      {entries.map(([k, v]) => (
        <div key={k}>
          <div className="mb-1 flex justify-between text-xs">
            <span className={v === max ? "font-semibold text-indigo-300" : "text-slate-400"}>{k}</span>
            <span className="tabular-nums text-slate-300">{(v * 100).toFixed(1)}%</span>
          </div>
          <div className="h-2.5 overflow-hidden rounded-full bg-slate-800">
            <div className={`h-full rounded-full transition-all ${v === max ? "bg-indigo-400" : "bg-slate-500"}`}
                 style={{ width: `${Math.max(v * 100, 0.5)}%` }} />
          </div>
        </div>
      ))}
    </div>
  );
};

export const ErrorBox = ({ msg }) => msg ? (
  <div className="rounded-xl border border-red-900 bg-red-950/50 px-3 py-2 text-sm text-red-300">{msg}</div>) : null;
