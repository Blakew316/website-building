#!/usr/bin/env python3
"""
site.py — render the Meridian Local static site from content/*.json.

Usage:
    python3 build/site.py --content content --out site
"""
from __future__ import annotations

import argparse
import html as htmlmod
import json
import math
import os
import re
import shutil
from collections import defaultdict
from datetime import datetime

from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning
import warnings

warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)

import icons as I  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# Site configuration
# ---------------------------------------------------------------------------
BRAND = "Meridian Local"
BRAND_SHORT = "Meridian"
TAGLINE = "Growth infrastructure for local business."
SITE_URL = "https://www.meridianlocal.com"
PHONE = "(855) 463-5490"
PHONE_TEL = "tel:+18554635490"
ADDRESS = "200 South College Street, Suite 400, Charlotte, NC 28202"
HOURS = "Monday – Friday, 9:00am – 5:00pm EST"
FORM_ENDPOINT = ""  # e.g. "https://formspree.io/f/xxxx" — leave empty to use the built-in success state
# Where "Client login" in the header/footer and /login/ send existing customers to view their
# platform and monthly reporting. Point this at the live Business Platform sign-in URL when known.
CLIENT_LOGIN_URL = "/help-center/sign-in/"
POSTS_PER_PAGE = 12
APP_IOS = "https://apps.apple.com/us/app/townsquare-app/id1493986303"
APP_ANDROID = "https://play.google.com/store/apps/details?id=com.townsquare.mobileapp&hl=en_US&gl=US"

GROW_ITEMS = [
    ("/website-design/", "Website Design & Management", "Conversion-focused sites, managed for you", "layout"),
    ("/search-engine-optimization/", "Search Everywhere Optimization", "SEO, AEO and AI visibility", "search"),
    ("/business-listings/", "Local Online Listings", "Accurate everywhere customers look", "pin"),
    ("/reputation-management/", "Reputation Management", "Monitor and grow your reviews", "star"),
    ("/social-media-marketing/", "Social Media Marketing", "Managed posting and engagement", "share"),
    ("/targeted-social-ads/", "Targeted Social Ads", "Facebook and Instagram campaigns", "megaphone"),
    ("/targeted-display-ads/", "Targeted Display Ads", "Reach your market across the web", "eye"),
    ("/lead-conversion-tool/", "Lead Conversion Tool", "Turn visitors into booked jobs", "target"),
    ("/monthly-reporting/", "Monthly Reporting", "Clear performance insights", "chart"),
    ("/online-ordering/", "Online Ordering", "Takeout, pickup and delivery", "utensils"),
]
RUN_ITEMS = [
    ("/integrated-inbox/", "Integrated Inbox", "Every conversation in one place", "inbox"),
    ("/integrated-calendar/", "Integrated Calendar", "Online booking and scheduling", "calendar"),
    ("/estimate-invoice-and-billing/", "Estimates, Invoices & Billing", "Quote, invoice and get paid", "invoice"),
    ("/cloud-based-crm/", "Cloud-Based CRM", "Leads, contacts and history", "users"),
    ("/automated-email-and-sms/", "Automated Email & SMS", "Follow up without the busywork", "mail"),
    ("/merchant-services/", "Merchant Services", "Fast, secure payments", "card"),
    ("/business-domains/", "Business Domains", "Register and manage your domain", "globe"),
    ("/business-email-management/", "Business Email Management", "Professional email for your team", "mail"),
    ("/ecommerce/", "Ecommerce", "Sell online, track everything", "bag"),
]
INDUSTRY_ITEMS = [
    ("/local-business-digital-marketing/", "Local Business", "hammer"),
    ("/hvac-marketing/", "HVAC", "snowflake"),
    ("/home-remodeling-marketing/", "Home Remodeling", "home"),
    ("/tree-service-marketing/", "Tree Service", "tree"),
    ("/food-and-beverage-marketing/", "Food & Beverage", "utensils"),
    ("/towing-marketing/", "Towing", "truck"),
    ("/roofing-marketing/", "Roofing", "roof"),
    ("/plumbing-marketing/", "Plumbing", "drop"),
    ("/legal-marketing-service/", "Legal", "scale"),
    ("/landscaping-marketing/", "Landscaping", "leaf"),
    ("/general-contracting-marketing/", "General Contracting", "wrench"),
]
SUPPORT_ITEMS = [
    ("/personal-support/", "Personal Support", "A team that knows your business", "headset"),
    ("/phone-support/", "Phone Support", "Real people, M–F 9–5 EST", "phone"),
    ("/relationship-manager/", "Dedicated Relationship Manager", "One point of contact", "user"),
    ("/what-to-expect/", "What to Expect", "How onboarding and campaigns work", "compass"),
    ("/frequently-asked-questions/", "FAQ", "Answers to common questions", "help"),
    ("/support/", "Contact Support", "Send us a message", "message"),
    ("/help-center/", "Help Center", "Sign in to your account", "key"),
    (CLIENT_LOGIN_URL, "Client login", "View your platform and monthly reporting", "chart"),
]
COMPANY_ITEMS = [
    ("/about-us/", "About Us", "Who we are and how we work", "users"),
    ("/case-studies/", "Case Studies", "Real results from real businesses", "award"),
    ("/our-work/", "Our Work", "A portfolio of client websites", "layout"),
    ("/pricing/", "Pricing & Packages", "Built around your business", "dollar"),
    ("/locations/", "Locations", "Markets we serve across the U.S.", "map"),
    ("/careers/", "Careers", "Join the team", "briefcase"),
    ("/blog/", "Blog", "Insights for local business", "document"),
    ("/directory-scan/", "Free Directory Scan", "Check your listings in seconds", "search"),
]

LEGAL_LINKS = [
    ("/privacy-policy/", "Privacy Policy"),
    ("/terms-of-service/", "Terms of Service"),
    ("/hosting-terms/", "Hosting Terms"),
    ("/exhibit-a-client-website-standard-terms-of-use/", "Client Website Terms of Use"),
    ("/exhibit-b-client-website-standard-privacy-policy/", "Client Website Privacy Policy"),
    ("/privacy-web-form/", "Privacy Request Form"),
]

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def esc(s) -> str:
    return htmlmod.escape(str(s or ""), quote=True)


def text_of(h: str) -> str:
    if not h:
        return ""
    return re.sub(r"\s+", " ", BeautifulSoup(h, "lxml").get_text(" ")).strip()


def heading_html(h: str, keep_br: bool = False) -> str:
    if not h:
        return ""
    if keep_br:
        return h
    if text_of(h).isupper() and len(text_of(h)) > 20:
        return h
    h = re.sub(r"\s*<br\s*/?>\s*", " ", h)
    return re.sub(r"\s+", " ", h).strip()


