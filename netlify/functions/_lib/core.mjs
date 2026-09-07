// Shared helpers for the Charlie Company Media API (Netlify Functions + Netlify Blobs).
import { createHmac, createHash, timingSafeEqual, randomBytes } from "node:crypto";

export const json = (data, status = 200, headers = {}) =>
  new Response(JSON.stringify(data), { status, headers: { "Content-Type": "application/json; charset=utf-8", "Cache-Control": "no-store", ...headers } });

export const text = (body, status = 200, headers = {}) =>
  new Response(body, { status, headers: { "Content-Type": "text/plain; charset=utf-8", "Cache-Control": "no-store", ...headers } });

const INV = 9999999999999; // inverted timestamps make lexicographic listings newest-first
export const invTs = (ms = Date.now()) => String(INV - ms).padStart(13, "0");
export const fromInvTs = (s) => INV - Number(s);
export const rand = (n = 4) => randomBytes(n).toString("hex");
export const day = (ms = Date.now()) => new Date(ms).toISOString().slice(0, 10);
export const enc = (s, max = 80) => encodeURIComponent(String(s ?? "").slice(0, max));
export const dec = (s) => { try { return decodeURIComponent(s); } catch { return s; } };

export const sha = (s) => createHash("sha256").update(String(s)).digest("hex");

// ---------- request helpers ----------
export const readJSON = async (req) => { try { return await req.json(); } catch { return null; } };
export const clientIp = (req, context) => context?.ip || req.headers.get("x-nf-client-connection-ip") || req.headers.get("x-forwarded-for")?.split(",")[0]?.trim() || "";
export const geoOf = (context) => {
  const g = context?.geo || {};
  return { country: g.country?.code || "", country_name: g.country?.name || "", region: g.subdivision?.code || "", city: g.city || "", tz: g.timezone || "" };
};

export const parseUA = (ua = "") => {
  const u = ua || "";
  const bot = /bot|crawl|spider|slurp|headless|lighthouse|pingdom|monitor|preview|facebookexternalhit|curl|wget|python-requests/i.test(u);
  const device = /iPad|Tablet|PlayBook|Silk/i.test(u) ? "tablet" : /Mobi|Android|iPhone|IEMobile/i.test(u) ? "mobile" : "desktop";
  const browser = /Edg\//.test(u) ? "Edge" : /OPR\/|Opera/.test(u) ? "Opera" : /SamsungBrowser/.test(u) ? "Samsung" : /Chrome\//.test(u) ? "Chrome" : /Firefox\//.test(u) ? "Firefox" : /Safari\//.test(u) ? "Safari" : /MSIE|Trident/.test(u) ? "IE" : "Other";
  const os = /Windows/.test(u) ? "Windows" : /iPhone|iPad|iPod/.test(u) ? "iOS" : /Mac OS X/.test(u) ? "macOS" : /Android/.test(u) ? "Android" : /CrOS/.test(u) ? "ChromeOS" : /Linux/.test(u) ? "Linux" : "Other";
  return { bot, device, browser, os };
};

// Classify where a visit came from: utm_source wins, then the referrer host.
export const sourceOf = (ref = "", utm = {}, host = "") => {
  if (utm && utm.utm_source) return String(utm.utm_source).toLowerCase().slice(0, 40);
  if (utm && utm.gclid) return "google ads";
  if (utm && utm.fbclid) return "facebook";
  if (!ref) return "direct";
  let h = "";
  try { h = new URL(ref).hostname.replace(/^www\./, ""); } catch { return "direct"; }
  if (!h || (host && h === host.replace(/^www\./, ""))) return "direct";
  if (/google\./.test(h)) return "google";
  if (/bing\.com/.test(h)) return "bing";
  if (/duckduckgo/.test(h)) return "duckduckgo";
  if (/yahoo\./.test(h)) return "yahoo";
  if (/facebook|fb\.com|instagram|l\.facebook/.test(h)) return /instagram/.test(h) ? "instagram" : "facebook";
  if (/linkedin/.test(h)) return "linkedin";
  if (/t\.co$|twitter|x\.com$/.test(h)) return "x";
  if (/youtube|youtu\.be/.test(h)) return "youtube";
  if (/reddit/.test(h)) return "reddit";
  if (/yelp/.test(h)) return "yelp";
  if (/nextdoor/.test(h)) return "nextdoor";
  if (/chatgpt|openai|perplexity|claude\.ai|anthropic|gemini\.google|copilot/.test(h)) return "ai assistants";
  return h.slice(0, 40);
};

// ---------- event keys ----------
// The essentials of every event are encoded into the blob key so a single listing of a day's
// prefix is enough to build every aggregate — no per-event reads. The full record is the value.
// events/<day>/<invts>-<rand>|<type>|<path>|<source>|<device>|<country>|<sid>|<vid>|<extra>
export const eventKey = (e) =>
  `events/${e.day}/${invTs(e.ts)}-${rand(2)}|${enc(e.type, 24)}|${enc(e.path, 90)}|${enc(e.source, 40)}|${(e.device || "d")[0]}|${enc(e.country, 2)}|${enc(e.sid, 10)}|${enc(e.vid, 10)}|${enc(e.extra || "", 60)}`;

export const parseEventKey = (key) => {
  const m = /^events\/(\d{4}-\d{2}-\d{2})\/(\d{13})-[0-9a-f]+\|(.*)$/.exec(key);
  if (!m) return null;
  const parts = m[3].split("|");
  const [type, path, source, device, country, sid, vid, extra] = parts;
  return { key, day: m[1], ts: fromInvTs(m[2]), type: dec(type || ""), path: dec(path || ""), source: dec(source || ""), device: { d: "desktop", m: "mobile", t: "tablet" }[device] || "desktop", country: dec(country || ""), sid: dec(sid || ""), vid: dec(vid || ""), extra: dec(extra || "") };
};

