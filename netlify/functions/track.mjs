// POST /api/track — first-party analytics beacon from main.js. Stores one blob per event.
import { json, text, readJSON, clientIp, geoOf, parseUA, sourceOf, eventKey, day, enc, sha } from "./_lib/core.mjs";
import { store } from "./_lib/store.mjs";

const TYPES = new Set(["pageview", "engagement", "cta_click", "call_click", "outbound", "search", "form_start", "form_step", "form_submit", "custom"]);

export default async (req, context) => {
  if (req.method !== "POST") return text("Method not allowed", 405);
  const body = await readJSON(req);
  if (!body || typeof body !== "object") return json({ ok: false, error: "bad request" }, 400);
  const ua = parseUA(req.headers.get("user-agent") || "");
  if (ua.bot) return json({ ok: true, ignored: "bot" }, 202);
  const type = TYPES.has(body.type) ? body.type : "custom";
  const ts = Date.now();
  const geo = geoOf(context);
  const host = req.headers.get("host") || "";
  const path = String(body.path || "/").slice(0, 200);
  const source = sourceOf(String(body.ref || ""), body.utm || {}, host);
  let extra = "";
  if (type === "engagement") extra = `s${Math.max(0, Math.min(100, Number(body.data?.scroll) || 0))}t${Math.max(0, Number(body.data?.seconds) || 0)}`;
  else if (type === "cta_click" || type === "search" || type === "outbound") extra = String(body.data?.label || body.data?.q || body.data?.href || "").slice(0, 60);
  else if (type.startsWith("form")) extra = String(body.data?.form || "").slice(0, 30);
  const ev = { ts, day: day(ts), type, path, title: String(body.title || "").slice(0, 160), ref: String(body.ref || "").slice(0, 300), source, utm: body.utm || {}, sid: String(body.sid || "").slice(0, 32), vid: String(body.vid || "").slice(0, 32), device: ua.device, browser: ua.browser, os: ua.os, lang: String(body.lang || "").slice(0, 12), screen: [Number(body.sw) || 0, Number(body.sh) || 0], ...geo, ip_hash: sha(clientIp(req, context)).slice(0, 16), data: body.data && typeof body.data === "object" ? body.data : {}, extra };
  await store("analytics").setJSON(eventKey(ev), ev);
  return json({ ok: true }, 202);
};
