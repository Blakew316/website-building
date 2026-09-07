# Charlie Company Media — website redesign

A complete, professional redesign and rebrand of the archived Townsquare Interactive site
(the six `tsi-*.zip` files in this repo) as **Charlie Company Media** — a consultative, Apple-style
marketing site with the Charlie Company emblem, a navy/off-white palette, a fully regenerated static
site, and a password-protected admin dashboard that records every visit and lead.

Every page in the archive is recreated: the home page, all Grow/Run product pages, every
industry page, all 235 location pages, pricing, about, FAQ, case studies, portfolio/projects,
careers (main site + careers sub-site merged), the help-center sign-in/agent/password pages,
every legal page, and the full blog — 719 posts, 44 categories, 590 tags and 5 author archives —
plus a working blog search, a 404 page, sitemap and robots.

```
build/               generator (Python 3.11+, beautifulsoup4, lxml)
  extract.py         archive HTML  →  content/*.json   (structured, rebranded content)
  site.py            content/*.json →  site/           (the finished website)
  icons.py           inline SVG icon set + animated product mockups
  assets/            main.css, main.js, emblem.svg, og.png, apple-touch-icon.png,
                     admin.html + admin.js (the /admin/ dashboard)
                     (CSS/JS are copied to site/assets/v/ with a content hash in the filename)
  checklinks.py      verifies every internal link in site/ resolves
content/             extracted content (pages, posts, taxonomy) — the "CMS"
site/                the generated website — deploy this folder as-is
netlify/functions/   track (analytics beacon), submit (form submissions), admin (dashboard API)
build.sh             one command: unzip → extract → render → link-check
```

## Build

```bash
pip install beautifulsoup4 lxml
./build.sh            # writes site/
python3 -m http.server -d site 8080
```

`build/site.py` alone re-renders the site from `content/` in ~30 seconds; `build/extract.py`
only needs to run again if the source archive changes.

## Admin dashboard, leads and analytics

Every page view, scroll depth, time on page, button/phone/outbound click, form start and form
submission is recorded first-party by `netlify/functions/track.mjs` and `submit.mjs` and stored in
Netlify Blobs (no third-party analytics). The dashboard at **`/admin/`** shows visitors, pageviews,
sessions, leads, conversion, sources, locations, devices, busiest hours, landing pages, a live
"online now" count, an activity feed, and a leads inbox with status/notes and CSV export.

* **Sign-in** uses the `ADMIN_PASSWORD` environment variable (Netlify → Site configuration →
  Environment variables). Sessions are signed HttpOnly cookies valid for 7 days; sign-in attempts are
  rate limited per IP. Optionally set `ADMIN_SESSION_SECRET` to rotate sessions independently.
* **Storage** — production and branch deploys share the site's global blob store; deploy previews use
  an isolated per-deploy store. Daily traffic rollups are cached so the dashboard stays fast.
* **Tests** — `npm test` exercises track → submit → admin against an in-memory store.

## Deploy

`site/` is plain static HTML — drop it on Netlify, Vercel, Cloudflare Pages, S3 or GitHub Pages.

* **Netlify** — `netlify.toml` at the repo root sets the publish directory to `site` with no build
  command and points functions at `netlify/functions` (`package.json` pulls in `@netlify/blobs`), so
  "import from Git" works as-is. Set `ADMIN_PASSWORD` before the first deploy to use `/admin/`. Deploy the branch that contains the redesign (this PR's
  branch, or `main` once it is merged); `main` before the merge only holds the zip archives, which is
  why a deploy from it shows Netlify's "Page not found". If you configured the site in the Netlify UI
  before this file existed, set *Site settings → Build & deploy → Publish directory* to `site` (or
  just trigger a new deploy — `netlify.toml` takes precedence). `site/_redirects` maps the old
  site's dead URLs to their new homes and serves `404.html` for unknown paths. If the Netlify
  production branch is currently the PR branch, switch it to `main` (Site settings → Build & deploy
  → Branches) right after merging and before deleting the branch, then trigger a deploy.
* **GitHub Pages** — `.github/workflows/pages.yml` builds and publishes `site/` on every push to
  `main` (enable Pages → "GitHub Actions" in the repo settings).
* **Anything else** — upload the contents of `site/` to the web root.

## Brand & design system