// submissions/<invts>-<rand>|<form>|<name>|<email>
export const submissionKey = (s) => `submissions/${invTs(s.ts)}-${rand(3)}|${enc(s.form, 24)}|${enc(s.name, 40)}|${enc(s.email, 60)}`;
export const parseSubmissionKey = (key) => {
  const m = /^submissions\/((\d{13})-[0-9a-f]+)\|(.*)$/.exec(key);
  if (!m) return null;
  const [form, name, email] = m[3].split("|");
  return { key, id: m[1], ts: fromInvTs(m[2]), form: dec(form || ""), name: dec(name || ""), email: dec(email || "") };
};

// ---------- aggregation ----------
export const emptyAgg = () => ({ pageviews: 0, events: 0, sessions: new Set(), visitors: new Set(), pages: {}, sources: {}, countries: {}, devices: {}, ctas: {}, calls: 0, outbound: 0, searches: 0, formStarts: 0, formSubmits: 0, scroll: [0, 0], seconds: [0, 0], hours: new Array(24).fill(0), entry: {} });
const bump = (o, k, n = 1) => { if (!k) return; o[k] = (o[k] || 0) + n; };

export const foldEvent = (agg, ev) => {
  agg.events++;
  if (ev.sid) agg.sessions.add(ev.sid);
  if (ev.vid) agg.visitors.add(ev.vid);
  if (ev.type === "pageview") {
    agg.pageviews++;
    bump(agg.pages, ev.path);
    bump(agg.sources, ev.source || "direct");
    bump(agg.countries, ev.country || "??");
    bump(agg.devices, ev.device);
    agg.hours[new Date(ev.ts).getUTCHours()]++;
    if (!agg.entry[ev.sid]) agg.entry[ev.sid] = ev.path;
  } else if (ev.type === "cta_click") bump(agg.ctas, ev.extra);
  else if (ev.type === "call_click") agg.calls++;
  else if (ev.type === "outbound") agg.outbound++;
  else if (ev.type === "search") agg.searches++;
  else if (ev.type === "form_start") agg.formStarts++;
  else if (ev.type === "form_submit") agg.formSubmits++;
  else if (ev.type === "engagement") {
    const m = /s(\d+)t(\d+)/.exec(ev.extra || "");
    if (m) { agg.scroll[0] += Number(m[1]); agg.scroll[1]++; agg.seconds[0] += Math.min(Number(m[2]), 1800); agg.seconds[1]++; }
  }
  return agg;
};

// Serialisable rollup (Sets → counts, maps trimmed)
const top = (o, n = 50) => Object.entries(o).sort((a, b) => b[1] - a[1]).slice(0, n);
export const finishAgg = (agg, dayStr) => ({
  day: dayStr, pageviews: agg.pageviews, events: agg.events, sessions: agg.sessions.size, visitors: agg.visitors.size,
  pages: top(agg.pages, 200), sources: top(agg.sources, 100), countries: top(agg.countries, 100), devices: top(agg.devices, 5), ctas: top(agg.ctas, 100),
  calls: agg.calls, outbound: agg.outbound, searches: agg.searches, formStarts: agg.formStarts, formSubmits: agg.formSubmits,
  avgScroll: agg.scroll[1] ? Math.round(agg.scroll[0] / agg.scroll[1]) : 0, avgSeconds: agg.seconds[1] ? Math.round(agg.seconds[0] / agg.seconds[1]) : 0,
  hours: agg.hours, entry: top(Object.values(agg.entry).reduce((o, p) => (bump(o, p), o), {}), 50),
});

// ---------- auth ----------
export const adminPassword = () => (globalThis.Netlify?.env?.get("ADMIN_PASSWORD") ?? process.env.ADMIN_PASSWORD ?? "").trim();
const sessionSecret = () => (globalThis.Netlify?.env?.get("ADMIN_SESSION_SECRET") ?? process.env.ADMIN_SESSION_SECRET ?? "") || sha("ccm-session:" + adminPassword());
const sign = (payload) => createHmac("sha256", sessionSecret()).update(payload).digest("base64url");

export const passwordMatches = (given) => {
  const want = adminPassword();
  if (!want || typeof given !== "string") return false;
  const a = Buffer.from(sha(given)), b = Buffer.from(sha(want));
  return a.length === b.length && timingSafeEqual(a, b);
};

export const SESSION_COOKIE = "ml_admin";
export const SESSION_TTL = 7 * 24 * 3600;
export const makeSession = () => { const exp = Date.now() + SESSION_TTL * 1000; const p = `${exp}.${rand(8)}`; return `${p}.${sign(p)}`; };
export const validSession = (token) => {
  if (!token || !adminPassword()) return false;
  const i = token.lastIndexOf(".");
  if (i < 0) return false;
  const p = token.slice(0, i), sig = token.slice(i + 1);
  const want = sign(p);
  if (want.length !== sig.length || !timingSafeEqual(Buffer.from(want), Buffer.from(sig))) return false;
  return Number(p.split(".")[0]) > Date.now();
};
export const cookieOf = (req, name) => { const m = new RegExp(`(?:^|;\\s*)${name}=([^;]+)`).exec(req.headers.get("cookie") || ""); return m ? m[1] : ""; };
export const sessionCookie = (token, maxAge = SESSION_TTL) => `${SESSION_COOKIE}=${token}; Path=/; HttpOnly; Secure; SameSite=Strict; Max-Age=${maxAge}`;

export const isAuthed = (req) => validSession(cookieOf(req, SESSION_COOKIE));

// ---------- CSV ----------
export const csvCell = (v) => { const s = v == null ? "" : String(v); return /[",\n\r]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s; };
