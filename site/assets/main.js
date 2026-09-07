/* Meridian Local — site behaviour (no dependencies) */
(function () {
  'use strict';
  const $ = (s, r) => (r || document).querySelector(s);
  const $$ = (s, r) => Array.from((r || document).querySelectorAll(s));
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- header ---------- */
  const header = $('.site-header');
  const onScroll = () => header && header.classList.toggle('scrolled', window.scrollY > 8);
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });

  const toggle = $('.nav-toggle');
  if (toggle) {
    toggle.addEventListener('click', () => {
      const open = document.body.classList.toggle('nav-open');
      toggle.setAttribute('aria-expanded', String(open));
    });
  }

  // mega menus: hover on desktop, click on touch / mobile
  const isDesktop = () => window.matchMedia('(min-width: 901px)').matches;
  $$('.nav > li.has-mega').forEach((li) => {
    const btn = $('.nav-link', li);
    let t;
    const open = () => { $$('.nav > li.open').forEach((o) => o !== li && o.classList.remove('open')); li.classList.add('open'); btn.setAttribute('aria-expanded', 'true'); };
    const close = () => { li.classList.remove('open'); btn.setAttribute('aria-expanded', 'false'); };
    li.addEventListener('mouseenter', () => { if (isDesktop()) { clearTimeout(t); open(); } });
    li.addEventListener('mouseleave', () => { if (isDesktop()) { t = setTimeout(close, 160); } });
    btn.addEventListener('click', (e) => { e.preventDefault(); li.classList.contains('open') ? close() : open(); });
    li.addEventListener('keydown', (e) => { if (e.key === 'Escape') { close(); btn.focus(); } });
    li.addEventListener('focusout', (e) => { if (isDesktop() && !li.contains(e.relatedTarget)) close(); });
  });
  document.addEventListener('click', (e) => { if (!e.target.closest('.nav')) $$('.nav > li.open').forEach((o) => o.classList.remove('open')); });

  /* ---------- reveal on scroll ---------- */
  const revealEls = $$('[data-reveal]');
  if ('IntersectionObserver' in window && !reduced) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((en) => { if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); } });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    revealEls.forEach((el) => io.observe(el));
  } else {
    revealEls.forEach((el) => el.classList.add('in'));
  }
  // auto-stagger children in grids
  $$('[data-stagger]').forEach((wrap) => { Array.from(wrap.children).forEach((c, i) => { c.style.setProperty('--i', i); }); });

  /* ---------- headline word animation ---------- */
  $$('.words').forEach((h) => {
    if (h.dataset.done) return; h.dataset.done = '1';
    const walk = (node) => {
      Array.from(node.childNodes).forEach((n) => {
        if (n.nodeType === 3) {
          const frag = document.createDocumentFragment();
          n.textContent.split(/(\s+)/).forEach((part) => {
            if (!part) return;
            if (/^\s+$/.test(part)) { frag.appendChild(document.createTextNode(part)); return; }
            const s = document.createElement('span'); s.className = 'w'; s.textContent = part; frag.appendChild(s);
          });
          n.replaceWith(frag);
        } else if (n.nodeType === 1 && n.tagName !== 'BR') { walk(n); }
      });
    };
    walk(h);
    $$('.w', h).forEach((w, i) => w.style.setProperty('--i', i));
  });

  /* ---------- counters ---------- */
  const fmt = (n, dec) => n.toLocaleString('en-US', { minimumFractionDigits: dec, maximumFractionDigits: dec });
  const animateCount = (el) => {
    const raw = el.dataset.count;
    const m = raw.match(/^([^\d]*)([\d,.]+)(.*)$/);
    if (!m) return;
    const prefix = m[1], suffix = m[3];
    const target = parseFloat(m[2].replace(/,/g, ''));
    const dec = (m[2].split('.')[1] || '').length;
    const dur = 1600, start = performance.now();
    const step = (now) => {
      const p = Math.min(1, (now - start) / dur);
      const e = 1 - Math.pow(1 - p, 4);
      el.textContent = prefix + fmt(target * e, dec) + suffix;
      if (p < 1) requestAnimationFrame(step); else el.textContent = raw;
    };
    requestAnimationFrame(step);
  };
  const counters = $$('[data-count]');
  if (counters.length) {
    if ('IntersectionObserver' in window && !reduced) {
      const io2 = new IntersectionObserver((entries) => { entries.forEach((en) => { if (en.isIntersecting) { animateCount(en.target); io2.unobserve(en.target); } }); }, { threshold: 0.4 });
      counters.forEach((c) => io2.observe(c));
    }
  }

  /* ---------- feature accordions ---------- */
  $$('.acc').forEach((acc) => {
    const items = $$('.acc-item', acc);
    items.forEach((it) => {
      const head = $('.acc-head', it);
      head.addEventListener('click', () => {
        const isOpen = it.classList.contains('open');
        items.forEach((o) => { o.classList.remove('open'); $('.acc-head', o).setAttribute('aria-expanded', 'false'); });
        if (!isOpen) { it.classList.add('open'); head.setAttribute('aria-expanded', 'true'); }
      });
    });
  });

  /* ---------- tabs ---------- */
  $$('.tabs').forEach((tabs) => {
    const btns = $$('.tab-list button', tabs), panes = $$('.tab-pane', tabs);
    btns.forEach((b, i) => b.addEventListener('click', () => {
      btns.forEach((x) => x.classList.remove('on')); panes.forEach((x) => x.classList.remove('on'));
      b.classList.add('on'); panes[i] && panes[i].classList.add('on');
    }));
  });

  /* ---------- carousels ---------- */
  $$('.carousel').forEach((c) => {
    const track = $('.carousel-track', c), prev = $('.prev', c), next = $('.next', c), dots = $('.carousel-dots', c);
    const slides = Array.from(track.children);
    if (dots) slides.forEach((s, i) => { const d = document.createElement('i'); if (i === 0) d.classList.add('on'); d.addEventListener('click', () => go(i)); dots.appendChild(d); });
    const go = (i) => { const s = slides[(i + slides.length) % slides.length]; track.scrollTo({ left: s.offsetLeft - track.offsetLeft, behavior: reduced ? 'auto' : 'smooth' }); };
    const cur = () => { let best = 0, bd = 1e9; slides.forEach((s, i) => { const d = Math.abs(s.offsetLeft - track.offsetLeft - track.scrollLeft); if (d < bd) { bd = d; best = i; } }); return best; };
    prev && prev.addEventListener('click', () => go(cur() - 1));
    next && next.addEventListener('click', () => go(cur() + 1));
    track.addEventListener('scroll', () => { if (!dots) return; const i = cur(); $$('i', dots).forEach((d, j) => d.classList.toggle('on', j === i)); }, { passive: true });
    let auto; const start = () => { if (reduced || c.dataset.auto === 'off') return; auto = setInterval(() => go(cur() + 1), 6000); };
    const stop = () => clearInterval(auto);
    c.addEventListener('mouseenter', stop); c.addEventListener('mouseleave', start); c.addEventListener('touchstart', stop, { passive: true });
    start();
  });

  /* ---------- lightbox ---------- */
  let lb = $('.lightbox');
  if (!lb) { lb = document.createElement('div'); lb.className = 'lightbox'; lb.innerHTML = '<button aria-label="Close"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg></button><div class="lb-body"></div>'; document.body.appendChild(lb); }
  const lbBody = $('.lb-body', lb);
  const closeLb = () => { lb.classList.remove('open'); lbBody.innerHTML = ''; };
  $('button', lb).addEventListener('click', closeLb);
  lb.addEventListener('click', (e) => { if (e.target === lb) closeLb(); });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') { closeLb(); document.body.classList.remove('nav-open'); } });
  document.addEventListener('click', (e) => {
    const a = e.target.closest('[data-lightbox]');
    if (!a) return;
    e.preventDefault();
    const src = a.getAttribute('data-lightbox') || a.getAttribute('href');
    if (/youtube|youtu\.be|vimeo/.test(src)) {
      const u = src.includes('?') ? src + '&autoplay=1' : src + '?autoplay=1';
      lbBody.innerHTML = '<iframe src="' + u + '" allow="autoplay; encrypted-media; picture-in-picture" allowfullscreen title="Video"></iframe>';
    } else if (/\.mp4(\?|$)/i.test(src)) {
      lbBody.innerHTML = '<video controls autoplay playsinline src="' + src + '" style="max-height:85vh;max-width:min(100%,1000px);border-radius:16px"></video>';
    } else {
      lbBody.innerHTML = '<img src="' + src + '" alt="">';
    }
    lb.classList.add('open');
  });

  /* ---------- inline videos ---------- */
  $$('.video-card').forEach((card) => {
    const v = $('video', card), play = $('.play', card);
    if (!v || !play) return;
    play.addEventListener('click', () => { card.classList.add('playing'); v.setAttribute('controls', ''); v.play().catch(() => {}); });
    v.addEventListener('error', () => { card.classList.add('broken'); });
  });

  /* ---------- filterable gallery ---------- */
  $$('.filter-bar').forEach((bar) => {
    const target = $(bar.dataset.target);
    if (!target) return;
    $$('button', bar).forEach((b) => b.addEventListener('click', () => {
      $$('button', bar).forEach((x) => x.classList.remove('on')); b.classList.add('on');
      const f = b.dataset.filter;
      $$('[data-cat]', target).forEach((it, i) => { const show = f === 'all' || it.dataset.cat === f; it.style.display = show ? '' : 'none'; if (show) { it.classList.remove('in'); it.style.setProperty('--i', i % 9); requestAnimationFrame(() => it.classList.add('in')); } });
    }));
  });

  /* ---------- rotating text ---------- */
  $$('.rotating').forEach((r) => {
    const items = Array.from(r.children); if (items.length < 2) return;
    let i = 0; items[0].classList.add('on');
    if (reduced) return;
    setInterval(() => { items[i].classList.remove('on'); i = (i + 1) % items.length; items[i].classList.add('on'); }, 2600);
  });

  /* ---------- image fallbacks ---------- */
  const fallbackSVG = (label) => {
    let t = (label || '').replace(/[^A-Za-z0-9 &'.,-]/g, '').trim();
    if (/^[\w-]+$/.test(t) && /[-_]|\d/.test(t)) t = '';           // looks like a filename → no caption
    if (/\.(png|jpe?g|webp|gif)$/i.test(t)) t = '';
    t = t.slice(0, 48);
    const caption = t ? '<text x="400" y="452" text-anchor="middle" font-family="-apple-system,Inter,Helvetica,Arial,sans-serif" font-size="22" font-weight="600" fill="#1d4fd7" opacity=".8">' + t.replace(/&/g, '&amp;') + '</text>' : '';
    return 'data:image/svg+xml;utf8,' + encodeURIComponent(
      '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600"><defs><linearGradient id="g" x1="0" x2="1" y1="0" y2="1"><stop offset="0" stop-color="#e9efff"/><stop offset=".55" stop-color="#efeaff"/><stop offset="1" stop-color="#e3f6f2"/></linearGradient><linearGradient id="a" x1="0" x2="1"><stop offset="0" stop-color="#2f6df6"/><stop offset="1" stop-color="#7a5af8"/></linearGradient></defs>'
      + '<rect width="800" height="600" fill="url(#g)"/>'
      + '<rect x="150" y="120" width="500" height="320" rx="26" fill="#fff" opacity=".85"/>'
      + '<rect x="150" y="120" width="500" height="44" rx="26" fill="#f2f4f9"/><rect x="150" y="146" width="500" height="18" fill="#f2f4f9"/>'
      + '<circle cx="176" cy="142" r="5" fill="#dfe4ee"/><circle cx="192" cy="142" r="5" fill="#dfe4ee"/><circle cx="208" cy="142" r="5" fill="#dfe4ee"/>'
      + '<rect x="180" y="190" width="150" height="14" rx="7" fill="#dfe4ee"/><rect x="180" y="216" width="220" height="10" rx="5" fill="#eaeef5"/><rect x="180" y="234" width="190" height="10" rx="5" fill="#eaeef5"/>'
      + '<rect x="180" y="270" width="120" height="34" rx="17" fill="url(#a)" opacity=".9"/>'
      + '<rect x="430" y="190" width="190" height="220" rx="16" fill="#f7f8fb"/>'
      + '<rect x="452" y="300" width="22" height="86" rx="6" fill="#2f6df6" opacity=".55"/><rect x="484" y="270" width="22" height="116" rx="6" fill="#2f6df6" opacity=".7"/><rect x="516" y="330" width="22" height="56" rx="6" fill="#7a5af8" opacity=".6"/><rect x="548" y="250" width="22" height="136" rx="6" fill="#7a5af8" opacity=".85"/><rect x="580" y="290" width="22" height="96" rx="6" fill="#0fa38f" opacity=".7"/>'
      + '<rect x="452" y="210" width="90" height="10" rx="5" fill="#dfe4ee"/>'
      + caption + '</svg>'
    );
  };
  const handleImgError = (img) => {
    if (img.dataset.fallback) return;
    img.dataset.fallback = '1';
    img.src = fallbackSVG(img.getAttribute('alt') || img.getAttribute('title') || '');
    img.style.objectFit = 'cover';
  };
  $$('img').forEach((img) => {
    if (img.complete && img.naturalWidth === 0 && img.src && !img.src.startsWith('data:')) handleImgError(img);
    img.addEventListener('error', () => handleImgError(img));
  });

  /* ---------- forms ---------- */
  const ENDPOINT = document.documentElement.dataset.formEndpoint || '';
  const validate = (fields) => {
    let ok = true;
    fields.forEach((f) => {
      const wrap = f.closest('.field');
      let valid = f.checkValidity();
      if (f.type === 'email' && f.value && !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(f.value)) valid = false;
      if (f.type === 'tel' && f.value && f.value.replace(/\D/g, '').length < 10) valid = false;
      f.setAttribute('aria-invalid', valid ? 'false' : 'true');
      wrap && wrap.classList.toggle('invalid', !valid);
      if (!valid) ok = false;
    });
    return ok;
  };
  $$('form[data-form]').forEach((form) => {
    const steps = $$('.form-step', form);
    const bar = $('.form-progress i', form), stepLabel = $('.form-steps .cur', form);
    let idx = 0;
    const show = (i) => {
      idx = i; steps.forEach((s, j) => s.classList.toggle('active', j === i));
      if (bar) bar.style.width = ((i + 1) / steps.length * 100) + '%';
      if (stepLabel) stepLabel.textContent = 'Step ' + (i + 1) + ' of ' + steps.length;
      const first = $('input:not([type=hidden]):not([type=checkbox])', steps[i]); if (first && i > 0) first.focus();
    };
    $$('[data-next]', form).forEach((b) => b.addEventListener('click', () => { if (validate($$('input,textarea,select', steps[idx]))) show(Math.min(idx + 1, steps.length - 1)); }));
    $$('[data-prev]', form).forEach((b) => b.addEventListener('click', () => show(Math.max(idx - 1, 0))));
    if (steps.length) show(0);
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const scope = steps.length ? steps[idx] : form;
      if (!validate($$('input,textarea,select', scope))) return;
      if ($('.hp input', form) && $('.hp input', form).value) return; // honeypot
      const btn = $('[type=submit]', form); btn && (btn.disabled = true, btn.textContent = 'Sending…');
      const data = new FormData(form);
      let sent = false;
      const action = form.getAttribute('action') || ENDPOINT;
      if (action) {
        try {
          const res = await fetch(action, { method: 'POST', body: data, headers: { Accept: 'application/json' } });
          sent = res.ok;
        } catch (err) { sent = false; }
      }
      try { localStorage.setItem('ml_lead_' + Date.now(), JSON.stringify(Object.fromEntries(data))); } catch (err) {}
      if (form.dataset.redirect && (sent || !action)) { window.location.href = form.dataset.redirect; return; }
      form.innerHTML = '<div class="form-success"><div class="icon-tile lg teal"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg></div><h3>Thanks — we\'ve got it.</h3><p class="muted">A member of our team will reach out shortly. If you contacted us after hours, we\'ll call you the next business day.</p></div>';
    });
  });

  /* ---------- cookie notice ---------- */
  const cookie = $('.cookie');
  if (cookie) {
    let seen = false; try { seen = localStorage.getItem('ml_cookie') === '1'; } catch (e) {}
    if (!seen) setTimeout(() => cookie.classList.add('show'), 1200);
    $('button', cookie).addEventListener('click', () => { cookie.classList.remove('show'); try { localStorage.setItem('ml_cookie', '1'); } catch (e) {} });
  }

  /* ---------- table of contents highlight ---------- */
  const toc = $('.toc');
  if (toc && 'IntersectionObserver' in window) {
    const links = $$('a', toc);
    const heads = links.map((a) => $(a.getAttribute('href'))).filter(Boolean);
    const io3 = new IntersectionObserver((entries) => { entries.forEach((en) => { if (en.isIntersecting) { links.forEach((l) => l.classList.toggle('on', l.getAttribute('href') === '#' + en.target.id)); } }); }, { rootMargin: '-20% 0px -70% 0px' });
    heads.forEach((h) => io3.observe(h));
  }

  /* ---------- subtle parallax on hero art ---------- */
  if (!reduced && window.matchMedia('(pointer: fine)').matches) {
    $$('.tilt').forEach((el) => {
      const parent = el.closest('.hero-art') || el.parentElement;
      parent.addEventListener('mousemove', (e) => {
        const r = parent.getBoundingClientRect();
        const x = (e.clientX - r.left) / r.width - 0.5, y = (e.clientY - r.top) / r.height - 0.5;
        el.style.transform = 'perspective(1200px) rotateY(' + (x * 6) + 'deg) rotateX(' + (-y * 6) + 'deg)';
      });
      parent.addEventListener('mouseleave', () => { el.style.transform = ''; });
    });
  }

  /* ---------- search ---------- */
  const searchRoot = $('[data-search]');
  if (searchRoot) {
    const input = $('input', searchRoot), results = $('.results', searchRoot), meta = $('.results-meta', searchRoot);
    let index = null;
    const esc = (s) => s.replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
    const hi = (s, q) => { if (!q) return esc(s); const rx = new RegExp('(' + q.split(/\s+/).filter(Boolean).map((w) => w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|') + ')', 'ig'); return esc(s).replace(rx, '<mark>$1</mark>'); };
    const run = () => {
      const q = input.value.trim().toLowerCase();
      if (!index) return;
      const words = q.split(/\s+/).filter(Boolean);
      const scored = index.map((p) => {
        const hay = (p.t + ' ' + p.e + ' ' + (p.c || '')).toLowerCase();
        let score = 0; words.forEach((w) => { if (p.t.toLowerCase().includes(w)) score += 5; if (hay.includes(w)) score += 1; });
        return { p, score };
      }).filter((x) => words.length ? x.score > 0 : true).sort((a, b) => b.score - a.score || (b.p.d > a.p.d ? 1 : -1)).slice(0, 60);
      meta.textContent = words.length ? scored.length + ' result' + (scored.length === 1 ? '' : 's') + ' for “' + input.value.trim() + '”' : 'Showing the latest articles. Type to search ' + index.length + ' posts.';
      results.innerHTML = scored.map(({ p }) => '<article class="post-card" data-reveal class="in"><div class="body"><div class="cats">' + (p.c ? p.c.split('|').slice(0, 2).map((c) => '<a href="' + c.split('~')[1] + '">' + esc(c.split('~')[0]) + '</a>').join('') : '') + '</div><h3><a href="' + p.u + '">' + hi(p.t, q) + '</a></h3><p class="excerpt">' + hi(p.e, q) + '</p><div class="meta"><span>' + esc(p.d) + '</span></div></div></article>').join('') || '<p class="muted">No matches. Try a different word, or browse the <a href="/blog/">latest posts</a>.</p>';
      $$('[data-reveal]', results).forEach((el) => el.classList.add('in'));
    };
    fetch('/search.json').then((r) => r.json()).then((d) => { index = d; const q = new URLSearchParams(location.search).get('q'); if (q) input.value = q; run(); });
    input.addEventListener('input', () => { run(); const u = new URL(location); u.searchParams.set('q', input.value); history.replaceState(null, '', u); });
  }
  $$('[data-search-open]').forEach((b) => b.addEventListener('click', () => { location.href = '/search/'; }));

  /* ---------- current year ---------- */
  $$('[data-year]').forEach((el) => { el.textContent = new Date().getFullYear(); });
})();
