// POST /api/submit — every website form (quote, demo, support, privacy, sign-in requests…)
// lands here and is stored as a lead in Netlify Blobs for the admin dashboard.
import { json, text, readJSON, clientIp, geoOf, parseUA, sourceOf, submissionKey, day, sha } from "./_lib/core.mjs";
import { store } from "./_lib/store.mjs";

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
  return json({ ok: true, id: key.slice("submissions/".length).split("|")[0] }, 201);
};
