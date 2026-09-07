"""Inline SVG icons and animated product mockups for the Meridian Local site."""
from __future__ import annotations

import re

_ATTRS = 'xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"'

ICONS = {
    "layout": '<rect x="3" y="4" width="18" height="16" rx="3"/><path d="M3 9h18M9 20V9"/>',
    "search": '<circle cx="11" cy="11" r="6.5"/><path d="M20 20l-4.2-4.2"/>',
    "users": '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20a6.5 6.5 0 0113 0"/><circle cx="17" cy="9" r="2.6"/><path d="M15.5 14.5a5 5 0 016 4.5"/>',
    "calendar": '<rect x="3" y="5" width="18" height="16" rx="3"/><path d="M3 10h18M8 3v4M16 3v4M8 15h3"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="3"/><path d="M3 8l9 6 9-6"/>',
    "message": '<path d="M4 6a3 3 0 013-3h10a3 3 0 013 3v8a3 3 0 01-3 3H9l-5 4V6z"/><path d="M8 8h8M8 12h5"/>',
    "card": '<rect x="2.5" y="5" width="19" height="14" rx="3"/><path d="M2.5 10h19M7 15h4"/>',
    "invoice": '<path d="M6 3h9l4 4v14H6z"/><path d="M15 3v4h4M9 12h6M9 16h6"/>',
    "pin": '<path d="M12 21s-6.5-5.3-6.5-11a6.5 6.5 0 0113 0c0 5.7-6.5 11-6.5 11z"/><circle cx="12" cy="10" r="2.5"/>',
    "star": '<path d="M12 3.5l2.6 5.4 5.9.8-4.3 4.1 1.1 5.9L12 16.9l-5.3 2.8 1.1-5.9-4.3-4.1 5.9-.8z"/>',
    "share": '<circle cx="18" cy="5" r="2.5"/><circle cx="6" cy="12" r="2.5"/><circle cx="18" cy="19" r="2.5"/><path d="M8.2 10.8l7.6-4.6M8.2 13.2l7.6 4.6"/>',
    "megaphone": '<path d="M3 10v4a1 1 0 001 1h2l6 4V5L6 9H4a1 1 0 00-1 1z"/><path d="M16 9a4 4 0 010 6M18.5 6.5a8 8 0 010 11"/>',
    "headset": '<path d="M4 13a8 8 0 0116 0"/><rect x="3" y="12" width="4" height="6" rx="1.5"/><rect x="17" y="12" width="4" height="6" rx="1.5"/><path d="M19 18a3 3 0 01-3 3h-3"/>',
    "chart": '<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>',
    "trend": '<path d="M3 17l6-6 4 4 8-8"/><path d="M15 7h6v6"/>',
    "globe": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 010 18M12 3a14 14 0 000 18"/>',
    "bag": '<path d="M5 8h14l-1 12H6z"/><path d="M9 8V6a3 3 0 016 0v2"/>',
    "sparkles": '<path d="M12 3l1.8 4.7L18.5 9.5l-4.7 1.8L12 16l-1.8-4.7L5.5 9.5l4.7-1.8z"/><path d="M19 15l.8 2.2L22 18l-2.2.8L19 21l-.8-2.2L16 18l2.2-.8z"/>',
    "target": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.2"/>',
    "inbox": '<path d="M4 4h16v16H4z"/><path d="M4 14h4l2 3h4l2-3h4"/>',
    "phone": '<rect x="7" y="2.5" width="10" height="19" rx="2.5"/><path d="M11 18h2"/>',
    "shield": '<path d="M12 3l7 3v6c0 4.5-3 7.5-7 9-4-1.5-7-4.5-7-9V6z"/><path d="M9 12l2 2 4-4"/>',
    "check": '<path d="M5 12.5l4.5 4.5L19 7.5"/>',
    "check-circle": '<circle cx="12" cy="12" r="9"/><path d="M8.5 12.5l2.5 2.5 4.5-5"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "map": '<path d="M9 4l6 2 6-2v14l-6 2-6-2-6 2V6z"/><path d="M9 4v14M15 6v14"/>',
    "list": '<path d="M8 6h13M8 12h13M8 18h13"/><circle cx="4" cy="6" r="1"/><circle cx="4" cy="12" r="1"/><circle cx="4" cy="18" r="1"/>',
    "home": '<path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10"/><path d="M10 20v-6h4v6"/>',
    "wrench": '<path d="M14.5 6.5a4 4 0 105.2 5.2L21 10l-3-3-1.5 1.5z"/><path d="M13 11L4 20l1 1 9-9"/>',
    "leaf": '<path d="M5 19c8 0 14-6 14-14-8 0-14 6-14 14z"/><path d="M5 19l8-8"/>',
    "cup": '<path d="M4 8h13v5a6 6 0 01-12 0V8z"/><path d="M17 10h2a2 2 0 010 4h-2M6 20h9"/>',
    "truck": '<path d="M2 7h11v9H2zM13 11h5l3 3v2h-8z"/><circle cx="6" cy="18" r="2"/><circle cx="17" cy="18" r="2"/>',
    "roof": '<path d="M3 12l9-8 9 8"/><path d="M6 10v9h12v-9"/>',
    "drop": '<path d="M12 3s6 6.5 6 11a6 6 0 01-12 0c0-4.5 6-11 6-11z"/>',
    "scale": '<path d="M12 3v18M4 7h16"/><path d="M6 7l-3 7a3 3 0 006 0zM18 7l-3 7a3 3 0 006 0z"/>',
    "tree": '<path d="M12 3l5 7h-3l4 5h-4l0 6h-4v-6H6l4-5H7z"/>',
    "hammer": '<path d="M14 4l6 6-2 2-6-6z"/><path d="M12 6L4 14l2 2 8-8"/><path d="M4 14l6 6"/>',
    "snowflake": '<path d="M12 3v18M4.2 7.5l15.6 9M4.2 16.5l15.6-9"/>',
    "briefcase": '<rect x="3" y="7" width="18" height="13" rx="3"/><path d="M9 7V5a2 2 0 012-2h2a2 2 0 012 2v2M3 12h18"/>',
    "heart": '<path d="M12 20s-7-4.5-7-10a4 4 0 017-2.5A4 4 0 0119 10c0 5.5-7 10-7 10z"/>',
    "award": '<circle cx="12" cy="9" r="5.5"/><path d="M8.5 14L7 21l5-2.5L17 21l-1.5-7"/>',
    "smile": '<circle cx="12" cy="12" r="9"/><path d="M8.5 14.5a4.5 4.5 0 007 0M9 10h.01M15 10h.01"/>',
    "lock": '<rect x="5" y="10" width="14" height="11" rx="2.5"/><path d="M8 10V7a4 4 0 018 0v3"/>',
    "key": '<circle cx="8" cy="14" r="4"/><path d="M11 11l8-8M15 7l2 2M18 4l2 2"/>',
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "arrow-left": '<path d="M19 12H5M11 6l-6 6 6 6"/>',
    "chevron": '<path d="M6 9l6 6 6-6"/>',
    "plus": '<path d="M12 5v14M5 12h14"/>',
    "play": '<path d="M7 5v14l11-7z" fill="currentColor" stroke="none"/>',
    "quote": '<path d="M7 7h4v4H8v3H6v-5a2 2 0 011-2zM15 7h4v4h-3v3h-2v-5a2 2 0 011-2z"/>',
    "zap": '<path d="M13 3L4 14h6l-1 7 9-11h-6z"/>',
    "refresh": '<path d="M20 12a8 8 0 01-14 5.3M4 12a8 8 0 0114-5.3"/><path d="M4 4v5h5M20 20v-5h-5"/>',
    "eye": '<path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
    "edit": '<path d="M4 20h4l10-10-4-4L4 16z"/><path d="M13 7l4 4"/>',
    "cloud": '<path d="M7 18a4 4 0 01-.5-8 5.5 5.5 0 0110.6 1.4A3.5 3.5 0 0117 18z"/>',
    "grid": '<rect x="3" y="3" width="7" height="7" rx="2"/><rect x="14" y="3" width="7" height="7" rx="2"/><rect x="3" y="14" width="7" height="7" rx="2"/><rect x="14" y="14" width="7" height="7" rx="2"/>',
    "dollar": '<path d="M12 3v18M16 7.5A3.5 3.5 0 0012.5 5h-1a3.5 3.5 0 000 7h1a3.5 3.5 0 010 7h-1A3.5 3.5 0 018 15.5"/>',
    "user": '<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0116 0"/>',
    "camera": '<path d="M4 8h3l2-3h6l2 3h3v11H4z"/><circle cx="12" cy="13" r="3.5"/>',
    "scissors": '<circle cx="6" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><path d="M20 4L8.5 15.5M8.5 8.5L20 20"/>',
    "paw": '<circle cx="8" cy="7" r="2"/><circle cx="16" cy="7" r="2"/><circle cx="4.5" cy="12" r="1.8"/><circle cx="19.5" cy="12" r="1.8"/><path d="M12 11c3 0 6 3 6 6a3 3 0 01-4 2.8 4 4 0 00-4 0A3 3 0 016 17c0-3 3-6 6-6z"/>',
    "utensils": '<path d="M6 3v18M4 3v6a2 2 0 004 0V3M15 3c-2 0-3 3-3 6s1 4 3 4v8"/>',
    "car": '<path d="M4 15l2-6h12l2 6"/><rect x="3" y="15" width="18" height="4" rx="1.5"/><circle cx="7.5" cy="19" r="1.5"/><circle cx="16.5" cy="19" r="1.5"/>',
    "spa": '<path d="M12 21c-5 0-8-4-8-9 3 0 6 1 8 4 2-3 5-4 8-4 0 5-3 9-8 9z"/><path d="M12 16V3"/>',
    "compass": '<circle cx="12" cy="12" r="9"/><path d="M15.5 8.5l-2 5-5 2 2-5z"/>',
    "document": '<path d="M6 3h9l4 4v14H6z"/><path d="M15 3v4h4"/>',
    "help": '<circle cx="12" cy="12" r="9"/><path d="M9.5 9.5a2.5 2.5 0 015 0c0 1.5-2.5 2-2.5 3.5M12 17h.01"/>',
    "link": '<path d="M10 14a4 4 0 005.7 0l3-3a4 4 0 00-5.7-5.7l-1 1"/><path d="M14 10a4 4 0 00-5.7 0l-3 3a4 4 0 005.7 5.7l1-1"/>',
    "bell": '<path d="M6 16V11a6 6 0 0112 0v5l2 2H4z"/><path d="M10 21a2 2 0 004 0"/>',
    "menu": '<path d="M4 7h16M4 12h16M4 17h16"/>',
    "x": '<path d="M6 6l12 12M18 6L6 18"/>',
}

