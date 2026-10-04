// Thin API layer. All requests go to /api (proxied by Vite in dev and by nginx in Docker).
export async function apiGet(path) {
  const r = await fetch(`/api${path}`);
  if (!r.ok) throw new Error(`Request failed (${r.status})`);
  return r.json();
}

export async function apiPost(path, form) {
  let r;
  try {
    r = await fetch(`/api${path}`, { method: "POST", body: form });
  } catch {
    throw new Error("Cannot reach the backend. Is the API container running?");
  }
  const j = await r.json().catch(() => null);
  if (!r.ok) {
    const d = j?.detail;
    throw new Error(Array.isArray(d) ? d.map((e) => e.msg).join("; ") : d || `Request failed (${r.status})`);
  }
  return j;
}

// Build the multipart form shared by the three restoration endpoints.
export function buildRestoreForm(file, ctl, extra = {}) {
  const f = new FormData();
  f.append("file", file);
  f.append("corruption", ctl.corruption);
  f.append("severity", ctl.severity);
  if (ctl.seed !== "" && ctl.seed != null) f.append("seed", ctl.seed);
  if (ctl.severity === "custom") {
    if (ctl.corruption === "salt_pepper") f.append("sp_prob", ctl.sp_prob);
    if (ctl.corruption === "blur") { f.append("blur_kernel", ctl.blur_kernel); f.append("blur_sigma", ctl.blur_sigma); }
    if (ctl.corruption === "occlusion") { f.append("occ_n", ctl.occ_n); f.append("occ_area", ctl.occ_area); }
  }
  Object.entries(extra).forEach(([k, v]) => f.append(k, v));
  return f;
}

export function downloadDataUri(uri, filename) {
  const a = document.createElement("a");
  a.href = uri; a.download = filename; document.body.appendChild(a); a.click(); a.remove();
}
