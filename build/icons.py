"""Inline SVG icons and animated product mockups for the Charlie Company Media site."""
from __future__ import annotations

import re

_ATTRS = 'xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"'

# SF Symbols-style glyphs: 24pt grid, 1.5pt rounded strokes, generous optical margins,
# continuous curves and no decorative detail.
ICONS = {
    "layout": '<rect x="3" y="4.5" width="18" height="15" rx="3.5"/><path d="M3 9.5h18M9.5 9.5v10"/>',
    "search": '<circle cx="10.75" cy="10.75" r="6.25"/><path d="M15.5 15.5L20 20"/>',
    "users": '<circle cx="9.5" cy="8.5" r="3.25"/><path d="M3.5 19.5a6 6 0 0 1 12 0"/><path d="M15.5 5.6a3.25 3.25 0 0 1 0 5.8"/><path d="M17.5 14.2a6 6 0 0 1 3 5.3"/>',
    "calendar": '<rect x="3.5" y="5" width="17" height="15.5" rx="3.5"/><path d="M3.5 10h17M8 3.5V6.5M16 3.5V6.5"/><path d="M8 14h.01M12 14h.01M16 14h.01" stroke-width="2.2"/>',
    "mail": '<rect x="3" y="5.5" width="18" height="13" rx="3.5"/><path d="M3.8 8.3 12 13.5l8.2-5.2"/>',
    "message": '<path d="M12 4c4.7 0 8.5 3.1 8.5 7s-3.8 7-8.5 7c-.9 0-1.8-.1-2.6-.3L5.5 19.5l.9-3.2C4.8 15 3.5 13.1 3.5 11c0-3.9 3.8-7 8.5-7Z"/>',
    "card": '<rect x="3" y="5.5" width="18" height="13" rx="3.5"/><path d="M3 10h18M7 14.5h3.5"/>',
    "invoice": '<path d="M6.5 3.5h7l4 4v13h-11Z"/><path d="M13.5 3.5v4h4M9.5 12h5M9.5 15.5h5"/>',
    "pin": '<path d="M12 21s-6.5-5.8-6.5-11a6.5 6.5 0 0 1 13 0c0 5.2-6.5 11-6.5 11Z"/><circle cx="12" cy="10" r="2.4"/>',
    "star": '<path d="M12 3.8l2.5 5.1 5.6.8-4.05 3.95.95 5.6L12 16.6l-5 2.65.95-5.6L3.9 9.7l5.6-.8Z"/>',
    "share": '<circle cx="17.5" cy="5.5" r="2.25"/><circle cx="6.5" cy="12" r="2.25"/><circle cx="17.5" cy="18.5" r="2.25"/><path d="M8.5 10.9l7-4.3M8.5 13.1l7 4.3"/>',
    "megaphone": '<path d="M4 10.5v3a1.5 1.5 0 0 0 1.5 1.5H7l6.5 3.5V5.5L7 9H5.5A1.5 1.5 0 0 0 4 10.5Z"/><path d="M17 9.5a3.5 3.5 0 0 1 0 5M19.5 7a7 7 0 0 1 0 10"/>',
    "headset": '<path d="M4.5 14v-2a7.5 7.5 0 0 1 15 0v2"/><path d="M4.5 13.5h1.5a1.5 1.5 0 0 1 1.5 1.5v2.5a1.5 1.5 0 0 1-1.5 1.5H4.5ZM19.5 13.5H18a1.5 1.5 0 0 0-1.5 1.5v2.5A1.5 1.5 0 0 0 18 19h1.5Z"/><path d="M19.5 19a3 3 0 0 1-3 2.5H13"/>',
    "chart": '<path d="M4 20V11M10 20V4.5M16 20v-6"/><path d="M3 20h18"/>',
    "trend": '<path d="M3.5 16.5 9 11l4 4 7-7"/><path d="M15.5 8H20v4.5"/>',
    "globe": '<circle cx="12" cy="12" r="8.5"/><path d="M3.5 12h17M12 3.5c2.6 2.4 3.9 5.2 3.9 8.5S14.6 18.1 12 20.5M12 3.5c-2.6 2.4-3.9 5.2-3.9 8.5s1.3 6.1 3.9 8.5"/>',
    "bag": '<path d="M5.5 8.5h13l-.9 10.2a1.8 1.8 0 0 1-1.8 1.6H8.2a1.8 1.8 0 0 1-1.8-1.6Z"/><path d="M9 8.5V7a3 3 0 0 1 6 0v1.5"/>',
    "sparkles": '<path d="M11 4.5l1.6 4.2 4.2 1.6-4.2 1.6L11 16.1l-1.6-4.2-4.2-1.6 4.2-1.6Z"/><path d="M18.5 14.5l.8 2 2 .8-2 .8-.8 2-.8-2-2-.8 2-.8Z"/>',
    "target": '<circle cx="12" cy="12" r="8.5"/><circle cx="12" cy="12" r="4.75"/><circle cx="12" cy="12" r="1" fill="currentColor"/>',
    "inbox": '<path d="M4 13.5V7.5A2.5 2.5 0 0 1 6.5 5h11A2.5 2.5 0 0 1 20 7.5v6"/><path d="M4 13.5h4l1.5 2.5h5l1.5-2.5h4V17a2.5 2.5 0 0 1-2.5 2.5h-11A2.5 2.5 0 0 1 4 17Z"/>',
    "phone": '<rect x="6.5" y="3" width="11" height="18" rx="3"/><path d="M10.5 17.5h3"/>',
    "shield": '<path d="M12 3.5 5.5 6v5.5c0 4.2 2.7 7.4 6.5 9 3.8-1.6 6.5-4.8 6.5-9V6Z"/><path d="M9.25 12.25 11 14l3.75-3.75"/>',
    "check": '<path d="M5.5 12.5 9.75 16.75 18.5 8"/>',
    "check-circle": '<circle cx="12" cy="12" r="8.5"/><path d="M8.5 12.25 10.9 14.65 15.5 9.75"/>',
    "clock": '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>',
    "map": '<path d="m9 4.5 6 2 5.5-2v13l-5.5 2-6-2-5.5 2v-13Z"/><path d="M9 4.5v13M15 6.5v13"/>',
    "list": '<path d="M9 6.5h11.5M9 12h11.5M9 17.5h11.5"/><path d="M4.5 6.5h.01M4.5 12h.01M4.5 17.5h.01" stroke-width="2.2"/>',
    "home": '<path d="M4 11 12 4.5 20 11"/><path d="M6 9.5V19a1 1 0 0 0 1 1h3.5v-5.5h3V20H17a1 1 0 0 0 1-1V9.5"/>',
    "wrench": '<path d="M14.7 4.2a4.6 4.6 0 0 0-1.1 5L5.2 17.6a1.6 1.6 0 1 0 2.2 2.2l8.4-8.4a4.6 4.6 0 0 0 5.7-6.2l-2.7 2.7-2.4-.6-.6-2.4Z"/>',
    "leaf": '<path d="M5 19c0-7.7 5.5-13 14-13-.3 8.2-5.3 13.4-13 13.4"/><path d="M5 19c2.5-4 5.5-7 9.5-9.5"/>',
    "cup": '<path d="M5 8.5h11.5v5.5a5.75 5.75 0 0 1-11.5 0Z"/><path d="M16.5 10h1.5a2 2 0 0 1 0 4h-1.5M7 20.5h8"/>',
    "truck": '<path d="M3.5 7h10.5v9H3.5Z"/><path d="M14 10.5h3.5l3 3V16H14Z"/><circle cx="7" cy="17.5" r="1.75"/><circle cx="17" cy="17.5" r="1.75"/>',
    "roof": '<path d="M3.5 12 12 4.5l8.5 7.5"/><path d="M6.5 10.5V19h11v-8.5"/>',
    "drop": '<path d="M12 3.8s5.5 6.2 5.5 10.2a5.5 5.5 0 0 1-11 0C6.5 10 12 3.8 12 3.8Z"/>',
    "scale": '<path d="M12 4v16M5 7h14M8 20h8"/><path d="m5 7-2.5 6a2.5 2.5 0 0 0 5 0ZM19 7l-2.5 6a2.5 2.5 0 0 0 5 0Z"/>',
    "tree": '<path d="M12 3.5 7 10h2.5L6.5 15H11v5h2v-5h4.5L14.5 10H17Z"/>',
    "hammer": '<path d="m14 5.5 4.5 4.5-1.5 1.5L12.5 7Z"/><path d="M12.5 7 4.8 14.7a1.5 1.5 0 0 0 2.1 2.1L14.6 9.1"/><path d="m15 6.5 1.5-1.5 2 2"/>',
    "snowflake": '<path d="M12 3.5v17M4.6 7.75l14.8 8.5M4.6 16.25l14.8-8.5"/><path d="M12 3.5 9.75 5.75M12 3.5l2.25 2.25M12 20.5 9.75 18.25M12 20.5l2.25-2.25"/>',
    "briefcase": '<rect x="3.5" y="7" width="17" height="12.5" rx="3"/><path d="M9 7V5.5A1.5 1.5 0 0 1 10.5 4h3A1.5 1.5 0 0 1 15 5.5V7M3.5 12h17"/>',
    "heart": '<path d="M12 19.5s-7-4.3-7-9.4a3.9 3.9 0 0 1 7-2.3 3.9 3.9 0 0 1 7 2.3c0 5.1-7 9.4-7 9.4Z"/>',
    "award": '<circle cx="12" cy="9" r="5.25"/><path d="m8.8 13.3-1.3 7 4.5-2.3 4.5 2.3-1.3-7"/>',
    "smile": '<circle cx="12" cy="12" r="8.5"/><path d="M8.5 14.25a4.5 4.5 0 0 0 7 0"/><path d="M9 9.5h.01M15 9.5h.01" stroke-width="2.2"/>',
    "lock": '<rect x="5" y="10.5" width="14" height="10" rx="3"/><path d="M8 10.5V8a4 4 0 0 1 8 0v2.5"/><path d="M12 14.5v2"/>',
    "key": '<circle cx="8.5" cy="14.5" r="4"/><path d="M11.4 11.6 19.5 3.5M16.5 6.5l2 2M14 9l2 2"/>',
    "arrow": '<path d="M5 12h14M13.5 6.5 19 12l-5.5 5.5"/>',
    "arrow-left": '<path d="M19 12H5M10.5 6.5 5 12l5.5 5.5"/>',
    "chevron": '<path d="m6.5 9.5 5.5 5.5 5.5-5.5"/>',
    "chevron-right": '<path d="m9.5 6.5 5.5 5.5-5.5 5.5"/>',
    "plus": '<path d="M12 5.5v13M5.5 12h13"/>',
    "play": '<path d="M8 5.5v13l10-6.5Z" fill="currentColor" stroke="none"/>',
    "quote": '<path d="M9.5 8.5H6.5A1.5 1.5 0 0 0 5 10v2.5a1.5 1.5 0 0 0 1.5 1.5h2v1.5a2 2 0 0 1-2 2M19 8.5h-3a1.5 1.5 0 0 0-1.5 1.5v2.5a1.5 1.5 0 0 0 1.5 1.5h2v1.5a2 2 0 0 1-2 2"/>',
    "zap": '<path d="M13 3.5 5.5 13.5H11l-1 7 7.5-10H12Z"/>',
    "refresh": '<path d="M19.5 12a7.5 7.5 0 0 1-13 5.1M4.5 12a7.5 7.5 0 0 1 13-5.1"/><path d="M4.5 7.5V11h3.5M19.5 16.5V13H16"/>',
    "eye": '<path d="M3 12s3.3-6 9-6 9 6 9 6-3.3 6-9 6-9-6-9-6Z"/><circle cx="12" cy="12" r="2.75"/>',
    "edit": '<path d="M4.5 19.5h4l10-10-4-4-10 10Z"/><path d="m12.5 7.5 4 4"/>',
    "cloud": '<path d="M7.5 18.5a4 4 0 0 1-.6-7.95A5.5 5.5 0 0 1 17.4 9.5 3.75 3.75 0 0 1 17 18.5Z"/>',
    "grid": '<rect x="4" y="4" width="6.5" height="6.5" rx="2"/><rect x="13.5" y="4" width="6.5" height="6.5" rx="2"/><rect x="4" y="13.5" width="6.5" height="6.5" rx="2"/><rect x="13.5" y="13.5" width="6.5" height="6.5" rx="2"/>',
    "dollar": '<path d="M12 4v16"/><path d="M15.5 8.25A3 3 0 0 0 12.5 6h-1.25a2.75 2.75 0 0 0 0 5.5h1.5a2.75 2.75 0 0 1 0 5.5h-1.5a3 3 0 0 1-3-2.5"/>',
    "user": '<circle cx="12" cy="8.5" r="3.75"/><path d="M4.5 20a7.5 7.5 0 0 1 15 0"/>',
    "camera": '<path d="M4 8.5h3.2l1.5-2.5h6.6l1.5 2.5H20v10.5H4Z"/><circle cx="12" cy="13.5" r="3.25"/>',
    "scissors": '<circle cx="6.5" cy="6.5" r="2.5"/><circle cx="6.5" cy="17.5" r="2.5"/><path d="M19.5 4.5 8.7 15.3M8.7 8.7 19.5 19.5"/>',
    "paw": '<circle cx="8" cy="7.5" r="1.75"/><circle cx="16" cy="7.5" r="1.75"/><circle cx="4.75" cy="12" r="1.5"/><circle cx="19.25" cy="12" r="1.5"/><path d="M12 11.5c2.8 0 5 2.8 5 5.2a2.6 2.6 0 0 1-3.6 2.4 3.6 3.6 0 0 0-2.8 0A2.6 2.6 0 0 1 7 16.7c0-2.4 2.2-5.2 5-5.2Z"/>',
    "utensils": '<path d="M6.5 3.5v17M4.5 3.5v5a2 2 0 0 0 4 0v-5"/><path d="M16 3.5c-2 0-3 3-3 5.5s1 3.5 3 3.5v8"/>',
    "car": '<path d="m4.5 14 2-5.5h11l2 5.5"/><rect x="3.5" y="14" width="17" height="4.5" rx="1.5"/><path d="M7.5 18.5v1.5M16.5 18.5v1.5"/>',
    "spa": '<path d="M12 20.5c-4.8 0-7.5-3.9-7.5-8.5 2.9 0 5.7 1 7.5 3.8 1.8-2.8 4.6-3.8 7.5-3.8 0 4.6-2.7 8.5-7.5 8.5Z"/><path d="M12 15.8V4"/>',
    "compass": '<circle cx="12" cy="12" r="8.5"/><path d="m15.2 8.8-1.8 4.6-4.6 1.8 1.8-4.6Z"/>',
    "document": '<path d="M6.5 3.5h7l4 4v13h-11Z"/><path d="M13.5 3.5v4h4"/>',
    "help": '<circle cx="12" cy="12" r="8.5"/><path d="M9.6 9.5a2.4 2.4 0 0 1 4.8 0c0 1.5-2.4 1.9-2.4 3.4"/><path d="M12 16.5h.01" stroke-width="2.2"/>',
    "link": '<path d="M10.5 13.5a3.5 3.5 0 0 0 5 0l2.5-2.5a3.5 3.5 0 0 0-5-5l-1 1"/><path d="M13.5 10.5a3.5 3.5 0 0 0-5 0L6 13a3.5 3.5 0 0 0 5 5l1-1"/>',
    "bell": '<path d="M6.5 16V11a5.5 5.5 0 0 1 11 0v5l1.5 1.5h-14Z"/><path d="M10.25 20a1.75 1.75 0 0 0 3.5 0"/>',
    "menu": '<path d="M4.5 7h15M4.5 12h15M4.5 17h15"/>',
    "x": '<path d="m6.5 6.5 11 11M17.5 6.5l-11 11"/>',
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


def _panel(x, y, w, h, r=14, fill="#fff", stroke="#e3e7ef"):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}"/>'


