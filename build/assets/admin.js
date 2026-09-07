/* Charlie Company Media — admin dashboard (vanilla JS, talks to /api/admin/*) */
(function () {
  'use strict';
  const API = document.documentElement.dataset.api || '/api';
  const $ = (s, r) => (r || document).querySelector(s);
  const $$ = (s, r) => Array.from((r || document).querySelectorAll(s));
  const esc = (s) => String(s == null ? '' : s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const fmt = (n) => (n == null ? '—' : Number(n).toLocaleString('en-US'));
  const pct = (n) => (n == null ? '—' : Math.round(n) + '%');
  const dur = (s) => (!s ? '—' : s < 60 ? s + 's' : Math.floor(s / 60) + 'm ' + (s % 60) + 's');
  const when = (ts) => { const d = new Date(ts); const diff = (Date.now() - ts) / 1000; if (diff < 60) return 'just now'; if (diff < 3600) return Math.floor(diff / 60) + ' min ago'; if (diff < 86400) return Math.floor(diff / 3600) + ' h ago'; return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) + (diff > 365 * 86400 ? ' ' + d.getFullYear() : ''); };
  const dateTime = (ts) => new Date(ts).toLocaleString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: 'numeric', minute: '2-digit' });
  const api = async (path, opts) => {
    const res = await fetch(API + '/admin/' + path, { credentials: 'same-origin', headers: { 'Content-Type': 'application/json' }, ...opts });
    if (res.status === 401 && path !== 'login' && path !== 'status') { showLogin(); throw new Error('unauthorized'); }
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error || ('Request failed (' + res.status + ')'));
    return data;
  };

  const login = $('#login'), shell = $('#shell'), main = $('#main');
  const state = { days: 30, view: 'overview', overview: null, leads: { items: [], next: '', q: '', status: '', form: '' }, activity: { day: '', type: '' } };
  let liveTimer = null;

  const showLogin = () => { shell.hidden = true; login.hidden = false; clearInterval(liveTimer); };
  const showApp = () => { login.hidden = true; shell.hidden = false; route(); };

  /* ---------- auth ---------- */
  api('status').then((s) => {
    $('#setup-note').hidden = s.configured;
    $('#ctx-label').textContent = s.context ? 'Deploy context: ' + s.context : '';
    if (s.authed) showApp();
  }).catch(() => {});
  $('#login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const err = $('#login-error'); err.hidden = true;
    const btn = $('button', e.target); btn.disabled = true; btn.textContent = 'Signing in…';
    try { await api('login', { method: 'POST', body: JSON.stringify({ password: $('#pw').value }) }); $('#pw').value = ''; showApp(); }
    catch (ex) { err.textContent = ex.message; err.hidden = false; }
    btn.disabled = false; btn.textContent = 'Sign in';
  });
  $('#logout').addEventListener('click', async (e) => { e.preventDefault(); await api('logout', { method: 'POST' }); showLogin(); });

  /* ---------- routing ---------- */
  const route = () => {
    const v = (location.hash || '#overview').slice(1).split('/')[0];
    state.view = ['overview', 'leads', 'customers', 'activity', 'pages', 'settings'].includes(v) ? v : 'overview';
    $$('#nav a').forEach((a) => a.classList.toggle('on', a.dataset.view === state.view));
    clearInterval(liveTimer);
    ({ overview: renderOverview, leads: renderLeads, customers: renderCustomers, activity: renderActivity, pages: renderPages, settings: renderSettings })[state.view]();
  };
  window.addEventListener('hashchange', () => { if (!shell.hidden) route(); });

  const top = (title, extra) => `<div class="adm-top"><h1>${esc(title)}</h1><div style="display:flex;gap:12px;align-items:center;flex-wrap:wrap">${extra || ''}</div></div>`;
  const rangeSeg = () => `<div class="seg" id="range">${[7, 30, 90, 365].map((d) => `<button class="${state.days === d ? 'on' : ''}" data-d="${d}">${d === 365 ? '1 year' : d + ' days'}</button>`).join('')}</div>`;
  const bindRange = (cb) => $$('#range button').forEach((b) => b.addEventListener('click', () => { state.days = Number(b.dataset.d); state.overview = null; cb(); }));
  const delta = (cur, prev, invert) => { if (!prev) return `<div class="d">${cur ? 'new' : '—'}</div>`; const p = Math.round((cur - prev) / prev * 100); const up = invert ? p < 0 : p > 0; return `<div class="d ${p === 0 ? '' : up ? 'up' : 'down'}">${p > 0 ? '+' : ''}${p}% vs prior period</div>`; };
  const kpi = (label, value, d) => `<div class="kpi"><div class="l">${esc(label)}</div><div class="v">${value}</div>${d || ''}</div>`;
  const bars = (items, fmtName) => items && items.length ? `<div class="bars">${items.map((it, i) => { const max = items[0].count || 1; return `<div class="bar-row"><div class="n"><i style="width:${Math.max(3, it.count / max * 100)}%"></i><span>${esc(fmtName ? fmtName(it.name) : it.name)}</span></div><div class="c">${fmt(it.count)}</div></div>`; }).join('')}</div>` : '<div class="empty">No data yet.</div>';

  /* ---------- charts (inline SVG) ---------- */
  const areaChart = (daily) => {
    const W = 720, H = 220, P = 28;
    const n = daily.length; if (!n) return '<div class="empty">No traffic recorded yet.</div>';
    const max = Math.max(1, ...daily.map((d) => d.pageviews));
    const x = (i) => P + (n === 1 ? (W - 2 * P) / 2 : i * (W - 2 * P) / (n - 1));
    const y = (v) => H - P - v / max * (H - 2 * P);
    const line = (key) => daily.map((d, i) => (i ? 'L' : 'M') + x(i).toFixed(1) + ' ' + y(d[key]).toFixed(1)).join(' ');
    const area = line('pageviews') + ` L${x(n - 1).toFixed(1)} ${H - P} L${x(0).toFixed(1)} ${H - P} Z`;
    const ticks = [0, 0.5, 1].map((f) => `<text x="${P - 8}" y="${y(max * f) + 4}" text-anchor="end" font-size="10" fill="#9aa5b8">${Math.round(max * f)}</text><line x1="${P}" x2="${W - P}" y1="${y(max * f)}" y2="${y(max * f)}" stroke="#0b1f3f" stroke-opacity=".06"/>`).join('');
    const labels = daily.map((d, i) => (n <= 14 || i % Math.ceil(n / 8) === 0 || i === n - 1) ? `<text x="${x(i)}" y="${H - 8}" text-anchor="middle" font-size="10" fill="#9aa5b8">${d.day.slice(5)}</text>` : '').join('');
    const dots = daily.map((d, i) => `<circle cx="${x(i)}" cy="${y(d.leads * (max / Math.max(1, ...daily.map((q) => q.leads))))}" r="0" />`).join('');
    return `<svg class="chart" viewBox="0 0 ${W} ${H}" role="img" aria-label="Traffic over time"><defs><linearGradient id="ga" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#2a5a9c" stop-opacity=".28"/><stop offset="1" stop-color="#2a5a9c" stop-opacity="0"/></linearGradient></defs>${ticks}${labels}<path d="${area}" fill="url(#ga)"/><path d="${line('pageviews')}" fill="none" stroke="#0b1f3f" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/><path d="${line('visitors')}" fill="none" stroke="#4f86c6" stroke-width="1.6" stroke-dasharray="4 4" stroke-linejoin="round"/>${dots}</svg>
      <div class="hint"><span style="display:inline-block;width:14px;height:2px;background:#0b1f3f;vertical-align:middle"></span> Pageviews &nbsp; <span style="display:inline-block;width:14px;height:2px;border-top:2px dashed #4f86c6;vertical-align:middle"></span> Visitors</div>`;
  };
  const leadBars = (daily) => {
    const max = Math.max(1, ...daily.map((d) => d.leads));
    return `<div class="hours" style="height:120px;grid-template-columns:repeat(${daily.length},1fr)">${daily.map((d) => `<i title="${d.day}: ${d.leads} lead${d.leads === 1 ? '' : 's'}" style="height:${Math.max(2, d.leads / max * 100)}%;opacity:${d.leads ? .85 : .18}"></i>`).join('')}</div><div class="hint">${daily[0] ? daily[0].day : ''} → ${daily.length ? daily[daily.length - 1].day : ''}</div>`;
  };
  const hoursChart = (hours) => { const max = Math.max(1, ...hours); return `<div class="hours">${hours.map((h, i) => `<i title="${i}:00 UTC — ${h}" style="height:${Math.max(2, h / max * 100)}%"></i>`).join('')}</div><div class="hint">Pageviews by hour (UTC)</div>`; };

  /* ---------- overview ---------- */
  const loadOverview = async () => { if (!state.overview || state.overview.days !== state.days) state.overview = await api('overview?days=' + state.days); return state.overview; };
  async function renderOverview() {
    main.innerHTML = top('Overview', rangeSeg() + '<span class="live" id="live-badge"><i></i>…</span>');
    bindRange(renderOverview);
    let o;
    try { o = await loadOverview(); } catch (e) { main.insertAdjacentHTML('beforeend', `<div class="panel"><div class="empty">${esc(e.message)}</div></div>`); return; }
    if (state.view !== 'overview') return;
    const t = o.totals, p = o.previous;
    const conv = t.sessions ? t.leads / t.sessions * 100 : 0, convP = p.sessions ? p.leads / p.sessions * 100 : 0;
    $('#live-badge').innerHTML = `<i></i>${fmt(o.live)} online now`;
    main.insertAdjacentHTML('beforeend', `
      <div class="kpis">
        ${kpi('Visitors', fmt(t.visitors), delta(t.visitors, p.visitors))}
        ${kpi('Pageviews', fmt(t.pageviews), delta(t.pageviews, p.pageviews))}
        ${kpi('Sessions', fmt(t.sessions), delta(t.sessions, p.sessions))}
        ${kpi('Leads', fmt(t.leads), delta(t.leads, p.leads))}
        ${kpi('Subscribers', fmt(o.customers ? o.customers.active : 0), `<div class="d">${o.customers && o.customers.total ? fmt(o.customers.total) + ' total · ' + fmt(o.customers.newInPeriod) + ' new' : '<a href="#customers">Import your list</a>'}</div>`)}
        ${kpi('Conversion', pct(conv), delta(conv, convP))}
        ${kpi('Calls tapped', fmt(t.calls), delta(t.calls, p.calls))}
        ${kpi('Avg. time', dur(t.avgSeconds), delta(t.avgSeconds, p.avgSeconds))}
        ${kpi('Avg. scroll', pct(t.avgScroll), delta(t.avgScroll, p.avgScroll))}
      </div>
      <div class="row2">
        <div class="panel"><h3>Traffic <span class="small muted">last ${o.days} days</span></h3>${areaChart(o.daily)}</div>
        <div class="panel"><h3>Leads per day</h3>${leadBars(o.daily)}<h3 style="margin-top:18px">By status</h3>${bars(Object.entries(o.statusCounts).map(([name, count]) => ({ name, count })).sort((a, b) => b.count - a.count))}</div>
      </div>
      <div class="row3">
        <div class="panel"><h3>Top pages</h3>${bars(t.pages.slice(0, 10))}</div>
        <div class="panel"><h3>Sources</h3>${bars(t.sources.slice(0, 10))}</div>
        <div class="panel"><h3>Locations</h3>${bars(t.countries.slice(0, 10), (c) => c === '??' ? 'Unknown' : c)}</div>
      </div>
      <div class="row3">
        <div class="panel"><h3>Devices</h3>${bars(t.devices)}<h3 style="margin-top:18px">Forms</h3>${bars(o.forms)}</div>
        <div class="panel"><h3>Buttons clicked</h3>${bars(t.ctas.slice(0, 10))}</div>
        <div class="panel"><h3>Busiest hours</h3>${hoursChart(t.hours)}<h3 style="margin-top:18px">Landing pages</h3>${bars(t.entry.slice(0, 6))}</div>
      </div>
      <div class="panel"><h3>Latest leads <a class="btn-link" href="#leads">All leads</a></h3>${leadsTable(o.recentLeads)}</div>`);
    bindLeadRows();
    liveTimer = setInterval(async () => { try { const s = await api('overview?days=1'); const b = $('#live-badge'); if (b) b.innerHTML = `<i></i>${fmt(s.live)} online now`; } catch (e) {} }, 30000);
  }

  /* ---------- leads ---------- */
  const leadsTable = (items) => items && items.length ? `<div style="overflow:auto"><table class="tbl"><thead><tr><th>When</th><th>Name</th><th>Contact</th><th>Form</th><th>Source</th><th>Status</th></tr></thead><tbody>${items.map((l) => `<tr data-id="${esc(l.id)}"><td class="mono" title="${esc(dateTime(l.ts))}">${esc(when(l.ts))}</td><td><strong>${esc(l.name || '—')}</strong>${l.business && l.business !== l.name ? '<br><span class="small muted">' + esc(l.business) + '</span>' : ''}</td><td>${esc(l.email || '')}${l.phone ? '<br><span class="small muted">' + esc(l.phone) + '</span>' : ''}</td><td>${esc(l.form)}</td><td>${esc(l.source || '')}${l.city ? '<br><span class="small muted">' + esc(l.city + (l.region ? ', ' + l.region : '')) + '</span>' : ''}</td><td><span class="status ${esc(l.status || 'new')}">${esc(l.status || 'new')}</span></td></tr>`).join('')}</tbody></table></div>` : '<div class="empty">No leads yet. Every form on the site lands here the moment it is submitted.</div>';
  const bindLeadRows = () => $$('tr[data-id]').forEach((tr) => tr.addEventListener('click', () => openLead(tr.dataset.id)));
  async function renderLeads(reset = true) {
    if (reset) { state.leads.items = []; state.leads.next = ''; }
    const L = state.leads;
    main.innerHTML = top('Leads', `<a class="btn btn-ghost btn-sm" href="${API}/admin/export.csv?days=3650">Export CSV</a>`) + `
      <div class="toolbar"><input type="search" id="lq" placeholder="Search name, email, company, message…" value="${esc(L.q)}">
        <select id="lstatus"><option value="">All statuses</option>${['new', 'contacted', 'qualified', 'won', 'lost', 'spam'].map((s) => `<option ${L.status === s ? 'selected' : ''}>${s}</option>`).join('')}</select>
        <select id="lform"><option value="">All forms</option>${['quote', 'support', 'privacy-request', 'signin', 'agent-signin', 'forgot-password', 'signup'].map((s) => `<option ${L.form === s ? 'selected' : ''}>${s}</option>`).join('')}</select></div>
      <div class="panel" id="leads-panel"><div class="empty">Loading…</div></div>`;
    let t;
    $('#lq').addEventListener('input', (e) => { clearTimeout(t); t = setTimeout(() => { L.q = e.target.value.trim(); loadLeads(true); }, 300); });
    $('#lstatus').addEventListener('change', (e) => { L.status = e.target.value; loadLeads(true); });
    $('#lform').addEventListener('change', (e) => { L.form = e.target.value; loadLeads(true); });
    loadLeads(true);
  }
  async function loadLeads(reset) {
    const L = state.leads; if (reset) { L.items = []; L.next = ''; }
    const qs = new URLSearchParams({ q: L.q, status: L.status, form: L.form, cursor: L.next, limit: 50 });
    let data; try { data = await api('submissions?' + qs); } catch (e) { $('#leads-panel').innerHTML = `<div class="empty">${esc(e.message)}</div>`; return; }
    L.items = L.items.concat(data.items); L.next = data.next;
    const panel = $('#leads-panel'); if (!panel) return;
    panel.innerHTML = `<h3>${fmt(data.total)} lead${data.total === 1 ? '' : 's'} <span class="small muted">newest first</span></h3>` + leadsTable(L.items) + (L.next ? '<div class="btn-row center" style="margin-top:14px"><button class="btn btn-ghost btn-sm" id="more">Load more</button></div>' : '');
    bindLeadRows();
    const more = $('#more'); if (more) more.addEventListener('click', () => loadLeads(false));
  }
  const drawer = $('#drawer'), scrim = $('#scrim');
  const closeDrawer = () => { drawer.classList.remove('open'); scrim.classList.remove('on'); };
  scrim.addEventListener('click', closeDrawer);
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeDrawer(); });
  async function openLead(id) {
    drawer.innerHTML = '<div class="empty">Loading…</div>'; drawer.classList.add('open'); scrim.classList.add('on');
    let l; try { l = await api('submission/' + id); } catch (e) { drawer.innerHTML = `<div class="empty">${esc(e.message)}</div>`; return; }
    const fields = Object.entries(l.fields || {}).filter(([k]) => !['form', 'source'].includes(k));
    drawer.innerHTML = `<div style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px"><div><span class="status ${esc(l.status || 'new')}">${esc(l.status || 'new')}</span><h2 style="margin-top:10px">${esc(l.name || l.email || 'Lead')}</h2><div class="small muted">${esc(l.form)} · ${esc(dateTime(l.ts))}</div></div><button class="btn btn-ghost btn-sm" id="close-drawer">Close</button></div>
      <dl>${fields.map(([k, v]) => `<dt>${esc(k.replace(/_/g, ' '))}</dt><dd>${k === 'email' ? `<a href="mailto:${esc(v)}">${esc(v)}</a>` : k === 'phone' ? `<a href="tel:${esc(v)}">${esc(v)}</a>` : esc(v)}</dd>`).join('')}
        <dt>Page</dt><dd>${esc(l.page || '')}</dd><dt>Source</dt><dd>${esc(l.source || '')}${l.ref ? ' · ' + esc(l.ref) : ''}</dd><dt>Location</dt><dd>${esc([l.city, l.region, l.country].filter(Boolean).join(', ') || '—')}</dd><dt>Device</dt><dd>${esc([l.device, l.browser, l.os].filter(Boolean).join(' · '))}</dd>${Object.keys(l.utm || {}).length ? `<dt>Campaign</dt><dd>${esc(Object.entries(l.utm).map(([k, v]) => k + '=' + v).join(' '))}</dd>` : ''}</dl>
      <div class="field"><label>Status</label><select id="d-status">${['new', 'contacted', 'qualified', 'won', 'lost', 'spam'].map((s) => `<option ${l.status === s ? 'selected' : ''}>${s}</option>`).join('')}</select></div>
      <div class="field"><label>Notes</label><textarea id="d-notes" rows="5" placeholder="Call notes, next steps…">${esc(l.notes || '')}</textarea></div>
      <div class="btn-row"><button class="btn btn-primary btn-sm" id="d-save">Save</button><button class="btn btn-ghost btn-sm" id="d-delete">Delete</button><span class="small muted" id="d-msg"></span></div>`;
    $('#close-drawer').addEventListener('click', closeDrawer);
    $('#d-save').addEventListener('click', async () => {
      const msg = $('#d-msg'); msg.textContent = 'Saving…';
      try { const r = await api('submission/' + id, { method: 'PATCH', body: JSON.stringify({ status: $('#d-status').value, notes: $('#d-notes').value }) }); msg.textContent = 'Saved'; const it = state.leads.items.find((x) => x.id === id); if (it) Object.assign(it, r); state.overview = null; $$(`tr[data-id="${id}"] .status`).forEach((s) => { s.className = 'status ' + r.status; s.textContent = r.status; }); }
      catch (e) { msg.textContent = e.message; }
    });
    $('#d-delete').addEventListener('click', async () => {
      if (!confirm('Delete this lead permanently?')) return;
      try { await api('submission/' + id, { method: 'DELETE' }); closeDrawer(); state.leads.items = state.leads.items.filter((x) => x.id !== id); state.overview = null; $$(`tr[data-id="${id}"]`).forEach((tr) => tr.remove()); } catch (e) { alert(e.message); }
    });
  }

  /* ---------- customers: subscribers / users / clients ---------- */
  const money = (n) => '$' + Number(n || 0).toLocaleString('en-US', { maximumFractionDigits: 0 });
  const parseCSV = (text) => {
    const rows = []; let row = [], cell = '', q = false;
    for (let i = 0; i < text.length; i++) {
      const c = text[i];
      if (q) { if (c === '"') { if (text[i + 1] === '"') { cell += '"'; i++; } else q = false; } else cell += c; }
      else if (c === '"') q = true;
      else if (c === ',' || c === '\t') { row.push(cell); cell = ''; }
      else if (c === '\n' || c === '\r') { if (c === '\r' && text[i + 1] === '\n') i++; row.push(cell); cell = ''; if (row.some((x) => x.trim())) rows.push(row); row = []; }
      else cell += c;
    }
    row.push(cell); if (row.some((x) => x.trim())) rows.push(row);
    if (!rows.length) return [];
    const head = rows[0].map((h) => h.trim());
    return rows.slice(1).map((r) => { const o = {}; head.forEach((k, i) => { if (k) o[k] = (r[i] || '').trim(); }); return o; });
  };
  const parseFile = async (file) => {
    const text = await file.text();
    if (/\.json$/i.test(file.name) || text.trim().startsWith('[') || text.trim().startsWith('{')) { const d = JSON.parse(text); const arr = Array.isArray(d) ? d : (d.data || d.rows || d.items || d.customers || d.users || d.subscribers || []); return arr; }
    return parseCSV(text);
  };
  const customersTable = (items) => items && items.length ? `<div style="overflow:auto"><table class="tbl"><thead><tr><th>Name</th><th>Contact</th><th>Company</th><th>Plan</th><th>Since</th><th>Status</th><th>MRR</th></tr></thead><tbody>${items.map((c) => `<tr data-cid="${esc(c.id)}"><td><strong>${esc(c.name || '—')}</strong><br><span class="small muted">${esc(c.kind)}</span></td><td>${esc(c.email || '')}${c.phone ? '<br><span class="small muted">' + esc(c.phone) + '</span>' : ''}</td><td>${esc(c.company || '')}${c.city ? '<br><span class="small muted">' + esc([c.city, c.state].filter(Boolean).join(', ')) + '</span>' : ''}</td><td>${esc(c.plan || '')}</td><td class="mono">${c.ts ? new Date(c.ts).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) : ''}</td><td><span class="status ${esc(c.status === 'active' ? 'qualified' : c.status === 'trial' ? 'new' : c.status === 'paused' ? 'contacted' : 'lost')}">${esc(c.status || 'unknown')}</span></td><td class="mono">${c.mrr ? money(c.mrr) : ''}</td></tr>`).join('')}</tbody></table></div>` : '<div class="empty">No customers imported yet. Drop a CSV or JSON export from your billing system, CRM or platform above.</div>';
  async function renderCustomers() {
    const C = state.customers || (state.customers = { items: [], next: '', q: '', kind: '', status: '' });
    main.innerHTML = top('Customers', `<a class="btn btn-ghost btn-sm" href="${API}/admin/customers.csv">Export CSV</a>`) + `
      <div class="panel" style="margin-bottom:14px"><h3>Import subscribers, users or clients</h3>
        <div class="toolbar"><select id="imp-kind"><option value="subscriber">Subscribers</option><option value="user">Users</option><option value="client">Clients</option></select><span class="small muted">De-duplicated by email. Columns like name, email, phone, company, plan, status, start date and MRR are recognised automatically; everything else is kept as extra fields.</span></div>
        <label class="drop" id="drop">Drop a CSV, TSV or JSON export here, or click to choose a file<input type="file" id="imp-file" accept=".csv,.tsv,.txt,.json"></label>
        <div id="imp-preview"></div></div>
      <div class="kpis" id="cust-kpis"></div>
      <div class="toolbar"><input type="search" id="cq" placeholder="Search customers…" value="${esc(C.q)}"><select id="ckind"><option value="">All types</option>${['subscriber', 'user', 'client'].map((k) => `<option value="${k}" ${C.kind === k ? 'selected' : ''}>${k}s</option>`).join('')}</select><select id="cstatus"><option value="">All statuses</option>${['active', 'trial', 'paused', 'cancelled', 'churned', 'lead', 'unknown'].map((k) => `<option ${C.status === k ? 'selected' : ''}>${k}</option>`).join('')}</select></div>
      <div class="panel" id="cust-panel"><div class="empty">Loading…</div></div>`;
    let t;
    $('#cq').addEventListener('input', (e) => { clearTimeout(t); t = setTimeout(() => { C.q = e.target.value.trim(); loadCustomers(true); }, 300); });
    $('#ckind').addEventListener('change', (e) => { C.kind = e.target.value; loadCustomers(true); });
    $('#cstatus').addEventListener('change', (e) => { C.status = e.target.value; loadCustomers(true); });
    const drop = $('#drop'), fileIn = $('#imp-file');
    drop.addEventListener('dragover', (e) => { e.preventDefault(); drop.classList.add('over'); });
    drop.addEventListener('dragleave', () => drop.classList.remove('over'));
    drop.addEventListener('drop', (e) => { e.preventDefault(); drop.classList.remove('over'); if (e.dataTransfer.files[0]) stageImport(e.dataTransfer.files[0]); });
    fileIn.addEventListener('change', () => { if (fileIn.files[0]) stageImport(fileIn.files[0]); });
    loadCustomers(true);
  }
  async function stageImport(file) {
    const box = $('#imp-preview');
    let rows; try { rows = await parseFile(file); } catch (e) { box.innerHTML = `<div class="empty">Could not read ${esc(file.name)}: ${esc(e.message)}</div>`; return; }
    if (!rows.length) { box.innerHTML = '<div class="empty">No rows found in that file.</div>'; return; }
    const cols = Object.keys(rows[0]).slice(0, 12);
    box.innerHTML = `<div class="hint" style="margin-top:14px"><strong>${esc(file.name)}</strong> · ${fmt(rows.length)} rows · columns: ${cols.map(esc).join(', ')}${Object.keys(rows[0]).length > 12 ? '…' : ''}</div>
      <div class="preview"><table class="tbl"><thead><tr>${cols.map((c) => `<th>${esc(c)}</th>`).join('')}</tr></thead><tbody>${rows.slice(0, 5).map((r) => `<tr>${cols.map((c) => `<td>${esc(String(r[c] ?? '').slice(0, 40))}</td>`).join('')}</tr>`).join('')}</tbody></table></div>
      <div class="btn-row" style="margin-top:14px"><button class="btn btn-primary btn-sm" id="imp-go">Import ${fmt(rows.length)} as ${esc($('#imp-kind').value)}s</button><span class="small muted" id="imp-msg"></span></div>`;
    $('#imp-go').addEventListener('click', async () => {
      const btn = $('#imp-go'), msg = $('#imp-msg'); btn.disabled = true;
      const kind = $('#imp-kind').value; let created = 0, updated = 0, skipped = 0;
      try {
        for (let i = 0; i < rows.length; i += 200) {
          msg.textContent = `Importing ${Math.min(i + 200, rows.length)} of ${rows.length}…`;
          const r = await api('import', { method: 'POST', body: JSON.stringify({ kind, source: file.name, rows: rows.slice(i, i + 200) }) });
          created += r.created; updated += r.updated; skipped += r.skipped;
        }
        msg.textContent = `Done: ${created} added, ${updated} updated, ${skipped} skipped.`; state.overview = null; loadCustomers(true);
      } catch (e) { msg.textContent = e.message; btn.disabled = false; }
    });
  }
  async function loadCustomers(reset) {
    const C = state.customers; if (reset) { C.items = []; C.next = ''; }
    let d; try { d = await api('customers?' + new URLSearchParams({ q: C.q, kind: C.kind, status: C.status, cursor: C.next, limit: 100 })); } catch (e) { const p = $('#cust-panel'); if (p) p.innerHTML = `<div class="empty">${esc(e.message)}</div>`; return; }
    C.items = C.items.concat(d.items); C.next = d.next;
    const k = $('#cust-kpis'); if (k) k.innerHTML = kpi('Customers', fmt(d.total)) + kpi('Active', fmt(d.byStatus.active || 0)) + kpi('Trial', fmt(d.byStatus.trial || 0)) + kpi('Paused / cancelled', fmt((d.byStatus.paused || 0) + (d.byStatus.cancelled || 0) + (d.byStatus.churned || 0))) + kpi('MRR', money(d.mrr));
    const panel = $('#cust-panel'); if (!panel) return;
    panel.innerHTML = `<h3>${fmt(d.total)} customer${d.total === 1 ? '' : 's'}</h3>` + customersTable(C.items) + (C.next ? '<div class="btn-row center" style="margin-top:14px"><button class="btn btn-ghost btn-sm" id="cmore">Load more</button></div>' : '');
    $$('tr[data-cid]').forEach((tr) => tr.addEventListener('click', () => openCustomer(tr.dataset.cid)));
    const more = $('#cmore'); if (more) more.addEventListener('click', () => loadCustomers(false));
  }
  async function openCustomer(id) {
    drawer.innerHTML = '<div class="empty">Loading…</div>'; drawer.classList.add('open'); scrim.classList.add('on');
    let c; try { c = await api('customer/' + id); } catch (e) { drawer.innerHTML = `<div class="empty">${esc(e.message)}</div>`; return; }
    const f = (k, label, type = 'text') => `<div class="field"><label>${label}</label><input id="c-${k}" type="${type}" value="${esc(c[k] ?? '')}" style="font:inherit;width:100%;padding:9px 12px;border-radius:12px;border:1px solid var(--line-2)"></div>`;
    drawer.innerHTML = `<div style="display:flex;justify-content:space-between;align-items:flex-start;gap:12px"><div><span class="status">${esc(c.kind)}</span><h2 style="margin-top:10px">${esc(c.name || c.email || 'Customer')}</h2><div class="small muted">Since ${esc(c.ts ? new Date(c.ts).toLocaleDateString() : '—')} · imported from ${esc(c.source || 'import')}</div></div><button class="btn btn-ghost btn-sm" id="close-drawer">Close</button></div>
      <div class="field-row" style="margin-top:18px">${f('name', 'Name')}${f('email', 'Email', 'email')}</div><div class="field-row">${f('phone', 'Phone')}${f('company', 'Company')}</div><div class="field-row">${f('plan', 'Plan')}${f('mrr', 'Monthly amount', 'number')}</div>
      <div class="field"><label>Status</label><select id="c-status">${['active', 'trial', 'paused', 'cancelled', 'churned', 'lead', 'unknown'].map((s) => `<option ${c.status === s ? 'selected' : ''}>${s}</option>`).join('')}</select></div>
      <div class="field"><label>Notes</label><textarea id="c-notes" rows="4">${esc(c.notes || '')}</textarea></div>
      ${Object.keys(c.fields || {}).length ? `<dl>${Object.entries(c.fields).map(([k, v]) => `<dt>${esc(k)}</dt><dd>${esc(v)}</dd>`).join('')}</dl>` : ''}
      <div class="btn-row"><button class="btn btn-primary btn-sm" id="c-save">Save</button><button class="btn btn-ghost btn-sm" id="c-delete">Delete</button><span class="small muted" id="c-msg"></span></div>`;
    $('#close-drawer').addEventListener('click', closeDrawer);
    $('#c-save').addEventListener('click', async () => {
      const msg = $('#c-msg'); msg.textContent = 'Saving…';
      const body = {}; ['name', 'email', 'phone', 'company', 'plan', 'mrr', 'status', 'notes'].forEach((k) => { body[k] = $('#c-' + k).value; });
      try { await api('customer/' + id, { method: 'PATCH', body: JSON.stringify(body) }); msg.textContent = 'Saved'; state.overview = null; loadCustomers(true); } catch (e) { msg.textContent = e.message; }
    });
    $('#c-delete').addEventListener('click', async () => { if (!confirm('Delete this customer?')) return; try { await api('customer/' + id, { method: 'DELETE' }); closeDrawer(); state.overview = null; loadCustomers(true); } catch (e) { alert(e.message); } });
  }

  /* ---------- activity ---------- */
  async function renderActivity() {
    const A = state.activity; if (!A.day) A.day = new Date().toISOString().slice(0, 10);
    main.innerHTML = top('Activity', `<input type="date" id="aday" value="${A.day}" style="font:inherit;padding:8px 12px;border-radius:12px;border:1px solid var(--line-2)"><select id="atype" style="font:inherit;padding:8px 12px;border-radius:12px;border:1px solid var(--line-2)"><option value="">All events</option>${['pageview', 'engagement', 'cta_click', 'call_click', 'outbound', 'form_start', 'form_step', 'form_submit', 'search'].map((t) => `<option ${A.type === t ? 'selected' : ''} value="${t}">${t.replace('_', ' ')}</option>`).join('')}</select><span class="live"><i></i>auto-refresh</span>`) + '<div class="panel" id="feed"><div class="empty">Loading…</div></div>';
    $('#aday').addEventListener('change', (e) => { A.day = e.target.value; loadFeed(); });
    $('#atype').addEventListener('change', (e) => { A.type = e.target.value; loadFeed(); });
    loadFeed();
    liveTimer = setInterval(loadFeed, 15000);
  }
  async function loadFeed() {
    const A = state.activity;
    let d; try { d = await api('events?' + new URLSearchParams({ day: A.day, type: A.type, limit: 200 })); } catch (e) { const f = $('#feed'); if (f) f.innerHTML = `<div class="empty">${esc(e.message)}</div>`; return; }
    const f = $('#feed'); if (!f) return;
    const label = (e) => e.type === 'engagement' ? `${e.data && e.data.scroll != null ? e.data.scroll + '% scrolled' : ''} ${e.data && e.data.seconds != null ? '· ' + dur(e.data.seconds) : ''}` : e.type === 'cta_click' || e.type === 'call_click' ? (e.data && e.data.label) || e.extra : e.type === 'outbound' ? (e.data && e.data.href) || e.extra : e.type.startsWith('form') ? (e.data && e.data.form) || e.extra : e.title || '';
    f.innerHTML = `<h3>${fmt(d.total)} events on ${esc(d.day)}</h3>` + (d.items.length ? `<div class="feed">${d.items.map((e) => `<div class="ev"><span class="t">${new Date(e.ts).toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })}</span><span class="k">${esc(e.type.replace('_', ' '))}</span><span class="p" title="${esc(e.path)}">${esc(e.path)} <span class="muted">${esc(label(e))}</span></span><span class="m">${esc([e.source, e.device, e.browser, e.city || e.country].filter(Boolean).join(' · '))}</span></div>`).join('')}</div>` : '<div class="empty">Nothing recorded for this day.</div>');
  }

  /* ---------- pages & sources ---------- */
  async function renderPages() {
    main.innerHTML = top('Pages & sources', rangeSeg()); bindRange(renderPages);
    let o; try { o = await loadOverview(); } catch (e) { main.insertAdjacentHTML('beforeend', `<div class="panel"><div class="empty">${esc(e.message)}</div></div>`); return; }
    if (state.view !== 'pages') return;
    const t = o.totals;
    main.insertAdjacentHTML('beforeend', `<div class="row2"><div class="panel"><h3>All pages <span class="small muted">${fmt(t.pageviews)} views</span></h3>${bars(t.pages)}</div><div><div class="panel" style="margin-bottom:14px"><h3>Sources</h3>${bars(t.sources)}</div><div class="panel" style="margin-bottom:14px"><h3>Landing pages</h3>${bars(t.entry)}</div><div class="panel"><h3>Countries</h3>${bars(t.countries, (c) => c === '??' ? 'Unknown' : c)}</div></div></div>
      <div class="row2"><div class="panel"><h3>Buttons &amp; links</h3>${bars(t.ctas)}</div><div class="panel"><h3>Engagement</h3>${bars([{ name: 'Outbound clicks', count: t.outbound }, { name: 'Phone taps', count: t.calls }, { name: 'Form starts', count: t.formStarts }, { name: 'Form submissions', count: t.formSubmits }, { name: 'Blog searches', count: t.searches }])}</div></div>`);
  }

  /* ---------- settings ---------- */
  function renderSettings() {
    main.innerHTML = top('Settings') + `<div class="row2"><div class="panel"><h3>How this works</h3>
      <div class="prose small"><p><strong>Data.</strong> Every page view, click, form start and submission on the website is recorded first-party by <code>/api/track</code> and <code>/api/submit</code> and stored in Netlify Blobs on this site. Nothing is sent to third parties.</p>
      <p><strong>Access.</strong> Sign-in uses the <code>ADMIN_PASSWORD</code> environment variable (Site configuration → Environment variables in Netlify). Change it there and redeploy to rotate it; sessions last 7 days and sign-in is rate limited.</p>
      <p><strong>Customers.</strong> Import subscriber, user or client lists (CSV, TSV or JSON) on the Customers page; rows are matched by email so re-importing an updated export refreshes records instead of duplicating them.</p>
      <p><strong>Exports.</strong> Leads and customers can be exported as CSV from their pages. Daily traffic rollups are cached so the dashboard stays fast as history grows.</p>
      <p><strong>Deploy contexts.</strong> Production and branch deploys share one data store; deploy previews use an isolated store so testing never pollutes real numbers.</p></div></div>
      <div class="panel"><h3>Account</h3><p class="small muted">Signed in as administrator.</p><div class="btn-row"><button class="btn btn-ghost btn-sm" id="logout2">Sign out</button><a class="btn btn-primary btn-sm" href="${API}/admin/export.csv?days=3650">Download all leads</a></div></div></div>`;
    $('#logout2').addEventListener('click', async () => { await api('logout', { method: 'POST' }); showLogin(); });
  }
})();
