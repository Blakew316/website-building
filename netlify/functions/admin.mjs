// /api/admin/* — password-protected admin API behind the /admin/ dashboard.
//   POST login | POST logout | GET status
//   GET overview?days=30            aggregates (daily rollups cached in Blobs)
//   GET submissions?q=&status=&form=&cursor=&limit=   leads, newest first
//   GET submission/:id | PATCH submission/:id {status,notes} | DELETE submission/:id
//   GET events?day=YYYY-MM-DD&type=&limit=            raw activity feed
//   GET export.csv?days=365          leads as CSV
import { json, text, readJSON, clientIp, parseEventKey, parseSubmissionKey, emptyAgg, foldEvent, finishAgg, day, adminPassword, passwordMatches, makeSession, sessionCookie, isAuthed, csvCell } from "./_lib/core.mjs";
import { store, listAll, mapLimit } from "./_lib/store.mjs";

const MAX_ATTEMPTS = 8, WINDOW_MS = 15 * 60 * 1000;

const route = (req) => {
  const p = new URL(req.url).pathname;
  const i = p.indexOf("/admin");
  return (i >= 0 ? p.slice(i + 6) : p).replace(/^\/+|\/+$/g, "");
};

export default async (req, context) => {
  const sub = route(req);
  const url = new URL(req.url);
  const auth = store("auth");

  if (sub === "status") return json({ configured: Boolean(adminPassword()), authed: isAuthed(req), context: globalThis.Netlify?.context?.deploy?.context || "" });

  if (sub === "login") {
    if (req.method !== "POST") return text("Method not allowed", 405);
    if (!adminPassword()) return json({ ok: false, error: "ADMIN_PASSWORD is not set in the site's environment variables." }, 503);
    const ip = clientIp(req, context) || "unknown";
    const key = `attempts/${ip.replace(/[^a-zA-Z0-9.:]/g, "_")}`;
    const rec = (await auth.get(key, { type: "json" })) || { n: 0, first: Date.now() };
    if (Date.now() - rec.first > WINDOW_MS) { rec.n = 0; rec.first = Date.now(); }
    if (rec.n >= MAX_ATTEMPTS) return json({ ok: false, error: "Too many attempts. Try again in 15 minutes." }, 429);
    const body = await readJSON(req);
    if (!passwordMatches(body?.password)) {
      rec.n++; await auth.setJSON(key, rec);
      return json({ ok: false, error: "Incorrect password.", remaining: MAX_ATTEMPTS - rec.n }, 401);
    }
    if (rec.n) await auth.delete(key);
    return json({ ok: true }, 200, { "Set-Cookie": sessionCookie(makeSession()) });
  }
  if (sub === "logout") return json({ ok: true }, 200, { "Set-Cookie": sessionCookie("", 0) });

  if (!isAuthed(req)) return json({ ok: false, error: "unauthorized" }, 401);

  const analytics = store("analytics"), leads = store("leads");

  // ---- overview ----
  if (sub === "overview") {
    const days = Math.max(1, Math.min(365, Number(url.searchParams.get("days")) || 30));
    const today = day();
    const rollupFor = async (d) => {
      if (d !== today) { const cached = await analytics.get(`rollups/${d}`, { type: "json" }); if (cached) return cached; }
      const keys = await listAll(analytics, `events/${d}/`);
      const agg = emptyAgg();
      for (const k of keys) { const ev = parseEventKey(k); if (ev) foldEvent(agg, ev); }
      const r = finishAgg(agg, d);
      if (d !== today) await analytics.setJSON(`rollups/${d}`, r);
      return r;
    };
    const range = (n, offset = 0) => { const out = []; for (let i = n - 1 + offset; i >= offset; i--) out.push(day(Date.now() - i * 86400000)); return out; };
    const cur = await mapLimit(range(days), 6, rollupFor);
    const prev = await mapLimit(range(days, days), 6, rollupFor);
    // leads in range (from keys only; cheap)
    const subKeys = (await listAll(leads, "submissions/")).map(parseSubmissionKey).filter(Boolean);
    const since = Date.now() - days * 86400000, sincePrev = since - days * 86400000;
    const leadsCur = subKeys.filter((s) => s.ts >= since), leadsPrev = subKeys.filter((s) => s.ts >= sincePrev && s.ts < since);
    const recent = await mapLimit(subKeys.slice(0, 8), 8, async (s) => ({ ...s, ...((await leads.get(s.key, { type: "json" })) || {}) }));
    const statusCounts = {};
    for (const r of await mapLimit(subKeys.slice(0, 300), 10, (s) => leads.get(s.key, { type: "json" }))) if (r) statusCounts[r.status || "new"] = (statusCounts[r.status || "new"] || 0) + 1;
    const merge = (list) => {
      const m = { pages: {}, sources: {}, countries: {}, devices: {}, ctas: {}, entry: {} }; const hours = new Array(24).fill(0);
      const t = { pageviews: 0, sessions: 0, visitors: 0, calls: 0, outbound: 0, searches: 0, formStarts: 0, formSubmits: 0, scrollSum: 0, scrollN: 0, secSum: 0, secN: 0 };
      for (const r of list) {
        t.pageviews += r.pageviews; t.sessions += r.sessions; t.visitors += r.visitors; t.calls += r.calls; t.outbound += r.outbound; t.searches += r.searches; t.formStarts += r.formStarts; t.formSubmits += r.formSubmits;
        if (r.avgScroll) { t.scrollSum += r.avgScroll * r.sessions; t.scrollN += r.sessions; }
        if (r.avgSeconds) { t.secSum += r.avgSeconds * r.sessions; t.secN += r.sessions; }
        for (const k of Object.keys(m)) for (const [name, n] of r[k] || []) m[k][name] = (m[k][name] || 0) + n;
        (r.hours || []).forEach((n, i) => { hours[i] += n; });
      }
      const top = (o, n = 25) => Object.entries(o).sort((a, b) => b[1] - a[1]).slice(0, n).map(([name, count]) => ({ name, count }));
      return { ...t, avgScroll: t.scrollN ? Math.round(t.scrollSum / t.scrollN) : 0, avgSeconds: t.secN ? Math.round(t.secSum / t.secN) : 0, pages: top(m.pages, 40), sources: top(m.sources), countries: top(m.countries), devices: top(m.devices), ctas: top(m.ctas), entry: top(m.entry), hours };
    };
    const daily = cur.map((r, i) => ({ day: r.day, pageviews: r.pageviews, visitors: r.visitors, sessions: r.sessions, leads: leadsCur.filter((s) => s.ts >= since && day(s.ts) === r.day).length }));
    // live: sessions with a pageview in the last 5 minutes (today's keys)
    const liveKeys = await listAll(analytics, `events/${today}/`);
    const live = new Set(); const cutoff = Date.now() - 5 * 60000;
    for (const k of liveKeys) { const ev = parseEventKey(k); if (ev && ev.ts >= cutoff && ev.sid) live.add(ev.sid); }
    return json({ days, generated: Date.now(), totals: { ...merge(cur), leads: leadsCur.length }, previous: { ...merge(prev), leads: leadsPrev.length }, daily, live: live.size, leadsTotal: subKeys.length, statusCounts, recentLeads: recent, forms: Object.entries(leadsCur.reduce((o, s) => (o[s.form] = (o[s.form] || 0) + 1, o), {})).map(([name, count]) => ({ name, count })) });
  }

  // ---- submissions ----
  if (sub === "submissions") {
    const q = (url.searchParams.get("q") || "").toLowerCase(), status = url.searchParams.get("status") || "", form = url.searchParams.get("form") || "";
    const limit = Math.max(1, Math.min(200, Number(url.searchParams.get("limit")) || 50)), cursor = url.searchParams.get("cursor") || "";
    let keys = (await listAll(leads, "submissions/")).map(parseSubmissionKey).filter(Boolean);
    if (form) keys = keys.filter((s) => s.form === form);
    if (cursor) { const i = keys.findIndex((s) => s.id === cursor); if (i >= 0) keys = keys.slice(i + 1); }
    const items = [];
    let scanned = 0;
    // values are fetched in batches, newest first, until a page is full (search and status filters need the record)
    for (let i = 0; i < keys.length && items.length < limit; i += 40) {
      const batch = keys.slice(i, i + 40);
      const vals = await mapLimit(batch, 10, (s) => leads.get(s.key, { type: "json" }));
      batch.forEach((s, j) => {
        const v = vals[j]; scanned++;
        if (!v || items.length >= limit) return;
        if (status && (v.status || "new") !== status) return;
        if (q && !(`${s.name} ${s.email} ${s.form} ${JSON.stringify(v.fields || {})} ${v.notes || ""} ${v.city || ""}`.toLowerCase().includes(q))) return;
        items.push({ id: s.id, key: s.key, ...v });
      });
    }
    const next = items.length === limit && scanned < keys.length ? items[items.length - 1].id : "";
    return json({ items, next, total: keys.length });
  }
  const sm = /^submission\/([0-9]{13}-[0-9a-f]+)$/.exec(sub);
  if (sm) {
    const id = sm[1];
    const keys = await listAll(leads, `submissions/${id}`);
    if (!keys.length) return json({ ok: false, error: "not found" }, 404);
    const key = keys[0];
    if (req.method === "GET") return json({ id, key, ...((await leads.get(key, { type: "json" })) || {}) });
    if (req.method === "DELETE") { await leads.delete(key); return json({ ok: true }); }
    if (req.method === "PATCH") {
      const body = (await readJSON(req)) || {};
      const cur = (await leads.get(key, { type: "json" })) || {};
      const STATUSES = ["new", "contacted", "qualified", "won", "lost", "spam"];
      if (body.status && STATUSES.includes(body.status)) cur.status = body.status;
      if (typeof body.notes === "string") cur.notes = body.notes.slice(0, 5000);
      cur.updated = Date.now();
      await leads.setJSON(key, cur);
      return json({ ok: true, id, key, ...cur });
    }
    return text("Method not allowed", 405);
  }

  // ---- events feed ----
  if (sub === "events") {
    const d = /^\d{4}-\d{2}-\d{2}$/.test(url.searchParams.get("day") || "") ? url.searchParams.get("day") : day();
    const type = url.searchParams.get("type") || "", limit = Math.max(1, Math.min(500, Number(url.searchParams.get("limit")) || 150));
    let keys = (await listAll(analytics, `events/${d}/`)).map(parseEventKey).filter(Boolean);
    if (type) keys = keys.filter((e) => e.type === type);
    keys.sort((a, b) => b.ts - a.ts);
    const page = keys.slice(0, limit);
    const full = await mapLimit(page, 12, (e) => analytics.get(e.key, { type: "json" }));
    return json({ day: d, total: keys.length, items: page.map((e, i) => ({ ...e, ...(full[i] || {}) })) });
  }

  // ---- CSV export ----
  if (sub === "export.csv") {
    const days = Math.max(1, Math.min(3650, Number(url.searchParams.get("days")) || 365));
    const since = Date.now() - days * 86400000;
    const keys = (await listAll(leads, "submissions/")).map(parseSubmissionKey).filter((s) => s && s.ts >= since);
    const rows = await mapLimit(keys, 12, (s) => leads.get(s.key, { type: "json" }));
    const fieldNames = new Set();
    rows.forEach((r) => r && Object.keys(r.fields || {}).forEach((k) => fieldNames.add(k)));
    const cols = ["id", "date", "form", "status", "name", "email", "phone", "business", "page", "source", "country", "region", "city", "device", "notes", ...fieldNames];
    const lines = [cols.join(",")];
    rows.forEach((r, i) => { if (!r) return; const s = keys[i]; const base = { id: s.id, date: new Date(r.ts).toISOString(), ...r }; lines.push(cols.map((c) => csvCell(c in base ? base[c] : (r.fields || {})[c])).join(",")); });
    return new Response(lines.join("\r\n"), { status: 200, headers: { "Content-Type": "text/csv; charset=utf-8", "Content-Disposition": `attachment; filename="charlie-company-leads-${day()}.csv"`, "Cache-Control": "no-store" } });
  }

  return json({ ok: false, error: "not found" }, 404);
};