def mock_dashboard(label: str = "Leads this month") -> str:
    bars = ""
    heights = [38, 56, 44, 72, 60, 88, 78]
    for i, h in enumerate(heights):
        x = 46 + i * 34
        color = "#2a5a9c" if i != 5 else "#4f86c6"
        bars += f'<rect class="bar" x="{x}" y="{236 - h}" width="20" height="{h}" rx="6" fill="{color}" opacity="{0.55 + i * 0.06:.2f}"/>'
    return f'''<svg class="mock" viewBox="0 0 560 420" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{label} dashboard">
<defs><linearGradient id="mdg" x1="0" x2="1"><stop offset="0" stop-color="#2a5a9c"/><stop offset="1" stop-color="#4f86c6"/></linearGradient>
<linearGradient id="mdf" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2a5a9c" stop-opacity=".22"/><stop offset="1" stop-color="#2a5a9c" stop-opacity="0"/></linearGradient></defs>
<rect x="8" y="8" width="544" height="404" rx="26" fill="#fff" stroke="#e3e7ef"/>
<rect x="8" y="8" width="544" height="52" rx="26" fill="#f7f8fb"/><rect x="8" y="34" width="544" height="26" fill="#f7f8fb"/>
<circle cx="34" cy="34" r="5" fill="#e3e7ef"/><circle cx="50" cy="34" r="5" fill="#e3e7ef"/><circle cx="66" cy="34" r="5" fill="#e3e7ef"/>
<rect x="200" y="24" width="160" height="20" rx="10" fill="#eceef4"/>
{_panel(28, 80, 150, 78)}{_panel(196, 80, 150, 78)}{_panel(364, 80, 168, 78)}
<text x="44" y="106" font-size="11" fill="#6b7890" {_FONT}>New leads</text><text class="type" x="44" y="138" font-size="24" font-weight="700" fill="#0b1f3f" {_FONT}>128</text><text x="98" y="138" font-size="11" fill="#2a5a9c" {_FONT}>▲ 24%</text>
<text x="212" y="106" font-size="11" fill="#6b7890" {_FONT}>Booked jobs</text><text class="type" x="212" y="138" font-size="24" font-weight="700" fill="#0b1f3f" {_FONT}>46</text><text x="258" y="138" font-size="11" fill="#2a5a9c" {_FONT}>▲ 12%</text>
<text x="380" y="106" font-size="11" fill="#6b7890" {_FONT}>Collected</text><text class="type" x="380" y="138" font-size="24" font-weight="700" fill="#0b1f3f" {_FONT}>$38,420</text>
{_panel(28, 176, 318, 216)}
<text x="44" y="204" font-size="12" font-weight="600" fill="#0b1f3f" {_FONT}>{label}</text>
<g transform="translate(0,140)">{bars}</g>
<path class="line-anim" d="M56 330 C 100 300, 120 320, 160 290 S 230 250, 270 236 S 310 220, 330 200" fill="none" stroke="url(#mdg)" stroke-width="3" stroke-linecap="round"/>
{_panel(364, 176, 168, 216)}
<text x="380" y="204" font-size="12" font-weight="600" fill="#0b1f3f" {_FONT}>Today</text>
<g class="type"><circle cx="388" cy="232" r="9" fill="#eef2f8"/><path d="M384 232l3 3 5-5" stroke="#2a5a9c" stroke-width="2" fill="none" stroke-linecap="round"/><text x="404" y="236" font-size="11" fill="#16305a" {_FONT}>Estimate sent · Ramirez</text></g>
<g class="type"><circle cx="388" cy="262" r="9" fill="#eef1f6"/><path d="M384 262l3 3 5-5" stroke="#5a6e96" stroke-width="2" fill="none" stroke-linecap="round"/><text x="404" y="266" font-size="11" fill="#16305a" {_FONT}>Review request · 5.0 ★</text></g>
<g class="type"><circle cx="388" cy="292" r="9" fill="#eef1f7"/><circle cx="388" cy="292" r="3" fill="#4f86c6"/><text x="404" y="296" font-size="11" fill="#16305a" {_FONT}>Booking · 2:30 PM</text></g>
<g class="type"><circle cx="388" cy="322" r="9" fill="#f1f3f7"/><circle cx="388" cy="322" r="3" fill="#8a9bbb"/><text x="404" y="326" font-size="11" fill="#16305a" {_FONT}>New message · Google</text></g>
<rect x="380" y="350" width="136" height="26" rx="13" fill="#e4e9f2"/><text x="448" y="367" font-size="11" font-weight="600" fill="#0b1f3f" text-anchor="middle" {_FONT}>Open inbox</text>
</svg>'''


