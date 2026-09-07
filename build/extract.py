#!/usr/bin/env python3
"""
extract.py — turn the raw HTML archive (the six tsi-*.zip files) into clean,
structured JSON that build/site.py renders with the new design.

Usage:
    python3 build/extract.py --src <dir-with-unzipped-archive> --out content/

The archive is a Divi/WordPress export. Every page is reduced to an ordered tree of
sections → rows → columns → blocks, where a block is one of: heading, paragraph, list,
image, button, blurb, pricing, testimonial, faq, feature_accordion, stat, form, video,
embed, quote, gallery, carousel, tabs, people, hr.

All copy is rebranded (Townsquare Interactive → Charlie Company Media) and every internal
link is rewritten to a root-relative path on the new site.
"""
from __future__ import annotations

import argparse
import copy
import csv
import html
import json
import os
import re
import sys
from collections import OrderedDict, defaultdict
from datetime import datetime
from urllib.parse import urlparse, unquote

from bs4 import BeautifulSoup, NavigableString, Tag, MarkupResemblesLocatorWarning
import warnings
warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)

# ---------------------------------------------------------------------------
# Brand
# ---------------------------------------------------------------------------
BRAND = "Charlie Company Media"
BRAND_SHORT = "Charlie Company"
BRAND_APP = "Charlie Company App"
BRAND_PLATFORM = "Charlie Company Business Platform"

REBRAND_RULES = [
    # order matters: longest / most specific first
    (re.compile(r"Townsquare Business Management Platform App", re.I), f"{BRAND_PLATFORM} App"),
    (re.compile(r"Townsquare Business Management Platform", re.I), BRAND_PLATFORM),
    (re.compile(r"Town\s?Square Interactive'?s", re.I), f"{BRAND}'s"),
    (re.compile(r"Town\s?Square Interactive", re.I), BRAND),
    (re.compile(r"Townsquare Media'?s", re.I), "Charlie Company Holdings'"),
    (re.compile(r"Townsquare Media", re.I), "Charlie Company Holdings"),
    (re.compile(r"Townsquare Hosting", re.I), f"{BRAND_SHORT} Hosting"),
    (re.compile(r"Townsquare Engage", re.I), f"{BRAND_SHORT} Engage"),
    (re.compile(r"Townsquare App'?s", re.I), f"{BRAND_APP}'s"),
    (re.compile(r"Townsquare App", re.I), BRAND_APP),
    (re.compile(r"Towsquare App", re.I), BRAND_APP),
    (re.compile(r"Townsquare'?s", re.I), f"{BRAND_SHORT}'s"),
    (re.compile(r"Townsqsuare'?s", re.I), f"{BRAND_SHORT}'s"),
    (re.compile(r"\bTownsquare\b", re.I), BRAND_SHORT),
    (re.compile(r"\bTown\s?Square\b", re.I), BRAND_SHORT),
    (re.compile(r"\bTSI\b"), BRAND_SHORT),
    (re.compile(r"\bvcita'?s\b", re.I), f"{BRAND_SHORT}'s"),
    (re.compile(r"townsquareinteractive\.com", re.I), "charliecompanymedia.com"),
    (re.compile(r"@townsquaremedia\.com", re.I), "@charliecompanymedia.com"),
]


def rebrand(text: str | None) -> str | None:
    if not text:
        return text
    for rx, rep in REBRAND_RULES:
        text = rx.sub(rep, text)
    return text


# ---------------------------------------------------------------------------
# Link rewriting
# ---------------------------------------------------------------------------
ORIGIN_HOSTS = {"www.townsquareinteractive.com", "townsquareinteractive.com"}
DEAD_LINKS = {
    "/automated-email-sms/": "/automated-email-and-sms/",
    "/business-management-platform/": "/run/",
    "/business-email-managment/": "/business-email-management/",
    "/free-report/": "/directory-scan/",
    "/social-ads/": "/targeted-social-ads/",
    "/what-is-crm/": "/cloud-based-crm/",
    "/contact/": "/support/",
    "/seo/": "/search-engine-optimization/",
    "/listings/": "/business-listings/",
    "/blog/6-google-business-profile-tips-for-contractors/": "/blog/gbp-tips-for-contractors-that-actually-work/",
    "/blog/how-to-get-more-google-reviews/": "/blog/category/google-reviews/",
    # legacy marketing pages that no longer exist on the source site
    "/social-media/": "/social-media-marketing/",
    "/ppc-advertising/": "/targeted-display-ads/",
    "/ppc-marketing/": "/targeted-display-ads/",
    "/customer-targeting/": "/targeted-display-ads/",
    "/business-tools/": "/run/",
    "/business-solutions/": "/run/",
    "/business-solutions/seo/": "/search-engine-optimization/",
    "/digital-marketing-services/": "/grow/",
    "/digital-marketing/": "/grow/",
    "/get-started/": "/book-a-demo/",
    "/contact-us/": "/support/",
    "/testimonials/": "/case-studies/",
    "/directories/": "/business-listings/",
    "/blog-subscription/": "/blog/",
    "/member-benefits/": "/about-us/",
    "/painting-marketing/": "/who-we-work-with/",
    "/roofing-search-engine-optimization/": "/roofing-marketing/",
    "/roofing-business-tools/": "/roofing-marketing/",
    "/willow-massage/": "/case-studies/",
    "/search-engine-optimization/)/": "/search-engine-optimization/",
}

KNOWN_PATHS: set[str] = set()  # filled once the manifest is read
UNRESOLVED: dict[str, int] = defaultdict(int)


def norm_path(p: str) -> str:
    p = unquote(p or "/")
    if not p.startswith("/"):
        p = "/" + p
    if not p.endswith("/") and "." not in p.rsplit("/", 1)[-1]:
        p += "/"
    return p


