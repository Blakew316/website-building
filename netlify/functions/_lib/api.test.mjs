// node --test: exercises track → submit → admin with an in-memory blob store.
import { test } from "node:test";
import assert from "node:assert/strict";
import { useStore } from "./store.mjs";
import track from "../track.mjs";
import submit from "../submit.mjs";
import admin from "../admin.mjs";

process.env.ADMIN_PASSWORD = "correct horse battery";
const mem = new Map();
class MemStore {
  constructor(name) { this.name = name; }
  k(key) { return this.name + "::" + key; }
  async setJSON(key, v) { mem.set(this.k(key), JSON.stringify(v)); }
  async get(key) { const v = mem.get(this.k(key)); return v == null ? null : JSON.parse(v); }
  async delete(key) { mem.delete(this.k(key)); }
  list({ prefix = "" } = {}) {
    const p = this.k(prefix);
    const blobs = [...mem.keys()].filter((k) => k.startsWith(p)).sort().map((k) => ({ key: k.slice(this.name.length + 2), etag: "x" }));
    return (async function* () { yield { blobs }; })();
  }
}
useStore((name) => new MemStore(name));
const ctx = { ip: "203.0.113.9", geo: { country: { code: "US", name: "United States" }, subdivision: { code: "NC" }, city: "Charlotte" } };
const post = (url, body, headers = {}) => new Request("https://example.com" + url, { method: "POST", body: JSON.stringify(body), headers: { "Content-Type": "application/json", "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1", ...headers } });

test("track stores events and ignores bots", async () => {
  let r = await track(post("/api/track", { type: "pageview", path: "/pricing/", ref: "https://www.google.com/", sid: "s1", vid: "v1" }), ctx);
  assert.equal(r.status, 202);
  r = await track(post("/api/track", { type: "engagement", path: "/pricing/", sid: "s1", vid: "v1", data: { scroll: 80, seconds: 45 } }), ctx);
  assert.equal(r.status, 202);
  r = await track(post("/api/track", { type: "cta_click", path: "/pricing/", sid: "s1", vid: "v1", data: { label: "Book a demo" } }), ctx);
  r = await track(post("/api/track", { type: "pageview", path: "/", sid: "s2", vid: "v2" }, { "User-Agent": "Googlebot/2.1" }), ctx);
  assert.equal((await r.json()).ignored, "bot");
  assert.equal([...mem.keys()].filter((k) => k.startsWith("analytics::events/")).length, 3);
});

test("submit stores a lead and honours the honeypot", async () => {
  let r = await submit(post("/api/submit", { form: "quote", page: "/", fields: { business: "Acme Plumbing", name: "Jo Doe", email: "jo@example.com", phone: "7045551234", zip: "28202" } }), ctx);
  assert.equal(r.status, 201);
  r = await submit(post("/api/submit", { form: "quote", fields: { name: "Spam", website: "http://spam" } }), ctx);
  assert.equal(r.status, 202);
  assert.equal([...mem.keys()].filter((k) => k.startsWith("leads::submissions/")).length, 1);
});

test("admin requires a session, then serves overview / leads / events / csv", async () => {
  const get = (p, cookie = "") => admin(new Request("https://example.com/api/admin/" + p, { headers: cookie ? { cookie } : {} }), ctx);
  assert.equal((await get("overview")).status, 401);
  let r = await admin(post("/api/admin/login", { password: "wrong" }), ctx);
  assert.equal(r.status, 401);
  r = await admin(post("/api/admin/login", { password: "correct horse battery" }), ctx);
  assert.equal(r.status, 200);
  const cookie = r.headers.get("set-cookie").split(";")[0];
  const o = await (await get("overview?days=7", cookie)).json();
  assert.equal(o.totals.pageviews, 1);
  assert.equal(o.totals.visitors, 1);
  assert.equal(o.totals.leads, 1);
  assert.equal(o.totals.sources[0].name, "google");
  assert.equal(o.totals.avgScroll, 80);
  assert.equal(o.totals.ctas[0].name, "Book a demo");
  assert.equal(o.recentLeads[0].name, "Jo Doe");
  const leads = await (await get("submissions?q=acme", cookie)).json();
  assert.equal(leads.items.length, 1);
  const id = leads.items[0].id;
  const patched = await (await admin(new Request("https://example.com/api/admin/submission/" + id, { method: "PATCH", body: JSON.stringify({ status: "contacted", notes: "called" }), headers: { cookie, "Content-Type": "application/json" } }), ctx)).json();
  assert.equal(patched.status, "contacted");
  const ev = await (await get("events?limit=10", cookie)).json();
  assert.equal(ev.items.length, 3);
  assert.equal(ev.items[0].city, "Charlotte");
  const csv = await (await get("export.csv", cookie)).text();
  assert.match(csv, /jo@example.com/);
  assert.match(csv, /contacted/);
  // customers import (CSV rows already parsed client-side), de-dup by email, list, csv
  const imp = await (await admin(new Request("https://example.com/api/admin/import", { method: "POST", body: JSON.stringify({ kind: "subscriber", source: "billing.csv", rows: [
    { "Customer Name": "Acme Plumbing", "Email": "OWNER@acme.com", "Phone": "704-555-0100", "Plan": "Grow + Run", "Status": "Active", "Start Date": "2024-03-01", "Monthly Amount": "$349" },
    { "Customer Name": "Blue Ridge Bakery", "Email": "hi@blueridge.com", "Status": "Cancelled", "Start Date": "2023-11-15", "MRR": "199" },
    { "Customer Name": "", "Email": "", "Phone": "" } ] }), headers: { cookie, "Content-Type": "application/json" } }), ctx)).json();
  assert.deepEqual([imp.created, imp.updated, imp.skipped], [2, 0, 1]);
  const imp2 = await (await admin(new Request("https://example.com/api/admin/import", { method: "POST", body: JSON.stringify({ kind: "subscriber", rows: [{ Email: "owner@acme.com", Plan: "Run", Notes: "upgraded" }] }), headers: { cookie, "Content-Type": "application/json" } }), ctx)).json();
  assert.deepEqual([imp2.created, imp2.updated], [0, 1]);
  const cl = await (await get("customers?kind=subscriber", cookie)).json();
  assert.equal(cl.total, 2);
  assert.equal(cl.byStatus.active, 1);
  assert.equal(cl.mrr, 548);
  const acme = cl.items.find((c) => c.email === "owner@acme.com");
  assert.equal(acme.plan, "Run");
  assert.equal(acme.mrr, 349);
  assert.equal(new Date(acme.ts).toISOString().slice(0, 10), "2024-03-01");
  const bak = cl.items.find((c) => c.email === "hi@blueridge.com");
  await admin(new Request("https://example.com/api/admin/customer/" + bak.id, { method: "PATCH", body: JSON.stringify({ status: "active", mrr: "249" }), headers: { cookie, "Content-Type": "application/json" } }), ctx);
  const cl2 = await (await get("customers?kind=subscriber", cookie)).json();
  assert.equal(cl2.total, 2);
  assert.equal(cl2.byStatus.active, 2);
  assert.equal(cl2.mrr, 598);
  const ov2 = await (await get("overview?days=7", cookie)).json();
  assert.equal(ov2.customers.total, 2);
  const ccsv = await (await get("customers.csv", cookie)).text();
  assert.match(ccsv, /Blue Ridge Bakery/);
  r = await admin(new Request("https://example.com/api/admin/logout", { method: "POST" }), ctx);
  assert.match(r.headers.get("set-cookie"), /Max-Age=0/);
});
