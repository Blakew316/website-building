// POST /api/submit — every website form (quote, demo, support, privacy, sign-in requests…)
// lands here and is stored as a lead in Netlify Blobs for the admin dashboard.
import { json, text, readJSON, clientIp, geoOf, parseUA, sourceOf, submissionKey, day, sha } from "./_lib/core.mjs";
import { store } from "./_lib/store.mjs";

const env = (k) => (globalThis.Netlify?.env?.get(k) ?? process.env[k] ?? "").trim();

// Email the owner directly when an email API key is present (Resend: RESEND_API_KEY, optional MAIL_FROM).
// Netlify Forms notifications cover the no-key case; this adds a second, instant channel.
const notify = async (sub) => {
  const to = env("NOTIFY_EMAIL"), key = env("RESEND_API_KEY");
  if (!to || !key) return;
  const rows = Object.entries(sub.fields).map(([k, v]) => `<tr><td style="padding:6px 12px 6px 0;color:#6b7890;text-transform:capitalize">${k.replace(/_/g, " ")}</td><td style="padding:6px 0;color:#0b1f3f"><strong>${String(v).replace(/[<>&]/g, (c) => ({ "<": "&lt;", ">": "&gt;", "&": "&amp;" }[c]))}</strong></td></tr>`).join("");
  const html = `<div style="font-family:-apple-system,Helvetica,Arial,sans-serif;max-width:560px"><h2 style="color:#0b1f3f;margin:0 0 4px">New ${sub.form} submission</h2><p style="color:#6b7890;margin:0 0 16px">${new Date(sub.ts).toLocaleString("en-US", { timeZone: "America/Chicago" })} · ${sub.page || ""} · ${[sub.city, sub.region].filter(Boolean).join(", ")} · source: ${sub.source}</p><table style="border-collapse:collapse;font-size:15px">${rows}</table><p style="margin-top:18px"><a href="${(env("URL") || "https://www.charliecompanymedia.com")}/admin/#leads" style="color:#1e4b8f">Open in the dashboard</a></p></div>`;
  const res = await fetch("https://api.resend.com/emails", { method: "POST", headers: { Authorization: `Bearer ${key}`, "Content-Type": "application/json" },
    body: JSON.stringify({ from: env("MAIL_FROM") || "Charlie Company Media <onboarding@resend.dev>", to: [to], reply_to: sub.email || undefined, subject: `New ${sub.form} lead: ${sub.name || sub.email || sub.phone || "website visitor"}`, html }) });
  if (!res.ok) throw new Error(`resend ${res.status}: ${await res.text()}`);
};

export default async (req, context) => {
  if (req.method !== "POST") return text("Method not allowed", 405);
  let body = await readJSON(req);
  if (!body) {
    // also accept classic form posts
    try { const fd = await req.formData(); const fields = {}; fd.forEach((v, k) => { fields[k] = String(v); }); body = { form: fields.form, fields }; } catch { body = null; }
  }
  if (!body || typeof body !== "object") return json({ ok: false, error: "bad request" }, 400);
  const fields = body.fields && typeof body.fields === "object" ? body.fields : {};
  if (fields.website) return json({ ok: true }, 202); // honeypot filled → silently accept
  const clean = {};
  for (const [k, v] of Object.entries(fields)) { if (k === "website" || k === "form") continue; clean[String(k).slice(0, 40)] = String(v ?? "").slice(0, 4000); }
  if (!Object.keys(clean).length) return json({ ok: false, error: "empty" }, 400);
  const ts = Date.now();
  const ua = parseUA(req.headers.get("user-agent") || "");
  const name = clean.name || [clean.first_name, clean.last_name].filter(Boolean).join(" ") || clean.business || clean.company || "";
  const sub = { ts, day: day(ts), form: String(body.form || fields.form || "form").slice(0, 24), name, email: clean.email || "", phone: clean.phone || "", business: clean.business || clean.company || "", fields: clean, page: String(body.page || "").slice(0, 200), ref: String(body.ref || "").slice(0, 300), source: sourceOf(String(body.ref || ""), body.utm || {}, req.headers.get("host") || ""), utm: body.utm || {}, sid: String(body.sid || "").slice(0, 32), vid: String(body.vid || "").slice(0, 32), device: ua.device, browser: ua.browser, os: ua.os, ...geoOf(context), ip_hash: sha(clientIp(req, context)).slice(0, 16), status: "new", notes: "", updated: ts };
  const key = submissionKey(sub);
  await store("leads").setJSON(key, sub);
  notify(sub).catch((e) => console.error("notify failed", e));
  return json({ ok: true, id: key.slice("submissions/".length).split("|")[0] }, 201);
};