def slugify(s: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")
    return s or "x"


def initials(name: str) -> str:
    parts = [p for p in re.split(r"\s+", re.sub(r"[^A-Za-z ]", "", name or "")) if p]
    return "".join(p[0] for p in parts[:2]).upper() or "M"


def fmt_date(d: str) -> str:
    try:
        return datetime.strptime(d, "%Y-%m-%d").strftime("%b %-d, %Y")
    except Exception:
        return d or ""


def reading_time(html: str) -> int:
    words = len(text_of(html).split())
    return max(1, round(words / 220))


def arrow() -> str:
    return I.icon("arrow", "arrow")


def btn(text: str, href: str, style: str = "primary", size: str = "", arrow_icon: bool = True, attrs: str = "") -> str:
    cls = f"btn btn-{style}" + (f" btn-{size}" if size else "")
    a = arrow() if arrow_icon and style != "ghost" else ""
    return f'<a class="{cls}" href="{esc(href)}" {attrs}>{esc(text)}{a}</a>'


OLD_BRAND_IMG = re.compile(r"TownsquareInteractive[_-]|Townsquare[_-]Interactive[_-]?(?:logo|lockup)|tsi-logo|TSI-logo|townsquare-logo|Black-Teal-Logo|tsi-icon", re.I)


def is_old_brand_image(src: str | None) -> bool:
    """Only the old company's logo/lock-up files — never the hostname of a hot-linked photo."""
    if not src:
        return False
    return bool(OLD_BRAND_IMG.search(os.path.basename(src.split("?")[0])))


AUTHOR_SLUGS = {
    "david-baloghtownsquaremedia-com": "david-balogh",
    "justin-scismtownsquareinteractive-com": "justin-scism",
    "kate-curtistownsquareinteractive-com": "kate-curtis",
    "stefanie-laschuktownsquareinteractive-com": "editorial-team",
    "victoria-putnamtownsquareinteractive-com": "victoria-putnam",
}
LEGACY: list[tuple[str, str]] = []  # (old path, new path) → redirect stubs + _redirects


def redirect_stub(new_path: str) -> str:
    return (f'<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><title>Redirecting…</title>'
            f'<meta name="robots" content="noindex"><link rel="canonical" href="{esc(SITE_URL + new_path)}">'
            f'<meta http-equiv="refresh" content="0; url={esc(new_path)}"><script>location.replace({json.dumps(new_path)})</script>'
            f'</head><body><p>This page has moved to <a href="{esc(new_path)}">{esc(new_path)}</a>.</p></body></html>')


def is_screenshot(b: dict) -> bool:
    """Product screenshots from the old platform are PNGs; photos are JPG/WEBP."""
    src = (b.get("src") or "").lower().split("?")[0]
    return src.endswith(".png") and not any(k in src for k in ("badge", "logo", "award", "workplace", "brightest", "charlotte-business"))


def mock_from_image(b: dict, ctx: dict, extra_key: str = "") -> str:
    label = re.sub(r"(?i)monthly reporting\s*-\s*", "", b.get("alt") or b.get("title") or "")
    label = re.sub(r"[-_]+", " ", label).strip()
    base = re.sub(r"\.[a-z0-9]+$", "", os.path.basename((b.get("src") or "").split("?")[0])).replace("-", " ").replace("_", " ")
    key = f'{base} {label} {extra_key} {ctx.get("path", "")}'
    return f'<div class="device tilt" data-reveal="scale" style="padding:0;border:0;background:transparent;box-shadow:none">{I.mock_for(key, (label or ctx.get("h1", ""))[:22])}</div>'


def group_label_lists(blocks: list[dict]) -> list[dict]:
    """A short label paragraph ("Technical SEO:") followed by a list → titled blurb."""
    out, i = [], 0
    while i < len(blocks):
        b = blocks[i]
        if b["type"] == "paragraph" and i + 1 < len(blocks) and blocks[i + 1]["type"] == "list":
            t = text_of(b["html"])
            if t and len(t) <= 70 and (t.endswith(":") or re.match(r"^\s*<strong>.*</strong>\s*:?\s*$", b["html"].strip(), re.S)):
                out.append({"type": "blurb", "title": t.rstrip(":").strip(), "blocks": [blocks[i + 1]], "grouped": True})
                i += 2
                continue
        out.append(b)
        i += 1
    return out


def expand_untitled(flat: list[dict]) -> list[dict]:
    out = []
    for b in flat:
        if b["type"] == "blurb" and not b.get("title"):
            out.extend(b["blocks"])
        else:
            out.append(b)
    return group_label_lists(out)


def fix_href(href: str | None, page_path: str, has_form: bool) -> str:
    if not href:
        return "/book-a-demo/"
    if href.startswith("#"):
        if has_form:
            return "#quote-form"
        return "/book-a-demo/"
    return href


def img_tag(b: dict, cls: str = "", lazy: bool = True, sizes_hint: str = "") -> str:
    src = b.get("src") or ""
    if is_old_brand_image(src):
        return ""
    alt = b.get("alt") or b.get("title") or ""
    wh = ""
    if b.get("w") and b.get("h"):
        wh = f' width="{b["w"]}" height="{b["h"]}"'
    lz = ' loading="lazy" decoding="async"' if lazy else ' decoding="async" fetchpriority="high"'
    c = f' class="{cls}"' if cls else ""
    return f'<img{c} src="{esc(src)}" alt="{esc(alt)}"{wh}{lz}>'


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------
LOGO_SVG = open(os.path.join(HERE, "assets", "logo.svg"), encoding="utf-8").read().strip()


def logo(with_word: bool = True) -> str:
    word = f'<span class="word">{BRAND_SHORT}<small>Local</small></span>' if with_word else ""
    return f'<a class="brand" href="/" aria-label="{BRAND} home">{LOGO_SVG}{word}</a>'


def mega(items, cols=2, promo=None, big=False) -> str:
    out = []
    per = math.ceil(len(items) / cols)
    for c in range(cols):
        chunk = items[c * per:(c + 1) * per]
        lis = "".join(
            f'<a class="item" href="{esc(h)}"><span class="icon-tile {I.tint(i + c * per)}">{I.icon(ic)}</span><span><strong>{esc(t)}</strong>'
            + (f"<span>{esc(d)}</span>" if d else "") + "</span></a>"
            for i, (h, t, d, ic) in enumerate(chunk))
        out.append(f"<div>{lis}</div>")
    promo_html = ""
    if promo:
        promo_html = f'<div class="promo"><div><strong>{esc(promo[0])}</strong><p>{esc(promo[1])}</p></div>{btn(promo[2], promo[3], "primary", "sm")}</div>'
    total_cols = cols + (1 if promo else 0)
    return f'<div class="mega" style="--cols:{total_cols}"><div class="mega-cols">{"".join(out)}{promo_html}</div></div>'


def header(current: str) -> str:
    def li(label, items, cols, promo):
        return (f'<li class="has-mega"><button class="nav-link" aria-expanded="false" aria-haspopup="true">{esc(label)}{I.icon("chevron")}</button>'
                f'{mega(items, cols, promo)}</li>')

    nav = "".join([
        li("Grow", GROW_ITEMS, 2, ("Grow overview", "See how every channel works together to bring in customers.", "Explore Grow", "/grow/")),
        li("Run", RUN_ITEMS, 2, ("Run overview", "One connected platform to run the day-to-day.", "Explore Run", "/run/")),
        li("Industries", [(h, t, "", ic) for h, t, ic in INDUSTRY_ITEMS] + [("/who-we-work-with/", "All industries", "", "grid")], 2, None),
        li("Support", SUPPORT_ITEMS, 2, None),
        li("Company", COMPANY_ITEMS, 2, None),
        f'<li class="mobile-cta"><div class="btn-row">{btn("Book a demo", "/book-a-demo/", "primary")}<a class="btn btn-ghost" href="{esc(CLIENT_LOGIN_URL)}">{I.icon("key")}Client login</a><a class="btn btn-ghost" href="{PHONE_TEL}">{esc(PHONE)}</a></div></li>',
    ])
    return f'''<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header"><div class="container bar">
  {logo()}
  <ul class="nav" id="nav">{nav}</ul>
  <div class="header-cta">
    <button class="search-btn" data-search-open aria-label="Search">{I.icon("search")}</button>
    <a class="login-link" href="{esc(CLIENT_LOGIN_URL)}">{I.icon("key")}<span>Client login</span></a>
    <a class="phone" href="{PHONE_TEL}">{esc(PHONE)}</a>
    {btn("Book a demo", "/book-a-demo/", "primary", "sm")}
    <button class="nav-toggle" aria-label="Menu" aria-expanded="false" aria-controls="nav"><span></span></button>
  </div>
</div></header>'''


def footer() -> str:
    def col(title, items):
        lis = "".join(f'<li><a href="{esc(h)}">{esc(t)}</a></li>' for h, t in items)
        return f"<div><h4>{esc(title)}</h4><ul>{lis}</ul></div>"

    grow = [(h, t) for h, t, _, _ in GROW_ITEMS]
    run = [(h, t) for h, t, _, _ in RUN_ITEMS]
    industries = [(h, t) for h, t, _ in INDUSTRY_ITEMS]
    company = [(h, t) for h, t, _, _ in COMPANY_ITEMS] + [("/support/", "Contact"), ("/what-to-expect/", "What to Expect"), (CLIENT_LOGIN_URL, "Client login")]
    social = (
        f'<a href="https://www.instagram.com/" aria-label="Instagram" target="_blank" rel="noopener"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor"/></svg></a>'
        f'<a href="https://www.facebook.com/" aria-label="Facebook" target="_blank" rel="noopener"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9"><path d="M14 8h3V4h-3a4 4 0 00-4 4v3H7v4h3v6h4v-6h3l1-4h-4V8z"/></svg></a>'
        f'<a href="https://www.linkedin.com/" aria-label="LinkedIn" target="_blank" rel="noopener"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9"><rect x="3" y="9" width="4" height="12"/><circle cx="5" cy="5" r="2"/><path d="M11 21v-7a3 3 0 016 0v7M11 9v12M17 21v-7"/></svg></a>'
        f'<a href="https://www.google.com/maps" aria-label="Google" target="_blank" rel="noopener">{I.icon("pin")}</a>'
    )
    return f'''<footer class="site-footer"><div class="container">
  <div class="footer-grid">
    <div class="footer-brand">
      {logo()}
      <p>{esc(TAGLINE)} Marketing, business tools and real people — connected in one platform for small and mid-size businesses.</p>
      <div class="reviews-badge"><span class="stars">★★★★★</span><span><strong>5,000+ five-star reviews</strong><span>Thousands of small businesses trust {esc(BRAND_SHORT)}.</span></span></div>
      <p style="margin-top:18px"><a href="{PHONE_TEL}"><strong>{esc(PHONE)}</strong></a><br>{esc(ADDRESS)}<br><span class="small">{esc(HOURS)}</span></p>
      <div class="social">{social}</div>
    </div>
    {col("Grow", grow)}
    {col("Run", run)}
    {col("Industries", industries)}
    {col("Company", company)}
  </div>
  <div class="footer-bottom">
    <div>© <span data-year>2026</span> {esc(BRAND)}. All rights reserved.</div>
    <div class="chip-row">{"".join(f'<a href="{esc(h)}">{esc(t)}</a>' for h, t in LEGAL_LINKS)}<a href="#" data-cookie>Cookie Policy</a></div>
  </div>
</div></footer>
<div class="cookie" role="dialog" aria-label="Cookie notice"><p>We use cookies to understand how the site is used and to improve your experience. See our <a href="/privacy-policy/">privacy policy</a>.</p><button class="btn btn-primary btn-sm">Got it</button></div>'''


_EXT_OLD_LINK = re.compile(r'<a href="https?://(?![^"]*(?:apple\.com|google\.com))[^"]*townsquare[^"]*"[^>]*>(.*?)</a>', re.I | re.S)
SLUG_MAP: dict[str, str] = {}


def finalize_html(html: str) -> str:
    """Last pass over rendered markup: drop links to the old company's sister sites,
    rebrand search queries and remap renamed post/author URLs."""
    html = _EXT_OLD_LINK.sub(r"\1", html)
    html = html.replace("/search/?q=townsquare+interactive", "/search/?q=meridian+local").replace("/search/?q=townsquare", "/search/?q=meridian")
    html = html.replace("townsquarewebhost.com", "meridianwebhost.com")
    for old, new in SLUG_MAP.items():
        html = html.replace(old, new)
    return html


def layout(page: dict, body: str, extra_head: str = "") -> str:
    title = page.get("title") or BRAND
    full_title = title if BRAND in title else f"{title} | {BRAND}"
    desc = page.get("description") or f"{BRAND} — {TAGLINE}"
    path = page.get("path", "/")
    robots = '<meta name="robots" content="noindex">' if page.get("noindex") else ""
    og_image = page.get("image") or f"{SITE_URL}/assets/og.png"
    canonical = SITE_URL + path
    ld = json.dumps({
        "@context": "https://schema.org", "@type": "Organization", "name": BRAND, "url": SITE_URL,
        "telephone": "+1-855-463-5490", "address": {"@type": "PostalAddress", "streetAddress": "200 South College Street, Suite 400", "addressLocality": "Charlotte", "addressRegion": "NC", "postalCode": "28202", "addressCountry": "US"},
    })
    body = finalize_html(body)
    return f'''<!DOCTYPE html>
<html lang="en" data-form-endpoint="{esc(FORM_ENDPOINT)}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(full_title)}</title>
<meta name="description" content="{esc(desc[:300])}">
{robots}
<link rel="canonical" href="{esc(canonical)}">
<meta property="og:type" content="{'article' if page.get('is_post') else 'website'}">
<meta property="og:site_name" content="{esc(BRAND)}">
<meta property="og:title" content="{esc(full_title)}">
<meta property="og:description" content="{esc(desc[:300])}">
<meta property="og:url" content="{esc(canonical)}">
<meta property="og:image" content="{esc(og_image)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#ffffff">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap">
<link rel="stylesheet" href="/assets/main.css">
<script type="application/ld+json">{ld}</script>
{extra_head}
</head>
<body>
{header(path)}
<main id="main">
{body}
</main>
{footer()}
<script src="/assets/main.js" defer></script>
</body>
</html>'''


# ---------------------------------------------------------------------------
# Shared components
# ---------------------------------------------------------------------------
def quote_form(title: str = "Start your free quote", sub: str = "It takes less than a minute. Yes, we timed it.", source: str = "", cta: str = "Get a free quote", compact: bool = False) -> str:
    return f'''<div class="form-card" id="quote-form">
  <h3 class="form-title">{esc(title)}</h3>
  <p class="form-sub">{esc(sub)}</p>
  <form data-form data-redirect="/thank-you/" method="post" action="{esc(FORM_ENDPOINT)}" novalidate>
    <input type="hidden" name="form" value="quote"><input type="hidden" name="source" value="{esc(source)}">
    <p class="hp"><label>Leave this empty<input type="text" name="website" tabindex="-1" autocomplete="off"></label></p>
    <div class="form-steps"><span class="cur">Step 1 of 2</span><span>~60 seconds</span></div>
    <div class="form-progress"><i></i></div>
    <div class="form-step active">
      <div class="field"><label for="q-business-{slugify(source)}">Business name</label><input id="q-business-{slugify(source)}" name="business" type="text" required autocomplete="organization"><span class="error">Please enter your business name.</span></div>
      <div class="field"><label for="q-name-{slugify(source)}">Your name</label><input id="q-name-{slugify(source)}" name="name" type="text" required autocomplete="name"><span class="error">Please enter your name.</span></div>
      <div class="field"><label for="q-email-{slugify(source)}">Email</label><input id="q-email-{slugify(source)}" name="email" type="email" required autocomplete="email"><span class="error">Please enter a valid email.</span></div>
      <div class="form-actions"><button type="button" class="btn btn-primary" data-next>Next {arrow()}</button></div>
    </div>
    <div class="form-step">
      <div class="field-row">
        <div class="field"><label for="q-zip-{slugify(source)}">Zip code</label><input id="q-zip-{slugify(source)}" name="zip" type="text" inputmode="numeric" pattern="[0-9]{{5}}(-[0-9]{{4}})?" required autocomplete="postal-code"><span class="error">Enter a 5-digit zip.</span></div>
        <div class="field"><label for="q-phone-{slugify(source)}">Phone</label><input id="q-phone-{slugify(source)}" name="phone" type="tel" required autocomplete="tel"><span class="error">Enter a valid phone number.</span></div>
      </div>
      <label class="check"><input type="checkbox" name="consent_sms" value="yes"> I consent to receive SMS account notifications from {esc(BRAND)}.</label>
      <label class="check"><input type="checkbox" name="consent_marketing" value="yes"> I consent to receive marketing messages from {esc(BRAND)}.</label>
      <div class="form-actions"><button type="button" class="btn btn-ghost" data-prev>Back</button><button type="submit" class="btn btn-blue">{esc(cta)}</button></div>
      <p class="form-fine">By clicking submit, you are providing express consent to be contacted by {esc(BRAND)} via SMS, call, or email, possibly using automated technology, at the number you provided. Consent is not a condition of purchase. Message and data rates may apply. Reply STOP to opt out. See our <a href="/privacy-policy/">Privacy Policy</a> and <a href="/terms-of-service/">Terms of Service</a>.</p>
    </div>
  </form>
</div>'''


def support_form() -> str:
    return f'''<div class="form-card" id="quote-form">
  <h3 class="form-title">Send us a message</h3>
  <p class="form-sub">We reply within one business day.</p>
  <form data-form data-redirect="/thank-you/" method="post" action="{esc(FORM_ENDPOINT)}" novalidate>
    <input type="hidden" name="form" value="support">
    <p class="hp"><label>Leave this empty<input type="text" name="website" tabindex="-1" autocomplete="off"></label></p>
    <div class="field"><label>Are you a current client?</label>
      <div class="radio-row"><label><input type="radio" name="current_client" value="yes" required> Yes</label><label><input type="radio" name="current_client" value="no"> No</label></div></div>
    <div class="field-row">
      <div class="field"><label for="s-first">First name</label><input id="s-first" name="first_name" type="text" required autocomplete="given-name"><span class="error">Required.</span></div>
      <div class="field"><label for="s-last">Last name</label><input id="s-last" name="last_name" type="text" required autocomplete="family-name"><span class="error">Required.</span></div>
    </div>
    <div class="field"><label for="s-company">Company</label><input id="s-company" name="company" type="text" required autocomplete="organization"><span class="error">Required.</span></div>
    <div class="field-row">
      <div class="field"><label for="s-phone">Phone</label><input id="s-phone" name="phone" type="tel" required autocomplete="tel"><span class="error">Enter a valid phone number.</span></div>
      <div class="field"><label for="s-email">Email</label><input id="s-email" name="email" type="email" required autocomplete="email"><span class="error">Enter a valid email.</span></div>
    </div>
    <div class="field"><label for="s-comments">How can we help?</label><textarea id="s-comments" name="comments" rows="5" required></textarea><span class="error">Please add a short message.</span></div>
    <div class="form-actions"><button type="submit" class="btn btn-blue">Submit {arrow()}</button></div>
    <p class="form-fine">By submitting, you agree to be contacted by {esc(BRAND)} about your request. See our <a href="/privacy-policy/">Privacy Policy</a>.</p>
  </form>
</div>'''


def app_promo(title: str = None, sub: str = None) -> str:
    title = title or f"Get the {BRAND_SHORT} Business Platform app"
    sub = sub or "Manage your business from anywhere, on any device."
    apple = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M16.4 12.6c0-2.5 2-3.7 2.1-3.8-1.2-1.7-3-1.9-3.6-2-1.5-.2-3 .9-3.8.9-.8 0-2-.9-3.3-.9-1.7 0-3.3 1-4.2 2.5-1.8 3.1-.5 7.7 1.3 10.2.9 1.2 1.9 2.6 3.2 2.6 1.3-.1 1.8-.8 3.3-.8s2 .8 3.3.8c1.4 0 2.3-1.3 3.1-2.5 1-1.4 1.4-2.8 1.4-2.9-.1 0-2.8-1.1-2.8-4.1zM14 5.3c.7-.8 1.2-2 1-3.2-1 0-2.2.7-2.9 1.5-.6.7-1.2 1.9-1 3 1.1.1 2.2-.5 2.9-1.3z"/></svg>'
    play = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M4 3.5v17l9.5-8.5L4 3.5z" opacity=".95"/><path d="M13.5 12l3.2-2.9 3.3 1.9c.9.5.9 1.5 0 2l-3.3 1.9L13.5 12z" opacity=".8"/><path d="M4 3.5l9.5 8.5-3.2 2.9L4 3.5z" opacity=".6"/></svg>'
    return f'''<section class="section"><div class="container"><div class="app-promo" data-reveal>
  <div>
    <span class="eyebrow">Mobile app</span>
    <h2>{esc(title)}</h2>
    <p class="lead">{esc(sub)} Answer leads, send invoices, book jobs and check performance from your phone.</p>
    <div class="badges">
      <a class="badge-store" href="{esc(APP_IOS)}" target="_blank" rel="noopener">{apple}<span><small>Download on the</small><strong>App Store</strong></span></a>
      <a class="badge-store" href="{esc(APP_ANDROID)}" target="_blank" rel="noopener">{play}<span><small>Get it on</small><strong>Google Play</strong></span></a>
    </div>
  </div>
  <div class="phone-mock device float" style="border-radius:44px;border:0;box-shadow:none;background:transparent">{I.mock_phone()}</div>
</div></div></section>'''


def cta_band(title: str = "Ready to grow faster and run smarter?", sub: str = "Get a personalized look at how the platform fits your business. No generic pitch, no pressure.", primary=("Book a demo", "/book-a-demo/"), secondary=("See pricing", "/pricing/")) -> str:
    return f'''<section class="section tight"><div class="container"><div class="cta-band" data-reveal>
  <h2>{esc(title)}</h2>
  <p class="lead">{esc(sub)}</p>
  <div class="btn-row center">{btn(primary[0], primary[1], "primary", "lg")}{btn(secondary[0], secondary[1], "ghost", "lg", False) if secondary else ""}</div>
</div></div></section>'''


def orbs() -> str:
    return '<div class="orbs" aria-hidden="true"><span class="orb a"></span><span class="orb b"></span><span class="orb c"></span><span class="orb d"></span></div>'


def breadcrumb(items: list[tuple[str, str]]) -> str:
    parts = []
    for i, (label, href) in enumerate(items):
        if href:
            parts.append(f'<a href="{esc(href)}">{esc(label)}</a>')
        else:
            parts.append(f"<span>{esc(label)}</span>")
        if i < len(items) - 1:
            parts.append(I.icon("chevron", ""))
    return f'<nav class="breadcrumb" aria-label="Breadcrumb">{"".join(parts)}</nav>'


def stars(n: int = 5) -> str:
    return '<span class="stars" aria-label="5 star rating">' + "★" * max(1, min(5, n)) + "</span>"


def quote_card(text_html: str, author: str, sub: str = "", n: int = 5) -> str:
    return f'''<div class="quote-card">{stars(n)}<blockquote>{text_html}</blockquote>
  <div class="who"><span class="avatar">{esc(initials(author))}</span><span><strong>{esc(author or "Verified customer")}</strong>{f"<span>{esc(sub)}</span>" if sub else ""}</span></div></div>'''


def carousel(slides_html: list[str], auto: bool = True) -> str:
    track = "".join(slides_html)
    return f'''<div class="carousel" data-auto="{'on' if auto else 'off'}"><div class="carousel-track">{track}</div>
  <div class="carousel-nav"><button class="prev" aria-label="Previous">{I.icon("arrow-left")}</button><div class="carousel-dots"></div><button class="next" aria-label="Next">{I.icon("arrow")}</button></div></div>'''


# ---------------------------------------------------------------------------
# Generic block rendering
# ---------------------------------------------------------------------------
def list_html(b: dict, cls: str = "checks") -> str:
    tag = "ol" if b.get("ordered") else "ul"
    items = []
    for it in b["items"]:
        s = it["html"]
        if it.get("sub"):
            s += list_html(it["sub"], "")
        items.append(f"<li>{s}</li>")
    c = f' class="{cls}"' if cls and tag == "ul" else ""
    return f"<{tag}{c}>{''.join(items)}</{tag}>"


def is_attrib(p: str) -> bool:
    t = text_of(p)
    return bool(re.match(r"^[–—\-–—]\s*", t)) and len(t) < 60


def render_prose(blocks: list[dict], ctx: dict, h_level: int = 2) -> str:
    """Render a run of simple blocks as prose (headings normalised)."""
    out = []
    skip = False
    for i, b in enumerate(blocks):
        if skip:
            skip = False
            continue
        t = b["type"]
        if t == "heading":
            ht = text_of(b["html"])
            if re.match(r"^[\d,.]+\+?[KkMm]?$", ht) and i + 1 < len(blocks) and blocks[i + 1]["type"] in ("heading", "paragraph"):
                label = text_of(blocks[i + 1]["html"])
                out.append(f'<div class="stat-inline" data-reveal><span class="stat-value" data-count="{esc(ht)}">{esc(ht)}</span><span class="stat-label">{esc(label)}</span></div>')
                skip = True
                continue
            lvl = h_level if b["level"] <= 2 else min(h_level + (b["level"] - 2), 4)
            if len(ht) > 90 and b["level"] >= 3:
                out.append(f'<p class="lead">{heading_html(b["html"])}</p>')
                continue
            out.append(f"<h{lvl}>{heading_html(b['html'])}</h{lvl}>")
        elif t == "paragraph":
            if is_attrib(b["html"]):
                out.append(f'<p class="attrib">{b["html"]}</p>')
            else:
                out.append(f"<p>{b['html']}</p>")
        elif t == "list":
            out.append(list_html(b))
        elif t == "image":
            if is_ui_chip_image(b):
                continue
            if is_screenshot(b):
                out.append(mock_from_image(b, ctx))
                continue
            out.append(f'<div class="img-wrap rounded shadow">{img_tag(b)}</div>')
        elif t == "button":
            out.append(f'<div class="btn-row">{btn(b["text"], fix_href(b["href"], ctx["path"], ctx["has_form"]), "primary")}</div>')
        elif t == "quote":
            out.append(f"<blockquote><p>{b['html']}</p></blockquote>")
        elif t == "hr":
            out.append("<hr>")
        elif t == "embed":
            out.append(f'<div class="embed"><iframe src="{esc(b["src"])}" loading="lazy" allowfullscreen title="Embedded content"></iframe></div>')
        elif t == "video":
            out.append(video_card(b))
        elif t == "table":
            rows = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in b["rows"])
            out.append(f'<div class="table-wrap"><table>{rows}</table></div>')
        elif t == "blurb":
            out.append(blurb_card(b, 0, ctx, plain=True))
        elif t == "faq":
            out.append(faq_html(b))
        elif t == "tabs":
            out.append(tabs_html(b, ctx))
        elif t == "columns":
            out.append(columns_generic(b, ctx))
        elif t == "app_badges":
            pass
        elif t == "form":
            out.append(quote_form(source=ctx["path"]) if b["kind"] != "support" else support_form())
        elif t == "stat":
            out.append(f'<div class="stat-inline"><span class="stat-value" data-count="{esc(b["value"])}">{esc(b["value"])}</span><span class="stat-label">{esc(b["label"])}</span></div>')
        elif t == "pricing":
            out.append(pricing_html([b], ctx))
        elif t == "testimonial":
            out.append(quote_card(b["html"], b["author"], b.get("position") or b.get("company", "")))
        elif t == "carousel":
            out.append(carousel([quote_card(s["html"], s["author"], "", s.get("stars", 5)) for s in b["slides"]]))
        elif t == "feature_accordion":
            out.append(accordion_html(b, ctx))
        elif t == "gallery":
            out.append(gallery_html(b["images"]))
        elif t == "person":
            out.append(person_html(b))
        elif t == "video_popup":
            out.append(f'<div class="btn-row"><a class="btn btn-ghost" href="{esc(b["src"])}" data-lightbox="{esc(b["src"])}">{I.icon("play")} Watch the video</a></div>')
        elif t == "rotating_text":
            out.append(rotating_html(b))
    return "\n".join(out)


def video_card(b: dict) -> str:
    src = b.get("src") or ""
    if not src or src == "about:blank":
        return ""
    if re.search(r"youtube|youtu\.be|vimeo", src):
        return f'<div class="embed video-card"><iframe src="{esc(src)}" loading="lazy" allowfullscreen title="Video"></iframe></div>'
    poster = f' poster="{esc(b["poster"])}"' if b.get("poster") else ""
    return f'''<div class="video-card"><video preload="metadata" playsinline{poster}><source src="{esc(src)}" type="video/mp4"></video>
  <button class="play" aria-label="Play video"><i>{I.icon("play")}</i></button></div>'''


def rotating_html(b: dict) -> str:
    items = "".join(f"<span>{esc(i)}</span>" for i in b["items"])
    return f'<h3 class="h2 center" style="margin:0">{esc(b.get("prefix") or "")} <span class="rotating grad-text">{items}</span></h3>'


def faq_html(b: dict) -> str:
    items = []
    for it in b["items"]:
        ans = render_prose(it["blocks"], {"path": "/", "has_form": False}, 4)
        items.append(f'<details><summary>{esc(it["q"])}<span class="plus">{I.icon("plus")}</span></summary><div class="answer">{ans}</div></details>')
    return f'<div class="faq">{"".join(items)}</div>'


def tabs_html(b: dict, ctx: dict) -> str:
    btns = "".join(f'<button class="{"on" if i == 0 else ""}" type="button">{esc(t["title"])}</button>' for i, t in enumerate(b["tabs"]))
    panes = "".join(f'<div class="tab-pane {"on" if i == 0 else ""}"><div class="prose">{render_prose(t["blocks"], ctx, 3)}</div></div>' for i, t in enumerate(b["tabs"]))
    return f'<div class="tabs"><div class="tab-list">{btns}</div>{panes}</div>'


def accordion_html(b: dict, ctx: dict, open_first: bool = True) -> str:
    items = []
    for i, it in enumerate(b["items"]):
        body = render_prose(it["blocks"], ctx, 4)
        link = f'<a class="btn-link" href="{esc(it["href"])}">Learn more {arrow()}</a>' if it.get("href") and it["href"] not in ("#", ctx["path"]) else ""
        items.append(f'''<div class="acc-item{' open' if i == 0 and open_first else ''}">
  <button class="acc-head" aria-expanded="{'true' if i == 0 and open_first else 'false'}"><span class="icon-tile {I.tint(i)}">{I.icon(I.icon_for(it["title"]))}</span><span>{esc(it["title"])}</span><span class="plus">{I.icon("plus")}</span></button>
  <div class="acc-body"><div><div class="inner">{body}{link}</div></div></div></div>''')
    return f'<div class="acc">{"".join(items)}</div>'