def mock_search(brand: str = "Your business") -> str:
    """Search-everywhere diagram: the business at the centre, every surface around it, a #1 result below."""
    nodes = [("Google", 0), ("Maps", 60), ("AI search", 120), ("Directories", 180), ("Social", 240), ("Reviews", 300)]
    g = ""
    import math
    cx, cy = 280, 230
    for i, (name, ang) in enumerate(nodes):
        a = math.radians(ang - 90)
        x, y = cx + 176 * math.cos(a), cy + 150 * math.sin(a)
        col = ["#2a5a9c", "#5a6e96", "#4f86c6", "#8a9bbb", "#8a9bbb", "#2a5a9c"][i]
        g += f'<line x1="{cx}" y1="{cy}" x2="{x:.0f}" y2="{y:.0f}" stroke="{col}" stroke-width="1.5" opacity=".35" stroke-dasharray="4 5"/>'
        g += f'<g class="type"><rect x="{x-52:.0f}" y="{y-18:.0f}" width="104" height="36" rx="18" fill="#fff" stroke="#e3e7ef"/><circle cx="{x-32:.0f}" cy="{y:.0f}" r="6" fill="{col}"/><text x="{x-20:.0f}" y="{y+4:.0f}" font-size="12" font-weight="600" fill="#0b1f3f" {_FONT}>{name}</text></g>'
    return f'''<svg class="mock" viewBox="0 0 560 500" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Search everywhere diagram">
<defs><linearGradient id="msg" x1="0" x2="1" y1="0" y2="1"><stop offset="0" stop-color="#dde5f1"/><stop offset="1" stop-color="#e9eef6"/></linearGradient></defs>
<circle class="ring" cx="{cx}" cy="{cy}" r="70" fill="none" stroke="#2a5a9c" stroke-width="2"/>
<circle class="ring" cx="{cx}" cy="{cy}" r="70" fill="none" stroke="#4f86c6" stroke-width="2" style="animation-delay:-1.6s"/>
<g class="spin" style="transform-origin:{cx}px {cy}px"><circle cx="{cx}" cy="{cy}" r="110" fill="none" stroke="#e3e7ef" stroke-dasharray="3 8"/></g>
{g}
<circle cx="{cx}" cy="{cy}" r="46" fill="url(#msg)"/>
<circle cx="{cx}" cy="{cy}" r="46" fill="none" stroke="#fff" stroke-width="3"/>
<text x="{cx}" y="{cy-4}" font-size="11" fill="#2a5a9c" text-anchor="middle" opacity=".9" {_FONT}>Your business</text>
<text x="{cx}" y="{cy+12}" font-size="12" font-weight="700" fill="#0b1f3f" text-anchor="middle" {_FONT}>Found</text>
<rect x="150" y="440" width="260" height="40" rx="20" fill="#fff" stroke="#e3e7ef"/>
<circle cx="172" cy="460" r="7" fill="none" stroke="#2a5a9c" stroke-width="2"/><path d="M177 465l4 4" stroke="#2a5a9c" stroke-width="2" stroke-linecap="round"/>
<text class="type" x="192" y="464" font-size="12" fill="#16305a" {_FONT}>best plumber near me</text>
<rect class="pulse" x="352" y="448" width="44" height="24" rx="12" fill="#eef2f8"/><text x="374" y="464" font-size="11" font-weight="700" fill="#1e4b8f" text-anchor="middle" {_FONT}>#1</text>
</svg>'''