def rewrite_link(href: str | None) -> str | None:
    """Map any archive link onto the new site's URL space."""
    if not href:
        return href
    href = href.strip()
    if href.startswith(("mailto:", "tel:", "sms:", "#", "javascript:")):
        return rebrand(href) if href.startswith("mailto:") else href
    if href.startswith("http://Read"):
        return "/support/"
    u = urlparse(href)
    host = (u.netloc or "").lower()
    if host == "careers.townsquareinteractive.com":
        p = norm_path(u.path)
        if p in ("/", ""):
            return "/careers/"
        if p.startswith("/jobs"):
            return "/careers/#open-roles"
        if p.startswith("/who-we-are"):
            return "/careers/#life-here"
        if p.startswith("/blog"):
            return "/blog/category/careers/"
        if "/wp-content/" in p:
            return href
        return "/careers/"
    if host == "helpcenter.townsquareinteractive.com":
        if "role=agent" in href:
            return "/help-center/agent-sign-in/"
        if "password" in href:
            return "/help-center/forgot-password/"
        if "register" in href:
            return "/help-center/sign-up/"
        return "/help-center/"
    if host in ORIGIN_HOSTS or (host == "" and href.startswith("/")):
        p = u.path or "/"
        if "/wp-content/" in p or "/files/" in p:
            # asset – keep absolute on the original CDN so it still resolves
            if host == "":
                return "https://www.townsquareinteractive.com" + p
            return href
        if "page_id=" in (u.query or ""):
            return "/case-studies/"
        p = norm_path(p)
        p = re.sub(r"/page/1/$", "/", p)
        if p in DEAD_LINKS:
            return DEAD_LINKS[p]
        if p in KNOWN_PATHS:
            return p + (("#" + u.fragment) if u.fragment else "")
        # legacy /YYYY/MM/DD/slug/ blog urls
        m = re.match(r"^/\d{4}/\d{2}/\d{2}/([^/]+)/$", p)
        if m:
            cand = f"/blog/{m.group(1)}/"
            return cand if cand in KNOWN_PATHS else search_url(m.group(1))
        m = re.match(r"^/blog/(tag|category|author)/", p)
        if m:
            return p  # taxonomy that may exist after generation
        m = re.match(r"^/category/(.+)$", p)
        if m:
            return "/blog/category/" + m.group(1)
        if p.startswith("/blog/"):
            slug = p.split("/")[2] if len(p.split("/")) > 2 else ""
            cand = f"/blog/{slug}/"
            if cand in KNOWN_PATHS:
                return cand
            UNRESOLVED[p] += 1
            return search_url(slug)
        if p.startswith("/search/"):
            return "/search/"
        if p.startswith("/testimonials/"):
            return "/case-studies/"
        if p.startswith(("/member-benefits/", "/partners/")):
            return "/about-us/"
        # sub-page of a known page (e.g. /towing-marketing/towing-website-design/)
        first = "/" + p.strip("/").split("/")[0] + "/"
        if first in KNOWN_PATHS:
            return first
        if first in DEAD_LINKS:
            return DEAD_LINKS[first]
        UNRESOLVED[p] += 1
        return p
    return href


def search_url(slug: str) -> str:
    words = re.sub(r"[-_]+", " ", slug).strip()
    words = re.sub(r"\b(reviews?|vs)\b", r"\1", words)
    from urllib.parse import quote_plus
    return "/search/?q=" + quote_plus(words[:80])


# ---------------------------------------------------------------------------
# HTML helpers
# ---------------------------------------------------------------------------
INLINE_KEEP = {"a", "strong", "b", "em", "i", "br", "u", "sup", "sub", "code", "mark", "s", "small"}


def classes(el: Tag) -> list[str]:
    c = el.get("class") if isinstance(el, Tag) else None
    return list(c) if c else []


def has_class_prefix(el: Tag, prefix: str) -> bool:
    return any(c.startswith(prefix) for c in classes(el))


def has_class(el: Tag, name: str) -> bool:
    return name in classes(el)