KEYWORDS = [
    (r"\b(website|web design|site)\b", "layout"),
    (r"\b(seo|search|rank|visibility|optimi)", "search"),
    (r"\b(crm|contact|customer management|client management)", "users"),
    (r"\b(calendar|schedul|booking|appointment)", "calendar"),
    (r"\b(email|sms|text|newsletter|follow[- ]up|messaging)", "mail"),
    (r"\b(inbox|conversation|communicat)", "inbox"),
    (r"\b(invoice|estimate|billing|payment|merchant|money|revenue|paid|pay)", "card"),
    (r"\b(listing|director|citation|local online)", "pin"),
    (r"\b(reputation|review|rating|trust)", "star"),
    (r"\b(social)", "share"),
    (r"\b(ads?|advertis|display|ppc|pay per click|campaign)", "megaphone"),
    (r"\b(support|help|phone|relationship manager|team)", "headset"),
    (r"\b(report|analytic|insight|track|monitor|performance|result)", "chart"),
    (r"\b(domain|hosting)", "globe"),
    (r"\b(ecommerce|online store|shop|ordering|sales)", "bag"),
    (r"\b(ai|aeo|artificial)", "sparkles"),
    (r"\b(lead|conversion|capture)", "target"),
    (r"\b(app|mobile|device|anywhere)", "phone"),
    (r"\b(grow|growth|scale|increase)", "trend"),
    (r"\b(secur|privacy|protect|ssl|backup)", "shield"),
    (r"\b(time|24/7|access|fast|speed|quick)", "clock"),
    (r"\b(hvac|air|heating|cooling)", "snowflake"),
    (r"\b(remodel|construct|contract|builder|home)", "hammer"),
    (r"\b(tree|landscap|lawn|garden)", "leaf"),
    (r"\b(food|restaurant|beverage|caf|bar|bakery)", "utensils"),
    (r"\b(tow|truck|auto|car|detail)", "truck"),
    (r"\b(roof)", "roof"),
    (r"\b(plumb|water)", "drop"),
    (r"\b(legal|law|attorney)", "scale"),
    (r"\b(pet|dog|canine|vet)", "paw"),
    (r"\b(spa|salon|beauty|wellness|health)", "spa"),
    (r"\b(career|job|opportunit|culture|pto|insurance|benefit)", "briefcase"),
    (r"\b(expert|guidance|consult|strategy|onboard)", "compass"),
    (r"\b(content|blog|page|faq|copy|writ)", "document"),
    (r"\b(local|market|community|area|city)", "map"),
    (r"\b(user|interface|simple|easy|friendly)", "smile"),
    (r"\b(integrat|connect|one place|platform|all[- ]in[- ]one)", "grid"),
    (r"\b(cost|afford|pric|budget|save)", "dollar"),
    (r"\b(commit|honest|transparen|reliab)", "heart"),
    (r"\b(award|best|top|win|recogni)", "award"),
    (r"\b(unlimited|change|update|edit|ongoing)", "refresh"),
]