def feature_cards(items: list[dict], ctx: dict, cols: int = 3) -> str:
    cards = []
    for i, it in enumerate(items):
        body = render_prose(it["blocks"], ctx, 4)
        link = f'<a class="card-link" href="{esc(it["href"])}" aria-label="{esc(it["title"])}"></a><a class="btn-link" href="{esc(it["href"])}">Learn more {arrow()}</a>' if it.get("href") and it["href"] != "#" else ""
        cards.append(f'<div class="card" data-reveal style="--i:{i % 6}"><span class="icon-tile {I.tint(i)}">{I.icon(I.icon_for(it["title"]))}</span><h3>{esc(it["title"])}</h3>{body}{link}</div>')
    return f'<div class="grid grid-{cols}">{"".join(cards)}</div>'


def blurb_card(b: dict, i: int, ctx: dict, plain: bool = False, media: bool = False) -> str:
    title = b.get("title") or ""
    body = render_prose(b.get("blocks", []), ctx, 4)
    href = b.get("href")
    if not title and plain:
        return f'<div class="prose">{body}</div>'
    if not title:
        return f'<div class="card" data-reveal style="--i:{i % 6}">{body}</div>'
    link = ""
    if href and href not in ("#", ctx["path"]):
        link = f'<a class="card-link" href="{esc(href)}" aria-label="{esc(title)}"></a><a class="btn-link" href="{esc(href)}">Learn more {arrow()}</a>'
    media_html = ""
    if media and b.get("image") and not is_screenshot(b["image"]):
        media_html = f'<div class="card-media">{img_tag(b["image"])}</div>'
    return f'<div class="card" data-reveal style="--i:{i % 6}">{media_html}<span class="icon-tile {I.tint(i)}">{I.icon(I.icon_for(title + " " + text_of(body)[:80]))}</span><h3>{esc(title)}</h3>{body}{link}</div>'


def person_html(b: dict, i: int = 0) -> str:
    name = b.get("name") or b.get("title") or ""
    pos = b.get("position") or ""
    img = b.get("image")
    photo = img_tag(img, lazy=True) if img else ""
    return f'''<div class="person" data-reveal style="--i:{i % 8}"><div class="photo"><span class="initials">{esc(initials(name))}</span>{photo}</div><strong>{esc(name)}</strong><span>{esc(pos)}</span></div>'''


def gallery_html(images: list[dict], cats: bool = False) -> str:
    tiles = []
    for i, im in enumerate(images):
        cap = im.get("cat") or ""
        cat_attr = f' data-cat="{slugify(cap)}"' if cats else ""
        alt = im.get("alt") or im.get("title") or (cap + " website") if cap else "Client website"
        cap_html = f'<span class="cap">{esc(cap)}</span>' if cap else ""
        tiles.append(f'<a href="{esc(im["src"])}" data-lightbox="{esc(im["src"])}"{cat_attr} data-reveal style="--i:{i % 9}"><img src="{esc(im["src"])}" alt="{esc(alt)}" loading="lazy" decoding="async">{cap_html}</a>')
    return f'<div class="gallery" id="gallery">{"".join(tiles)}</div>'


def tables_are_steps(blocks: list[dict]) -> bool:
    tables = [t for b in blocks for t in b["tables"]]
    return bool(tables) and all(re.match(r"^step\s*\d", t["title"], re.I) for t in tables)


def pricing_html(blocks: list[dict], ctx: dict) -> str:
    tables = [t for b in blocks for t in b["tables"]]
    if tables and all(re.match(r"^step\s*\d", t["title"], re.I) for t in tables):
        steps = []
        for i, t in enumerate(tables):
            items = "".join(f"<li>{x}</li>" for x in t["items"])
            steps.append(f'<div class="step" data-reveal style="--i:{i}"><div class="step-no">{i + 1:02d}</div><h3>{esc(t["subtitle"] or t["title"])}</h3><ul>{items}</ul></div>')
        return f'<div class="steps">{"".join(steps)}</div>'
    plans = []
    for i, t in enumerate(tables):
        items = "".join(f"<li>{x}</li>" for x in t["items"])
        b = t.get("button")
        button = btn(b["text"], fix_href(b["href"], ctx["path"], ctx["has_form"]), "primary" if i == 1 else "ghost") if b else btn("Book a demo", "/book-a-demo/", "ghost")
        price = f'<div class="price">{esc(t["price"])}</div>' if t.get("price") else ""
        plans.append(f'<div class="plan{" featured" if i == 1 else ""}" data-reveal style="--i:{i}"><div class="plan-kicker">{esc(["Grow", "Support", "Run"][i % 3])}</div><h3>{esc(t["title"])}</h3><p class="sub">{esc(t["subtitle"])}</p>{price}<ul>{items}</ul>{button}</div>')
    return f'<div class="plans">{"".join(plans)}</div>'


def columns_generic(b: dict, ctx: dict) -> str:
    cols = b["cols"]
    n = len(cols)
    inner = "".join(f'<div class="stack">{render_prose(c, ctx, 3)}</div>' for c in cols)
    return f'<div class="grid grid-{min(n, 4)}">{inner}</div>'


# ---------------------------------------------------------------------------
# Section classification & rendering
# ---------------------------------------------------------------------------
def flatten(blocks: list[dict]) -> list[dict]:
    out = []
    for b in blocks:
        if b["type"] == "columns":
            for c in b["cols"]:
                out.extend(flatten(c))
        else:
            out.append(b)
    return out


def types(blocks: list[dict]) -> list[str]:
    return [b["type"] for b in flatten(blocks)]


def first_heading(blocks: list[dict]):
    for b in flatten(blocks):
        if b["type"] == "heading":
            return b
    return None


def split_head(blocks: list[dict]):
    """Return (intro_blocks, rest) where intro is the leading headings/paragraphs."""
    intro, rest = [], []
    for b in blocks:
        if not rest and is_ui_chip_image(b):
            continue
        if not rest and b["type"] in ("heading", "paragraph") and not (b["type"] == "paragraph" and len(text_of(b["html"])) > 400):
            intro.append(b)
        else:
            rest.append(b)
    return intro, rest


def intro_html(intro: list[dict], eyebrow: str = "", center: bool = True, level: int = 2) -> str:
    if not intro and not eyebrow:
        return ""
    parts = []
    if eyebrow:
        parts.append(f'<span class="eyebrow">{esc(eyebrow)}</span>')
    seen_h = False
    for b in intro:
        if b["type"] == "heading":
            if not seen_h:
                parts.append(f"<h{level}>{heading_html(b['html'])}</h{level}>")
                seen_h = True
            else:
                parts.append(f'<p class="lead">{heading_html(b["html"])}</p>')
        else:
            parts.append(f'<p class="lead">{b["html"]}</p>' if len(text_of(b["html"])) < 260 else f"<p>{b['html']}</p>")
    return f'<div class="section-head{"" if center else " left"}" data-reveal>{"".join(parts)}</div>'


def is_ui_chip_image(b: dict) -> bool:
    return b["type"] == "image" and b.get("w") and b.get("h") and (b["w"] / max(b["h"], 1) > 2.6 or b["w"] < 200)


def media_html(blocks: list[dict], ctx: dict, key: str = "") -> str:
    """Render the media side of a split (image / video / form / mockup)."""
    all_imgs = [b for b in blocks if b["type"] == "image" and not is_ui_chip_image(b)]
    imgs = [b for b in all_imgs if not is_screenshot(b)]
    vids = [b for b in blocks if b["type"] == "video"]
    forms = [b for b in blocks if b["type"] == "form"]
    if forms:
        return quote_form(source=ctx["path"]) if forms[0]["kind"] != "support" else support_form()
    if vids:
        return video_card(vids[0])
    if imgs:
        b = imgs[0]
        return f'<div class="img-wrap rounded shadow tilt" data-reveal="scale">{img_tag(b)}</div>'
    if all_imgs:
        return mock_from_image(all_imgs[0], ctx, key)
    # fallback: on-brand mockup
    return f'<div class="device tilt" data-reveal="scale" style="padding:0;border:0;background:transparent;box-shadow:none">{I.mock_for(key or ctx["path"] + " " + ctx.get("title", ""), ctx.get("h1", "")[:16])}</div>'


def cards_from_columns(b: dict, ctx: dict) -> str | None:
    """Columns whose content looks like [image?, heading, paragraph, button] → media cards."""
    cols = b["cols"]
    if len(cols) < 2:
        return None
    ok = 0
    for c in cols:
        ts = [x["type"] for x in c]
        if "heading" in ts and ("button" in ts or "image" in ts) and len(c) <= 5 and "form" not in ts:
            ok += 1
    if ok < len(cols):
        return None
    cards = []
    for i, c in enumerate(cols):
        img = next((x for x in c if x["type"] == "image"), None)
        h = next((x for x in c if x["type"] == "heading"), None)
        ps = [x for x in c if x["type"] == "paragraph"]
        bt = next((x for x in c if x["type"] == "button"), None)
        href = fix_href(bt["href"], ctx["path"], ctx["has_form"]) if bt else None
        if href == "/" and "case-studies" in ctx["path"]:
            href = "/case-studies/"
        title = heading_html(h["html"]) if h else ""
        media = f'<div class="card-media">{img_tag(img)}</div>' if img and not is_screenshot(img) else ""
        if img and is_screenshot(img):
            img = None
        body = "".join(f"<p>{p['html']}</p>" for p in ps)
        link = f'<a class="card-link" href="{esc(href)}" aria-label="{esc(text_of(title))}"></a><a class="btn-link" href="{esc(href)}">{esc(bt["text"].title() if bt else "Learn more")} {arrow()}</a>' if href else ""
        if not img:
            media = f'<span class="icon-tile {I.tint(i)}">{I.icon(I.icon_for(text_of(title)))}</span>'
        cards.append(f'<div class="card" data-reveal style="--i:{i % 6}">{media}<h3>{title}</h3>{body}{link}</div>')
    n = min(len(cols), 4)
    return f'<div class="grid grid-{n}">{"".join(cards)}</div>'


def people_grid(blurbs: list[dict]) -> str:
    return f'<div class="people">{"".join(person_html({"name": b.get("title"), "position": text_of(" ".join(x.get("html", "") for x in b["blocks"])), "image": b.get("image")}, i) for i, b in enumerate(blurbs))}</div>'


def looks_like_people(blurbs: list[dict]) -> bool:
    if not blurbs:
        return False
    for b in blurbs:
        if not b.get("image"):
            return False
        txt = text_of(" ".join(x.get("html", "") for x in b["blocks"]))
        if len(txt) > 70 or "“" in txt or '"' in txt:
            return False
    return True


def render_split(text_blocks: list[dict], media_blocks: list[dict], ctx: dict, reverse: bool, eyebrow: str, key: str) -> str:
    text = render_prose(text_blocks, ctx, 2)
    eb = f'<span class="eyebrow">{esc(eyebrow)}</span>' if eyebrow else ""
    return f'<div class="split{" reverse" if reverse else ""}"><div class="prose" data-reveal="{"right" if reverse else "left"}">{eb}{text}</div><div>{media_html(media_blocks, ctx, key)}</div></div>'


def classify_columns(b: dict):
    """Return ('split', text_idx, media_idx) or None."""
    cols = b["cols"]
    if len(cols) != 2:
        return None
    def score(c):
        ts = [x["type"] for x in c]
        media = sum(t in ("image", "video", "form") for t in ts)
        text = sum(t in ("heading", "paragraph", "list", "button", "blurb", "feature_accordion", "quote") for t in ts)
        return media, text
    m0, t0 = score(cols[0]); m1, t1 = score(cols[1])
    if m0 and not m1 and t1:
        return ("split", 1, 0)
    if m1 and not m0 and t0:
        return ("split", 0, 1)
    if m1 and m0 == 0 and t0 == 0 and t1 == 0:
        return None
    return None


SECTION_EYEBROW = {"Grow": "Features", "Run": "Features", "Industries": "How we help", "Markets": "What is included",
                   "Support": "How it works", "Case study": "The solution", "Pricing": "Packages", "Company": "Highlights"}


def steps_from_columns(b: dict, ctx: dict) -> str | None:
    """Columns that each start with a numeric heading (01, 02…) → numbered steps."""
    cols = b["cols"]
    if len(cols) < 2:
        return None
    for c in cols:
        if not c or c[0]["type"] != "heading" or not re.match(r"^\d{1,2}$", text_of(c[0]["html"])):
            return None
    steps = []
    for i, c in enumerate(cols):
        num = text_of(c[0]["html"])
        title = next((x for x in c[1:] if x["type"] == "heading"), None)
        rest = [x for x in c[1:] if x is not title]
        body = "".join(render_prose(x["blocks"], ctx, 4) if x["type"] == "blurb" else render_prose([x], ctx, 4) for x in rest)
        steps.append(f'<div class="step" data-reveal style="--i:{i}"><div class="step-no">{esc(num)}</div><h3>{heading_html(title["html"]) if title else ""}</h3>{body}</div>')
    return f'<div class="steps" style="grid-template-columns:repeat({min(len(cols), 3)},minmax(0,1fr))">{"".join(steps)}</div>'


def statement_from_columns(b: dict, ctx: dict) -> str | None:
    """Two text columns where the first holds only headings → statement layout."""
    cols = b["cols"]
    if len(cols) != 2 or not cols[0] or not all(x["type"] == "heading" for x in cols[0]):
        return None
    if not all(x["type"] in ("paragraph", "list", "button") for x in cols[1]):
        return None
    hs = cols[0]
    left = f"<h2>{heading_html(hs[0]['html'])}</h2>" + "".join(f'<p class="lead">{heading_html(h["html"])}</p>' for h in hs[1:])
    return f'<div class="statement"><div data-reveal="left">{left}</div><div class="prose" data-reveal="right">{render_prose(cols[1], ctx, 3)}</div></div>'


def zigzag_from_columns(blocks: list[dict], ctx: dict) -> str | None:
    """Section made of rows [image | blurbs] → alternating splits with feature lists."""
    cols_blocks = [b for b in blocks if b["type"] == "columns"]
    if not cols_blocks or any(b["type"] not in ("columns", "heading", "paragraph") for b in blocks):
        return None
    rows = []
    for cb in cols_blocks:
        if len(cb["cols"]) != 2:
            return None
        a, c = cb["cols"]
        def kind(col):
            ts = {x["type"] for x in col}
            if ts <= {"image"}:
                return "img"
            if ts <= {"blurb", "heading", "paragraph"} and any(x["type"] == "blurb" for x in col):
                return "blurbs"
            return None
        ka, kc = kind(a), kind(c)
        if {ka, kc} != {"img", "blurbs"}:
            return None
        rows.append((a if ka == "img" else c, c if kc == "blurbs" else a, ka == "blurbs"))
    intro, _ = split_head(blocks)
    out = [intro_html(intro, "")]
    for i, (imgs, blurbs, reverse) in enumerate(rows):
        items = []
        for j, bl in enumerate(blurbs):
            if bl["type"] != "blurb":
                items.append(render_prose([bl], ctx, 3))
                continue
            body = render_prose(bl["blocks"], ctx, 4)
            items.append(f'<div class="item" data-reveal style="--i:{j}"><span class="icon-tile {I.tint(i * 2 + j)}">{I.icon(I.icon_for(bl.get("title") or ""))}</span><div><strong>{esc(bl.get("title") or "")}</strong>{body}</div></div>')
        media = media_html(imgs, ctx)
        out.append(f'<div class="split{" reverse" if reverse else ""}" style="margin-top:{"48px" if i else "0"}"><div class="feature-list">{"".join(items)}</div><div>{media}</div></div>')
    return "".join(out)