def clean_text(s: str | None) -> str:
    if s is None:
        return ""
    s = html.unescape(s)
    s = s.replace("\xa0", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return rebrand(s)


def img_src(img: Tag) -> str | None:
    for attr in ("data-lazy-src", "data-src", "data-lazy-original", "src"):
        v = img.get(attr)
        if v and not v.startswith("data:"):
            return v.strip()
    return None


def img_ratio(img: Tag) -> tuple[int, int] | None:
    w, h = img.get("width"), img.get("height")
    try:
        if w and h and int(w) > 0 and int(h) > 0:
            return int(w), int(h)
    except ValueError:
        pass
    src = img.get("src") or ""
    m = re.search(r"viewBox='0%200%20(\d+)%20(\d+)'", src)
    if m and int(m.group(1)) > 0 and int(m.group(2)) > 0:
        return int(m.group(1)), int(m.group(2))
    return None


def image_block(img: Tag, link: str | None = None) -> dict | None:
    src = img_src(img)
    if not src:
        return None
    b = {"type": "image", "src": src, "alt": clean_text(img.get("alt") or ""),
         "title": clean_text(img.get("title") or "")}
    r = img_ratio(img)
    if r:
        b["w"], b["h"] = r
    if link:
        b["href"] = rewrite_link(link)
    return b


def inline_html(el: Tag, top: bool = True) -> str:
    """Serialize an element's children keeping only safe inline markup."""
    out = []
    for node in el.children:
        if isinstance(node, NavigableString):
            if node.parent and node.parent.name in ("script", "style"):
                continue
            out.append(html.escape(clean_text(str(node)) if False else rebrand(html.unescape(str(node)).replace("\xa0", " ")), quote=False))
        elif isinstance(node, Tag):
            name = node.name.lower()
            if name in ("script", "style", "noscript", "form", "input", "button", "svg"):
                continue
            if name == "br":
                out.append("<br>")
                continue
            inner = inline_html(node, top=False)
            if name == "a":
                href = rewrite_link(node.get("href"))
                if not inner.strip():
                    continue
                attrs = f' href="{html.escape(href or "#", quote=True)}"'
                if href and href.startswith("http"):
                    attrs += ' target="_blank" rel="noopener"'
                out.append(f"<a{attrs}>{inner}</a>")
            elif name in ("strong", "b"):
                out.append(f"<strong>{inner}</strong>" if inner.strip() else inner)
            elif name in ("em", "i"):
                out.append(f"<em>{inner}</em>" if inner.strip() else inner)
            elif name in ("u", "sup", "sub", "code", "mark", "s", "small"):
                out.append(f"<{name}>{inner}</{name}>")
            else:
                out.append(inner)
    s = "".join(out)
    s = re.sub(r"[ \t\r\n]+", " ", s)
    s = re.sub(r"\s*<br>\s*", "<br>", s)
    return s.strip() if top else s


def list_block(el: Tag) -> dict:
    items = []
    for li in el.find_all("li", recursive=False):
        sub = None
        for child in li.find_all(["ul", "ol"], recursive=False):
            sub = list_block(child)
            child.extract()
        t = inline_html(li)
        if t or sub:
            item = {"html": t}
            if sub:
                item["sub"] = sub
            items.append(item)
    return {"type": "list", "ordered": el.name == "ol", "items": items}


FORM_NAME_RX = re.compile(r"^(.{0,50}\bForm\b.{0,30}|Universal Blog Form|Inbound Dynamic Form|webform|Locations Form.*)$", re.I)


def rich_blocks(el: Tag) -> list[dict]:
    """Convert arbitrary rich HTML (Divi text module, blurb description, post body)
    into a flat list of blocks."""
    blocks: list[dict] = []

    def push_par(html_str: str):
        html_str = html_str.strip()
        if not html_str:
            return
        plain = clean_text(BeautifulSoup(html_str, "lxml").get_text(" "))
        if not plain:
            return
        if FORM_NAME_RX.match(plain) and len(plain) < 60:
            return  # editor-only labels like "Website Pricing Form"
        blocks.append({"type": "paragraph", "html": html_str})

    def walk(node: Tag):
        for child in node.children:
            if isinstance(child, NavigableString):
                t = str(child)
                if t.strip():
                    push_par(html.escape(rebrand(html.unescape(t)).strip(), quote=False))
                continue
            if not isinstance(child, Tag):
                continue
            name = child.name.lower()
            cls = classes(child)
            if name in ("script", "style", "noscript", "form", "input", "button", "select", "textarea", "label", "svg"):
                continue
            if "gform_wrapper" in cls or "gform_heading" in cls:
                continue
            if name in ("h1", "h2", "h3", "h4", "h5", "h6"):
                txt = inline_html(child)
                if clean_text(BeautifulSoup(txt, "lxml").get_text()):
                    blocks.append({"type": "heading", "level": int(name[1]), "html": txt})
            elif name == "p":
                imgs = child.find_all("img")
                if imgs and not clean_text(child.get_text()):
                    for im in imgs:
                        a = im.find_parent("a")
                        b = image_block(im, a.get("href") if a else None)
                        if b:
                            blocks.append(b)
                    continue
                for im in imgs:  # image inside a text paragraph
                    a = im.find_parent("a")
                    b = image_block(im, a.get("href") if a else None)
                    if b:
                        blocks.append(b)
                    im.extract()
                for ifr in child.find_all("iframe"):
                    src = ifr.get("src") or ifr.get("data-src") or ""
                    if src and src != "about:blank":
                        blocks.append({"type": "embed", "src": src})
                    ifr.extract()
                push_par(inline_html(child))
            elif name in ("ul", "ol"):
                lb = list_block(child)
                if lb["items"]:
                    blocks.append(lb)
            elif name == "img":
                a = child.find_parent("a")
                b = image_block(child, a.get("href") if a else None)
                if b:
                    blocks.append(b)
            elif name == "a" and child.find("img") and not clean_text(child.get_text()):
                for im in child.find_all("img"):
                    b = image_block(im, child.get("href"))
                    if b:
                        blocks.append(b)
            elif name == "blockquote":
                inner = rich_blocks(child)
                text = " ".join(b.get("html", "") for b in inner if b["type"] == "paragraph")
                if text:
                    blocks.append({"type": "quote", "html": text})
            elif name == "hr":
                blocks.append({"type": "hr"})
            elif name == "iframe":
                src = child.get("src") or child.get("data-src") or ""
                if src and src != "about:blank":
                    blocks.append({"type": "embed", "src": src})
            elif name == "video":
                srcs = [s.get("src") for s in child.find_all("source") if s.get("src")]
                src = child.get("src") or (srcs[0] if srcs else None)
                if src:
                    blocks.append({"type": "video", "src": src})
            elif name == "table":
                rows = []
                for tr in child.find_all("tr"):
                    rows.append([inline_html(td) for td in tr.find_all(["td", "th"])])
                if rows:
                    blocks.append({"type": "table", "rows": rows})
            elif name in ("div", "section", "article", "center", "span", "figure", "figcaption", "header", "footer", "main", "aside", "nav", "font", "small", "big", "pre", "address", "dl", "dt", "dd", "details", "summary"):
                # containers: if it only holds inline content treat as paragraph
                if name in ("div", "span", "center", "font", "figcaption", "dd", "dt", "pre", "address", "small", "big") and not child.find(
                        ["p", "div", "ul", "ol", "h1", "h2", "h3", "h4", "h5", "h6", "img", "table", "blockquote", "iframe", "video", "section", "article", "figure"]):
                    push_par(inline_html(child))
                else:
                    walk(child)
            elif name in INLINE_KEEP:
                push_par(inline_html(child))
            else:
                walk(child)

    walk(el)
    return blocks


# ---------------------------------------------------------------------------
# Divi module parsing
# ---------------------------------------------------------------------------
MODULE_PREFIXES = (
    "et_pb_text", "et_pb_heading", "et_pb_blurb", "et_pb_image", "et_pb_button_module_wrapper",
    "et_pb_code", "et_pb_pricing_tables", "et_pb_testimonial", "et_pb_accordion", "et_pb_toggle",
    "et_pb_video", "et_pb_tabs", "et_pb_gravity_forms", "et_pb_group_carousel", "dtq_accordion",
    "dtq_number_counter", "dtq_image_carousel", "et_pb_icon", "et_pb_menu", "et_pb_blog",
    "et_pb_post_title", "et_pb_post_content", "et_pb_posts_nav", "et_pb_team_member", "et_pb_cta",
    "et_pb_number_counter", "et_pb_counters", "et_pb_gallery", "et_pb_slider", "et_pb_divider",
    "et_pb_social_media_follow", "et_pb_map", "et_pb_search", "et_pb_sidebar", "et_pb_login",
    "et_pb_signup", "et_pb_contact_form", "et_pb_comments", "et_pb_portfolio", "et_pb_filterable_portfolio",
    "et_pb_shop", "et_pb_audio", "et_pb_circle_counter", "et_pb_bar_counters", "et_pb_fullwidth",
    "et_pb_countdown_timer", "et_pb_group",
)
SKIP_MODULES = ("et_pb_icon", "et_pb_menu", "et_pb_blog", "et_pb_post_title", "et_pb_post_content",
                "et_pb_posts_nav", "et_pb_divider", "et_pb_social_media_follow", "et_pb_search",
                "et_pb_sidebar", "et_pb_comments", "dtq_image_carousel")


def module_kind(el: Tag) -> str | None:
    cls = classes(el)
    for c in cls:
        if c == "et_pb_group_carousel":
            return "et_pb_group_carousel"
    for c in cls:
        if c == "et_pb_group":
            return "et_pb_group"
    for c in cls:
        for p in MODULE_PREFIXES:
            if p in ("et_pb_group", "et_pb_group_carousel"):
                continue
            if c == p or (c.startswith(p) and re.match(rf"^{re.escape(p)}(_\d+)?(_tb_\w+)?$", c)):
                return p
        if c.startswith("dtq_accordion") and "item" not in c:
            return "dtq_accordion"
        if c.startswith("dtq_number_counter"):
            return "dtq_number_counter"
        if c.startswith("dtq_image_carousel") and "item" not in c:
            return "dtq_image_carousel"
        if c.startswith("dtq_video_modal"):
            return "dtq_video_modal"
        if c.startswith("dtq_animated_text"):
            return "dtq_animated_text"
    return None


def is_row(el: Tag) -> bool:
    return any(c in ("et_pb_row", "et_flex_row", "et_block_row", "et_pb_row_inner") for c in classes(el))


def is_column(el: Tag) -> bool:
    return any(c in ("et_pb_column", "et_flex_column", "et_block_column", "et_pb_column_inner") for c in classes(el))


def button_block(el: Tag) -> dict | None:
    a = el if el.name == "a" else el.find("a")
    if not a:
        return None
    for ic in a.select(".et_pb_icon, .et-pb-icon"):
        ic.extract()
    text = clean_text(a.get_text(" "))
    href = rewrite_link(a.get("href"))
    if not text:
        return None
    return {"type": "button", "text": text, "href": href or "#"}


def blurb_block(el: Tag) -> dict:
    b: dict = {"type": "blurb"}
    hdr = el.select_one(".et_pb_module_header")
    if hdr:
        a = hdr.find("a")
        b["title"] = clean_text(hdr.get_text(" "))
        if a and a.get("href"):
            b["href"] = rewrite_link(a.get("href"))
    img = el.select_one(".et_pb_main_blurb_image img")
    if img:
        ib = image_block(img)
        if ib:
            b["image"] = ib
    icon = el.select_one(".et_pb_main_blurb_image .et-pb-icon")
    if icon is not None:
        b["icon"] = True
    desc = el.select_one(".et_pb_blurb_description")
    b["blocks"] = rich_blocks(desc) if desc else []
    link = el.find("a", href=True)
    if link and "href" not in b and has_class(el, "et_clickable"):
        b["href"] = rewrite_link(link["href"])
    return b


def pricing_block(el: Tag) -> dict:
    tables = []
    for t in el.select(".et_pb_pricing_table"):
        title = t.select_one(".et_pb_pricing_title")
        sub = t.select_one(".et_pb_best_value")
        price = t.select_one(".et_pb_et_price")
        items = [inline_html(li) for li in t.select("ul.et_pb_pricing li")]
        items = [i for i in items if i]
        btn = t.select_one(".et_pb_pricing_table_button")
        tb = {
            "title": clean_text(title.get_text()) if title else "",
            "subtitle": clean_text(sub.get_text()) if sub else "",
            "price": clean_text(price.get_text()) if price else "",
            "items": items,
            "featured": has_class(t, "et_pb_featured_table"),
        }
        if btn:
            tb["button"] = {"text": clean_text(btn.get_text()), "href": rewrite_link(btn.get("href"))}
        tables.append(tb)
    return {"type": "pricing", "tables": tables}


def testimonial_block(el: Tag) -> dict:
    content = el.select_one(".et_pb_testimonial_content") or el.select_one(".et_pb_testimonial_description_inner")
    text = " ".join(b["html"] for b in rich_blocks(content) if b["type"] == "paragraph") if content else ""
    author = el.select_one(".et_pb_testimonial_author")
    pos = el.select_one(".et_pb_testimonial_position")
    comp = el.select_one(".et_pb_testimonial_company")
    b = {"type": "testimonial", "html": text,
         "author": clean_text(author.get_text()) if author else "",
         "position": clean_text(pos.get_text()) if pos else "",
         "company": clean_text(comp.get_text()) if comp else ""}
    img = el.select_one(".et_pb_testimonial_portrait")
    if img and img.get("style"):
        m = re.search(r"url\((['\"]?)(.*?)\1\)", img["style"])
        if m:
            b["image"] = m.group(2)
    return b


def faq_block(el: Tag) -> dict:
    items = []
    for t in el.select(".et_pb_toggle"):
        title = t.select_one(".et_pb_toggle_title")
        content = t.select_one(".et_pb_toggle_content")
        items.append({"q": clean_text(title.get_text()) if title else "",
                      "blocks": rich_blocks(content) if content else []})
    return {"type": "faq", "items": items}


def dtq_accordion_block(el: Tag) -> dict:
    items = []
    for it in el.select(".dtq-accordion__item"):
        title = it.select_one(".dtq-accordion__title-text")
        a = it.select_one(".dtq-accordion__title-anchor")
        content = it.select_one(".dtq-accordion__content-inner")
        items.append({
            "title": clean_text(title.get_text()) if title else "",
            "href": rewrite_link(a.get("href")) if a else None,
            "blocks": rich_blocks(content) if content else [],
        })
    return {"type": "feature_accordion", "items": items}


def stat_block(el: Tag) -> dict:
    num = el.select_one(".dtq-number-text")
    title = el.select_one(".dtq-number-title-text")
    return {"type": "stat", "value": clean_text(num.get_text()) if num else "",
            "label": clean_text(title.get_text()) if title else ""}


def video_block(el: Tag) -> dict | None:
    src = None
    v = el.find("video")
    if v:
        src = v.get("src") or next((s.get("src") for s in v.find_all("source") if s.get("src")), None)
    ifr = el.find("iframe")
    if not src and ifr:
        src = ifr.get("src") or ifr.get("data-src")
    if not src:
        return None
    b = {"type": "video", "src": src}
    ov = el.select_one(".et_pb_video_overlay")
    if ov and ov.get("style"):
        m = re.search(r"url\((['\"]?)(.*?)\1\)", ov["style"])
        if m:
            b["poster"] = m.group(2)
    return b


def form_block(form: Tag) -> dict:
    fid = form.get("id") or ""
    inputs = {i.get("name") for i in form.find_all(["input", "textarea", "select"]) if i.get("name")}
    if "gform_5" in fid or "input_4" in inputs and "input_11" in inputs:
        kind = "quote"
    elif "gform_3" in fid or "input_7" in inputs:
        kind = "support"
    elif form.get("id") == "login-form" or form.find("input", {"type": "password"}):
        kind = "login"
    else:
        kind = "quote"
    wrapper = form.find_parent(class_="gform_wrapper")
    title = ""
    if wrapper:
        h = wrapper.select_one(".gform_title")
        if h:
            title = clean_text(h.get_text())
    return {"type": "form", "kind": kind, "title": title}


def code_blocks(el: Tag) -> list[dict]:
    inner = el.select_one(".et_pb_code_inner") or el
    form = inner.find("form")
    if form:
        return [form_block(form)]
    blocks: list[dict] = []
    links = inner.find_all("a", href=True)
    app_links = [a for a in links if "apps.apple.com" in a["href"] or "play.google.com" in a["href"]]
    if app_links:
        blocks.append({"type": "app_badges", "ios": next((a["href"] for a in app_links if "apple" in a["href"]), None),
                       "android": next((a["href"] for a in app_links if "google" in a["href"]), None)})
        return blocks
    ifr = inner.find("iframe")
    if ifr:
        src = ifr.get("src") or ifr.get("data-src")
        if src and src != "about:blank":
            blocks.append({"type": "embed", "src": src})
    v = inner.find("video")
    if v:
        vb = video_block(inner)
        if vb:
            blocks.append(vb)
    if not blocks:
        blocks = rich_blocks(inner)
    return blocks


def tabs_block(el: Tag) -> dict:
    titles = [clean_text(a.get_text()) for a in el.select(".et_pb_tabs_controls a")]
    panes = el.select(".et_pb_all_tabs .et_pb_tab")
    tabs = []
    for i, pane in enumerate(panes):
        content = pane.select_one(".et_pb_tab_content") or pane
        tabs.append({"title": titles[i] if i < len(titles) else f"Tab {i+1}", "blocks": rich_blocks(content)})
    return {"type": "tabs", "tabs": tabs}


def carousel_block(el: Tag) -> dict:
    slides = []
    for s in el.select(".et_pb_group_carousel_slide"):
        texts = [b for b in rich_blocks(s) if b["type"] == "paragraph"]
        quote = texts[0]["html"] if texts else ""
        author = ""
        if len(texts) > 1:
            author = clean_text(BeautifulSoup(texts[-1]["html"], "lxml").get_text()).lstrip("-–— ").strip()
        stars = len(s.select(".et_pb_icon"))
        if quote:
            slides.append({"html": quote, "author": author, "stars": min(stars, 5) or 5})
    return {"type": "carousel", "slides": slides}


def team_block(el: Tag) -> dict:
    name = el.select_one(".et_pb_module_header")
    pos = el.select_one(".et_pb_member_position")
    img = el.select_one(".et_pb_team_member_image img")
    desc = el.select_one(".et_pb_team_member_description")
    b = {"type": "person", "name": clean_text(name.get_text()) if name else "",
         "position": clean_text(pos.get_text()) if pos else ""}
    if img:
        ib = image_block(img)
        if ib:
            b["image"] = ib
    if desc:
        b["blocks"] = [x for x in rich_blocks(desc) if x["type"] == "paragraph"]
    return b


def module_blocks(el: Tag, kind: str) -> list[dict]:
    if kind in SKIP_MODULES:
        return []
    if kind == "et_pb_text":
        inner = el.select_one(".et_pb_text_inner") or el
        return rich_blocks(inner)
    if kind == "et_pb_heading":
        h = el.find(re.compile(r"^h[1-6]$"))
        if h:
            txt = inline_html(h)
            if clean_text(BeautifulSoup(txt, "lxml").get_text()):
                return [{"type": "heading", "level": int(h.name[1]), "html": txt}]
        return []
    if kind == "et_pb_blurb":
        return [blurb_block(el)]
    if kind == "et_pb_image":
        img = el.find("img")
        a = el.find("a", href=True)
        if img:
            b = image_block(img, a["href"] if a else None)
            return [b] if b else []
        return []
    if kind == "et_pb_button_module_wrapper":
        b = button_block(el)
        return [b] if b else []
    if kind == "et_pb_code":
        return code_blocks(el)
    if kind == "et_pb_pricing_tables":
        return [pricing_block(el)]
    if kind == "et_pb_testimonial":
        return [testimonial_block(el)]
    if kind in ("et_pb_accordion", "et_pb_toggle"):
        if kind == "et_pb_toggle" and el.find_parent(class_="et_pb_accordion"):
            return []
        return [faq_block(el)]
    if kind == "et_pb_video":
        vb = video_block(el)
        return [vb] if vb else []
    if kind == "et_pb_tabs":
        return [tabs_block(el)]
    if kind == "et_pb_gravity_forms":
        form = el.find("form")
        return [form_block(form)] if form else []
    if kind == "et_pb_group_carousel":
        return [carousel_block(el)]
    if kind == "dtq_accordion":
        return [dtq_accordion_block(el)]
    if kind == "dtq_number_counter":
        return [stat_block(el)]
    if kind == "et_pb_team_member":
        return [team_block(el)]
    if kind == "dtq_video_modal":
        a = el.select_one("[data-video-url]")
        if a and a.get("data-video-url"):
            return [{"type": "video_popup", "src": a["data-video-url"]}]
        return []
    if kind == "dtq_animated_text":
        prefix = el.select_one(".dtq-animated-text-prefix")
        items = [clean_text(li.get_text()) for li in el.select(".dtq-animated-text-main li")]
        items = [i for i in items if i]
        if items:
            return [{"type": "rotating_text", "prefix": clean_text(prefix.get_text()) if prefix else "", "items": items}]
        return []
    if kind == "et_pb_cta":
        return rich_blocks(el) + ([button_block(el.select_one(".et_pb_button"))] if el.select_one(".et_pb_button") else [])
    if kind == "et_pb_gallery":
        out = []
        for a in el.select(".et_pb_gallery_item"):
            img = a.find("img")
            if img:
                b = image_block(img, (a.find("a") or {}).get("href"))
                if b:
                    out.append(b)
        return [{"type": "gallery", "images": out}] if out else []
    if kind in ("et_pb_number_counter", "et_pb_circle_counter"):
        num = el.select_one(".percent-value, .percent")
        title = el.select_one(".title")
        return [{"type": "stat", "value": clean_text(num.get_text()) if num else "", "label": clean_text(title.get_text()) if title else ""}]
    # generic fallback
    return rich_blocks(el)


def parse_container(el: Tag) -> list[dict]:
    """Walk a Divi container and return an ordered list of blocks; rows with
    multiple non-empty columns become {'type':'columns'} blocks."""
    blocks: list[dict] = []
    for child in el.children:
        if not isinstance(child, Tag):
            continue
        cls = classes(child)
        if child.name in ("script", "style", "noscript"):
            continue
        if is_row(child):
            cols = []
            for col in child.children:
                if isinstance(col, Tag) and is_column(col):
                    cb = parse_container(col)
                    if cb:
                        cols.append(cb)
            if not cols:
                # row with no explicit columns (flex) – flatten
                blocks.extend(parse_container(child))
            elif len(cols) == 1:
                blocks.extend(cols[0])
            else:
                blocks.append({"type": "columns", "cols": cols})
            continue
        if is_column(child):
            blocks.extend(parse_container(child))
            continue
        kind = module_kind(child)
        if kind == "et_pb_group":
            blocks.extend(parse_container(child))
            continue
        if kind:
            blocks.extend(module_blocks(child, kind))
            continue
        # unknown wrapper: recurse
        blocks.extend(parse_container(child))
    return blocks


def section_meta(sec: Tag) -> dict:
    meta = {}
    style = sec.get("style") or ""
    m = re.search(r"background-image:\s*url\((['\"]?)(.*?)\1\)", style)
    if m:
        meta["bg_image"] = m.group(2)
    if sec.select_one(".et_pb_bg_layout_dark"):
        meta["dark"] = True
    custom = [c for c in classes(sec) if not c.startswith("et_") and not c.startswith("et-")]
    if custom:
        meta["classes"] = custom
    vid = sec.select_one(".et_pb_section_video_bg source, .et_pb_section_video_bg video, .et-pb-background-video source, .et-pb-background-video video")
    if vid and (vid.get("src") or vid.get("data-src")):
        meta["bg_video"] = vid.get("src") or vid.get("data-src")
    return meta


def top_sections(root: Tag) -> list[Tag]:
    secs = root.select(".et_pb_section")
    out = []
    for s in secs:
        if any(p is not root and has_class(p, "et_pb_section") for p in s.parents):
            continue
        if s.find_parent(class_="et-l--header") or s.find_parent(class_="et-l--footer"):
            continue
        out.append(s)
    return out


# ---------------------------------------------------------------------------
# Page extraction
# ---------------------------------------------------------------------------
def load_soup(path: str) -> BeautifulSoup:
    with open(path, encoding="utf-8", errors="ignore") as fh:
        return BeautifulSoup(fh.read(), "lxml")


def page_head(soup: BeautifulSoup) -> dict:
    title = soup.title.string if soup.title and soup.title.string else ""
    title = clean_text(title)
    title = re.sub(r"\s*\|\s*Charlie Company Media(\s*\|\s*Page \d+)?$", "", title)
    desc = ""
    md = soup.find("meta", attrs={"name": "description"})
    if md and md.get("content"):
        desc = clean_text(md["content"])
    og = soup.find("meta", attrs={"property": "og:image"})
    ogimg = og["content"] if og and og.get("content") else None
    body_cls = classes(soup.body) if soup.body else []
    return {"title": title, "description": desc, "og_image": ogimg, "body_classes": body_cls}


def extract_page(path: str, url_path: str) -> dict:
    soup = load_soup(path)
    for t in soup(["script", "style", "noscript"]):
        t.decompose()
    head = page_head(soup)
    root = soup.select_one("#main-content") or soup.body
    sections = []
    for sec in top_sections(root):
        blocks = parse_container(sec)
        if not blocks:
            continue
        sections.append({"meta": section_meta(sec), "blocks": blocks})
    h1 = root.find("h1")
    return {
        "path": url_path,
        "title": head["title"],
        "description": head["description"],
        "h1": clean_text(h1.get_text(" ")) if h1 else "",
        "sections": sections,
    }


# ---------------------------------------------------------------------------
# Blog
# ---------------------------------------------------------------------------
def clean_post_content(content: Tag) -> str:
    """Return sanitized HTML for a post body."""
    content = copy.copy(content)
    for t in content(["script", "style", "noscript", "form", "input", "button", "select", "textarea", "label"]):
        t.decompose()
    for t in content.select(".gform_wrapper, .gform_heading, .sharedaddy, .jp-relatedposts, .addtoany_share_save_container, .wp-block-buttons"):
        t.decompose()
    blocks = rich_blocks(content)
    return blocks_to_html(blocks)


def blocks_to_html(blocks: list[dict]) -> str:
    out = []
    for b in blocks:
        t = b["type"]
        if t == "heading":
            lvl = max(2, min(4, b["level"]))
            out.append(f"<h{lvl}>{b['html']}</h{lvl}>")
        elif t == "paragraph":
            out.append(f"<p>{b['html']}</p>")
        elif t == "list":
            out.append(list_html(b))
        elif t == "image":
            attrs = f' src="{html.escape(b["src"], True)}" alt="{html.escape(b.get("alt") or "", True)}" loading="lazy" decoding="async"'
            if b.get("w") and b.get("h"):
                attrs += f' width="{b["w"]}" height="{b["h"]}"'
            img = f"<img{attrs}>"
            if b.get("href") and not re.search(r"\.(jpe?g|png|gif|webp)$", b["href"], re.I):
                img = f'<a href="{html.escape(b["href"], True)}">{img}</a>'
            out.append(f'<figure class="post-figure">{img}</figure>')
        elif t == "quote":
            out.append(f"<blockquote><p>{b['html']}</p></blockquote>")
        elif t == "hr":
            out.append("<hr>")
        elif t == "embed":
            out.append(f'<div class="embed"><iframe src="{html.escape(b["src"], True)}" loading="lazy" allowfullscreen title="Embedded content"></iframe></div>')
        elif t == "video":
            out.append(f'<div class="embed"><video controls preload="metadata" src="{html.escape(b["src"], True)}"></video></div>')
        elif t == "table":
            rows = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in b["rows"])
            out.append(f'<div class="table-wrap"><table>{rows}</table></div>')
    return "\n".join(out)