TINTS = ["blue", "teal", "violet", "amber", "rose", "green"]


def icon(name: str, cls: str = "") -> str:
    body = ICONS.get(name) or ICONS["check-circle"]
    c = f' class="{cls}"' if cls else ""
    return f"<svg{c} {_ATTRS}>{body}</svg>"


def icon_for(text: str, default: str = "check-circle") -> str:
    t = (text or "").lower()
    for rx, name in KEYWORDS:
        if re.search(rx, t):
            return name
    return default


def tint(i: int) -> str:
    return TINTS[i % len(TINTS)]


# ---------------------------------------------------------------------------
# Product mockups (self-contained SVG, animated with CSS classes from main.css)
# ---------------------------------------------------------------------------
_FONT = 'font-family="-apple-system,BlinkMacSystemFont,Inter,Helvetica,Arial,sans-serif"'


def _panel(x, y, w, h, r=14, fill="#fff", stroke="#e6e9f0"):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}"/>'


def mock_dashboard(label: str = "Leads this month") -> str:
    bars = ""
    heights = [38, 56, 44, 72, 60, 88, 78]
    for i, h in enumerate(heights):
        x = 46 + i * 34
        color = "#2f6df6" if i != 5 else "#7a5af8"
        bars += f'<rect class="bar" x="{x}" y="{236 - h}" width="20" height="{h}" rx="6" fill="{color}" opacity="{0.55 + i * 0.06:.2f}"/>'
    return f'''<svg class="mock" viewBox="0 0 560 420" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{label} dashboard">
<defs><linearGradient id="mdg" x1="0" x2="1"><stop offset="0" stop-color="#2f6df6"/><stop offset="1" stop-color="#7a5af8"/></linearGradient>
<linearGradient id="mdf" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2f6df6" stop-opacity=".22"/><stop offset="1" stop-color="#2f6df6" stop-opacity="0"/></linearGradient></defs>
<rect x="8" y="8" width="544" height="404" rx="26" fill="#fff" stroke="#e6e9f0"/>
<rect x="8" y="8" width="544" height="52" rx="26" fill="#f7f8fb"/><rect x="8" y="34" width="544" height="26" fill="#f7f8fb"/>
<circle cx="34" cy="34" r="5" fill="#e6e9f0"/><circle cx="50" cy="34" r="5" fill="#e6e9f0"/><circle cx="66" cy="34" r="5" fill="#e6e9f0"/>
<rect x="200" y="24" width="160" height="20" rx="10" fill="#eef1f6"/>
{_panel(28, 80, 150, 78)}{_panel(196, 80, 150, 78)}{_panel(364, 80, 168, 78)}
<text x="44" y="106" font-size="11" fill="#6b7484" {_FONT}>New leads</text><text class="type" x="44" y="138" font-size="24" font-weight="700" fill="#0b1220" {_FONT}>128</text><text x="98" y="138" font-size="11" fill="#22a06b" {_FONT}>▲ 24%</text>
<text x="212" y="106" font-size="11" fill="#6b7484" {_FONT}>Booked jobs</text><text class="type" x="212" y="138" font-size="24" font-weight="700" fill="#0b1220" {_FONT}>46</text><text x="258" y="138" font-size="11" fill="#22a06b" {_FONT}>▲ 12%</text>
<text x="380" y="106" font-size="11" fill="#6b7484" {_FONT}>Collected</text><text class="type" x="380" y="138" font-size="24" font-weight="700" fill="#0b1220" {_FONT}>$38,420</text>
{_panel(28, 176, 318, 216)}
<text x="44" y="204" font-size="12" font-weight="600" fill="#0b1220" {_FONT}>{label}</text>
<g transform="translate(0,140)">{bars}</g>
<path class="line-anim" d="M56 330 C 100 300, 120 320, 160 290 S 230 250, 270 236 S 310 220, 330 200" fill="none" stroke="url(#mdg)" stroke-width="3" stroke-linecap="round"/>
{_panel(364, 176, 168, 216)}
<text x="380" y="204" font-size="12" font-weight="600" fill="#0b1220" {_FONT}>Today</text>
<g class="type"><circle cx="388" cy="232" r="9" fill="#e9efff"/><path d="M384 232l3 3 5-5" stroke="#2f6df6" stroke-width="2" fill="none" stroke-linecap="round"/><text x="404" y="236" font-size="11" fill="#1c2433" {_FONT}>Estimate sent · Ramirez</text></g>
<g class="type"><circle cx="388" cy="262" r="9" fill="#e3f6f2"/><path d="M384 262l3 3 5-5" stroke="#0fa38f" stroke-width="2" fill="none" stroke-linecap="round"/><text x="404" y="266" font-size="11" fill="#1c2433" {_FONT}>Review request · 5.0 ★</text></g>
<g class="type"><circle cx="388" cy="292" r="9" fill="#efeaff"/><circle cx="388" cy="292" r="3" fill="#7a5af8"/><text x="404" y="296" font-size="11" fill="#1c2433" {_FONT}>Booking · 2:30 PM</text></g>
<g class="type"><circle cx="388" cy="322" r="9" fill="#fff4e3"/><circle cx="388" cy="322" r="3" fill="#f0a33a"/><text x="404" y="326" font-size="11" fill="#1c2433" {_FONT}>New message · Google</text></g>
<rect x="380" y="350" width="136" height="26" rx="13" fill="#0b1220"/><text x="448" y="367" font-size="11" font-weight="600" fill="#fff" text-anchor="middle" {_FONT}>Open inbox</text>
</svg>'''