def mock_inbox() -> str:
    rows = [("Google", "New lead — wants a quote for Friday", "#2a5a9c", "2m"),
            ("SMS", "Thanks! Can we move to 3 PM?", "#5a6e96", "18m"),
            ("Email", "Invoice #1042 paid · $1,250", "#4f86c6", "1h"),
            ("Facebook", "Do you service Kalamazoo?", "#8a9bbb", "3h")]
    r = ""
    for i, (src, msg, col, when) in enumerate(rows):
        y = 118 + i * 62
        r += f'<g class="type">{_panel(40, y, 480, 50, 14, "#fff" if i else "#f3f5f9", "#e3e7ef")}<circle cx="70" cy="{y+25}" r="13" fill="{col}" opacity=".18"/><circle cx="70" cy="{y+25}" r="5" fill="{col}"/><text x="96" y="{y+21}" font-size="11" font-weight="700" fill="#0b1f3f" {_FONT}>{src}</text><text x="96" y="{y+38}" font-size="11" fill="#6b7890" {_FONT}>{msg}</text><text x="500" y="{y+22}" font-size="10" fill="#9aa5b8" text-anchor="end" {_FONT}>{when}</text></g>'
    return f'''<svg class="mock" viewBox="0 0 560 420" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Unified inbox">
<rect x="8" y="8" width="544" height="404" rx="26" fill="#fff" stroke="#e3e7ef"/>
<rect x="8" y="8" width="544" height="52" rx="26" fill="#f7f8fb"/><rect x="8" y="34" width="544" height="26" fill="#f7f8fb"/>
<text x="40" y="40" font-size="14" font-weight="700" fill="#0b1f3f" {_FONT}>Inbox</text>
<rect x="100" y="24" width="52" height="22" rx="11" fill="#eef2f8"/><text x="126" y="39" font-size="11" font-weight="600" fill="#1e4b8f" text-anchor="middle" {_FONT}>All 12</text>
<rect x="160" y="24" width="60" height="22" rx="11" fill="#fff" stroke="#e3e7ef"/><text x="190" y="39" font-size="11" fill="#6b7890" text-anchor="middle" {_FONT}>Unread</text>
<rect x="40" y="76" width="480" height="30" rx="15" fill="#f7f8fb"/><text x="60" y="95" font-size="11" fill="#9aa5b8" {_FONT}>Search conversations</text>
{r}
<rect x="380" y="370" width="140" height="30" rx="15" fill="#e4e9f2"/><text x="450" y="389" font-size="11" font-weight="600" fill="#0b1f3f" text-anchor="middle" {_FONT}>Reply from one place</text>
</svg>'''


