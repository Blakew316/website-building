// /api/admin/* — password-protected admin API behind the /admin/ dashboard.
//   POST login | POST logout | GET status
//   GET overview?days=30            aggregates (daily rollups cached in Blobs)
//   GET submissions?q=&status=&form=&cursor=&limit=   leads, newest first
//   GET submission/:id | PATCH submission/:id {status,notes} | DELETE submission/:id
//   GET events?day=YYYY-MM-DD&type=&limit=            raw activity feed
//   GET export.csv?days=365          leads as CSV
//   POST import {kind, rows:[{...}]}  bulk import of subscribers/users/clients (de-duplicated by email)
//   GET customers?q=&kind=&status=&cursor=&limit=   |  GET/PATCH/DELETE customer/:id  |  GET customers.csv?kind=
import { json, text, readJSON, clientIp, parseEventKey, parseSubmissionKey, emptyAgg, foldEvent, finishAgg, day, adminPassword, passwordMatches, makeSession, sessionCookie, isAuthed, csvCell, sha, invTs, fromInvTs, rand, enc, dec } from "./_lib/core.mjs";
import { store, listAll, mapLimit } from "./_lib/store.mjs";

const MAX_ATTEMPTS = 8, WINDOW_MS = 15 * 60 * 1000;
const KINDS = ["subscriber", "user", "client"];
const STATUSES_C = ["active", "trial", "paused", "cancelled", "churned", "lead", "unknown"];