def render_section(sec: dict, idx: int, ctx: dict, page: dict) -> str:
    blocks = sec["blocks"]
    flat = flatten(blocks)
    ts = [b["type"] for b in flat]
    path = ctx["path"]
    eyebrow = SECTION_EYEBROW.get(ctx.get("eyebrow", ""), "")

    # --- app promo (standard component) ---
    h = first_heading(blocks)
    if "app_badges" in ts or (h and re.search(r"\bapp\b", text_of(h["html"]), re.I) and "image" in ts and len(flat) <= 5):
        return app_promo()

    # --- stats ---
    if ts and all(t == "stat" for t in ts):
        cards = "".join(f'<div class="stat" data-reveal style="--i:{i}"><div class="stat-value" data-count="{esc(b["value"])}">{esc(b["value"])}</div><div class="stat-label">{esc(b["label"])}</div></div>' for i, b in enumerate(flat))
        return f'<section class="section tight"><div class="container"><div class="stats">{cards}</div></div></section>'

    # --- FAQ ---
    if "faq" in ts:
        intro, rest = split_head(blocks)
        faqs = "".join(faq_html(b) for b in flat if b["type"] == "faq")
        other = render_prose([b for b in rest if b["type"] != "faq"], ctx, 3)
        return f'<section class="section paper"><div class="container">{intro_html(intro, "FAQ")}{faqs}{other}</div></section>'

    # --- forms ---
    if "form" in ts and "heading" in ts and 1 not in [b.get("level") for b in flat if b["type"] == "heading"]:
        intro = [b for b in flat if b["type"] in ("heading", "paragraph")]
        form = next(b for b in flat if b["type"] == "form")
        fh = quote_form(source=path) if form["kind"] != "support" else support_form()
        head = intro_html(intro, "Get started", center=False, level=2)
        return f'<section class="section paper" id="get-started"><div class="container"><div class="split"><div>{head}<ul class="checks" data-reveal><li>No long-term contracts</li><li>Unlimited US-based support</li><li>Monthly reporting and insights</li></ul></div><div data-reveal="scale">{fh}</div></div></div></section>'
    if ts == ["form"]:
        form = flat[0]
        fh = quote_form(source=path) if form["kind"] != "support" else support_form()
        return f'<section class="section paper" id="get-started"><div class="narrow" data-reveal="scale">{fh}</div></section>'

    # --- pricing / steps ---
    if "pricing" in ts:
        intro, rest = split_head(blocks)
        pr = pricing_html([b for b in flat if b["type"] == "pricing"], ctx)
        others = [b for b in flatten(rest) if b["type"] not in ("pricing",)]
        blurbs = [b for b in others if b["type"] == "blurb"]
        tail = ""
        if blurbs:
            tail = f'<div style="margin-top:36px">{feature_cards([{"title": b.get("title") or "", "blocks": b["blocks"], "href": b.get("href")} for b in blurbs], ctx, 3 if len(blurbs) != 2 else 2)}</div>'
        rest_html = render_prose([b for b in others if b["type"] not in ("blurb",)], ctx, 3)
        tagline = f'<p class="lead center" style="margin-top:36px" data-reveal>{rest_html}</p>' if rest_html and "<p" not in rest_html else (f'<div class="center" style="margin-top:36px" data-reveal>{rest_html}</div>' if rest_html else "")
        steps_mode = bool(tables_are_steps([b for b in flat if b["type"] == "pricing"]))
        return f'<section class="section paper"><div class="container">{intro_html(intro, "How it works" if steps_mode else "Packages")}{pr}{tail}{tagline}</div></section>'

    # --- testimonials / carousel ---
    if "testimonial" in ts or "carousel" in ts:
        intro, rest = split_head(blocks)
        quotes = [b for b in flat if b["type"] == "testimonial"]
        cars = [b for b in flat if b["type"] == "carousel"]
        body = ""
        if quotes:
            qcards = "".join(f'<div data-reveal>{quote_card(q["html"], q["author"], q.get("position") or q.get("company", ""))}</div>' for q in quotes)
            body = f'<div class="grid grid-{min(3, len(quotes))}" data-stagger>{qcards}</div>'
        for c in cars:
            body += carousel([quote_card(s["html"], s["author"], "", s.get("stars", 5)) for s in c["slides"]])
        buttons = [b for b in flat if b["type"] == "button"]
        bh = f'<div class="btn-row center" style="margin-top:32px">{"".join(btn(b["text"], fix_href(b["href"], path, ctx["has_form"]), "ghost") for b in buttons)}</div>' if buttons else ""
        intro = [b for b in intro if b["type"] != "button"]
        return f'<section class="section"><div class="container">{intro_html(intro, eyebrow or "What clients say")}{body}{bh}</div></section>'

    # --- feature accordion ---
    if "feature_accordion" in ts:
        accs = [b for b in flat if b["type"] == "feature_accordion"]
        text = [b for b in flat if b["type"] in ("heading", "paragraph", "button")]
        if len(accs) == 1:
            merged = accs[0]
            eb = f'<span class="eyebrow">{esc(eyebrow)}</span>' if eyebrow else ""
            left = f'<div class="prose" data-reveal="left">{eb}{render_prose(text, ctx, 2)}</div>'
            return f'<section class="section"><div class="container"><div class="split" style="align-items:start"><div style="position:sticky;top:calc(var(--header-h) + 32px)">{left}</div><div data-reveal="right">{accordion_html(merged, ctx)}</div></div></div></section>'
        items = [it for a in accs for it in a["items"]]
        intro, _ = split_head([b for b in blocks if b["type"] != "feature_accordion"])
        return f'<section class="section paper"><div class="container">{intro_html(intro, "What is included")}{feature_cards(items, ctx, 3)}</div></section>'

    # --- gallery (lightbox images) ---
    imgs = [b for b in flat if b["type"] == "image"]
    if imgs and len(imgs) >= 3 and all(b.get("href") for b in imgs) and not any(t in ts for t in ("heading", "paragraph", "blurb")):
        return f'<section class="section tight"><div class="container">{gallery_html(imgs)}</div></section>'
    if imgs and len(imgs) >= 4 and not any(t in ts for t in ("heading", "paragraph", "blurb", "button", "form")):
        tiles = "".join(f'<div class="tile" style="aspect-ratio:1;border-radius:20px;overflow:hidden" data-reveal="scale" data-stagger>{img_tag(b, "")}</div>' for b in imgs)
        return f'<section class="section tight"><div class="container"><div class="grid grid-4">{tiles}</div></div></section>'

    # --- people / blurbs ---
    blurbs = [b for b in flat if b["type"] == "blurb"]
    if blurbs and any(b["type"] == "columns" and steps_from_columns(b, ctx) for b in blocks):
        return render_columns_section(blocks, idx, ctx, eyebrow)
    if blurbs:
        zz = zigzag_from_columns(blocks, ctx)
        if zz:
            return f'<section class="section{" paper" if idx % 2 else ""}"><div class="container">{zz}</div></section>'
        flat = expand_untitled(flat)
        blurbs = [b for b in flat if b["type"] == "blurb" and (b.get("title") or b["blocks"])]
    if blurbs:
        intro, rest = split_head(blocks)
        rest_flat = expand_untitled(flatten(rest))
        # paragraphs that were pulled out of untitled blurbs become surrounding prose
        others = [b for b in rest_flat if b["type"] != "blurb"]
        blurbs = [b for b in rest_flat if b["type"] == "blurb" and (b.get("title") or b["blocks"])]
        if not blurbs:
            blurbs = [b for b in flat if b["type"] == "blurb" and (b.get("title") or b["blocks"])]
        pre_imgs = [b for b in others if b["type"] == "image" and not is_ui_chip_image(b)]
        buttons = [b for b in others if b["type"] == "button"]
        lists = [b for b in others if b["type"] == "list"]
        others = [b for b in others if b["type"] not in ("image", "button", "list")]
        if looks_like_people(blurbs):
            body = people_grid(blurbs)
            return f'<section class="section"><div class="container">{intro_html(intro, "Our team")}{body}</div></section>'
        titled = [b for b in blurbs if b.get("title")]
        untitled = [b for b in blurbs if not b.get("title")] + [{"type": "blurb", "blocks": [l]} for l in lists]
        if len(untitled) < 2 and lists:
            others = others + lists
            untitled = [b for b in blurbs if not b.get("title")]
        pre = render_prose(others, ctx, 3)
        # attach buttons that immediately follow blurbs inside the same column (industry pages) as card links
        if buttons and len(buttons) == len(titled):
            for b, bt in zip(titled, buttons):
                b["href"] = fix_href(bt["href"], path, ctx["has_form"])
            buttons = []
        body = ""
        if len(untitled) >= 2:
            cards = []
            for i, b in enumerate(untitled):
                inner = render_prose(b["blocks"], ctx, 4)
                inner = re.sub(r"<p><strong>([^<]{3,60}:?)</strong>\s*:?\s*</p>", r"<h4>\1</h4>", inner)
                inner = re.sub(r"<p>([A-Z][^<]{3,50}:)</p>", r"<h4>\1</h4>", inner)
                cards.append(f'<div class="card" data-reveal style="--i:{i % 6}">{inner}</div>')
            body += f'<div class="grid grid-{3 if len(untitled) != 2 and len(untitled) != 4 else 2}">{"".join(cards)}</div>'
        elif untitled:
            body += f'<div class="narrow prose" data-reveal>{"".join(render_prose(b["blocks"], ctx, 3) for b in untitled)}</div>'
        if titled:
            n = 3 if len(titled) % 3 == 0 or len(titled) > 4 else (2 if len(titled) in (2, 4) else 3)
            if len(titled) == 1:
                n = 1
            has_media = any(b.get("image") for b in titled)
            cards = "".join(blurb_card(b, i, ctx, media=has_media) for i, b in enumerate(titled))
            body += f'<div class="grid grid-{n}" style="margin-top:{"36px" if untitled else "0"}">{cards}</div>'
        media = ""
        if pre_imgs and not is_ui_chip_image(pre_imgs[0]):
            # image + blurbs → split with image on one side
            left = intro_html(intro, eyebrow, center=False) + body
            return f'<section class="section"><div class="container"><div class="split{" reverse" if idx % 2 else ""}"><div>{left}</div><div>{media_html(pre_imgs, ctx)}</div></div>{pre}</div></section>'
        bh = f'<div class="btn-row center" style="margin-top:32px">{"".join(btn(b["text"], fix_href(b["href"], path, ctx["has_form"]), "primary") for b in buttons)}</div>' if buttons else ""
        return f'<section class="section paper"><div class="container">{intro_html(intro, eyebrow)}{pre}{body}{bh}</div></section>'

    # --- columns ---
    col_blocks = [b for b in blocks if b["type"] == "columns"]
    if col_blocks:
        return render_columns_section(blocks, idx, ctx, eyebrow)
    return render_tail_section(blocks, idx, ctx, eyebrow, flat, ts, imgs)


def render_columns_section(blocks: list[dict], idx: int, ctx: dict, eyebrow: str) -> str:
    path = ctx["path"]
    if True:
        intro, rest = split_head(blocks)
        parts = [intro_html(intro, eyebrow)]
        for b in rest:
            if b["type"] != "columns":
                parts.append(f'<div class="narrow prose" data-reveal>{render_prose([b], ctx, 3)}</div>')
                continue
            cards = cards_from_columns(b, ctx)
            if cards:
                parts.append(cards)
                continue
            st = steps_from_columns(b, ctx)
            if st:
                parts.append(st)
                continue
            stm = statement_from_columns(b, ctx)
            if stm:
                parts.append(stm)
                continue
            cl = classify_columns(b)
            if cl:
                _, ti, mi = cl
                text_blocks = b["cols"][ti]
                media_blocks = b["cols"][mi]
                if not intro and not parts[0]:
                    parts.append(render_split(text_blocks, media_blocks, ctx, reverse=(mi == 0), eyebrow=eyebrow, key=text_of(first_heading(text_blocks)["html"]) if first_heading(text_blocks) else ""))
                else:
                    parts.append(render_split(text_blocks, media_blocks, ctx, reverse=(mi == 0), eyebrow="", key=""))
                continue
            # text-only columns → prose cards
            cols = b["cols"]
            if all(all(x["type"] in ("heading", "paragraph", "list", "button") for x in c) for c in cols):
                inner = "".join(f'<div class="card" data-reveal style="--i:{i}"><div class="prose">{render_prose(c, ctx, 3)}</div></div>' for i, c in enumerate(cols))
                parts.append(f'<div class="grid grid-{min(len(cols), 3)}">{inner}</div>')
            else:
                parts.append(columns_generic(b, ctx))
        return f'<section class="section{" paper" if idx % 2 == 0 and idx > 0 else ""}"><div class="container">{"".join(parts)}</div></section>'


def render_tail_section(blocks: list[dict], idx: int, ctx: dict, eyebrow: str, flat: list[dict], ts: list[str], imgs: list[dict]) -> str:
    path = ctx["path"]
    # --- button-only sections ---
    if ts and all(t == "button" for t in ts):
        return f'<section class="section tight"><div class="container btn-only" data-reveal>{"".join(btn(b["text"], fix_href(b["href"], path, ctx["has_form"]), "ghost" if i else "primary") for i, b in enumerate(flat))}</div></section>'

    # --- CTA (heading + short text + button) ---
    if "button" in ts and "heading" in ts and len(flat) <= 5 and not imgs:
        hd = first_heading(blocks)
        ps = [b for b in flat if b["type"] == "paragraph"]
        buttons = [b for b in flat if b["type"] == "button"]
        subs = [b for b in flat if b["type"] == "heading" and b is not hd]
        sub = " ".join(text_of(b["html"]) for b in subs) + " " + " ".join(text_of(p["html"]) for p in ps)
        prim = buttons[0]
        sec_btn = ("See pricing", "/pricing/") if len(buttons) == 1 else (buttons[1]["text"], fix_href(buttons[1]["href"], path, ctx["has_form"]))
        return cta_band(text_of(hd["html"]), sub.strip()[:320], (prim["text"], fix_href(prim["href"], path, ctx["has_form"])), sec_btn)

    # --- video popup / rotating text (careers) ---
    if "rotating_text" in ts:
        return f'<section class="section tight"><div class="container">{render_prose(flat, ctx, 2)}</div></section>'

    # --- lists as checks with heading ---
    # --- default prose ---
    if not flat:
        return ""
    intro, rest = split_head(blocks)
    body = render_prose(rest, ctx, 3)
    if intro and not rest:
        # a section with only headings/paragraphs → section head styled
        return f'<section class="section{" paper" if idx % 2 else ""}"><div class="container">{intro_html(intro, eyebrow)}</div></section>'
    return f'<section class="section{" paper" if idx % 2 else ""}"><div class="container">{intro_html(intro, eyebrow)}<div class="narrow prose" data-reveal>{body}</div></div></section>'


# ---------------------------------------------------------------------------
# Hero rendering
# ---------------------------------------------------------------------------
def hero_from_section(sec: dict, ctx: dict, page: dict, variant: str = "auto") -> str:
    flat = flatten(sec["blocks"])
    h1 = next((b for b in flat if b["type"] == "heading" and b["level"] == 1), None) or next((b for b in flat if b["type"] == "heading"), None)
    subs = [b for b in flat if b["type"] == "heading" and b is not h1]
    paras = [b for b in flat if b["type"] == "paragraph"]
    buttons = [b for b in flat if b["type"] == "button"]
    forms = [b for b in flat if b["type"] == "form"]
    all_imgs = [b for b in flat if b["type"] == "image" and not is_ui_chip_image(b)]
    imgs = [b for b in all_imgs if not is_screenshot(b)]
    shots = [b for b in all_imgs if is_screenshot(b)]
    vids = [b for b in flat if b["type"] == "video_popup"]
    lists = [b for b in flat if b["type"] == "list"]
    title = heading_html(h1["html"], keep_br=True) if h1 else esc(page["title"])
    # subtitle: first sub heading unless it's a form label
    sub = ""
    for s in subs:
        t = text_of(s["html"])
        if re.search(r"free quote|fill out the form|takes less than", t, re.I) or not t:
            continue
        sub = heading_html(s["html"])
        break
    attrib = ""
    lead_ps = []
    for p in paras:
        if is_attrib(p["html"]):
            attrib = text_of(p["html"]).lstrip("–—- ")
        elif not re.search(r"^\s*(Days of operation)", text_of(p["html"])):
            lead_ps.append(p)
    lead = lead_ps[0]["html"] if lead_ps else ""
    extra = "".join(f"<p>{p['html']}</p>" for p in lead_ps[1:])
    eyebrow = ctx.get("eyebrow", "")
    eb = f'<span class="eyebrow">{esc(eyebrow)}</span>' if eyebrow else ""
    # buttons
    if buttons:
        bh = "".join(btn(b["text"], fix_href(b["href"], ctx["path"], ctx["has_form"] or bool(forms)), "primary" if i == 0 else "ghost", "lg", i == 0) for i, b in enumerate(buttons[:2]))
    else:
        bh = btn("Book a demo", "/book-a-demo/", "primary", "lg") + btn("See pricing", "/pricing/", "ghost", "lg", False)
    for v in vids:
        bh += f'<a class="btn btn-ghost btn-lg" href="{esc(v["src"])}" data-lightbox="{esc(v["src"])}">{I.icon("play")}Watch the video</a>'
    if ctx["has_form"] and not forms and ctx.get("form_anchor"):
        bh = btn("Get a free quote", "#quote-form", "primary", "lg") + btn("Book a demo", "/book-a-demo/", "ghost", "lg", False)
    quote_style = bool(sub) and (sub.startswith("“") or sub.startswith('"'))
    if quote_style:
        sub_html = f'<p class="quote-big">{sub}</p>' + (f'<p class="attrib">— {esc(attrib)}</p>' if attrib else "")
    else:
        sub_html = f'<p class="h1-sub">{sub}</p>' if sub else ""
    lead_html = f'<p class="lead">{lead}</p>' if lead else ""
    list_html_ = "".join(list_html(l) for l in lists)
    note = '<div class="hero-note"><span class="avatars"><span></span><span></span><span></span><span></span></span><span><span class="stars">★★★★★</span> Rated 5.0 by 5,000+ businesses</span></div>' if variant != "quiet" else ""
    copy = f'<div class="hero-copy">{eb}<h1 class="words">{title}</h1>{sub_html}{lead_html}{extra}{list_html_}<div class="btn-row">{bh}</div>{note}</div>'

    bg_video = ""
    if sec.get("meta", {}).get("bg_video"):
        bg_video = f'<div class="bg-video" aria-hidden="true"><video autoplay muted loop playsinline preload="metadata"><source src="{esc(sec["meta"]["bg_video"])}" type="video/mp4"></video></div>'

    if forms:
        form = quote_form(source=ctx["path"], title="Start your free quote", sub="It takes less than a minute. Yes, we timed it.")
        art = f'<div class="hero-art" data-reveal="right">{form}<p class="hero-form-note">No contracts · Unlimited support · Cancel anytime</p></div>'
        return f'<section class="hero">{orbs()}{bg_video}<div class="container hero-grid">{copy}{art}</div></section>'
    if imgs:
        b = imgs[0]
        square = b.get("w") and b.get("h") and abs(b["w"] / b["h"] - 1) < 0.15
        art = f'<div class="hero-art"><div class="glow"></div><div class="img-wrap rounded shadow tilt" data-reveal="scale" style="{"max-width:460px;margin-inline:auto" if square else ""}">{img_tag(b, lazy=False)}</div></div>'
        return f'<section class="hero">{orbs()}{bg_video}<div class="container hero-grid">{copy}{art}</div></section>'
    if variant == "center":
        return f'<section class="hero compact">{orbs()}{bg_video}<div class="container"><div class="hero-center">{copy}</div></div></section>'
    # default: copy + mockup
    key = ctx["path"] + " " + text_of(title) + " " + " ".join((s.get("alt") or s.get("title") or "") + " " + os.path.basename(s.get("src", "")).rsplit(".", 1)[0].replace("-", " ") for s in shots)
    mock = I.mock_for(key, text_of(title)[:18])
    floating = ""
    if "/" == ctx["path"]:
        floating = (f'<div class="floating-card tl"><span class="icon-tile teal">{I.icon("target")}</span><span><strong>New lead</strong>Booked from Google</span></div>'
                    f'<div class="floating-card br"><span class="icon-tile amber">{I.icon("star")}</span><span><strong>5.0 ★ review</strong>Request sent automatically</span></div>')
    art = f'<div class="hero-art"><div class="glow"></div><div class="device tilt float" data-reveal="scale" style="padding:0;border:0;background:transparent;box-shadow:none">{mock}</div>{floating}</div>'
    return f'<section class="hero">{orbs()}{bg_video}<div class="container hero-grid">{copy}{art}</div></section>'


# ---------------------------------------------------------------------------
# Page builders
# ---------------------------------------------------------------------------
def page_ctx(page: dict, eyebrow: str = "") -> dict:
    ts = types([b for s in page["sections"] for b in s["blocks"]])
    return {"path": page["path"], "title": page["title"], "h1": page.get("h1", ""), "has_form": "form" in ts,
            "eyebrow": eyebrow, "form_anchor": "form" in ts}


def eyebrow_for(path: str) -> str:
    if path in [h for h, *_ in GROW_ITEMS] or path == "/grow/":
        return "Grow"
    if path in [h for h, *_ in RUN_ITEMS] or path == "/run/":
        return "Run"
    if path in [h for h, *_ in INDUSTRY_ITEMS] or path == "/who-we-work-with/":
        return "Industries"
    if path.startswith("/locations/"):
        return "Markets"
    if path in [h for h, *_ in SUPPORT_ITEMS]:
        return "Support"
    if path.startswith("/case-studies/"):
        return "Case study"
    return ""