def list_html(b: dict) -> str:
    tag = "ol" if b.get("ordered") else "ul"
    items = []
    for it in b["items"]:
        s = it["html"]
        if it.get("sub"):
            s += list_html(it["sub"])
        items.append(f"<li>{s}</li>")
    return f"<{tag}>{''.join(items)}</{tag}>"


def parse_date(soup: BeautifulSoup, root: Tag) -> str:
    m = soup.find("meta", attrs={"property": "article:published_time"})
    if m and m.get("content"):
        return m["content"][:10]
    pub = root.select_one(".published")
    if pub:
        try:
            return datetime.strptime(clean_text(pub.get_text()), "%b %d, %Y").strftime("%Y-%m-%d")
        except ValueError:
            pass
    return "1970-01-01"


def extract_post(path: str, slug: str) -> dict:
    soup = load_soup(path)
    jsonld_author = None
    jsonld_image = None
    for s in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(s.string or "")
        except Exception:
            continue
        graph = data.get("@graph", [data]) if isinstance(data, dict) else data
        for node in graph if isinstance(graph, list) else []:
            if not isinstance(node, dict):
                continue
            if node.get("@type") == "Person" and node.get("name"):
                jsonld_author = clean_text(node["name"])
            if node.get("@type") == "BlogPosting" and isinstance(node.get("image"), dict):
                jsonld_image = node["image"].get("url")
    for t in soup(["script", "style", "noscript"]):
        t.decompose()
    head = page_head(soup)
    root = soup.select_one("#main-content") or soup.body
    title_el = root.select_one("h1.entry-title") or root.find("h1")
    title = clean_text(title_el.get_text(" ")) if title_el else head["title"]
    meta = root.select_one(".et_pb_title_meta_container")
    cats = []
    author_slug, author_name = None, None
    if meta:
        for a in meta.find_all("a", href=True):
            h = a["href"]
            if "/blog/category/" in h:
                cslug = h.rstrip("/").split("/blog/category/")[-1]
                cats.append({"slug": cslug.split("/")[-1], "path": norm_path("/blog/category/" + cslug.split("/")[-1]), "name": clean_text(a.get_text())})
            elif "/blog/author/" in h:
                author_slug = h.rstrip("/").split("/")[-1]
                author_name = clean_text(a.get_text())
    feat = root.select_one(".et_pb_title_featured_container img")
    image = img_src(feat) if feat else None
    if not image:
        image = jsonld_image
    content_el = root.select_one(".et_pb_post_content")
    body_html = clean_post_content(content_el) if content_el else ""
    nav_prev = root.select_one(".et_pb_posts_nav .nav-previous a")
    nav_next = root.select_one(".et_pb_posts_nav .nav-next a")
    excerpt = head["description"]
    if not excerpt and content_el:
        p = content_el.find("p")
        excerpt = clean_text(p.get_text(" "))[:220] if p else ""
    return {
        "slug": slug,
        "path": f"/blog/{slug}/",
        "title": title,
        "seo_title": head["title"],
        "excerpt": excerpt,
        "date": parse_date(soup, root),
        "author_slug": author_slug,
        "author_name": author_name or jsonld_author or BRAND,
        "categories": cats,
        "image": image,
        "html": body_html,
        "prev": rewrite_link(nav_prev["href"]) if nav_prev else None,
        "next": rewrite_link(nav_next["href"]) if nav_next else None,
    }