def mock_search(brand: str = "Your business") -> str:
    nodes = [("Google", 0), ("Maps", 60), ("AI search", 120), ("Directories", 180), ("Social", 240), ("Reviews", 300)]
    g = ""
    import math
    for i, (name, ang) in enumerate(nodes):
        a = math.radians(ang - 90)
        x, y = 280 + 170 * math.cos(a), 210 + 150 * math.sin(a)
        col = ["#2f6df6", "#0fa38f", "#7a5af8", "#f0a33a", "#ee6a8e", "#22a06b"][i]
        g += f'<line x1="280" y1="210" x2="{x:.0f}" y2="{y:.0f}" stroke="{col}" stroke-width="1.5" opacity=".35" stroke-dasharray="4 5"/>'
        g += f'<g class="type"><rect x="{x-52:.0f}" y="{y-18:.0f}" width="104" height="36" rx="18" fill="#fff" stroke="#e6e9f0"/><circle cx="{x-32:.0f}" cy="{y:.0f}" r="6" fill="{col}"/><text x="{x-20:.0f}" y="{y+4:.0f}" font-size="12" font-weight="600" fill="#1c2433" {_FONT}>{name}</text></g>'
    return f'''<svg class="mock" viewBox="0 0 560 420" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Search everywhere diagram">
<defs><linearGradient id="msg" x1="0" x2="1" y1="0" y2="1"><stop offset="0" stop-color="#2f6df6"/><stop offset=".6" stop-color="#7a5af8"/><stop offset="1" stop-color="#0fa38f"/></linearGradient></defs>
<circle class="ring" cx="280" cy="210" r="70" fill="none" stroke="#2f6df6" stroke-width="2"/>
<circle class="ring" cx="280" cy="210" r="70" fill="none" stroke="#7a5af8" stroke-width="2" style="animation-delay:-1.6s"/>
<g class="spin" style="transform-origin:280px 210px"><circle cx="280" cy="210" r="110" fill="none" stroke="#e6e9f0" stroke-dasharray="3 8"/></g>
{g}
<circle cx="280" cy="210" r="46" fill="url(#msg)"/>
<circle cx="280" cy="210" r="46" fill="none" stroke="#fff" stroke-width="3"/>
<text x="280" y="206" font-size="11" fill="#fff" text-anchor="middle" opacity=".85" {_FONT}>{brand[:16]}</text>
<text x="280" y="222" font-size="12" font-weight="700" fill="#fff" text-anchor="middle" {_FONT}>Found</text>
<rect x="150" y="360" width="260" height="40" rx="20" fill="#fff" stroke="#e6e9f0"/>
<circle cx="172" cy="380" r="7" fill="none" stroke="#2f6df6" stroke-width="2"/><path d="M177 385l4 4" stroke="#2f6df6" stroke-width="2" stroke-linecap="round"/>
<text class="type" x="192" y="384" font-size="12" fill="#1c2433" {_FONT}>best plumber near me</text>
<rect class="pulse" x="352" y="368" width="44" height="24" rx="12" fill="#e9efff"/><text x="374" y="384" font-size="11" font-weight="700" fill="#1d4fd7" text-anchor="middle" {_FONT}>#1</text>
</svg>'''