* **Name / logo** — *Charlie Company Media*: the supplied eagle-globe-anchor emblem, redrawn as a
  single-colour vector (`build/assets/emblem.svg`) so it scales from the favicon to the OG image.
  Wordmark "Charlie Company" with a small "MEDIA" descriptor.
* **Typography** — Apple system stack (`-apple-system, SF Pro, Helvetica Neue…`) with Inter as the
  cross-platform fallback; tight negative letter-spacing on display sizes, fluid `clamp()` scale.
* **Color** — the emblem's navy (`#0b1f3f`) and off-white (`#f5f6fa`) only. Every accent is a
  tint or shade of that navy (navy → steel → sky → mist): gradient orbs behind heroes, soft squircle
  icon tiles, chips, gradient text — never solid colour blocks. Buttons are Apple-style pills:
  navy primary, light-grey secondary, blue text links with a chevron.
* **Copy** — headings carry the message; descriptive sub-copy under headings was removed
  everywhere except documents (blog posts, legal pages, FAQ answers).
* **Icons** — an SF Symbols-style set (1.5pt rounded strokes on a 24pt grid) in `build/icons.py`.
* **Motion** — word-by-word headline reveal, scroll-reveal with stagger, animated count-up stats,
  floating device mockups with pointer tilt, drifting gradient orbs, industry marquee, smooth
  accordions, testimonial carousel, lightbox, multi-step quote form with progress bar. All motion
  respects `prefers-reduced-motion`.
* **Mockups** — the old platform's screenshots were replaced by self-contained animated SVG
  product mockups (dashboard, CRM, inbox, calendar, invoice, reviews, search-everywhere diagram,
  ads, map, phone) so no page depends on external imagery to look finished.

## What changed vs. the archive (and why)

| Area | Decision |
| --- | --- |
| Brand text | Every "Townsquare Interactive / Townsquare / TSI" mention is rewritten to Meridian Local. |
| Navigation | The five-link header became mega-menus (Grow, Run, Industries, Support, Company) that reach every page. |
| Imagery | The archive only hot-linked a CDN that no longer serves anything. Photography is now self-hosted under `build/assets/photos/` (27 Adobe Stock free-collection photos licensed to the site owner's Adobe account, served at 1600w/800w), chosen per industry and article topic by `build/illustrations.py`; the old app screenshots are SVG mockups, the portfolio uses browser-frame cards, and the "trusted nationwide" section is a real Albers-projected map of the lower 48 (`build/usmap.py`, state boundaries from `build/data/us-states.json`) with one linked pin per market. No page depends on an external image or video. |
| Forms | Every form (quote, demo, support, privacy request, help-center sign-in/sign-up/reset) is validated in the browser and then sent three ways: to `/api/submit` (stored in Netlify Blobs for the `/admin/` leads inbox), to **Netlify Forms** (the hidden definitions live at `/forms/`; Netlify emails each submission to the address configured under *Forms → Form notifications*), and, when `RESEND_API_KEY` is set alongside `NOTIFY_EMAIL`, straight to the owner's inbox from the function. Passwords are never forwarded. `FORM_ENDPOINT` in `build/site.py` can add a fourth destination. |
| Privacy web form | The Osano DSAR iframe is replaced by a native privacy-request form. |
| Help center | The Zendesk sign-in / agent sign-in / password pages are recreated as static pages under `/help-center/`. |
| Careers | `careers.townsquareinteractive.com` is merged into `/careers/` (jobs link → `#open-roles`). |
| Blog archives | Same URLs for every post, category, tag and author; archives paginate 12 per page (`/page/N/`), so page numbers differ from the original. |
| Search | New `/search/` page with a client-side index of all posts (also used by the 404 page and old dead blog links). |
| Dead links | ~100 legacy links found in the archive are mapped to their nearest live page (see `DEAD_LINKS` in `build/extract.py`). |
| Contact details | Phone, address and hours are kept from the archive. Social links point to generic profiles — replace them in `build/site.py` (`footer()`). |
| Test pages | `/form-test/` and `/locations-test/` are kept but marked `noindex`. |

## Verification

`python3 build/checklinks.py site` checks every internal `href`/`src` in the generated site
(316k references, 0 missing). Page coverage was checked against `MANIFEST.csv` from the archive:
every non-pagination URL exists in `site/`.