// customers/<kind>/<invts>-<rand>|<name>|<email>|<status>|<mrr>
const customerKey = (c) => `customers/${c.kind}/${invTs(c.ts)}-${rand(3)}|${enc(c.name, 40)}|${enc(c.email, 60)}|${enc(c.status, 12)}|${Math.round(c.mrr || 0)}`;
// Rewrite a record under a key that reflects its current name/email/status/mrr (keys feed the summaries)
const rekeyCustomer = async (store, oldKey, rec) => {
  const pc = parseCustomerKey(oldKey);
  const newKey = `customers/${pc.kind}/${pc.id}|${enc(rec.name, 40)}|${enc(rec.email, 60)}|${enc(rec.status, 12)}|${Math.round(rec.mrr || 0)}`;
  await store.setJSON(newKey, rec);
  if (newKey !== oldKey) { await store.delete(oldKey); if (rec.email) await store.setJSON(`index/${pc.kind}/${sha(rec.email.toLowerCase())}`, { key: newKey }); }
  return newKey;
};
const parseCustomerKey = (key) => {
  const m = /^customers\/([a-z]+)\/((\d{13})-[0-9a-f]+)\|(.*)$/.exec(key);
  if (!m) return null;
  const [name, email, status, mrr] = m[4].split("|");
  return { key, kind: m[1], id: m[2], ts: fromInvTs(m[3]), name: dec(name || ""), email: dec(email || ""), status: dec(status || "unknown"), mrr: Number(mrr) || 0 };
};
const pick = (row, ...names) => { for (const n of names) { const k = Object.keys(row).find((k) => k.trim().toLowerCase().replace(/[\s_-]+/g, " ") === n); if (k != null && String(row[k] ?? "").trim() !== "") return String(row[k]).trim(); } return ""; };
const parseDate = (v) => { if (!v) return NaN; const n = Number(v); if (!Number.isNaN(n) && n > 1e11) return n; if (!Number.isNaN(n) && n > 1e8) return n * 1000; const d = Date.parse(v); return Number.isNaN(d) ? NaN : d; };
const normaliseStatus = (v) => { const t = String(v || "").toLowerCase(); if (!t) return ""; if (/active|paid|current|live|subscribed|enabled|yes/.test(t)) return "active"; if (/trial/.test(t)) return "trial"; if (/pause|hold|suspend/.test(t)) return "paused"; if (/cancel/.test(t)) return "cancelled"; if (/churn|lost|inactive|expired|disabled|no\b/.test(t)) return "churned"; if (/lead|prospect/.test(t)) return "lead"; return STATUSES_C.includes(t) ? t : "unknown"; };
// Map a row from any CSV/JSON export (CRM, billing, platform) onto one customer record.
const normaliseCustomer = (row, kind, source) => {
  const r = row && typeof row === "object" ? row : {};
  const first = pick(r, "first name", "firstname", "first", "given name"), last = pick(r, "last name", "lastname", "last", "surname", "family name");
  const name = pick(r, "name", "full name", "contact", "contact name", "customer", "customer name", "owner") || [first, last].filter(Boolean).join(" ");
  const email = pick(r, "email", "email address", "e mail", "contact email", "login", "username").toLowerCase();
  const startedRaw = pick(r, "start date", "started", "start", "signup date", "signed up", "created", "created at", "date created", "joined", "join date", "date", "since", "customer since", "subscribed");
  const started = parseDate(startedRaw);
  const mrr = Number(String(pick(r, "mrr", "monthly", "monthly amount", "monthly price", "amount", "price", "revenue", "value", "plan price", "subscription amount")).replace(/[^0-9.\-]/g, "")) || 0;
  const used = new Set();
  const fields = {};
  for (const [k, v] of Object.entries(r)) { if (v == null || String(v).trim() === "") continue; fields[String(k).slice(0, 40)] = String(v).slice(0, 500); }
  return { ts: Number.isNaN(started) ? Date.now() : started, kind, source, name: name.slice(0, 120), email: email.slice(0, 160), phone: pick(r, "phone", "phone number", "mobile", "cell", "telephone", "tel").slice(0, 40), company: pick(r, "company", "business", "business name", "company name", "organization", "account", "account name").slice(0, 160), plan: pick(r, "plan", "package", "product", "tier", "subscription", "service", "services").slice(0, 80), status: normaliseStatus(pick(r, "status", "subscription status", "account status", "state", "active")), mrr, city: pick(r, "city", "town").slice(0, 80), state: pick(r, "state", "region", "province").slice(0, 40), zip: pick(r, "zip", "zip code", "postal code", "postcode").slice(0, 16), notes: pick(r, "notes", "note", "comments").slice(0, 2000), fields, updated: Date.now() };
};

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

  const analytics = store("analytics"), leads = store("leads"), customers = store("customers");

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
    const custKeys = (await listAll(customers, "customers/")).map(parseCustomerKey).filter(Boolean);
    const customerStats = { total: custKeys.length, byKind: {}, active: 0, mrr: 0, newInPeriod: 0 };
    for (const c of custKeys) { customerStats.byKind[c.kind] = (customerStats.byKind[c.kind] || 0) + 1; if (c.status === "active") customerStats.active++; if (c.ts >= since) customerStats.newInPeriod++; customerStats.mrr += c.mrr || 0; }
    return json({ days, generated: Date.now(), totals: { ...merge(cur), leads: leadsCur.length }, previous: { ...merge(prev), leads: leadsPrev.length }, daily, live: live.size, leadsTotal: subKeys.length, statusCounts, recentLeads: recent, forms: Object.entries(leadsCur.reduce((o, s) => (o[s.form] = (o[s.form] || 0) + 1, o), {})).map(([name, count]) => ({ name, count })), customers: customerStats });
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

  // ---- customers: subscribers / users / clients ----
  if (sub === "import") {
    if (req.method !== "POST") return text("Method not allowed", 405);
    const body = await readJSON(req);
    const rows = Array.isArray(body?.rows) ? body.rows.slice(0, 500) : null;
    if (!rows) return json({ ok: false, error: "rows[] required" }, 400);
    const kind = KINDS.includes(body.kind) ? body.kind : "subscriber";
    let created = 0, updated = 0, skipped = 0;
    for (const raw of rows) {
      const c = normaliseCustomer(raw, kind, body.source || "import");
      if (!c.email && !c.name && !c.phone) { skipped++; continue; }
      const idxKey = c.email ? `index/${kind}/${sha(c.email.toLowerCase())}` : "";
      const existingKey = idxKey ? await customers.get(idxKey, { type: "json" }) : null;
      if (existingKey && existingKey.key) {
        // update in place: only columns present in the new export overwrite the stored record
        const prev = (await customers.get(existingKey.key, { type: "json" })) || {};
        const upd = Object.fromEntries(Object.entries(c).filter(([k, v]) => !["fields", "ts", "updated"].includes(k) && v !== "" && v != null && !(k === "mrr" && v === 0)));
        const merged = { ...prev, ...upd, fields: { ...(prev.fields || {}), ...c.fields }, ts: prev.ts || c.ts, updated: Date.now(), imported: Date.now() };
        await rekeyCustomer(customers, existingKey.key, merged); updated++;
      } else {
        c.status = c.status || "active";
        const key = customerKey(c);
        await customers.setJSON(key, { ...c, imported: Date.now() });
        if (idxKey) await customers.setJSON(idxKey, { key });
        created++;
      }
    }
    return json({ ok: true, created, updated, skipped });
  }
  if (sub === "customers") {
    const q = (url.searchParams.get("q") || "").toLowerCase(), kind = url.searchParams.get("kind") || "", status = url.searchParams.get("status") || "";
    const limit = Math.max(1, Math.min(500, Number(url.searchParams.get("limit")) || 100)), cursor = url.searchParams.get("cursor") || "";
    let keys = (await listAll(customers, "customers/")).map(parseCustomerKey).filter(Boolean).sort((a, b) => b.ts - a.ts);
    if (kind) keys = keys.filter((c) => c.kind === kind);
    if (status) keys = keys.filter((c) => c.status === status);
    if (cursor) { const i = keys.findIndex((c) => c.id === cursor); if (i >= 0) keys = keys.slice(i + 1); }
    const items = [];
    let scanned = 0;
    for (let i = 0; i < keys.length && items.length < limit; i += 50) {
      const batch = keys.slice(i, i + 50);
      const vals = await mapLimit(batch, 10, (c) => customers.get(c.key, { type: "json" }));
      batch.forEach((c, j) => { const v = vals[j]; scanned++; if (!v || items.length >= limit) return; if (q && !JSON.stringify(v).toLowerCase().includes(q)) return; items.push({ id: c.id, key: c.key, ...v }); });
    }
    const summary = { total: keys.length, byStatus: {}, mrr: 0 };
    for (const c of keys) { summary.byStatus[c.status || "unknown"] = (summary.byStatus[c.status || "unknown"] || 0) + 1; summary.mrr += c.mrr || 0; }
    return json({ items, next: items.length === limit && scanned < keys.length ? items[items.length - 1].id : "", ...summary });
  }
  const cm = /^customer\/([0-9]{13}-[0-9a-f]+)$/.exec(sub);
  if (cm) {
    const keys = await listAll(customers, "customers/");
    const key = keys.find((k) => k.includes(`/${cm[1]}|`));
    if (!key) return json({ ok: false, error: "not found" }, 404);
    if (req.method === "GET") return json({ id: cm[1], key, ...((await customers.get(key, { type: "json" })) || {}) });
    if (req.method === "DELETE") { const v = await customers.get(key, { type: "json" }); await customers.delete(key); if (v?.email) await customers.delete(`index/${v.kind}/${sha(v.email.toLowerCase())}`); return json({ ok: true }); }
    if (req.method === "PATCH") {
      const body = (await readJSON(req)) || {};
      const cur = (await customers.get(key, { type: "json" })) || {};
      for (const f of ["name", "email", "phone", "company", "plan", "status", "notes", "city", "state"]) if (typeof body[f] === "string") cur[f] = body[f].slice(0, 500);
      if (body.mrr != null && !Number.isNaN(Number(body.mrr))) cur.mrr = Number(body.mrr);
      cur.updated = Date.now();
      const newKey = await rekeyCustomer(customers, key, cur);
      return json({ ok: true, id: cm[1], key: newKey, ...cur });
    }
    return text("Method not allowed", 405);
  }
  if (sub === "customers.csv") {
    const kind = url.searchParams.get("kind") || "";
    let keys = (await listAll(customers, "customers/")).map(parseCustomerKey).filter(Boolean).sort((a, b) => b.ts - a.ts);
    if (kind) keys = keys.filter((c) => c.kind === kind);
    const rows = await mapLimit(keys, 12, (c) => customers.get(c.key, { type: "json" }));
    const extra = new Set(); rows.forEach((r) => r && Object.keys(r.fields || {}).forEach((k) => extra.add(k)));
    const cols = ["id", "kind", "status", "name", "email", "phone", "company", "plan", "mrr", "city", "state", "started", "source", "notes", ...extra];
    const lines = [cols.join(",")];
    rows.forEach((r, i) => { if (!r) return; const base = { id: keys[i].id, started: r.ts ? new Date(r.ts).toISOString().slice(0, 10) : "", ...r }; lines.push(cols.map((c) => csvCell(c in base ? base[c] : (r.fields || {})[c])).join(",")); });
    return new Response(lines.join("\r\n"), { status: 200, headers: { "Content-Type": "text/csv; charset=utf-8", "Content-Disposition": `attachment; filename="customers-${kind || "all"}-${day()}.csv"`, "Cache-Control": "no-store" } });
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