def build_generic(page: dict, hero_variant: str = "auto", eyebrow: str = None, extra_after_hero: str = "", tail: str = "", skip_app: bool = False, noindex: bool = False) -> str:
    ctx = page_ctx(page, eyebrow if eyebrow is not None else eyebrow_for(page["path"]))
    sections = page["sections"]
    parts = []
    if sections:
        parts.append(hero_from_section(sections[0], ctx, page, hero_variant))
    else:
        parts.append(f'<section class="hero compact">{orbs()}<div class="container hero-center"><h1 class="words">{esc(page["title"])}</h1></div></section>')
    parts.append(extra_after_hero)
    has_app = False
    for i, sec in enumerate(sections[1:], start=1):
        html = render_section(sec, i, ctx, page)
        if 'class="app-promo"' in html:
            if has_app or skip_app:
                continue
            has_app = True
        parts.append(html)
    parts.append(tail)
    if not any("cta-band" in p for p in parts):
        parts.append(cta_band())
    page = dict(page)
    page["noindex"] = noindex
    return layout(page, "\n".join(parts))


# ---------- home ----------
def build_home(page: dict, posts: list[dict]) -> str:
    ctx = page_ctx(page, "")
    S = page["sections"]
    hero = hero_from_section(S[0], ctx, page)
    stats_html = render_section(S[1], 1, ctx, page)
    # everything you need + dashboard image
    s2 = flatten(S[2]["blocks"])
    s3 = flatten(S[3]["blocks"])
    h = [b for b in s2 if b["type"] == "heading"]
    p = [b for b in s2 if b["type"] == "paragraph"]
    dash_img = next((b for b in s3 if b["type"] == "image"), None)
    everything = f'''<section class="section"><div class="container">
  <div class="split" style="align-items:end;margin-bottom:44px"><div data-reveal="left"><span class="eyebrow">One connected platform</span><h2>{heading_html(h[0]["html"]) if h else ""}</h2><p class="lead">{heading_html(h[1]["html"]) if len(h) > 1 else ""}</p></div><div class="prose" data-reveal="right">{"".join(f"<p>{x['html']}</p>" for x in p)}<div class="btn-row">{btn("Explore Grow", "/grow/", "primary")}{btn("Explore Run", "/run/", "ghost", arrow_icon=False)}</div></div></div>
  <div class="device frame" data-reveal="scale">{img_tag(dash_img, lazy=True) if dash_img and not is_screenshot(dash_img) else I.mock_dashboard("Run your business")}</div>
</div></section>'''
    # three accordion groups
    groups = []
    for si, label, desc, eb in ((4, "Get Seen", "Show up wherever customers are searching — search, maps, social and AI.", "Grow"),
                                (5, "Build Trust", "Turn visibility into credibility with advertising, social and reputation.", "Grow"),
                                (6, "Drive Growth", "Capture, book and keep customers with tools that run the day-to-day.", "Run")):
        acc = next(b for b in flatten(S[si]["blocks"]) if b["type"] == "feature_accordion")
        reverse = si == 5
        groups.append(f'''<div class="split{" reverse" if reverse else ""}" style="align-items:start;margin-bottom:64px">
  <div style="position:sticky;top:calc(var(--header-h) + 32px)" data-reveal="{"right" if reverse else "left"}"><span class="eyebrow">{esc(eb)}</span><h2>{esc(label)}</h2><p class="lead">{esc(desc)}</p></div>
  <div data-reveal="{"left" if reverse else "right"}">{accordion_html(acc, ctx)}</div></div>''')
    three = f'<section class="section paper"><div class="container"><div class="section-head"><span class="eyebrow">Everything in one place</span><h2>Get seen. Build trust. Drive growth.</h2><p class="lead">Marketing and business tools designed to work together — not another stack of logins.</p></div>{"".join(groups)}</div></section>'
    # industries
    s7 = flatten(S[7]["blocks"])
    h7 = [b for b in s7 if b["type"] == "heading"]
    p7 = [b for b in s7 if b["type"] == "paragraph"]
    ind_cards = "".join(f'<a class="industry-card" href="{esc(h)}" data-reveal style="--i:{i % 6}"><span class="label"><span class="icon-tile {I.tint(i)}">{I.icon(ic)}</span>{esc(t)}{arrow()}</span></a>' for i, (h, t, ic) in enumerate(INDUSTRY_ITEMS))
    marquee = "".join(f'<span class="chip"><span class="icon-tile {I.tint(i)}">{I.icon(ic)}</span>{esc(t)}</span>' for i, (h, t, ic) in enumerate(INDUSTRY_ITEMS + INDUSTRY_ITEMS))
    industries = f'''<section class="section"><div class="container">
  <div class="split" style="margin-bottom:44px"><div data-reveal="left"><span class="eyebrow">Industries</span><h2>{heading_html(h7[0]["html"])}</h2><p class="lead">{heading_html(h7[1]["html"]) if len(h7) > 1 else ""}</p></div><div class="prose" data-reveal="right">{"".join(f"<p>{x['html']}</p>" for x in p7)}</div></div>
  </div><div class="marquee" data-reveal><div class="marquee-track">{marquee}</div></div>
  <div class="container" style="margin-top:44px"><div class="grid grid-4">{ind_cards}</div><div class="btn-row center" style="margin-top:32px">{btn("See who we work with", "/who-we-work-with/", "ghost", arrow_icon=False)}</div></div></section>'''
    # expert support
    s8 = flatten(S[8]["blocks"]); s9 = flatten(S[9]["blocks"])
    h8 = [b for b in s8 if b["type"] == "heading"]
    acc9 = next(b for b in s9 if b["type"] == "feature_accordion")
    t9 = [b for b in s9 if b["type"] in ("heading", "paragraph")]
    support = f'''<section class="section paper"><div class="container">
  <div class="section-head"><span class="eyebrow teal">Support</span><h2>{heading_html(h8[0]["html"])}</h2><p class="lead">{heading_html(h8[1]["html"]) if len(h8) > 1 else ""}</p></div>
  <div class="split" style="align-items:start"><div class="prose" data-reveal="left"><div class="card tint-teal"><span class="icon-tile teal lg">{I.icon("headset")}</span>{render_prose(t9, ctx, 3)}<div class="btn-row">{btn("Meet your support team", "/personal-support/", "primary")}</div></div></div><div data-reveal="right">{accordion_html(acc9, ctx)}</div></div>
</div></section>'''
    # search has changed
    s10 = S[10]
    cols = next(b for b in s10["blocks"] if b["type"] == "columns")
    search = f'<section class="section"><div class="container">{render_split(cols["cols"][0], [], ctx, reverse=False, eyebrow="Search Everywhere Optimization", key="search")}</div></section>'
    # trusted map
    s11 = flatten(S[11]["blocks"])
    h11 = [b for b in s11 if b["type"] == "heading"]
    p11 = [b for b in s11 if b["type"] == "paragraph"]
    map_img = next((b for b in s11 if b["type"] == "image"), None)
    trusted = f'''<section class="section paper"><div class="container">
  <div class="section-head"><span class="eyebrow violet">Trusted nationwide</span><h2>{heading_html(h11[0]["html"])}</h2><p class="lead">{heading_html(h11[1]["html"]) if len(h11) > 1 else ""} {p11[0]["html"] if p11 else ""}</p></div>
  <div class="device frame" data-reveal="scale">{img_tag(map_img) if map_img and not is_screenshot(map_img) else I.mock_map()}</div>
  <p class="center small muted" style="margin-top:14px">{p11[1]["html"] if len(p11) > 1 else ""}</p>
</div></section>'''
    # testimonials
    s12 = flatten(S[12]["blocks"])
    car = next(b for b in s12 if b["type"] == "carousel")
    h12 = next(b for b in s12 if b["type"] == "heading")
    testimonials = f'''<section class="section"><div class="container">
  <div class="section-head"><span class="eyebrow amber">Reviews</span><h2>{heading_html(h12["html"])}</h2><p class="lead">Real words from business owners who chose {esc(BRAND_SHORT)}.</p></div>
  {carousel([quote_card(s["html"], s["author"], "", s.get("stars", 5)) for s in car["slides"]])}
  <div class="btn-row center" style="margin-top:20px">{btn("See our case studies", "/case-studies/", "ghost", arrow_icon=False)}</div>
</div></section>'''
    # latest insights
    latest = "".join(post_card(p, i) for i, p in enumerate(posts[:3]))
    insights = f'<section class="section paper"><div class="container"><div class="section-head"><span class="eyebrow">From the blog</span><h2>Insights for local business</h2><p class="lead">Practical guidance on getting found, getting chosen and running smarter.</p></div><div class="post-grid">{latest}</div><div class="btn-row center" style="margin-top:32px">{btn("Read the blog", "/blog/", "ghost", arrow_icon=False)}</div></div></section>'
    body = "\n".join([hero, stats_html, everything, three, industries, support, search, trusted, testimonials, insights, cta_band(), app_promo()])
    return layout({**page, "title": f"{BRAND} | Digital Marketing, Websites, SEO & Business Management Platform"}, body)


# ---------- locations index ----------
def build_locations(page: dict) -> str:
    ctx = page_ctx(page, "Markets")
    S = page["sections"]
    hero = hero_from_section(S[0], ctx, page, "center")
    states = []
    for sec in S[1:]:
        flat = flatten(sec["blocks"])
        st = next((b for b in flat if b["type"] == "heading"), None)
        if not st:
            continue
        cities = []
        cur = None
        for b in flat:
            if b["type"] == "blurb":
                cur = {"name": b.get("title") or "", "links": []}
                cities.append(cur)
            elif b["type"] == "button" and cur is not None:
                cur["links"].append((b["text"], b["href"]))
        states.append((text_of(st["html"]), cities))
    jump = "".join(f'<a href="#{slugify(s)}">{esc(s)}</a>' for s, _ in states)
    blocks = []
    for s, cities in states:
        cards = ""
        for i, c in enumerate(cities):
            links = "".join(f'<a href="{esc(h)}">{esc(t)}</a>' for t, h in c["links"])
            cards += f'<div class="city-card" data-reveal style="--i:{i % 6}"><strong>{I.icon("pin")}{esc(c["name"])}</strong><div class="links">{links}</div></div>'
        blocks.append(f'<div class="state-block" id="{slugify(s)}" style="margin-bottom:40px"><h3>{esc(s)}</h3><div class="state-grid">{cards}</div></div>')
    total = sum(len(c) for _, c in states)
    body = f'''{hero}
<section class="section tight"><div class="container"><div class="stats" style="grid-template-columns:repeat(3,1fr)"><div class="stat" data-reveal><div class="stat-value" data-count="{len(states)}">{len(states)}</div><div class="stat-label">States</div></div><div class="stat" data-reveal style="--i:1"><div class="stat-value" data-count="{total}">{total}</div><div class="stat-label">Local markets</div></div><div class="stat" data-reveal style="--i:2"><div class="stat-value" data-count="3">3</div><div class="stat-label">Services per market</div></div></div></div></section>
<section class="section paper"><div class="container"><div class="state-jump">{jump}</div>{"".join(blocks)}</div></section>
{cta_band("Don't see your market?", "We work with businesses across the country. Tell us where you are and we'll build a plan around your area.")}'''
    return layout(page, body)


def location_siblings(path: str) -> str:
    m = re.match(r"^/locations/(digital-marketing|seo|web-design)-(.+)/$", path)
    if not m:
        return ""
    kind, city = m.groups()
    links = [("digital-marketing", "Digital Marketing"), ("web-design", "Web Design"), ("seo", "SEO")]
    pills = "".join(f'<a href="/locations/{k}-{city}/" class="{"on" if k == kind else ""}">{esc(t)}</a>' for k, t in links)
    return f'<section class="section tight" style="padding-top:0"><div class="container"><div class="pill-nav" data-reveal><a href="/locations/">{I.icon("map")}All locations</a>{pills}</div></div></section>'


# ---------- case studies ----------
def build_case_studies(page: dict) -> str:
    ctx = page_ctx(page, "Case studies")
    S = page["sections"]
    hero = hero_from_section(S[0], ctx, page)
    stories, more_cols, heading_more, lead_more, buttons = [], None, None, None, []
    for b in S[1]["blocks"]:
        if b["type"] == "columns":
            bl = next((x for c in b["cols"] for x in c if x["type"] == "blurb"), None)
            vid = next((x for c in b["cols"] for x in c if x["type"] == "video"), None)
            if bl:
                stories.append((bl, vid))
            else:
                more_cols = b
        elif b["type"] == "heading":
            heading_more = b
        elif b["type"] == "paragraph":
            lead_more = b
        elif b["type"] == "button":
            buttons.append(b)
    cards = []
    for i, (bl, vid) in enumerate(stories):
        quote = render_prose(bl["blocks"], ctx, 4)
        qtext = esc(text_of(quote).strip("“”\""))
        if vid and vid.get("src") and vid["src"] != "about:blank":
            media = video_card(vid)
        elif bl.get("image"):
            media = f'<div class="img-wrap rounded shadow">{img_tag(bl["image"])}</div>'
        else:
            media = ""
        cards.append(f'<div data-reveal style="--i:{i % 4}">{media}<div class="quote-card" style="margin-top:16px;height:auto">{stars()}<blockquote>{qtext}</blockquote><div class="who"><span class="avatar">{esc(initials(bl.get("title") or ""))}</span><span><strong>{esc(bl.get("title") or "")}</strong><span>{esc(BRAND_SHORT)} client</span></span></div></div></div>')
    videos = f'<section class="section"><div class="container"><div class="section-head"><span class="eyebrow">In their words</span><h2>Business owners on working with {esc(BRAND_SHORT)}</h2><p class="lead">Watch and read what our clients say about the people, the platform and the results.</p></div><div class="grid grid-2">{"".join(cards)}</div></div></section>'
    more = ""
    if more_cols:
        more = f'<section class="section paper"><div class="container"><div class="section-head"><span class="eyebrow teal">Success stories</span><h2>{heading_html(heading_more["html"]) if heading_more else "More success stories"}</h2><p class="lead">{lead_more["html"] if lead_more else ""}</p></div>{cards_from_columns(more_cols, ctx) or ""}<div class="btn-row center" style="margin-top:32px">{btn("Start your free quote", "#quote-form", "primary")}</div></div></section>'
    rest = "".join(render_section(s, i, ctx, page) for i, s in enumerate(S[2:], start=2))
    return layout(page, hero + videos + more + rest + cta_band("Your business could be our next success story.", "See how a connected marketing and business platform helps businesses like yours grow."))


# ---------- pricing ----------
def build_pricing(page: dict) -> str:
    return build_generic(page, eyebrow="Pricing")


# ---------- about ----------
def build_about(page: dict) -> str:
    ctx = page_ctx(page, "Company")
    S = page["sections"]
    flat0 = flatten(S[0]["blocks"])
    h1 = next(b for b in flat0 if b["type"] == "heading")
    lead = next((b for b in flat0 if b["type"] == "paragraph"), None)
    blurbs = [b for b in flat0 if b["type"] == "blurb"]
    hero = f'<section class="hero compact">{orbs()}<div class="container"><div class="hero-center"><span class="eyebrow">Company</span><h1 class="words">{heading_html(h1["html"])}</h1><p class="lead">{lead["html"] if lead else ""}</p><div class="btn-row">{btn("Book a demo", "/book-a-demo/", "primary", "lg")}{btn("See careers", "/careers/", "ghost", "lg", False)}</div></div></div></section>'
    stats = f'<section class="section tight"><div class="container"><div class="stats"><div class="stat" data-reveal><div class="stat-value" data-count="23,000+">23,000+</div><div class="stat-label">Businesses growing with {esc(BRAND_SHORT)}</div></div><div class="stat" data-reveal style="--i:1"><div class="stat-value" data-count="5,000+">5,000+</div><div class="stat-label">Positive reviews</div></div><div class="stat" data-reveal style="--i:2"><div class="stat-value" data-count="15+">15+</div><div class="stat-label">Years in local digital marketing</div></div><div class="stat" data-reveal style="--i:3"><div class="stat-value" data-count="78">78</div><div class="stat-label">Local markets served</div></div></div></div></section>'
    values = f'<section class="section"><div class="container"><div class="section-head"><span class="eyebrow">How we work</span><h2>Small business mindset, big company support</h2><p class="lead">The tools and expertise of a major agency, delivered with the personal touch of a local partner.</p></div>{feature_cards([{"title": b.get("title"), "blocks": b["blocks"], "href": None} for b in blurbs], ctx, 3)}</div></section>'
    rest = []
    for i, sec in enumerate(S[1:], start=1):
        html = render_section(sec, i, ctx, page)
        rest.append(html)
    body = "\n".join([hero, stats, values] + rest + [cta_band("Let's build something together.", "See how a connected marketing and business platform can work for you.")])
    return layout(page, body)


# ---------- FAQ ----------
def build_faq(page: dict) -> str:
    tail = cta_band("Still have questions?", "Talk to a real person. Our Charlotte-based team is available Monday–Friday, 9am–5pm EST.", ("Contact support", "/support/"), ("Call " + PHONE, PHONE_TEL))
    return build_generic(page, "center", "Help", tail=tail)


# ---------- our work ----------
def build_our_work(page: dict) -> str:
    ctx = page_ctx(page, "Portfolio")
    S = page["sections"]
    flat0 = flatten(S[0]["blocks"])
    h = next(b for b in flat0 if b["type"] == "heading")
    p = next((b for b in flat0 if b["type"] == "paragraph"), None)
    hero = f'<section class="hero compact">{orbs()}<div class="container"><div class="hero-center"><span class="eyebrow">Portfolio</span><h1 class="words">{heading_html(h["html"])}</h1><p class="lead">{p["html"] if p else ""}</p></div></div></section>'
    images, cats = [], []
    form_sec = None
    for sec in S[1:]:
        flat = flatten(sec["blocks"])
        if any(b["type"] == "form" for b in flat):
            form_sec = sec
            continue
        cat = next((text_of(b["html"]) for b in flat if b["type"] == "paragraph"), "")
        if cat and cat not in cats:
            cats.append(cat)
        for b in flat:
            if b["type"] == "image":
                images.append({**b, "cat": cat})
    filters = '<button class="on" data-filter="all" type="button">All</button>' + "".join(f'<button data-filter="{slugify(c)}" type="button">{esc(c)}</button>' for c in cats)
    gallery = f'<section class="section"><div class="container"><div class="filter-bar" data-target="#gallery">{filters}</div>{gallery_html(images, cats=True)}</div></section>'
    form_html = render_section(form_sec, 2, ctx, page) if form_sec else ""
    body = "\n".join([hero, gallery, form_html, cta_band("Want a website that works this hard?", "Every site we build is mobile-first, search-ready and connected to your business tools.")])
    return layout(page, body)


# ---------- projects ----------
def project_card(p: dict, cats: dict, i: int) -> str:
    cat = next((c for c in cats.values() if p["slug"] in c["projects"]), None)
    return f'''<a class="post-card" href="{esc(p["path"])}" data-reveal style="--i:{i % 6}"><div class="thumb"><img src="{esc(p["image"] or "")}" alt="{esc(p["title"])} website" loading="lazy"></div>
<div class="body"><div class="cats">{f"<span>{esc(cat['name'])}</span>" if cat else ""}</div><h3>{esc(p["title"])}</h3><p class="excerpt">Custom website design and build for a {esc(cat["name"].lower() if cat else "local")} business.</p><div class="meta"><span>{esc(fmt_date(p.get("date") or ""))}</span></div></div></a>'''