def archive_slugs(path: str) -> tuple[str, list[str], list[str]]:
    """Return (name, post slugs, project slugs) listed on an archive page."""
    soup = load_soup(path)
    for t in soup(["script", "style", "noscript"]):
        t.decompose()
    root = soup.select_one("#main-content") or soup.body
    h1 = root.find("h1")
    name = clean_text(h1.get_text()) if h1 else ""
    if not name:
        t = clean_text(soup.title.string if soup.title else "")
        name = re.split(r"\s*\|\s*", t)[0]
    posts, projects = [], []
    for art in root.select("article"):
        a = art.select_one("h2.entry-title a, .entry-title a, a.entry-featured-image-url")
        if not a or not a.get("href"):
            continue
        p = urlparse(a["href"]).path
        m = re.match(r"^/blog/([^/]+)/$", p)
        if m and m.group(1) not in ("tag", "category", "author", "page"):
            posts.append(m.group(1))
            continue
        m = re.match(r"^/project/([^/]+)/$", p)
        if m and m.group(1) != "page":
            projects.append(m.group(1))
    return name, posts, projects


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def read_manifest(src: str) -> list[dict]:
    rows = []
    with open(os.path.join(src, "MANIFEST.csv"), newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            rows.append(r)
    return rows


def dedupe(seq):
    seen = set()
    out = []
    for x in seq:
        if x in seen:
            continue
        seen.add(x)
        out.append(x)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    src, out = args.src, args.out
    os.makedirs(out, exist_ok=True)
    os.makedirs(os.path.join(out, "posts"), exist_ok=True)

    www = os.path.join(src, "www.townsquareinteractive.com")
    manifest = read_manifest(src)

    # all known paths on the original site → used by rewrite_link
    for r in manifest:
        u = r["url"].split(" ")[0]
        pu = urlparse(u)
        if pu.netloc in ORIGIN_HOSTS:
            KNOWN_PATHS.add(norm_path(pu.path))
    KNOWN_PATHS.update({"/careers/", "/help-center/", "/help-center/sign-in/", "/help-center/agent-sign-in/",
                        "/help-center/forgot-password/", "/help-center/sign-up/", "/search/"})

    pages: "OrderedDict[str, dict]" = OrderedDict()
    posts: dict[str, dict] = {}
    categories: dict[str, dict] = {}
    tags: dict[str, dict] = {}
    authors: dict[str, dict] = {}
    project_cats: dict[str, dict] = {}
    projects: dict[str, dict] = {}

    post_rx = re.compile(r"^/blog/([^/]+)/$")
    arch_rx = re.compile(r"^/blog/(tag|category|author|project_category)/(.+?)/(?:page/(\d+)/)?$")

    for r in manifest:
        url = r["url"].split(" ")[0]
        file = os.path.join(src, r["file"])
        pu = urlparse(url)
        if pu.netloc not in ORIGIN_HOSTS:
            continue
        p = norm_path(pu.path)
        if not os.path.exists(file):
            print("missing file", file, file=sys.stderr)
            continue
        if p == "/" and "404" in r["file"]:
            continue
        m = arch_rx.match(p)
        if m:
            kind, slug, page_no = m.group(1), m.group(2).strip("/"), m.group(3)
            name, pslugs, prslugs = archive_slugs(file)
            store = {"tag": tags, "category": categories, "author": authors, "project_category": project_cats}[kind]
            parent = slug.split("/")[-2] if "/" in slug else None
            slug = slug.split("/")[-1]
            entry = store.setdefault(slug, {"slug": slug, "name": "", "posts": [], "projects": [],
                                            "path": f"/blog/{kind}/{slug}/"})
            if parent:
                entry["parent"] = parent
            if name and (not entry["name"] or not page_no):
                entry["name"] = name
            entry["posts"].extend(pslugs)
            entry["projects"].extend(prslugs)
            continue
        m = post_rx.match(p)
        if m and m.group(1) not in ("tag", "category", "author", "page", "project_category"):
            slug = m.group(1)
            try:
                posts[slug] = extract_post(file, slug)
            except Exception as e:  # pragma: no cover
                print("post failed", slug, e, file=sys.stderr)
            continue
        if p.startswith("/project/") and p != "/project/" and not p.startswith("/project/page/"):
            slug = p.strip("/").split("/")[1]
            soup = load_soup(file)
            for t in soup(["script", "style", "noscript"]):
                t.decompose()
            head = page_head(soup)
            og = head["og_image"]
            projects[slug] = {"slug": slug, "path": p, "title": head["title"], "image": og,
                              "categories": [c.replace("project_category-", "") for c in head["body_classes"] if c.startswith("project_category-")],
                              "date": None}
            m2 = soup.find("meta", attrs={"property": "article:published_time"})
            if m2 and m2.get("content"):
                projects[slug]["date"] = m2["content"][:10]
            continue
        if p.startswith("/project/page/") or p.startswith("/blog/page/"):
            continue
        # regular page
        try:
            pages[p] = extract_page(file, p)
        except Exception as e:  # pragma: no cover
            print("page failed", p, e, file=sys.stderr)
            raise

    # careers sub-site + help center (different hosts)
    careers_file = os.path.join(src, "careers.townsquareinteractive.com", "index.html")
    if os.path.exists(careers_file):
        pages["/careers-site/"] = extract_page(careers_file, "/careers-site/")

    # project archive pages: derive dates/categories from index listing
    idx = os.path.join(www, "project", "index.html")
    if os.path.exists(idx):
        soup = load_soup(idx)
        for art in soup.select("article"):
            a = art.select_one(".entry-title a")
            if not a:
                continue
            slug = urlparse(a["href"]).path.strip("/").split("/")[-1]
            img = art.find("img")
            d = art.select_one(".published")
            if slug in projects:
                if img and img_src(img):
                    projects[slug]["image"] = img_src(img)
                if d:
                    try:
                        projects[slug]["date"] = datetime.strptime(clean_text(d.get_text()), "%b %d, %Y").strftime("%Y-%m-%d")
                    except ValueError:
                        pass
    idx2 = os.path.join(www, "project", "page", "2", "index.html")
    if os.path.exists(idx2):
        soup = load_soup(idx2)
        for art in soup.select("article"):
            a = art.select_one(".entry-title a")
            if not a:
                continue
            slug = urlparse(a["href"]).path.strip("/").split("/")[-1]
            img = art.find("img")
            d = art.select_one(".published")
            if slug in projects:
                if img and img_src(img):
                    projects[slug]["image"] = img_src(img)
                if d:
                    try:
                        projects[slug]["date"] = datetime.strptime(clean_text(d.get_text()), "%b %d, %Y").strftime("%Y-%m-%d")
                    except ValueError:
                        pass

    # tags per post (from tag archives) and cleanup
    for store in (tags, categories, authors, project_cats):
        for e in store.values():
            e["posts"] = dedupe([s for s in e["posts"] if s in posts])
            e["projects"] = dedupe([s for s in e["projects"] if s in projects])
            e["name"] = rebrand(e["name"])
    for slug, post in posts.items():
        post["tags"] = [t["slug"] for t in tags.values() if slug in t["posts"]]
        # ensure category membership is mirrored both ways
        for c in post["categories"]:
            entry = categories.setdefault(c["slug"], {"slug": c["slug"], "name": c["name"], "posts": [], "projects": [], "path": c["path"]})
            if slug not in entry["posts"]:
                entry["posts"].append(slug)
        if post["author_slug"]:
            entry = authors.setdefault(post["author_slug"], {"slug": post["author_slug"], "name": post["author_name"], "posts": [], "projects": [], "path": f"/blog/author/{post['author_slug']}/"})
            if slug not in entry["posts"]:
                entry["posts"].append(slug)

    # author display names
    for a in authors.values():
        if a["name"] in (BRAND, BRAND_SHORT, ""):
            a["name"] = f"{BRAND_SHORT} Editorial Team"
    for post in posts.values():
        if post["author_slug"] in authors:
            post["author_name"] = authors[post["author_slug"]]["name"]

    # category hierarchy (google-reviews/google-business-profile)
    for c in categories.values():
        c.setdefault("parent", None)
        c["path"] = f"/blog/category/{c['slug']}/"
    for post in posts.values():
        for c in post["categories"]:
            c["path"] = f"/blog/category/{c['slug']}/"

    # write
    with open(os.path.join(out, "pages.json"), "w", encoding="utf-8") as fh:
        json.dump(list(pages.values()), fh, ensure_ascii=False, indent=1)
    for slug, post in posts.items():
        with open(os.path.join(out, "posts", f"{slug}.json"), "w", encoding="utf-8") as fh:
            json.dump(post, fh, ensure_ascii=False, indent=1)
    with open(os.path.join(out, "taxonomy.json"), "w", encoding="utf-8") as fh:
        json.dump({"categories": categories, "tags": tags, "authors": authors,
                   "project_categories": project_cats, "projects": projects}, fh, ensure_ascii=False, indent=1)
    with open(os.path.join(out, "known_paths.json"), "w", encoding="utf-8") as fh:
        json.dump(sorted(KNOWN_PATHS), fh, indent=0)
    with open(os.path.join(out, "unresolved_links.json"), "w", encoding="utf-8") as fh:
        json.dump(dict(sorted(UNRESOLVED.items(), key=lambda kv: -kv[1])), fh, indent=1)

    print(f"pages={len(pages)} posts={len(posts)} categories={len(categories)} tags={len(tags)} "
          f"authors={len(authors)} projects={len(projects)} project_categories={len(project_cats)} unresolved={len(UNRESOLVED)}")


if __name__ == "__main__":
    main()