def mock_inbox() -> str:
    rows = [("Google", "New lead — wants a quote for Friday", "#2f6df6", "2m"),
            ("SMS", "Thanks! Can we move to 3 PM?", "#0fa38f", "18m"),
            ("Email", "Invoice #1042 paid · $1,250", "#7a5af8", "1h"),
            ("Facebook", "Do you service Kalamazoo?", "#f0a33a", "3h")]
    r = ""
    for i, (src, msg, col, when) in enumerate(rows):
        y = 118 + i * 62
        r += f'<g class="type">{_panel(40, y, 480, 50, 14, "#fff" if i else "#f2f6ff", "#e6e9f0")}<circle cx="70" cy="{y+25}" r="13" fill="{col}" opacity=".18"/><circle cx="70" cy="{y+25}" r="5" fill="{col}"/><text x="96" y="{y+21}" font-size="11" font-weight="700" fill="#0b1220" {_FONT}>{src}</text><text x="96" y="{y+38}" font-size="11" fill="#6b7484" {_FONT}>{msg}</text><text x="500" y="{y+22}" font-size="10" fill="#9aa3b2" text-anchor="end" {_FONT}>{when}</text></g>'
    return f'''<svg class="mock" viewBox="0 0 560 420" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Unified inbox">
<rect x="8" y="8" width="544" height="404" rx="26" fill="#fff" stroke="#e6e9f0"/>
<rect x="8" y="8" width="544" height="52" rx="26" fill="#f7f8fb"/><rect x="8" y="34" width="544" height="26" fill="#f7f8fb"/>
<text x="40" y="40" font-size="14" font-weight="700" fill="#0b1220" {_FONT}>Inbox</text>
<rect x="100" y="24" width="52" height="22" rx="11" fill="#e9efff"/><text x="126" y="39" font-size="11" font-weight="600" fill="#1d4fd7" text-anchor="middle" {_FONT}>All 12</text>
<rect x="160" y="24" width="60" height="22" rx="11" fill="#fff" stroke="#e6e9f0"/><text x="190" y="39" font-size="11" fill="#6b7484" text-anchor="middle" {_FONT}>Unread</text>
<rect x="40" y="76" width="480" height="30" rx="15" fill="#f7f8fb"/><text x="60" y="95" font-size="11" fill="#9aa3b2" {_FONT}>Search conversations</text>
{r}
<rect x="380" y="370" width="140" height="30" rx="15" fill="#0b1220"/><text x="450" y="389" font-size="11" font-weight="600" fill="#fff" text-anchor="middle" {_FONT}>Reply from one place</text>
</svg>'''