def build_projects(projects: dict, pcats: dict, title: str = "Projects", path: str = "/project/", filter_cat: dict = None) -> str:
    items = sorted(projects.values(), key=lambda p: (p.get("date") or "", p["slug"]), reverse=True)
    if filter_cat:
        items = [p for p in items if p["slug"] in filter_cat["projects"]]
    pills = f'<a href="/project/" class="{"on" if not filter_cat else ""}">All projects</a>' + "".join(f'<a href="{esc(c["path"])}" class="{"on" if filter_cat and c["slug"] == filter_cat["slug"] else ""}">{esc(c["name"])}</a>' for c in pcats.values())
    hero = f'<section class="hero compact">{orbs()}<div class="container"><div class="hero-center"><span class="eyebrow">Portfolio</span><h1 class="words">{esc(title)}</h1><p class="lead">Recent website builds for local businesses — mobile-first, search-ready and connected to the {esc(BRAND_SHORT)} platform.</p><div class="pill-nav" style="justify-content:center">{pills}</div></div></div></section>'
    grid = f'<section class="section"><div class="container"><div class="post-grid">{"".join(project_card(p, pcats, i) for i, p in enumerate(items))}</div><div class="btn-row center" style="margin-top:36px">{btn("See the full portfolio", "/our-work/", "ghost", arrow_icon=False)}</div></div></section>'
    desc = f"{title} — recent website builds by {BRAND}."
    return layout({"path": path, "title": title, "description": desc}, hero + grid + cta_band("Want a website like these?", "Tell us about your business and we'll show you what's possible."))


def build_project(p: dict, projects: dict, pcats: dict) -> str:
    cat = next((c for c in pcats.values() if p["slug"] in c["projects"]), None)
    related = [x for x in projects.values() if x["slug"] != p["slug"] and (not cat or x["slug"] in cat["projects"])][:3]
    hero = f'''<section class="hero compact">{orbs()}<div class="container">{breadcrumb([("Home", "/"), ("Projects", "/project/"), (cat["name"], cat["path"]) if cat else ("Project", ""), (p["title"], "")])}
<div class="hero-center"><span class="eyebrow">{esc(cat["name"] if cat else "Project")}</span><h1 class="words">{esc(p["title"])}</h1><p class="lead">A custom {esc(cat["name"].lower() if cat else "business")} website designed and built by the {esc(BRAND_SHORT)} team.</p></div></div></section>
<section class="section tight"><div class="container"><div class="device frame" data-reveal="scale"><a href="{esc(p["image"] or "#")}" data-lightbox="{esc(p["image"] or "")}"><img src="{esc(p["image"] or "")}" alt="{esc(p["title"])} website" loading="eager"></a></div></div></section>
<section class="section paper"><div class="container"><div class="grid grid-3"><div class="card"><span class="icon-tile">{I.icon("layout")}</span><h3>Mobile-first design</h3><p>Built to look sharp and load fast on every device.</p></div><div class="card"><span class="icon-tile teal">{I.icon("search")}</span><h3>Search-ready structure</h3><p>Service pages, geo pages and FAQs structured for local search.</p></div><div class="card"><span class="icon-tile violet">{I.icon("target")}</span><h3>Lead conversion built in</h3><p>Booking, quotes and click-to-call wired into the platform.</p></div></div></div></section>'''
    rel = f'<section class="section"><div class="container"><div class="section-head"><h2>More projects</h2></div><div class="post-grid">{"".join(project_card(x, pcats, i) for i, x in enumerate(related))}</div></div></section>' if related else ""
    return layout({"path": p["path"], "title": p["title"], "description": f"{p['title']} — a custom website built by {BRAND}.", "image": p.get("image")}, hero + rel + cta_band("Ready for a site like this?", "We'll design, build and manage it — and connect it to the tools that run your business."))


# ---------- careers ----------
def build_careers(main: dict, sub: dict) -> str:
    ctx = page_ctx(sub, "Careers")
    S = sub["sections"]
    m0 = flatten(main["sections"][0]["blocks"])
    h1 = next(b for b in m0 if b["type"] == "heading")
    vid = next((b for b in m0 if b["type"] == "video_popup"), None)
    bg = main["sections"][0].get("meta", {}).get("bg_video")
    rot = next((b for s in main["sections"] for b in flatten(s["blocks"]) if b["type"] == "rotating_text"), None)
    bg_video = f'<div class="bg-video" aria-hidden="true"><video autoplay muted loop playsinline preload="metadata"><source src="{esc(bg)}" type="video/mp4"></video></div>' if bg else ""
    watch = f'<a class="btn btn-ghost btn-lg" href="{esc(vid["src"])}" data-lightbox="{esc(vid["src"])}">{I.icon("play")}Life at {esc(BRAND_SHORT)}</a>' if vid else ""
    hero = f'<section class="hero">{orbs()}{bg_video}<div class="container"><div class="hero-center"><span class="eyebrow">Careers · Charlotte, NC & Phoenix, AZ</span><h1 class="words">{h1["html"]}</h1><div class="btn-row">{btn("Explore open roles", "#open-roles", "primary", "lg")}{watch}</div></div></div></section>'
    rotating = f'<section class="section tight"><div class="container">{rotating_html(rot)}</div></section>' if rot else ""
    parts = [hero, rotating]
    for i, sec in enumerate(S[1:], start=1):
        flat = flatten(sec["blocks"])
        imgs = [b for b in flat if b["type"] == "image"]
        blurbs = [b for b in flat if b["type"] == "blurb"]
        if imgs and len(imgs) == 3 and not blurbs:  # awards
            h = first_heading(sec["blocks"])
            tiles = "".join(f'<div class="award" data-reveal style="--i:{j}"><img src="{esc(b["src"])}" alt="{esc(b.get("alt") or b.get("title") or "Award")}" loading="lazy"><span class="icon-tile amber">{I.icon("award")}</span><strong>{esc(t)}</strong></div>' for j, (b, t) in enumerate(zip(imgs, ["Charlotte Business Journal — Best Places to Work", "Best & Brightest Companies to Work For", "Top Workplace"])))
            parts.append(f'<section class="section paper"><div class="container"><div class="section-head"><span class="eyebrow amber">Awards</span><h2>{heading_html(h["html"]) if h else "Award-winning workplace"}</h2></div><div class="grid grid-3">{tiles}</div></div></section>')
            continue
        if imgs and len(imgs) >= 6 and not blurbs:  # team photos
            tiles = "".join(f'<div class="tile" style="aspect-ratio:1;border-radius:20px;overflow:hidden;background:var(--grad-soft)" data-reveal="scale" data-stagger><img src="{esc(b["src"])}" alt="{esc(BRAND_SHORT)} team member" loading="lazy" style="width:100%;height:100%;object-fit:cover"></div>' for b in imgs)
            parts.append(f'<section class="section tight" id="life-here"><div class="container"><div class="grid grid-4">{tiles}</div></div></section>')
            continue
        if blurbs and all(b.get("icon") for b in blurbs):  # team quotes
            h = first_heading(sec["blocks"]); p = next((b for b in flat if b["type"] == "paragraph" and b not in [x for bl in blurbs for x in bl["blocks"]]), None)
            cards = []
            for j, b in enumerate(blurbs):
                ps = [text_of(x["html"]) for x in b["blocks"] if x["type"] == "paragraph"]
                quote = next((x for x in ps if x.startswith("“") or x.startswith('"')), ps[-1] if ps else "")
                role = " · ".join(x for x in ps if x != quote)[:80]
                cards.append(f'<div data-reveal style="--i:{j % 6}">{quote_card(esc(quote), b.get("title") or "", role)}</div>')
            parts.append(f'<section class="section"><div class="container"><div class="section-head"><span class="eyebrow">Our team</span><h2>{heading_html(h["html"]) if h else ""}</h2><p class="lead">{p["html"] if p else ""}</p></div><div class="grid grid-3">{"".join(cards)}</div></div></section>')
            continue
        if blurbs and all(b.get("image") for b in blurbs):  # perks
            for b in blurbs:
                b.pop("image", None)
            h = first_heading(sec["blocks"]); p = next((b for b in flat if b["type"] == "paragraph" and b not in [x for bl in blurbs for x in bl["blocks"]]), None)
            parts.append(f'<section class="section paper"><div class="container"><div class="section-head"><span class="eyebrow teal">Perks</span><h2>{heading_html(h["html"]) if h else ""}</h2><p class="lead">{p["html"] if p else ""}</p></div>{feature_cards([{"title": b.get("title"), "blocks": b["blocks"]} for b in blurbs], ctx, 3)}</div></section>')
            continue
        parts.append(render_section(sec, i, ctx, sub))
    roles = f'''<section class="section paper" id="open-roles"><div class="container"><div class="section-head"><span class="eyebrow">Open roles</span><h2>Find your next role at {esc(BRAND_SHORT)}</h2><p class="lead">We hire across sales, client success, production and marketing in Charlotte, NC and Phoenix, AZ — and we've promoted from within 120+ times in the last decade.</p></div>
<div class="grid grid-4">{"".join(f'<div class="card" data-reveal style="--i:{i}"><span class="icon-tile {I.tint(i)}">{I.icon(ic)}</span><h3>{esc(t)}</h3><p>{esc(d)}</p></div>' for i, (t, d, ic) in enumerate([("Inside Sales", "Consult with local business owners and build campaigns that fit their goals.", "headset"), ("Client Success", "Be the trusted point of contact who helps clients grow month after month.", "heart"), ("Production & Design", "Build websites, content and campaigns that get results.", "layout"), ("Marketing & Operations", "Keep the engine running — from recruiting to systems to strategy.", "compass")]))}</div>
<div class="btn-row center" style="margin-top:32px">{btn("Introduce yourself", "/support/", "primary", "lg")}<a class="btn btn-ghost btn-lg" href="mailto:careers@meridianlocal.com">careers@meridianlocal.com</a></div></div></section>'''
    parts.append(roles)
    page = {"path": "/careers/", "title": f"Careers | {BRAND} | Charlotte, NC & Phoenix, AZ", "description": sub.get("description") or main.get("description")}
    return layout(page, "\n".join(parts))


# ---------- help center ----------
def build_help_center() -> list[tuple[str, str]]:
    out = []
    tiles = "".join(f'<a class="tile-link" href="{esc(h)}" data-reveal style="--i:{i}"><span class="icon-tile {I.tint(i)}">{I.icon(ic)}</span>{esc(t)}</a>' for i, (h, t, ic) in enumerate([(CLIENT_LOGIN_URL, "Client login — view your reporting", "chart"), ("/help-center/sign-in/", "Sign in to your account", "key"), ("/help-center/agent-sign-in/", "Agent sign in", "user"), ("/help-center/forgot-password/", "Reset your password", "lock"), ("/help-center/sign-up/", "Create an account", "edit"), ("/support/", "Contact support", "message"), ("/frequently-asked-questions/", "Browse the FAQ", "help")]))
    body = f'''<section class="hero compact">{orbs()}<div class="container"><div class="hero-center"><span class="eyebrow">Help Center</span><h1 class="words">How can we help?</h1><p class="lead">Sign in to view your monthly reporting and manage your {esc(BRAND_SHORT)} Business Platform, browse answers, or reach a real person Monday–Friday, 9am–5pm EST.</p><div class="search-box" style="max-width:560px;margin:8px auto 0"><input type="search" placeholder="Search articles and guides…" aria-label="Search help" onkeydown="if(event.key==='Enter'){{location.href='/search/?q='+encodeURIComponent(this.value)}}"><button class="btn btn-primary" data-search-open>Search</button></div></div></div></section>
<section class="section"><div class="container"><div class="tile-grid">{tiles}</div></div></section>
<section class="section paper"><div class="container"><div class="contact-tiles"><div class="card"><span class="icon-tile">{I.icon("phone")}</span><h3>Call us</h3><p><a href="{PHONE_TEL}">{esc(PHONE)}</a><br><span class="small muted">{esc(HOURS)}</span></p></div><div class="card"><span class="icon-tile teal">{I.icon("mail")}</span><h3>Email support</h3><p>24/7 by email — we reply the next business day.</p></div><div class="card"><span class="icon-tile violet">{I.icon("phone")}</span><h3>In the app</h3><p>Message your team directly from the {esc(BRAND_SHORT)} Business Platform.</p></div></div></div></section>'''
    out.append(("/help-center/", layout({"path": "/help-center/", "title": "Help Center", "description": f"{BRAND} help center — sign in, reset your password or contact support."}, body)))

    def login_page(path, title, sub, agent=False):
        form = f'''<div class="form-card login-card"><h1 class="h3" style="margin-bottom:4px">{esc(title)}</h1><p class="form-sub">{esc(sub)}</p>
<form data-form novalidate method="post" action="{esc(FORM_ENDPOINT)}"><input type="hidden" name="form" value="{'agent-signin' if agent else 'signin'}">
<div class="field"><label for="l-email">Email</label><input id="l-email" type="email" name="email" required autocomplete="username"><span class="error">Enter a valid email.</span></div>
<div class="field"><label for="l-pass">Password</label><input id="l-pass" type="password" name="password" required minlength="8" autocomplete="current-password"><span class="error">Password must be at least 8 characters.</span></div>
<button class="btn btn-primary" type="submit" style="width:100%">Sign in</button>
<div class="links"><a href="/help-center/forgot-password/">Forgot password?</a><a href="/help-center/sign-up/">New here? Sign up</a></div>
<div class="divider">or</div><p class="small muted center" style="margin:0">Emailed us for support? <a href="/help-center/forgot-password/">Request a password</a> to track your tickets.</p></form></div>'''
        return layout({"path": path, "title": title, "description": f"{title} — {BRAND} help center.", "noindex": True}, f'<section class="hero compact">{orbs()}<div class="container">{form}</div></section>')

    out.append(("/help-center/sign-in/", login_page("/help-center/sign-in/", f"Sign in to {BRAND}", "Sign in with your password to manage support requests.")))
    out.append(("/help-center/agent-sign-in/", login_page("/help-center/agent-sign-in/", "Agent sign in", f"For {BRAND} support agents.", agent=True)))
    forgot = f'''<div class="form-card login-card"><h1 class="h3" style="margin-bottom:4px">Reset your password</h1><p class="form-sub">Enter your email and we'll send you a link to reset your password.</p>
<form data-form novalidate method="post" action="{esc(FORM_ENDPOINT)}"><input type="hidden" name="form" value="forgot-password">
<div class="field"><label for="f-email">Email</label><input id="f-email" type="email" name="email" required><span class="error">Enter a valid email.</span></div>
<button class="btn btn-primary" type="submit" style="width:100%">Send reset link</button>
<div class="links"><a href="/help-center/sign-in/">Back to sign in</a><a href="/support/">Contact support</a></div></form></div>'''
    out.append(("/help-center/forgot-password/", layout({"path": "/help-center/forgot-password/", "title": "Reset your password", "description": "Reset your password.", "noindex": True}, f'<section class="hero compact">{orbs()}<div class="container">{forgot}</div></section>')))
    signup = f'''<div class="form-card login-card"><h1 class="h3" style="margin-bottom:4px">Create your account</h1><p class="form-sub">Track support requests and manage your {esc(BRAND_SHORT)} services.</p>
<form data-form novalidate method="post" action="{esc(FORM_ENDPOINT)}"><input type="hidden" name="form" value="signup">
<div class="field"><label for="su-name">Full name</label><input id="su-name" type="text" name="name" required><span class="error">Required.</span></div>
<div class="field"><label for="su-email">Email</label><input id="su-email" type="email" name="email" required><span class="error">Enter a valid email.</span></div>
<button class="btn btn-primary" type="submit" style="width:100%">Sign up</button>
<div class="links"><a href="/help-center/sign-in/">Already have an account? Sign in</a></div></form></div>'''
    out.append(("/help-center/sign-up/", layout({"path": "/help-center/sign-up/", "title": "Sign up", "description": "Create an account.", "noindex": True}, f'<section class="hero compact">{orbs()}<div class="container">{signup}</div></section>')))
    return out


# ---------- legal ----------
def build_legal(page: dict) -> str:
    ctx = page_ctx(page, "Legal")
    S = page["sections"]
    flat0 = flatten(S[0]["blocks"]) if S else []
    h1 = next((b for b in flat0 if b["type"] == "heading" and b["level"] == 1), None)
    title = heading_html(h1["html"]) if h1 else esc(page["title"])
    # body = everything except the first heading; single-tab blocks are unwrapped;
    # one-item uppercase lists (numbered clause titles) become headings
    body_blocks = []
    first = True
    def norm(blocks):
        out = []
        for b in blocks:
            if first_flag[0] and b is h1:
                first_flag[0] = False
                continue
            if b["type"] == "tabs" and len(b["tabs"]) == 1:
                out.extend(norm(b["tabs"][0]["blocks"]))
                continue
            if b["type"] == "columns":
                for c in b["cols"]:
                    out.extend(norm(c))
                continue
            if b["type"] == "list" and len(b["items"]) == 1 and not b["items"][0].get("sub"):
                t = text_of(b["items"][0]["html"])
                if t and len(t) < 90 and t.upper() == t:
                    out.append({"type": "heading", "level": 2, "html": esc(t.rstrip(".").title() if len(t) > 30 else t.rstrip("."))})
                    continue
            if b["type"] == "paragraph":
                t = text_of(b["html"])
                if re.match(r"^\d{1,2}(\.\d{1,2})?\.?\s+[A-Z][^.]{2,60}\.$", t) and len(t) < 80:
                    out.append({"type": "heading", "level": 3, "html": b["html"]})
                    continue
            out.append(b)
        return out
    first_flag = [True]
    for s in S:
        body_blocks.extend(norm(s["blocks"]))
    # inject ids on h2/h3 for TOC
    html = render_prose(body_blocks, ctx, 2)
    toc = []
    def add_id(m):
        lvl, inner = m.group(1), m.group(2)
        t = text_of(inner)
        sid = slugify(t)[:60]
        if lvl == "2" and t:
            toc.append((sid, t))
        return f'<h{lvl} id="{sid}">{inner}</h{lvl}>'
    html = re.sub(r"<h([23])>(.*?)</h\1>", add_id, html, flags=re.S)
    toc_links = "".join(f'<a href="#{sid}">{esc(t)}</a>' for sid, t in toc[:40])
    toc_html = f'<nav class="toc" aria-label="On this page"><h4 class="small muted" style="margin-bottom:10px;text-transform:uppercase;letter-spacing:.1em;font-size:.72rem">On this page</h4>{toc_links}</nav>' if len(toc) > 2 else ""
    body = f'''<section class="hero compact">{orbs()}<div class="container">{breadcrumb([("Home", "/"), ("Legal", "/privacy-policy/"), (text_of(title), "")])}<div class="hero-copy"><span class="eyebrow">Legal</span><h1 class="words">{title}</h1><p class="lead">Last reviewed {datetime.now().strftime("%B %Y")}. Questions? <a href="/support/">Contact us</a>.</p></div></div></section>
<section class="section legal"><div class="container"><div class="two-col-doc">{toc_html or "<div></div>"}<div class="prose">{html}</div></div></div></section>'''
    return layout(page, body)


