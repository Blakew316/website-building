# Meridian Local — website redesign

A complete, professional redesign and rebrand of the archived Townsquare Interactive site
(the six `tsi-*.zip` files in this repo) as **Meridian Local** — a consultative, Apple-style
marketing site with a new brand, a new logo and a fully regenerated static site.

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
  assets/            main.css, main.js, logo.svg, og.png, apple-touch-icon.png
  checklinks.py      verifies every internal link in site/ resolves
content/             extracted content (pages, posts, taxonomy) — the "CMS"
site/                the generated website — deploy this folder as-is
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

## Deploy

`site/` is plain static HTML — drop it on Netlify, Vercel, Cloudflare Pages, S3 or GitHub Pages.
A `_redirects` file (Netlify format) maps the old site's dead URLs to their new homes, and
`.github/workflows/pages.yml` builds and publishes `site/` to GitHub Pages on every push to `main`
(enable Pages → "GitHub Actions" in the repo settings).

## Brand & design system

* **Name / logo** — *Meridian Local*: a dark rounded square holding a circle bisected by a
  gradient meridian line with a marker at the apex. Wordmark "Meridian" with a small "LOCAL"
  descriptor. Source: `build/assets/logo.svg` (also used as the favicon).
* **Typography** — Apple system stack (`-apple-system, SF Pro, Helvetica Neue…`) with Inter as the
  cross-platform fallback; tight negative letter-spacing on display sizes, fluid `clamp()` scale.
* **Color** — white and soft "paper" surfaces only. Blue, violet, teal, amber, rose and green
  appear as *hues*: gradient orbs behind heroes, tinted icon tiles, chips, the gradient meridian
  line, gradient text — never as solid color blocks. Buttons are ink-black pills.
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
| Product screenshots | PNG screenshots of the old app are replaced with SVG mockups; photos (JPG/WEBP) are kept and hot-linked from the original CDN with a branded fallback if they ever fail to load. |
| Forms | The Gravity Forms quote/support forms are rebuilt as accessible, validated forms. Set `FORM_ENDPOINT` in `build/site.py` (Formspree, Netlify Forms, your API) to receive submissions; until then submissions show an inline success state / redirect to `/thank-you/`. |
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