def mock_calendar() -> str:
    cells = ""
    for i in range(28):
        x = 48 + (i % 7) * 66
        y = 128 + (i // 7) * 58
        booked = i in (3, 5, 9, 12, 16, 17, 23, 24)
        fill = "#eef2f8" if booked else "#fff"
        cells += f'<rect x="{x}" y="{y}" width="58" height="50" rx="10" fill="{fill}" stroke="#e3e7ef"/><text x="{x+10}" y="{y+18}" font-size="10" fill="#6b7890" {_FONT}>{i+1}</text>'
        if booked:
            cells += f'<rect class="type" x="{x+8}" y="{y+26}" width="42" height="14" rx="7" fill="#2a5a9c" opacity=".85"/>'
    return f'''<svg class="mock" viewBox="0 0 560 420" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Online scheduling calendar">
<rect x="8" y="8" width="544" height="404" rx="26" fill="#fff" stroke="#e3e7ef"/>
<text x="48" y="60" font-size="16" font-weight="700" fill="#0b1f3f" {_FONT}>October</text>
<rect x="420" y="40" width="92" height="28" rx="14" fill="#e4e9f2"/><text x="466" y="58" font-size="11" font-weight="600" fill="#0b1f3f" text-anchor="middle" {_FONT}>+ Booking</text>
{"".join(f'<text x="{48+i*66+29}" y="112" font-size="10" fill="#9aa5b8" text-anchor="middle" {_FONT}>{d}</text>' for i, d in enumerate(["M","T","W","T","F","S","S"]))}
{cells}
<g class="type"><rect x="330" y="340" width="190" height="56" rx="14" fill="#fff" stroke="#e3e7ef" filter="drop-shadow(0 8px 16px rgba(16,24,40,.12))"/><circle cx="352" cy="368" r="10" fill="#eef1f6"/><path d="M347 368l3 3 6-6" stroke="#5a6e96" stroke-width="2" fill="none" stroke-linecap="round"/><text x="370" y="364" font-size="11" font-weight="700" fill="#0b1f3f" {_FONT}>Booked · Sat 10:30 AM</text><text x="370" y="380" font-size="10" fill="#6b7890" {_FONT}>Reminder sent automatically</text></g>
</svg>'''


def mock_invoice() -> str:
    return f'''<svg class="mock" viewBox="0 0 560 420" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Estimate and invoice">
<rect x="70" y="24" width="420" height="380" rx="24" fill="#fff" stroke="#e3e7ef"/>
<text x="100" y="70" font-size="18" font-weight="700" fill="#0b1f3f" {_FONT}>Invoice #1042</text>
<rect x="380" y="52" width="80" height="24" rx="12" fill="#eef1f6"/><text x="420" y="68" font-size="11" font-weight="700" fill="#2a5a9c" text-anchor="middle" {_FONT}>PAID</text>
<text x="100" y="96" font-size="11" fill="#6b7890" {_FONT}>Billed to Ramirez Residence · Due Oct 14</text>
<line x1="100" y1="120" x2="460" y2="120" stroke="#e3e7ef"/>
<g class="type"><text x="100" y="150" font-size="12" fill="#16305a" {_FONT}>Full system tune-up</text><text x="460" y="150" font-size="12" fill="#16305a" text-anchor="end" {_FONT}>$420.00</text></g>
<g class="type"><text x="100" y="180" font-size="12" fill="#16305a" {_FONT}>Replacement filter (x2)</text><text x="460" y="180" font-size="12" fill="#16305a" text-anchor="end" {_FONT}>$64.00</text></g>
<g class="type"><text x="100" y="210" font-size="12" fill="#16305a" {_FONT}>Labor · 3 hrs</text><text x="460" y="210" font-size="12" fill="#16305a" text-anchor="end" {_FONT}>$285.00</text></g>
<line x1="100" y1="236" x2="460" y2="236" stroke="#e3e7ef"/>
<text x="100" y="268" font-size="13" font-weight="700" fill="#0b1f3f" {_FONT}>Total</text><text class="type" x="460" y="268" font-size="20" font-weight="700" fill="#0b1f3f" text-anchor="end" {_FONT}>$769.00</text>
<rect x="100" y="300" width="360" height="42" rx="21" fill="#e4e9f2"/><text x="280" y="326" font-size="13" font-weight="600" fill="#0b1f3f" text-anchor="middle" {_FONT}>Pay with card · Apple Pay · ACH</text>
<g class="type"><rect x="100" y="356" width="360" height="28" rx="14" fill="#f7f8fb"/><circle cx="118" cy="370" r="6" fill="#2a5a9c"/><text x="132" y="374" font-size="11" fill="#16305a" {_FONT}>Deposited to your account in 1–2 business days</text></g>
</svg>'''


def mock_reviews() -> str:
    cards = ""
    people = [("Dawn J.", "Consistent calls and clients a year in.", "#2a5a9c"), ("Tex M.", "Fabulous job designing the website.", "#5a6e96"), ("Peter M.", "Everyone I've spoken with is knowledgeable.", "#4f86c6")]
    for i, (n, q, c) in enumerate(people):
        y = 90 + i * 104
        cards += f'<g class="type">{_panel(60, y, 440, 86, 18)}<circle cx="96" cy="{y+30}" r="16" fill="{c}" opacity=".18"/><text x="96" y="{y+35}" font-size="12" font-weight="700" fill="{c}" text-anchor="middle" {_FONT}>{n[0]}</text><text x="124" y="{y+26}" font-size="12" font-weight="700" fill="#0b1f3f" {_FONT}>{n}</text><text x="124" y="{y+44}" font-size="12" fill="#8a9bbb" {_FONT}>★★★★★</text><text x="124" y="{y+64}" font-size="11" fill="#3d4a63" {_FONT}>{q}</text></g>'
    return f'''<svg class="mock" viewBox="0 0 560 420" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Customer reviews">
<rect x="8" y="8" width="544" height="404" rx="26" fill="#fff" stroke="#e3e7ef"/>
<text x="60" y="56" font-size="15" font-weight="700" fill="#0b1f3f" {_FONT}>Reputation</text>
<rect class="pulse" x="400" y="36" width="100" height="28" rx="14" fill="#f1f3f7"/><text x="450" y="54" font-size="12" font-weight="700" fill="#5a6e96" text-anchor="middle" {_FONT}>4.9 ★ · 312</text>
{cards}
</svg>'''


def mock_map() -> str:
    import random
    rnd = random.Random(7)
    dots = ""
    for i in range(70):
        x, y = rnd.randint(60, 500), rnd.randint(70, 340)
        r = rnd.choice([3, 3, 4, 5])
        col = rnd.choice(["#2a5a9c", "#4f86c6", "#5a6e96", "#8a9bbb"])
        dots += f'<circle class="pulse" cx="{x}" cy="{y}" r="{r}" fill="{col}" opacity=".7" style="animation-delay:-{rnd.random()*3:.1f}s"/>'
    return f'''<svg class="mock" viewBox="0 0 560 420" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Markets across the country">
<rect x="8" y="8" width="544" height="404" rx="26" fill="#fff" stroke="#e3e7ef"/>
<path d="M60 130 C 120 80, 260 60, 330 90 S 480 70, 500 150 S 470 300, 380 330 S 220 360, 140 320 S 40 220, 60 130z" fill="#f3f5f9" stroke="#dce4f0"/>
{dots}
<g class="type"><rect x="300" y="330" width="220" height="56" rx="16" fill="#fff" stroke="#e3e7ef"/><text x="318" y="352" font-size="12" font-weight="700" fill="#0b1f3f" {_FONT}>31.2M+ local searches</text><text x="318" y="372" font-size="11" fill="#6b7890" {_FONT}>1.9M+ conversion points · 20K+ businesses</text></g>
</svg>'''


def mock_phone(screen: str = "inbox") -> str:
    inner = ""
    if screen == "inbox":
        for i, (t, c) in enumerate([("New lead · Google", "#2a5a9c"), ("Booking confirmed", "#5a6e96"), ("Invoice paid $769", "#4f86c6"), ("New 5★ review", "#8a9bbb")]):
            y = 150 + i * 66
            inner += f'<g class="type"><rect x="46" y="{y}" width="188" height="52" rx="14" fill="#f7f8fb"/><circle cx="70" cy="{y+26}" r="10" fill="{c}" opacity=".2"/><circle cx="70" cy="{y+26}" r="4" fill="{c}"/><text x="90" y="{y+24}" font-size="10.5" font-weight="700" fill="#0b1f3f" {_FONT}>{t}</text><text x="90" y="{y+40}" font-size="9.5" fill="#6b7890" {_FONT}>Tap to respond</text></g>'
    return f'''<svg class="mock" viewBox="0 0 280 560" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Mobile app">
<rect x="10" y="10" width="260" height="540" rx="44" fill="#e4e9f2"/>
<rect x="20" y="20" width="240" height="520" rx="36" fill="#fff"/>
<rect x="100" y="30" width="80" height="22" rx="11" fill="#0b1f3f"/>
<text x="46" y="98" font-size="17" font-weight="700" fill="#0b1f3f" {_FONT}>Good morning</text>
<text x="46" y="118" font-size="11" fill="#6b7890" {_FONT}>4 things need you today</text>
{inner}
<rect x="46" y="430" width="188" height="40" rx="20" fill="#e4e9f2"/><text x="140" y="455" font-size="11" font-weight="600" fill="#0b1f3f" text-anchor="middle" {_FONT}>Open dashboard</text>
<rect x="40" y="500" width="200" height="1" fill="#e3e7ef"/>
{"".join(f'<circle cx="{70+i*50}" cy="520" r="6" fill="{"#2a5a9c" if i==0 else "#e3e7ef"}"/>' for i in range(4))}
</svg>'''


def mock_crm() -> str:
    rows = [("Ramirez Residence", "Estimate sent · $769", "#2a5a9c", "Lead"), ("Blue Ridge Bakery", "Booked · Fri 10:30 AM", "#5a6e96", "Customer"),
            ("Patterson HVAC", "Invoice paid", "#4f86c6", "Customer"), ("Nguyen Family", "Review requested", "#8a9bbb", "Lead"), ("Carter Landscaping", "Follow-up scheduled", "#8a9bbb", "Prospect")]
    r = ""
    for i, (name, note, col, tag) in enumerate(rows):
        y = 118 + i * 54
        r += f'<g class="type"><rect x="40" y="{y}" width="480" height="44" rx="12" fill="#fff" stroke="#e3e7ef"/><circle cx="66" cy="{y+22}" r="13" fill="{col}" opacity=".18"/><text x="66" y="{y+26}" font-size="10" font-weight="700" fill="{col}" text-anchor="middle" {_FONT}>{name[0]}</text><text x="90" y="{y+19}" font-size="11" font-weight="700" fill="#0b1f3f" {_FONT}>{name}</text><text x="90" y="{y+34}" font-size="10" fill="#6b7890" {_FONT}>{note}</text><rect x="440" y="{y+12}" width="64" height="20" rx="10" fill="#f3f5f9"/><text x="472" y="{y+26}" font-size="9.5" font-weight="600" fill="#3d4a63" text-anchor="middle" {_FONT}>{tag}</text></g>'
    return f'''<svg class="mock" viewBox="0 0 560 420" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Customer relationship manager">
<rect x="8" y="8" width="544" height="404" rx="26" fill="#fff" stroke="#e3e7ef"/>
<rect x="8" y="8" width="544" height="52" rx="26" fill="#f7f8fb"/><rect x="8" y="34" width="544" height="26" fill="#f7f8fb"/>
<text x="40" y="40" font-size="14" font-weight="700" fill="#0b1f3f" {_FONT}>Contacts</text>
<rect x="400" y="24" width="120" height="24" rx="12" fill="#e4e9f2"/><text x="460" y="40" font-size="11" font-weight="600" fill="#0b1f3f" text-anchor="middle" {_FONT}>+ Add contact</text>
<rect x="40" y="76" width="300" height="30" rx="15" fill="#f7f8fb"/><text x="60" y="95" font-size="11" fill="#9aa5b8" {_FONT}>Search contacts, notes, invoices…</text>
<rect x="352" y="76" width="80" height="30" rx="15" fill="#eef2f8"/><text x="392" y="95" font-size="11" font-weight="600" fill="#1e4b8f" text-anchor="middle" {_FONT}>Leads 24</text>
<rect x="440" y="76" width="80" height="30" rx="15" fill="#fff" stroke="#e3e7ef"/><text x="480" y="95" font-size="11" fill="#6b7890" text-anchor="middle" {_FONT}>All 1,204</text>
{r}
</svg>'''


def mock_ads() -> str:
    return f'''<svg class="mock" viewBox="0 0 560 420" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Targeted advertising">
<rect x="150" y="16" width="260" height="388" rx="28" fill="#e4e9f2"/><rect x="158" y="24" width="244" height="372" rx="22" fill="#fff"/>
<rect x="240" y="32" width="80" height="16" rx="8" fill="#0b1f3f"/>
<g class="type"><rect x="174" y="70" width="212" height="180" rx="16" fill="#f7f8fb" stroke="#e3e7ef"/>
<circle cx="196" cy="92" r="10" fill="#2a5a9c" opacity=".2"/><circle cx="196" cy="92" r="4" fill="#2a5a9c"/><text x="212" y="90" font-size="9.5" font-weight="700" fill="#0b1f3f" {_FONT}>Your Business</text><text x="212" y="101" font-size="8" fill="#9aa5b8" {_FONT}>Sponsored · Charlotte, NC</text>
<rect x="186" y="112" width="188" height="90" rx="12" fill="url(#adg)"/>
<text x="280" y="152" font-size="12" font-weight="700" fill="#0b1f3f" text-anchor="middle" {_FONT}>Fall tune-up special</text><text x="280" y="168" font-size="9" fill="#2a5a9c" text-anchor="middle" opacity=".9" {_FONT}>Book this week and save 15%</text>
<rect x="186" y="212" width="90" height="24" rx="12" fill="#e4e9f2"/><text x="231" y="228" font-size="9" font-weight="600" fill="#0b1f3f" text-anchor="middle" {_FONT}>Book now</text></g>
<defs><linearGradient id="adg" x1="0" x2="1" y1="0" y2="1"><stop offset="0" stop-color="#dde5f1"/><stop offset="1" stop-color="#e9eef6"/></linearGradient></defs>
<g class="type"><rect x="174" y="264" width="212" height="60" rx="14" fill="#fff" stroke="#e3e7ef"/><text x="188" y="286" font-size="9.5" font-weight="700" fill="#0b1f3f" {_FONT}>Campaign performance</text><text x="188" y="304" font-size="9" fill="#2a5a9c" {_FONT}>▲ 3.2% CTR · 148 clicks · 19 leads</text></g>
<g class="type"><rect x="20" y="120" width="120" height="70" rx="14" fill="#fff" stroke="#e3e7ef"/><text x="34" y="144" font-size="9.5" fill="#6b7890" {_FONT}>Audience</text><text x="34" y="168" font-size="14" font-weight="700" fill="#0b1f3f" {_FONT}>Homeowners</text><text x="34" y="182" font-size="9" fill="#9aa5b8" {_FONT}>within 25 miles</text></g>
<g class="type"><rect x="420" y="200" width="120" height="70" rx="14" fill="#fff" stroke="#e3e7ef"/><text x="434" y="224" font-size="9.5" fill="#6b7890" {_FONT}>Reach this week</text><text class="pulse" x="434" y="250" font-size="16" font-weight="700" fill="#0b1f3f" {_FONT}>48,200</text></g>
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