# ---------- blog ----------
def post_card(p: dict, i: int = 0, featured: bool = False) -> str:
    cats = "".join(f'<a href="{esc(c["path"])}">{esc(c["name"])}</a>' for c in p["categories"][:2])
    img = f'<img src="{esc(p["image"])}" alt="{esc(p["title"])}" loading="lazy" decoding="async">' if p.get("image") and not is_old_brand_image(p["image"]) else ""
    ph = f'<span class="ph">{I.icon("document")}</span>' if not img else ""
    if featured:
        return f'''<article class="post-featured" data-reveal><div class="thumb">{img}{ph}</div><div class="body"><div class="cats" style="margin-bottom:12px">{cats}</div><h2><a href="{esc(p["path"])}">{esc(p["title"])}</a></h2><p class="lead" style="font-size:1.05rem">{esc(p["excerpt"][:240])}</p><div class="meta small muted">{esc(fmt_date(p["date"]))} · {reading_time(p["html"])} min read · {esc(p["author_name"])}</div><div class="btn-row" style="margin-top:18px">{btn("Read article", p["path"], "primary")}</div></div></article>'''
    return f'''<article class="post-card" data-reveal style="--i:{i % 6}"><div class="thumb">{img}{ph}</div><div class="body"><div class="cats">{cats}</div><h3><a href="{esc(p["path"])}">{esc(p["title"])}</a></h3><p class="excerpt">{esc(p["excerpt"][:200])}</p><div class="meta"><span>{esc(fmt_date(p["date"]))}</span><span>·</span><span>{reading_time(p["html"])} min read</span></div></div></article>'''


def pagination(base: str, page_no: int, total: int) -> str:
    if total <= 1:
        return ""
    def href(n):
        return base if n == 1 else f"{base}page/{n}/"
    parts = []
    if page_no > 1:
        parts.append(f'<a href="{href(page_no - 1)}" aria-label="Previous">{I.icon("arrow-left")}</a>')
    shown = sorted(set([1, 2, total - 1, total, page_no - 1, page_no, page_no + 1]))
    last = 0
    for n in shown:
        if n < 1 or n > total:
            continue
        if n - last > 1:
            parts.append('<span class="gap">…</span>')
        parts.append(f'<span class="current">{n}</span>' if n == page_no else f'<a href="{href(n)}">{n}</a>')
        last = n
    if page_no < total:
        parts.append(f'<a href="{href(page_no + 1)}" aria-label="Next">{I.icon("arrow")}</a>')
    return f'<nav class="pagination" aria-label="Pagination">{"".join(parts)}</nav>'


def sidebar(tax: dict, posts_by_slug: dict) -> str:
    cats = sorted(tax["categories"].values(), key=lambda c: -len(c["posts"]))
    cat_html = "".join(f'<li><a href="{esc(c["path"])}">{esc(c["name"])}<span>{len(c["posts"])}</span></a></li>' for c in cats[:18])
    tags = sorted(tax["tags"].values(), key=lambda t: -len(t["posts"]))[:24]
    tag_html = "".join(f'<a href="{esc(t["path"])}">{esc(t["name"])}</a>' for t in tags)
    return f'''<aside class="sidebar">
<div class="card"><h4>Search</h4><form action="/search/" method="get" class="search-box"><input type="search" name="q" placeholder="Search articles…" aria-label="Search articles"></form></div>
<div class="card"><h4>Categories</h4><ul class="catlist">{cat_html}</ul><p style="margin:12px 0 0"><a class="btn-link" href="/blog/categories/">All categories {arrow()}</a></p></div>
<div class="card"><h4>Popular topics</h4><div class="taglist">{tag_html}</div></div>
<div class="card tint-blue"><h4>Free quote</h4><p><strong>See what {esc(BRAND_SHORT)} can do for your business.</strong></p><p class="small muted">Takes less than a minute — no obligation.</p>{btn("Start free quote", "/book-a-demo/", "primary", "sm")}</div>
</aside>'''


def archive_page(path: str, title: str, lead: str, posts: list[dict], tax: dict, posts_by_slug: dict, page_no: int, eyebrow: str = "Blog", intro_extra: str = "", desc: str = "") -> str:
    total = max(1, math.ceil(len(posts) / POSTS_PER_PAGE))
    chunk = posts[(page_no - 1) * POSTS_PER_PAGE: page_no * POSTS_PER_PAGE]
    featured = ""
    grid_posts = chunk
    if page_no == 1 and path == "/blog/" and chunk:
        featured = post_card(chunk[0], featured=True)
        grid_posts = chunk[1:]
    grid = "".join(post_card(p, i) for i, p in enumerate(grid_posts))
    empty = '<p class="muted">No posts yet.</p>' if not chunk else ""
    ptitle = title if page_no == 1 else f"{title} — Page {page_no}"
    body = f'''<section class="archive-hero">{orbs()}<div class="container"><div class="hero-copy" style="max-width:760px">{breadcrumb([("Home", "/"), ("Blog", "/blog/"), (title, "")]) if path != "/blog/" else ""}<span class="eyebrow">{esc(eyebrow)}</span><h1 class="words">{esc(title)}</h1><p class="lead">{lead}</p>{intro_extra}</div></div></section>
<section class="section" style="padding-top:24px"><div class="container">{featured}<div class="blog-layout" style="margin-top:{"40px" if featured else "0"}"><div><div class="post-grid" style="grid-template-columns:repeat(2,minmax(0,1fr))">{grid}</div>{empty}{pagination(path, page_no, total)}</div>{sidebar(tax, posts_by_slug)}</div></div></section>'''
    return layout({"path": path if page_no == 1 else f"{path}page/{page_no}/", "title": ptitle, "description": desc or text_of(lead)}, body)


def build_post(p: dict, posts_by_slug: dict, tax: dict, all_posts: list[dict]) -> str:
    cats = "".join(f'<a class="chip" href="{esc(c["path"])}">{esc(c["name"])}</a>' for c in p["categories"][:4])
    tags = "".join(f'<a href="/blog/tag/{esc(t)}/">{esc(tax["tags"][t]["name"])}</a>' for t in p.get("tags", []) if t in tax["tags"])
    author = tax["authors"].get(p["author_slug"] or "", {"name": p["author_name"], "path": "/blog/"})
    hero_img = f'<div class="hero-img" data-reveal="scale"><img src="{esc(p["image"])}" alt="{esc(p["title"])}" fetchpriority="high"></div>' if p.get("image") and not is_old_brand_image(p["image"]) else ""
    # inline CTA after the 3rd paragraph-ish block
    body_html = re.sub(r'<figure class="post-figure">(?:(?!</figure>).)*?TownsquareInteractive(?:(?!</figure>).)*?</figure>', "", p["html"], flags=re.S | re.I)
    cta = f'<div class="cta-inline"><div class="card tint-blue" style="display:flex;gap:18px;align-items:center;flex-wrap:wrap"><span class="icon-tile lg">{I.icon("zap")}</span><div style="flex:1;min-width:220px"><strong>Want more customers from search, maps and AI?</strong><p class="small muted" style="margin:4px 0 0">Get a free, no-obligation look at how {esc(BRAND_SHORT)} would work for your business.</p></div>{btn("Get a free quote", "/book-a-demo/", "primary", "sm")}</div></div>'
    parts = re.split(r"(?=<h2)", body_html, maxsplit=2)
    if len(parts) >= 3:
        body_html = parts[0] + parts[1] + cta + "".join(parts[2:])
    else:
        body_html = body_html + cta
    # related: same first category, newest
    related = []
    seen = {p["slug"]}
    for c in p["categories"]:
        for s in tax["categories"].get(c["slug"], {}).get("posts", []):
            if s not in seen and s in posts_by_slug:
                related.append(posts_by_slug[s]); seen.add(s)
            if len(related) >= 3:
                break
        if len(related) >= 3:
            break
    if len(related) < 3:
        for q in all_posts:
            if q["slug"] not in seen:
                related.append(q); seen.add(q["slug"])
            if len(related) >= 3:
                break
    prev_html = f'<a class="prev" href="{esc(p["prev"])}"><small>Previous</small>{esc(posts_by_slug[p["prev"].strip("/").split("/")[-1]]["title"]) if p["prev"].strip("/").split("/")[-1] in posts_by_slug else "Previous article"}</a>' if p.get("prev") and p["prev"].startswith("/blog/") and p["prev"] != "/blog/" else "<span></span>"
    next_html = f'<a class="next" href="{esc(p["next"])}"><small>Next</small>{esc(posts_by_slug[p["next"].strip("/").split("/")[-1]]["title"]) if p["next"].strip("/").split("/")[-1] in posts_by_slug else "Next article"}</a>' if p.get("next") and p["next"].startswith("/blog/") and p["next"] != "/blog/" else "<span></span>"
    url = SITE_URL + p["path"]
    share = f'''<div class="share"><span class="small muted">Share</span>
<a href="https://www.linkedin.com/sharing/share-offsite/?url={esc(url)}" target="_blank" rel="noopener" aria-label="Share on LinkedIn"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9"><rect x="3" y="9" width="4" height="12"/><circle cx="5" cy="5" r="2"/><path d="M11 21v-7a3 3 0 016 0v7M11 9v12M17 21v-7"/></svg></a>
<a href="https://www.facebook.com/sharer/sharer.php?u={esc(url)}" target="_blank" rel="noopener" aria-label="Share on Facebook"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9"><path d="M14 8h3V4h-3a4 4 0 00-4 4v3H7v4h3v6h4v-6h3l1-4h-4V8z"/></svg></a>
<a href="https://twitter.com/intent/tweet?url={esc(url)}&text={esc(p["title"])}" target="_blank" rel="noopener" aria-label="Share on X">{I.icon("share")}</a>
<a href="mailto:?subject={esc(p["title"])}&body={esc(url)}" aria-label="Share by email">{I.icon("mail")}</a></div>'''
    ld = json.dumps({"@context": "https://schema.org", "@type": "BlogPosting", "headline": p["title"], "datePublished": p["date"], "author": {"@type": "Person", "name": author["name"]}, "publisher": {"@type": "Organization", "name": BRAND}, "image": None if is_old_brand_image(p.get("image")) else p.get("image"), "mainEntityOfPage": url, "description": p["excerpt"][:300]})
    body = f'''<section class="article-hero">{orbs()}<div class="narrow" style="position:relative;z-index:1">{breadcrumb([("Home", "/"), ("Blog", "/blog/"), (p["categories"][0]["name"], p["categories"][0]["path"]) if p["categories"] else ("Article", ""), ])}
<div class="chip-row" style="margin-bottom:16px">{cats}</div>
<h1 class="words" style="font-size:clamp(2rem,4.4vw,3.4rem)">{esc(p["title"])}</h1>
<div class="meta"><span class="avatar">{esc(initials(author["name"]))}</span><span>By <a href="{esc(author["path"])}">{esc(author["name"])}</a></span><span>·</span><span>{esc(fmt_date(p["date"]))}</span><span>·</span><span>{reading_time(p["html"])} min read</span></div>
{hero_img}</div></section>
<section class="article-body"><div class="narrow"><div class="prose">{body_html}</div>
{f'<div class="taglist" style="margin-top:36px">{tags}</div>' if tags else ""}
{share}
<div class="post-nav">{prev_html}{next_html}</div>
<div class="author-card card" style="margin-top:36px"><span class="avatar">{esc(initials(author["name"]))}</span><div><strong>{esc(author["name"])}</strong><p class="small muted" style="margin:4px 0 0">Writing about local marketing, search and running a small business at {esc(BRAND)}. <a href="{esc(author["path"])}">More from this author</a></p></div></div>
</div></section>
<section class="section paper"><div class="container"><div class="section-head"><span class="eyebrow">Keep reading</span><h2>Related articles</h2></div><div class="post-grid">{"".join(post_card(r, i) for i, r in enumerate(related))}</div></div></section>
{cta_band("Turn insight into action.", "See how a connected marketing and business platform can help you get found, get chosen and grow.")}'''
    page = {"path": p["path"], "title": p["seo_title"] or p["title"], "description": p["excerpt"], "image": None if is_old_brand_image(p.get("image")) else p.get("image"), "is_post": True}
    return layout(page, body, extra_head=f'<script type="application/ld+json">{ld}</script>')


def build_categories_index(tax: dict) -> str:
    cats = sorted(tax["categories"].values(), key=lambda c: c["name"].lower())
    cards = "".join(f'<a class="tile-link" href="{esc(c["path"])}" data-reveal style="--i:{i % 9}"><span class="icon-tile {I.tint(i)}">{I.icon(I.icon_for(c["name"]))}</span><span>{esc(c["name"])}<br><span class="small muted" style="font-weight:400">{len(c["posts"])} article{"s" if len(c["posts"]) != 1 else ""}</span></span></a>' for i, c in enumerate(cats))
    tags = sorted(tax["tags"].values(), key=lambda t: t["name"].lower())
    tag_html = "".join(f'<a href="{esc(t["path"])}">{esc(t["name"])} <span class="muted">({len(t["posts"])})</span></a>' for t in tags)
    body = f'''<section class="archive-hero">{orbs()}<div class="container"><div class="hero-copy"><span class="eyebrow">Blog</span><h1 class="words">Browse by topic</h1><p class="lead">Every category and tag from the {esc(BRAND_SHORT)} blog in one place.</p></div></div></section>
<section class="section" style="padding-top:24px"><div class="container"><h2 class="h3" style="margin-bottom:20px">Categories</h2><div class="tile-grid">{cards}</div><h2 class="h3" style="margin:56px 0 20px">All tags</h2><div class="taglist">{tag_html}</div></div></section>'''
    return layout({"path": "/blog/categories/", "title": "Blog categories & tags", "description": f"Browse every category and tag on the {BRAND} blog."}, body)


def build_search(tax: dict) -> str:
    body = f'''<section class="archive-hero">{orbs()}<div class="container"><div class="hero-copy" style="max-width:760px"><span class="eyebrow">Search</span><h1 class="words">Search the blog</h1><p class="lead">Find articles on SEO, websites, reviews, CRM, email and everything else that helps a local business grow.</p></div></div></section>
<section class="section" style="padding-top:12px"><div class="container" data-search><div class="search-box" style="max-width:760px"><input type="search" placeholder="Try “Google Business Profile” or “email marketing”…" aria-label="Search articles" autofocus></div><p class="results-meta">Loading…</p><div class="results post-grid"></div></div></section>'''
    return layout({"path": "/search/", "title": "Search", "description": f"Search the {BRAND} blog."}, body)


def build_404(posts: list[dict]) -> str:
    links = "".join(f'<a class="tile-link" href="{esc(h)}"><span class="icon-tile {I.tint(i)}">{I.icon(ic)}</span>{esc(t)}</a>' for i, (h, t, ic) in enumerate([("/", "Home", "home"), ("/grow/", "Grow", "trend"), ("/run/", "Run", "grid"), ("/pricing/", "Pricing", "dollar"), ("/blog/", "Blog", "document"), ("/support/", "Contact support", "headset")]))
    body = f'''<section class="hero compact">{orbs()}<div class="container"><div class="hero-center"><div class="big-404">404</div><h1 class="words">No results found</h1><p class="lead">The page you requested could not be found. Try refining your search, or use the navigation to find what you're looking for.</p><div class="search-box" style="max-width:520px;margin:0 auto"><input type="search" placeholder="Search the blog…" aria-label="Search" onkeydown="if(event.key==='Enter'){{location.href='/search/?q='+encodeURIComponent(this.value)}}"><button class="btn btn-primary" data-search-open>Search</button></div></div></div></section>
<section class="section"><div class="container"><div class="tile-grid">{links}</div></div></section>
<section class="section paper"><div class="container"><div class="section-head"><h2>Latest from the blog</h2></div><div class="post-grid">{"".join(post_card(p, i) for i, p in enumerate(posts[:3]))}</div></div></section>'''
    return layout({"path": "/404.html", "title": "Page not found", "description": "The page could not be found.", "noindex": True}, body)


# ---------- special pages that need small tweaks ----------
def build_support(page: dict) -> str:
    ctx = page_ctx(page, "Support")
    S = page["sections"]
    flat0 = flatten(S[0]["blocks"])
    h1 = next(b for b in flat0 if b["type"] == "heading")
    sub = next((b for b in flat0 if b["type"] == "heading" and b is not h1), None)
    tiles = f'''<div class="contact-tiles" style="margin-top:36px"><div class="card" data-reveal><span class="icon-tile">{I.icon("phone")}</span><h3>Call us</h3><p><a href="{PHONE_TEL}"><strong>{esc(PHONE)}</strong></a><br><span class="small muted">{esc(HOURS)}</span></p></div><div class="card" data-reveal style="--i:1"><span class="icon-tile teal">{I.icon("mail")}</span><h3>Email</h3><p>Available 24/7 by email — we reply the next business day.</p></div><div class="card" data-reveal style="--i:2"><span class="icon-tile violet">{I.icon("pin")}</span><h3>Visit</h3><p>{esc(ADDRESS)}</p></div></div>'''
    hero = f'<section class="hero compact">{orbs()}<div class="container"><div class="hero-center"><span class="eyebrow">Support</span><h1 class="words">{heading_html(h1["html"])}</h1><p class="lead">{heading_html(sub["html"]) if sub else ""}</p></div>{tiles}</div></section>'
    form = f'<section class="section paper" id="get-started"><div class="container"><div class="split" style="align-items:start"><div data-reveal="left"><span class="eyebrow">Talk to us</span><h2>Real people. Real answers.</h2><p class="lead">Current clients can also reach their team directly through the {esc(BRAND_SHORT)} Business Platform. Not a client yet? Tell us about your business and we\'ll show you what\'s possible.</p><ul class="checks"><li>Charlotte, NC based support team</li><li>Phone support {esc(HOURS)}</li><li>24/7 email support</li></ul></div><div data-reveal="right">{support_form()}</div></div></div></section>'
    return layout(page, hero + form + cta_band("Prefer a walkthrough?", "Book a personalized demo and see the platform in action.", ("Book a demo", "/book-a-demo/"), ("Read the FAQ", "/frequently-asked-questions/")))