def mock_calendar() -> str:
    cells = ""
    for i in range(28):
        x = 48 + (i % 7) * 66
        y = 128 + (i // 7) * 58
        booked = i in (3, 5, 9, 12, 16, 17, 23, 24)
        fill = "#e9efff" if booked else "#fff"
        cells += f'<rect x="{x}" y="{y}" width="58" height="50" rx="10" fill="{fill}" stroke="#e6e9f0"/><text x="{x+10}" y="{y+18}" font-size="10" fill="#6b7484" {_FONT}>{i+1}</text>'
        if booked:
            cells += f'<rect class="type" x="{x+8}" y="{y+26}" width="42" height="14" rx="7" fill="#2f6df6" opacity=".85"/>'
    return f'''<svg class="mock" viewBox="0 0 560 420" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Online scheduling calendar">
<rect x="8" y="8" width="544" height="404" rx="26" fill="#fff" stroke="#e6e9f0"/>
<text x="48" y="60" font-size="16" font-weight="700" fill="#0b1220" {_FONT}>October</text>
<rect x="420" y="40" width="92" height="28" rx="14" fill="#0b1220"/><text x="466" y="58" font-size="11" font-weight="600" fill="#fff" text-anchor="middle" {_FONT}>+ Booking</text>
{"".join(f'<text x="{48+i*66+29}" y="112" font-size="10" fill="#9aa3b2" text-anchor="middle" {_FONT}>{d}</text>' for i, d in enumerate(["M","T","W","T","F","S","S"]))}
{cells}
<g class="type"><rect x="330" y="340" width="190" height="56" rx="14" fill="#fff" stroke="#e6e9f0" filter="drop-shadow(0 8px 16px rgba(16,24,40,.12))"/><circle cx="352" cy="368" r="10" fill="#e3f6f2"/><path d="M347 368l3 3 6-6" stroke="#0fa38f" stroke-width="2" fill="none" stroke-linecap="round"/><text x="370" y="364" font-size="11" font-weight="700" fill="#0b1220" {_FONT}>Booked · Sat 10:30 AM</text><text x="370" y="380" font-size="10" fill="#6b7484" {_FONT}>Reminder sent automatically</text></g>
</svg>'''


def mock_invoice() -> str:
    return f'''<svg class="mock" viewBox="0 0 560 420" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Estimate and invoice">
<rect x="70" y="24" width="420" height="380" rx="24" fill="#fff" stroke="#e6e9f0"/>
<text x="100" y="70" font-size="18" font-weight="700" fill="#0b1220" {_FONT}>Invoice #1042</text>
<rect x="380" y="52" width="80" height="24" rx="12" fill="#e3f6f2"/><text x="420" y="68" font-size="11" font-weight="700" fill="#0b7d6d" text-anchor="middle" {_FONT}>PAID</text>
<text x="100" y="96" font-size="11" fill="#6b7484" {_FONT}>Billed to Ramirez Residence · Due Oct 14</text>
<line x1="100" y1="120" x2="460" y2="120" stroke="#e6e9f0"/>
<g class="type"><text x="100" y="150" font-size="12" fill="#1c2433" {_FONT}>Full system tune-up</text><text x="460" y="150" font-size="12" fill="#1c2433" text-anchor="end" {_FONT}>$420.00</text></g>
<g class="type"><text x="100" y="180" font-size="12" fill="#1c2433" {_FONT}>Replacement filter (x2)</text><text x="460" y="180" font-size="12" fill="#1c2433" text-anchor="end" {_FONT}>$64.00</text></g>
<g class="type"><text x="100" y="210" font-size="12" fill="#1c2433" {_FONT}>Labor · 3 hrs</text><text x="460" y="210" font-size="12" fill="#1c2433" text-anchor="end" {_FONT}>$285.00</text></g>
<line x1="100" y1="236" x2="460" y2="236" stroke="#e6e9f0"/>
<text x="100" y="268" font-size="13" font-weight="700" fill="#0b1220" {_FONT}>Total</text><text class="type" x="460" y="268" font-size="20" font-weight="700" fill="#0b1220" text-anchor="end" {_FONT}>$769.00</text>
<rect x="100" y="300" width="360" height="42" rx="21" fill="#0b1220"/><text x="280" y="326" font-size="13" font-weight="600" fill="#fff" text-anchor="middle" {_FONT}>Pay with card · Apple Pay · ACH</text>
<g class="type"><rect x="100" y="356" width="360" height="28" rx="14" fill="#f7f8fb"/><circle cx="118" cy="370" r="6" fill="#22a06b"/><text x="132" y="374" font-size="11" fill="#1c2433" {_FONT}>Deposited to your account in 1–2 business days</text></g>
</svg>'''


def mock_reviews() -> str:
    cards = ""
    people = [("Dawn J.", "Consistent calls and clients a year in.", "#2f6df6"), ("Tex M.", "Fabulous job designing the website.", "#0fa38f"), ("Peter M.", "Everyone I've spoken with is knowledgeable.", "#7a5af8")]
    for i, (n, q, c) in enumerate(people):
        y = 90 + i * 104
        cards += f'<g class="type">{_panel(60, y, 440, 86, 18)}<circle cx="96" cy="{y+30}" r="16" fill="{c}" opacity=".18"/><text x="96" y="{y+35}" font-size="12" font-weight="700" fill="{c}" text-anchor="middle" {_FONT}>{n[0]}</text><text x="124" y="{y+26}" font-size="12" font-weight="700" fill="#0b1220" {_FONT}>{n}</text><text x="124" y="{y+44}" font-size="12" fill="#f0a33a" {_FONT}>★★★★★</text><text x="124" y="{y+64}" font-size="11" fill="#3b4658" {_FONT}>{q}</text></g>'
    return f'''<svg class="mock" viewBox="0 0 560 420" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Customer reviews">
<rect x="8" y="8" width="544" height="404" rx="26" fill="#fff" stroke="#e6e9f0"/>
<text x="60" y="56" font-size="15" font-weight="700" fill="#0b1220" {_FONT}>Reputation</text>
<rect class="pulse" x="400" y="36" width="100" height="28" rx="14" fill="#fff4e3"/><text x="450" y="54" font-size="12" font-weight="700" fill="#a35f0a" text-anchor="middle" {_FONT}>4.9 ★ · 312</text>
{cards}
</svg>'''


def mock_map() -> str:
    import random
    rnd = random.Random(7)
    dots = ""
    for i in range(70):
        x, y = rnd.randint(60, 500), rnd.randint(70, 340)
        r = rnd.choice([3, 3, 4, 5])
        col = rnd.choice(["#2f6df6", "#7a5af8", "#0fa38f", "#f0a33a"])
        dots += f'<circle class="pulse" cx="{x}" cy="{y}" r="{r}" fill="{col}" opacity=".7" style="animation-delay:-{rnd.random()*3:.1f}s"/>'
    return f'''<svg class="mock" viewBox="0 0 560 420" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Markets across the country">
<rect x="8" y="8" width="544" height="404" rx="26" fill="#fff" stroke="#e6e9f0"/>
<path d="M60 130 C 120 80, 260 60, 330 90 S 480 70, 500 150 S 470 300, 380 330 S 220 360, 140 320 S 40 220, 60 130z" fill="#f2f6ff" stroke="#dbe4ff"/>
{dots}
<g class="type"><rect x="300" y="330" width="220" height="56" rx="16" fill="#fff" stroke="#e6e9f0"/><text x="318" y="352" font-size="12" font-weight="700" fill="#0b1220" {_FONT}>31.2M+ local searches</text><text x="318" y="372" font-size="11" fill="#6b7484" {_FONT}>1.9M+ conversion points · 20K+ businesses</text></g>
</svg>'''


def mock_phone(screen: str = "inbox") -> str:
    inner = ""
    if screen == "inbox":
        for i, (t, c) in enumerate([("New lead · Google", "#2f6df6"), ("Booking confirmed", "#0fa38f"), ("Invoice paid $769", "#7a5af8"), ("New 5★ review", "#f0a33a")]):
            y = 150 + i * 66
            inner += f'<g class="type"><rect x="46" y="{y}" width="188" height="52" rx="14" fill="#f7f8fb"/><circle cx="70" cy="{y+26}" r="10" fill="{c}" opacity=".2"/><circle cx="70" cy="{y+26}" r="4" fill="{c}"/><text x="90" y="{y+24}" font-size="10.5" font-weight="700" fill="#0b1220" {_FONT}>{t}</text><text x="90" y="{y+40}" font-size="9.5" fill="#6b7484" {_FONT}>Tap to respond</text></g>'
    return f'''<svg class="mock" viewBox="0 0 280 560" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Mobile app">
<rect x="10" y="10" width="260" height="540" rx="44" fill="#0b1220"/>
<rect x="20" y="20" width="240" height="520" rx="36" fill="#fff"/>
<rect x="100" y="30" width="80" height="22" rx="11" fill="#0b1220"/>
<text x="46" y="98" font-size="17" font-weight="700" fill="#0b1220" {_FONT}>Good morning</text>
<text x="46" y="118" font-size="11" fill="#6b7484" {_FONT}>4 things need you today</text>
{inner}
<rect x="46" y="430" width="188" height="40" rx="20" fill="#0b1220"/><text x="140" y="455" font-size="11" font-weight="600" fill="#fff" text-anchor="middle" {_FONT}>Open dashboard</text>
<rect x="40" y="500" width="200" height="1" fill="#e6e9f0"/>
{"".join(f'<circle cx="{70+i*50}" cy="520" r="6" fill="{"#2f6df6" if i==0 else "#e6e9f0"}"/>' for i in range(4))}
</svg>'''


def mock_crm() -> str:
    rows = [("Ramirez Residence", "Estimate sent · $769", "#2f6df6", "Lead"), ("Blue Ridge Bakery", "Booked · Fri 10:30 AM", "#0fa38f", "Customer"),
            ("Patterson HVAC", "Invoice paid", "#7a5af8", "Customer"), ("Nguyen Family", "Review requested", "#f0a33a", "Lead"), ("Carter Landscaping", "Follow-up scheduled", "#ee6a8e", "Prospect")]
    r = ""
    for i, (name, note, col, tag) in enumerate(rows):
        y = 118 + i * 54
        r += f'<g class="type"><rect x="40" y="{y}" width="480" height="44" rx="12" fill="#fff" stroke="#e6e9f0"/><circle cx="66" cy="{y+22}" r="13" fill="{col}" opacity=".18"/><text x="66" y="{y+26}" font-size="10" font-weight="700" fill="{col}" text-anchor="middle" {_FONT}>{name[0]}</text><text x="90" y="{y+19}" font-size="11" font-weight="700" fill="#0b1220" {_FONT}>{name}</text><text x="90" y="{y+34}" font-size="10" fill="#6b7484" {_FONT}>{note}</text><rect x="440" y="{y+12}" width="64" height="20" rx="10" fill="#f2f4f9"/><text x="472" y="{y+26}" font-size="9.5" font-weight="600" fill="#3b4658" text-anchor="middle" {_FONT}>{tag}</text></g>'
    return f'''<svg class="mock" viewBox="0 0 560 420" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Customer relationship manager">
<rect x="8" y="8" width="544" height="404" rx="26" fill="#fff" stroke="#e6e9f0"/>
<rect x="8" y="8" width="544" height="52" rx="26" fill="#f7f8fb"/><rect x="8" y="34" width="544" height="26" fill="#f7f8fb"/>
<text x="40" y="40" font-size="14" font-weight="700" fill="#0b1220" {_FONT}>Contacts</text>
<rect x="400" y="24" width="120" height="24" rx="12" fill="#0b1220"/><text x="460" y="40" font-size="11" font-weight="600" fill="#fff" text-anchor="middle" {_FONT}>+ Add contact</text>
<rect x="40" y="76" width="300" height="30" rx="15" fill="#f7f8fb"/><text x="60" y="95" font-size="11" fill="#9aa3b2" {_FONT}>Search contacts, notes, invoices…</text>
<rect x="352" y="76" width="80" height="30" rx="15" fill="#e9efff"/><text x="392" y="95" font-size="11" font-weight="600" fill="#1d4fd7" text-anchor="middle" {_FONT}>Leads 24</text>
<rect x="440" y="76" width="80" height="30" rx="15" fill="#fff" stroke="#e6e9f0"/><text x="480" y="95" font-size="11" fill="#6b7484" text-anchor="middle" {_FONT}>All 1,204</text>
{r}
</svg>'''


def mock_ads() -> str:
    return f'''<svg class="mock" viewBox="0 0 560 420" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Targeted advertising">
<rect x="150" y="16" width="260" height="388" rx="28" fill="#0b1220"/><rect x="158" y="24" width="244" height="372" rx="22" fill="#fff"/>
<rect x="240" y="32" width="80" height="16" rx="8" fill="#0b1220"/>
<g class="type"><rect x="174" y="70" width="212" height="180" rx="16" fill="#f7f8fb" stroke="#e6e9f0"/>
<circle cx="196" cy="92" r="10" fill="#2f6df6" opacity=".2"/><circle cx="196" cy="92" r="4" fill="#2f6df6"/><text x="212" y="90" font-size="9.5" font-weight="700" fill="#0b1220" {_FONT}>Your Business</text><text x="212" y="101" font-size="8" fill="#9aa3b2" {_FONT}>Sponsored · Charlotte, NC</text>
<rect x="186" y="112" width="188" height="90" rx="12" fill="url(#adg)"/>
<text x="280" y="152" font-size="12" font-weight="700" fill="#fff" text-anchor="middle" {_FONT}>Fall tune-up special</text><text x="280" y="168" font-size="9" fill="#fff" text-anchor="middle" opacity=".9" {_FONT}>Book this week and save 15%</text>
<rect x="186" y="212" width="90" height="24" rx="12" fill="#0b1220"/><text x="231" y="228" font-size="9" font-weight="600" fill="#fff" text-anchor="middle" {_FONT}>Book now</text></g>
<defs><linearGradient id="adg" x1="0" x2="1" y1="0" y2="1"><stop offset="0" stop-color="#2f6df6"/><stop offset="1" stop-color="#7a5af8"/></linearGradient></defs>
<g class="type"><rect x="174" y="264" width="212" height="60" rx="14" fill="#fff" stroke="#e6e9f0"/><text x="188" y="286" font-size="9.5" font-weight="700" fill="#0b1220" {_FONT}>Campaign performance</text><text x="188" y="304" font-size="9" fill="#22a06b" {_FONT}>▲ 3.2% CTR · 148 clicks · 19 leads</text></g>
<g class="type"><rect x="20" y="120" width="120" height="70" rx="14" fill="#fff" stroke="#e6e9f0"/><text x="34" y="144" font-size="9.5" fill="#6b7484" {_FONT}>Audience</text><text x="34" y="168" font-size="14" font-weight="700" fill="#0b1220" {_FONT}>Homeowners</text><text x="34" y="182" font-size="9" fill="#9aa3b2" {_FONT}>within 25 miles</text></g>
<g class="type"><rect x="420" y="200" width="120" height="70" rx="14" fill="#fff" stroke="#e6e9f0"/><text x="434" y="224" font-size="9.5" fill="#6b7484" {_FONT}>Reach this week</text><text class="pulse" x="434" y="250" font-size="16" font-weight="700" fill="#0b1220" {_FONT}>48,200</text></g>
</svg>'''


def mock_for(key: str, label: str = "") -> str:
    key = (key or "").lower()
    if re.search(r"crm|contact|customer", key):
        return mock_crm()
    if re.search(r"ads?\b|advertis|display|social|campaign|targeted", key):
        return mock_ads()
    if re.search(r"seo|search|rank|visib|grow|listing|director|\bai\b|domain|email", key):
        return mock_search(label or "Your business")
    if re.search(r"inbox|sms|email|message|communicat|support|relationship|lead", key):
        return mock_inbox()
    if re.search(r"calendar|schedul|booking|appointment", key):
        return mock_calendar()
    if re.search(r"invoice|estimate|billing|merchant|payment|ecommerce|order", key):
        return mock_invoice()
    if re.search(r"reputation|review|social", key):
        return mock_reviews()
    if re.search(r"location|market|map", key):
        return mock_map()
    return mock_dashboard(label or "Leads this month")
