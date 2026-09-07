// Blob store selection: production and branch deploys share the global site store so the
// dashboard sees every visit and lead; deploy previews get their own isolated store.
import { getStore, getDeployStore } from "@netlify/blobs";

let override = null;
export const useStore = (factory) => { override = factory; }; // tests inject an in-memory store

export const store = (name) => {
  if (override) return override(name);
  const ctx = globalThis.Netlify?.context?.deploy?.context;
  if (ctx === "deploy-preview") return getDeployStore(name);
  return getStore(name);
};

export const listAll = async (s, prefix) => {
  const keys = [];
  for await (const page of s.list({ prefix, paginate: true })) for (const b of page.blobs) keys.push(b.key);
  return keys;
};

export const mapLimit = async (items, limit, fn) => {
  const out = new Array(items.length); let i = 0;
  const workers = new Array(Math.min(limit, items.length)).fill(0).map(async () => { while (i < items.length) { const idx = i++; out[idx] = await fn(items[idx], idx); } });
  await Promise.all(workers);
  return out;
};