def build_thank_you(page: dict) -> str:
    ctx = page_ctx(page, "")
    flat = flatten(page["sections"][0]["blocks"])
    ps = [b for b in flat if b["type"] == "paragraph"]
    msg = ps[0]["html"] if ps else "Thank you for reaching out."
    steps = "".join(f'<div class="step" data-reveal style="--i:{i}"><div class="step-no">{i + 1:02d}</div><h3>{esc(t)}</h3><p>{esc(d)}</p></div>' for i, (t, d) in enumerate([("We review your request", "A member of our digital marketing team reads what you sent."), ("We reach out", "Expect a call or email — the next business day if you contacted us after hours."), ("We build your plan", "Together we shape a strategy around your business, market and goals.")]))
    body = f'''<section class="hero compact">{orbs()}<div class="container"><div class="hero-center"><span class="icon-tile lg teal" style="margin:0 auto 20px">{I.icon("check")}</span><h1 class="words">Thank you</h1><p class="lead">{msg}</p><p class="muted">Days of operation: {esc(HOURS)}</p><div class="btn-row">{btn("Back to home", "/", "primary")}{btn("Read the blog", "/blog/", "ghost", arrow_icon=False)}</div></div></div></section>
<section class="section paper"><div class="container"><div class="section-head"><h2>What happens next</h2></div><div class="steps" style="grid-template-columns:repeat(3,minmax(0,1fr))">{steps}</div></div></section>
{app_promo()}'''
    return layout({**page, "noindex": True}, body)


def build_book_demo(page: dict) -> str:
    ctx = page_ctx(page, "Book a demo")
    S = page["sections"]
    cols = next(b for b in S[0]["blocks"] if b["type"] == "columns")
    left, right = cols["cols"]
    h1 = next(b for b in left if b["type"] == "heading" and b["level"] == 1)
    sub = next((b for b in left if b["type"] == "heading" and b is not h1), None)
    ps = [b for b in left if b["type"] == "paragraph"]
    rh = next((b for b in right if b["type"] == "heading"), None)
    rp = next((b for b in right if b["type"] == "paragraph"), None)
    hero = f'''<section class="hero">{orbs()}<div class="container hero-grid"><div class="hero-copy"><span class="eyebrow">Book a demo</span><h1 class="words">{heading_html(h1["html"])}</h1><p class="h1-sub">{heading_html(sub["html"]) if sub else ""}</p><p class="lead">{ps[0]["html"] if ps else ""}</p>
<ul class="checks" style="margin-top:20px"><li>A one-hour personalized walkthrough</li><li>Built around your business, market and goals</li><li>No contracts — we earn your business monthly</li></ul>
<div class="hero-note"><span class="avatars"><span></span><span></span><span></span><span></span></span><span><span class="stars">★★★★★</span> Rated 5.0 by 5,000+ businesses</span></div></div>
<div class="hero-art" data-reveal="right">{quote_form(title=text_of(rh["html"]) if rh else "Let's talk growth.", sub=text_of(rp["html"]) if rp else "", source="/book-a-demo/", cta="Request my demo")}</div></div></section>'''
    rest = "".join(render_section(s, i, ctx, page) for i, s in enumerate(S[1:], start=1))
    return layout(page, hero + rest + cta_band("Not ready for a demo?", "Start with a free directory scan and see how your business shows up online.", ("Free directory scan", "/directory-scan/"), ("Read the FAQ", "/frequently-asked-questions/")))


def build_directory_scan(page: dict) -> str:
    ctx = page_ctx(page, "Free tool")
    flat = flatten(page["sections"][0]["blocks"])
    h = next(b for b in flat if b["type"] == "heading")
    ps = [b for b in flat if b["type"] == "paragraph"]
    bt = next((b for b in flat if b["type"] == "button"), None)
    img = next((b for b in flat if b["type"] == "image"), None)
    hero = f'''<section class="hero">{orbs()}<div class="container hero-grid"><div class="hero-copy"><span class="eyebrow">Free tool</span><h1 class="words">{heading_html(h["html"])}</h1><p class="lead">{ps[0]["html"] if ps else ""}</p>{"".join(f"<p>{p['html']}</p>" for p in ps[1:])}<div class="btn-row">{btn("Run my free scan", "#quote-form", "primary", "lg")}{f'<a class="btn btn-ghost btn-lg" href="{esc(bt["href"])}" target="_blank" rel="noopener">{esc(bt["text"])}</a>' if bt else ""}</div></div>
<div class="hero-art"><div class="glow"></div><div class="img-wrap rounded shadow tilt" data-reveal="scale">{img_tag(img, lazy=False) if img else I.mock_search()}</div></div></div></section>'''
    scan_steps = "".join(f'<div class="step"><div class="step-no">{i+1:02d}</div><h3>{esc(t)}</h3><p>{esc(d)}</p></div>' for i, (t, d) in enumerate([("Tell us about your business", "Name, zip and phone. That is all we need."), ("We scan the major directories", "Google, Apple, Bing, Yelp, Facebook and dozens more."), ("You get a clear report", "Where you are missing, where you are wrong and what to fix first.")]))
    form = f'<section class="section paper"><div class="container"><div class="split" style="align-items:start"><div data-reveal="left"><span class="eyebrow">How it works</span><h2>See how directories see you</h2><div class="steps" style="grid-template-columns:1fr">{scan_steps}</div></div><div data-reveal="right">{quote_form(title="Run my free directory scan", sub="No obligation. Results in minutes.", source="/directory-scan/", cta="Run my scan")}</div></div></div></section>'
    return layout(page, hero + form + cta_band("Fix every listing, everywhere.", "Our Local Online Listings service keeps your business accurate across 200+ directories.", ("Explore Local Listings", "/business-listings/"), ("Book a demo", "/book-a-demo/")))


def build_privacy_form(page: dict) -> str:
    form = f'''<div class="form-card" id="quote-form"><h2 class="form-title">Privacy request form</h2><p class="form-sub">Use this form to exercise your privacy rights, including requests to access, correct, delete or opt out of the sale or sharing of your personal information.</p>
<form data-form data-redirect="/thank-you/" method="post" action="{esc(FORM_ENDPOINT)}" novalidate><input type="hidden" name="form" value="privacy-request">
<p class="hp"><label>Leave this empty<input type="text" name="website" tabindex="-1" autocomplete="off"></label></p>
<div class="field-row"><div class="field"><label for="p-first">First name</label><input id="p-first" name="first_name" type="text" required><span class="error">Required.</span></div><div class="field"><label for="p-last">Last name</label><input id="p-last" name="last_name" type="text" required><span class="error">Required.</span></div></div>
<div class="field-row"><div class="field"><label for="p-email">Email</label><input id="p-email" name="email" type="email" required><span class="error">Enter a valid email.</span></div><div class="field"><label for="p-phone">Phone (optional)</label><input id="p-phone" name="phone" type="tel"></div></div>
<div class="field"><label for="p-state">State of residence</label><input id="p-state" name="state" type="text" required autocomplete="address-level1"><span class="error">Required.</span></div>
<div class="field"><label>I am a…</label><div class="radio-row"><label><input type="radio" name="relationship" value="customer" required> Customer</label><label><input type="radio" name="relationship" value="prospect"> Prospect</label><label><input type="radio" name="relationship" value="employee"> Employee / applicant</label><label><input type="radio" name="relationship" value="other"> Other</label></div></div>
<div class="field"><label for="p-type">Request type</label><select id="p-type" name="request_type" required><option value="">Select one…</option><option>Access my personal information</option><option>Correct my personal information</option><option>Delete my personal information</option><option>Opt out of sale or sharing</option><option>Limit use of sensitive personal information</option><option>Other</option></select><span class="error">Select a request type.</span></div>
<div class="field"><label for="p-details">Details</label><textarea id="p-details" name="details" rows="5" placeholder="Tell us anything that helps us locate your information."></textarea></div>
<label class="check"><input type="checkbox" name="attest" value="yes" required> I confirm that I am the person (or the authorized agent of the person) whose information is the subject of this request.</label>
<div class="form-actions"><button type="submit" class="btn btn-blue">Submit request {arrow()}</button></div>
<p class="form-fine">We will verify your identity before acting on your request and respond within the time required by applicable law. See our <a href="/privacy-policy/">Privacy Policy</a> for details.</p></form></div>'''
    body = f'''<section class="hero compact">{orbs()}<div class="container">{breadcrumb([("Home", "/"), ("Privacy Policy", "/privacy-policy/"), ("Privacy request form", "")])}<div class="hero-copy"><span class="eyebrow">Legal</span><h1 class="words">Privacy web form</h1><p class="lead">Submit a request about the personal information {esc(BRAND)} holds about you.</p></div></div></section>
<section class="section legal"><div class="container"><div class="two-col-doc"><div class="prose small"><h3 class="h4">Your rights</h3><p>Depending on where you live, you may have the right to know what personal information we collect, to correct or delete it, and to opt out of its sale or sharing.</p><p>You can also call us at <a href="{PHONE_TEL}">{esc(PHONE)}</a> or write to {esc(ADDRESS)}.</p></div>{form}</div></div></section>'''
    return layout(page, body)


# ---------------------------------------------------------------------------
# main build
# ---------------------------------------------------------------------------
def write(out: str, path: str, html: str):
    last = path.rstrip("/").rsplit("/", 1)[-1]
    if not path.endswith("/") and ("." in last or last.startswith("_")):
        full = os.path.join(out, path.lstrip("/"))
    else:
        full = os.path.join(out, path.strip("/"), "index.html")
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as fh:
        fh.write(html)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--content", default="content")
    ap.add_argument("--out", default="site")
    args = ap.parse_args()
    C, OUT = args.content, args.out
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)

    pages = {p["path"]: p for p in json.load(open(os.path.join(C, "pages.json"), encoding="utf-8"))}
    tax = json.load(open(os.path.join(C, "taxonomy.json"), encoding="utf-8"))
    posts = []
    for f in sorted(os.listdir(os.path.join(C, "posts"))):
        posts.append(json.load(open(os.path.join(C, "posts", f), encoding="utf-8")))
    posts.sort(key=lambda p: (p["date"], p["slug"]), reverse=True)
    # --- rebrand leftovers in URLs: author slugs and a handful of post slugs ---
    for old, new in AUTHOR_SLUGS.items():
        if old in tax["authors"]:
            tax["authors"][old]["path"] = f"/blog/author/{new}/"
            LEGACY.append((f"/blog/author/{old}/", f"/blog/author/{new}/"))
    slug_renames = {}
    for p in posts:
        if "townsquare" in p["slug"]:
            new_slug = p["slug"].replace("townsquare", "meridian")
            slug_renames[p["slug"]] = new_slug
            LEGACY.append((p["path"], f"/blog/{new_slug}/"))
            SLUG_MAP[p["path"]] = f"/blog/{new_slug}/"
            p["slug"], p["path"] = new_slug, f"/blog/{new_slug}/"
    for store in ("categories", "tags", "authors"):
        for t in tax[store].values():
            t["posts"] = [slug_renames.get(s, s) for s in t["posts"]]
            if store != "authors" and "townsquare" in t["slug"]:
                new_slug = t["slug"].replace("townsquare", "meridian")
                kind = "category" if store == "categories" else "tag"
                LEGACY.append((t["path"], f"/blog/{kind}/{new_slug}/"))
                SLUG_MAP[t["path"]] = f"/blog/{kind}/{new_slug}/"
                t["slug"], t["path"] = new_slug, f"/blog/{kind}/{new_slug}/"
    for p in posts:
        for c in p["categories"]:
            if "townsquare" in c["slug"]:
                c["slug"] = c["slug"].replace("townsquare", "meridian")
                c["path"] = f"/blog/category/{c['slug']}/"
        p["tags"] = [t.replace("townsquare", "meridian") for t in p.get("tags", [])]
    for store in ("categories", "tags"):
        tax[store] = {t["slug"]: t for t in tax[store].values()}
    for p in posts:
        for k in ("prev", "next"):
            if p.get(k):
                p[k] = SLUG_MAP.get(p[k], p[k])
    if "/townsquare-hosting-terms/" in pages:
        pg = pages.pop("/townsquare-hosting-terms/")
        pg["path"] = "/hosting-terms/"
        pages["/hosting-terms/"] = pg
        LEGACY.append(("/townsquare-hosting-terms/", "/hosting-terms/"))
    posts_by_slug = {p["slug"]: p for p in posts}

    urls = []

    def emit(path, html, priority="0.6"):
        write(OUT, path, html)
        if not path.endswith(".html") and not path.startswith("/help-center/") and path not in ("/thank-you/", "/form-test/", "/locations-test/"):
            urls.append((path, priority))

    # assets
    shutil.copytree(os.path.join(HERE, "assets"), os.path.join(OUT, "assets"))
    shutil.copy(os.path.join(HERE, "assets", "logo.svg"), os.path.join(OUT, "assets", "favicon.svg"))

    # home
    emit("/", build_home(pages["/"], posts), "1.0")

    special = {
        "/locations/": lambda p: build_locations(p),
        "/pricing/": build_pricing,
        "/about-us/": build_about,
        "/frequently-asked-questions/": build_faq,
        "/our-work/": build_our_work,
        "/support/": build_support,
        "/thank-you/": build_thank_you,
        "/book-a-demo/": build_book_demo,
        "/directory-scan/": build_directory_scan,
        "/privacy-web-form/": build_privacy_form,
        "/case-studies/": build_case_studies,
    }
    legal_paths = {h for h, _ in LEGAL_LINKS}
    for path, page in pages.items():
        if path in ("/", "/<any-nonexistent-url>/", "/blog/", "/project/", "/careers/", "/careers-site/"):
            continue
        if path in special:
            emit(path, special[path](page), "0.8")
        elif path in legal_paths:
            emit(path, build_legal(page), "0.3")
        elif path.startswith("/locations/"):
            emit(path, build_generic(page, extra_after_hero=location_siblings(path)), "0.5")
        elif path in ("/grow/", "/run/", "/personal-support/"):
            emit(path, build_generic(page, "center"), "0.9")
        elif path in ("/form-test/", "/locations-test/"):
            emit(path, build_generic(page, noindex=True), "0.1")
        elif path in ("/who-we-work-with/", "/what-to-expect/"):
            emit(path, build_generic(page), "0.8")
        else:
            emit(path, build_generic(page), "0.7")

    # careers (merged)
    emit("/careers/", build_careers(pages["/careers/"], pages["/careers-site/"]), "0.7")

    # help center
    for path, html in build_help_center():
        emit(path, html)

    # projects
    projects = tax["projects"]; pcats = tax["project_categories"]
    emit("/project/", build_projects(projects, pcats), "0.5")
    for c in pcats.values():
        emit(c["path"], build_projects(projects, pcats, title=f"{c['name']} websites", path=c["path"], filter_cat=c), "0.4")
    for p in projects.values():
        emit(p["path"], build_project(p, projects, pcats), "0.4")

    # blog
    total = math.ceil(len(posts) / POSTS_PER_PAGE)
    lead = f"Practical guidance on getting found, getting chosen and running smarter — from the {BRAND_SHORT} team."
    for n in range(1, total + 1):
        html = archive_page("/blog/", "Insights for local business", lead, posts, tax, posts_by_slug, n, desc=f"Business software and marketing blog from {BRAND}.")
        emit("/blog/" if n == 1 else f"/blog/page/{n}/", html, "0.8" if n == 1 else "0.3")
    emit("/blog/categories/", build_categories_index(tax), "0.4")
    for p in posts:
        emit(p["path"], build_post(p, posts_by_slug, tax, posts), "0.6")
    for kind, store, eyebrow in (("category", tax["categories"], "Category"), ("tag", tax["tags"], "Topic"), ("author", tax["authors"], "Author")):
        for t in store.values():
            tposts = [posts_by_slug[s] for s in t["posts"] if s in posts_by_slug]
            tposts.sort(key=lambda p: (p["date"], p["slug"]), reverse=True)
            tot = max(1, math.ceil(len(tposts) / POSTS_PER_PAGE))
            if kind == "author":
                lead_t = f"{len(tposts)} article{'s' if len(tposts) != 1 else ''} by {t['name']}."
                title = t["name"]
            elif kind == "tag":
                lead_t = f"{len(tposts)} article{'s' if len(tposts) != 1 else ''} tagged “{t['name']}”."
                title = t["name"]
            else:
                parent = tax["categories"].get(t.get("parent") or "")
                lead_t = f"{len(tposts)} article{'s' if len(tposts) != 1 else ''} in {t['name']}" + (f" (part of {parent['name']})." if parent else ".")
                title = t["name"]
            for n in range(1, tot + 1):
                html = archive_page(t["path"], title, lead_t, tposts, tax, posts_by_slug, n, eyebrow=eyebrow)
                emit(t["path"] if n == 1 else f"{t['path']}page/{n}/", html, "0.4" if n == 1 else "0.2")

    # short login aliases → client login
    for alias in ("/login/", "/client-login/", "/sign-in/"):
        LEGACY.append((alias, CLIENT_LOGIN_URL))
    # redirect stubs for renamed URLs
    for old, new in LEGACY:
        write(OUT, old, redirect_stub(new))

    # search + 404
    emit("/search/", build_search(tax), "0.3")
    write(OUT, "/404.html", build_404(posts))
    # search index
    idx = [{"t": p["title"], "e": p["excerpt"][:200], "u": p["path"], "d": fmt_date(p["date"]), "c": "|".join(f"{c['name']}~{c['path']}" for c in p["categories"][:3])} for p in posts]
    write(OUT, "/search.json", json.dumps(idx, ensure_ascii=False))
    # sitemap / robots / redirects
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"<url><loc>{esc(SITE_URL + u)}</loc><priority>{pr}</priority></url>\n" for u, pr in urls) + "</urlset>\n"
    write(OUT, "/sitemap.xml", sm)
    write(OUT, "/robots.txt", f"User-agent: *\nAllow: /\nDisallow: /help-center/\nDisallow: /thank-you/\nSitemap: {SITE_URL}/sitemap.xml\n")
    redirects = "\n".join([
        "/automated-email-sms/ /automated-email-and-sms/ 301", "/business-management-platform/ /run/ 301", "/business-email-managment/ /business-email-management/ 301",
        "/free-report/ /directory-scan/ 301", "/social-ads/ /targeted-social-ads/ 301", "/what-is-crm/ /cloud-based-crm/ 301", "/contact/ /support/ 301",
        "/seo/ /search-engine-optimization/ 301", "/listings/ /business-listings/ 301", "/careers-site/ /careers/ 301", "/blog/category/google-reviews/google-business-profile/* /blog/category/google-business-profile/:splat 301",
    ] + [f"{old} {new} 301" for old, new in LEGACY] + ["/* /404.html 404"])
    write(OUT, "/_redirects", redirects)
    with open(os.path.join(OUT, ".nojekyll"), "w") as fh:
        fh.write("")
    print(f"wrote {len(urls)} pages to {OUT}")


if __name__ == "__main__":
    main()
