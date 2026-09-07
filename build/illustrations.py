"""Self-hosted illustrations for Charlie Company Media.

The archive hot-linked every photo from a CDN that no longer serves them, so the site draws its own
imagery: flat, single-palette scenes (navy hues on paper) for industries, products and articles, and a
real map of the markets we serve. Everything is inline SVG — no requests, no broken images.
"""
from __future__ import annotations

import hashlib
import math
import re

NAVY, DEEP, STEEL, SKY, MIST, PAPER, PAPER2, LINE = "#0b1f3f", "#14325f", "#2a5a9c", "#4f86c6", "#8a9bbb", "#f5f6fa", "#eceef4", "#dfe4ee"
_FONT = 'font-family="-apple-system,BlinkMacSystemFont,Inter,Helvetica,Arial,sans-serif"'
W, H = 800, 500


def _wrap(body: str, label: str, defs: str = "", bg: str = "", w: int = W, h: int = H) -> str:
    bg = bg or f'<rect width="{w}" height="{h}" fill="url(#sky)"/>'
    return (f'<svg class="art" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{label}" preserveAspectRatio="xMidYMid slice">'
            f'<defs><linearGradient id="sky" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#eef2f9"/><stop offset="1" stop-color="#f7f8fb"/></linearGradient>'
            f'<linearGradient id="deep" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{STEEL}"/><stop offset="1" stop-color="{NAVY}"/></linearGradient>'
            f'<linearGradient id="soft" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{SKY}" stop-opacity=".35"/><stop offset="1" stop-color="{SKY}" stop-opacity=".05"/></linearGradient>{defs}</defs>{bg}{body}</svg>')


def _sun(x=650, y=110, r=42):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{SKY}" opacity=".25"/><circle cx="{x}" cy="{y}" r="{r*0.62:.0f}" fill="{SKY}" opacity=".45"/>'


def _ground(y=380):
    return f'<path d="M0 {y} Q 200 {y-30} 400 {y} T 800 {y} V500 H0Z" fill="{PAPER2}"/><path d="M0 {y+40} Q 260 {y+10} 520 {y+40} T 800 {y+30} V500 H0Z" fill="{LINE}" opacity=".6"/>'


def _house(x, y, w=260, h=150, roof=70, fill=NAVY, stroke=None):
    """Simple house: body + gabled roof + door + windows (origin = bottom-left)."""
    body = (f'<rect x="{x}" y="{y-h}" width="{w}" height="{h}" rx="6" fill="#fff" stroke="{stroke or LINE}" stroke-width="3"/>'
            f'<path d="M{x-18} {y-h} L{x+w/2} {y-h-roof} L{x+w+18} {y-h}Z" fill="{fill}"/>'
            f'<rect x="{x+w*0.42}" y="{y-h*0.55}" width="{w*0.16}" height="{h*0.55}" rx="4" fill="{fill}"/>'
            f'<rect x="{x+w*0.1}" y="{y-h*0.78}" width="{w*0.2}" height="{h*0.3}" rx="4" fill="{SKY}" opacity=".35"/>'
            f'<rect x="{x+w*0.7}" y="{y-h*0.78}" width="{w*0.2}" height="{h*0.3}" rx="4" fill="{SKY}" opacity=".35"/>')
    return body


def _tree(x, y, s=1.0, fill=STEEL):
    return (f'<rect x="{x-6*s}" y="{y-40*s}" width="{12*s}" height="{40*s}" rx="4" fill="{DEEP}"/>'
            f'<circle cx="{x}" cy="{y-70*s}" r="{44*s}" fill="{fill}" opacity=".9"/><circle cx="{x-30*s}" cy="{y-50*s}" r="{30*s}" fill="{fill}" opacity=".75"/><circle cx="{x+30*s}" cy="{y-52*s}" r="{32*s}" fill="{fill}" opacity=".8"/>')


def scene_local() -> str:
    b = (_sun() + _ground(400)
         + f'<rect x="150" y="190" width="500" height="210" rx="10" fill="#fff" stroke="{LINE}" stroke-width="3"/>'
         + f'<path d="M130 190 h540 v22 a30 30 0 0 1 -60 0 a30 30 0 0 1 -60 0 a30 30 0 0 1 -60 0 a30 30 0 0 1 -60 0 a30 30 0 0 1 -60 0 a30 30 0 0 1 -60 0 a30 30 0 0 1 -60 0 a30 30 0 0 1 -60 0 a30 30 0 0 1 -60 0 z" fill="{NAVY}"/>'
         + f'<rect x="130" y="150" width="540" height="40" rx="8" fill="{DEEP}"/>'
         + f'<rect x="185" y="250" width="150" height="120" rx="8" fill="{SKY}" opacity=".3"/><rect x="465" y="250" width="150" height="120" rx="8" fill="{SKY}" opacity=".3"/>'
         + f'<rect x="365" y="270" width="70" height="130" rx="8" fill="{NAVY}"/><circle cx="422" cy="340" r="4" fill="#fff"/>'
         + f'<rect x="300" y="160" width="200" height="20" rx="6" fill="#fff" opacity=".9"/>'
         + f'<text x="400" y="176" font-size="14" font-weight="700" fill="{NAVY}" text-anchor="middle" letter-spacing="3" {_FONT}>OPEN</text>')
    return _wrap(b, "Local storefront")


def scene_hvac() -> str:
    b = (_sun(660, 100) + _ground(400) + _house(200, 400, 300, 160, 80)
         + f'<rect x="540" y="330" width="110" height="70" rx="10" fill="#fff" stroke="{LINE}" stroke-width="3"/>'
         + f'<circle cx="595" cy="365" r="24" fill="none" stroke="{STEEL}" stroke-width="5"/><circle cx="595" cy="365" r="6" fill="{STEEL}"/>'
         + ''.join(f'<path d="M{595+34*math.cos(a)} {365+34*math.sin(a)} L{595+24*math.cos(a)} {365+24*math.sin(a)}" stroke="{STEEL}" stroke-width="4" stroke-linecap="round"/>' for a in [i*math.pi/3 for i in range(6)])
         + ''.join(f'<path d="M{680+i*26} 300 c 12 -20 -12 -40 0 -60" fill="none" stroke="{SKY}" stroke-width="5" stroke-linecap="round" opacity="{.9-i*.25}"/>' for i in range(3))
         + f'<path d="M470 330 h70 v70" fill="none" stroke="{MIST}" stroke-width="5"/>'
         + f'<rect x="120" y="120" width="60" height="18" rx="9" fill="{SKY}" opacity=".3"/><rect x="80" y="150" width="90" height="18" rx="9" fill="{SKY}" opacity=".2"/>')
    return _wrap(b, "Heating and cooling")


def scene_plumbing() -> str:
    pipe = f'<path d="M120 120 h200 a40 40 0 0 1 40 40 v90 a40 40 0 0 0 40 40 h260" fill="none" stroke="{NAVY}" stroke-width="34" stroke-linecap="round" stroke-linejoin="round"/><path d="M120 120 h200 a40 40 0 0 1 40 40 v90 a40 40 0 0 0 40 40 h260" fill="none" stroke="{STEEL}" stroke-width="16" stroke-linecap="round" stroke-linejoin="round" opacity=".8"/>'
    valve = f'<circle cx="400" cy="290" r="46" fill="#fff" stroke="{NAVY}" stroke-width="10"/><circle cx="400" cy="290" r="12" fill="{NAVY}"/><path d="M400 244 v-40 M370 214 h60" stroke="{NAVY}" stroke-width="10" stroke-linecap="round"/>'
    drops = ''.join(f'<path d="M{x} {y} c-16 22 -16 40 0 40 c16 0 16 -18 0 -40z" fill="{SKY}" opacity="{o}"/>' for x, y, o in [(660, 330, .8), (700, 380, .5), (640, 400, .35)])
    b = _ground(430) + pipe + valve + drops + f'<rect x="110" y="98" width="30" height="44" rx="6" fill="{NAVY}"/><rect x="640" y="268" width="30" height="44" rx="6" fill="{NAVY}"/>'
    return _wrap(b, "Plumbing")


def scene_roofing() -> str:
    rows = ''.join(f'<path d="M{160+i*10} {150+i*22} L{640-i*10} {150+i*22}" stroke="{"#fff" if i % 2 else SKY}" stroke-opacity=".8" stroke-width="4" stroke-dasharray="{34 if i%2 else 30} 8"/>' for i in range(1, 9))
    b = (_sun(120, 100, 36) + _ground(410)
         + f'<rect x="230" y="320" width="340" height="90" rx="6" fill="#fff" stroke="{LINE}" stroke-width="3"/>'
         + f'<path d="M150 330 L400 130 L650 330Z" fill="url(#deep)"/>' + rows
         + f'<path d="M150 330 L400 130 L650 330" fill="none" stroke="{NAVY}" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/>'
         + f'<rect x="500" y="150" width="34" height="70" rx="4" fill="{NAVY}"/>'
         + f'<path d="M600 250 l70 -40 M620 290 l70 -40 M600 330 l70 -40" stroke="{MIST}" stroke-width="6" stroke-linecap="round" opacity=".7"/><path d="M640 200 v150" stroke="{MIST}" stroke-width="6" stroke-linecap="round" opacity=".7"/>')
    return _wrap(b, "Roofing")


def scene_remodel() -> str:
    b = (_ground(420) + _house(170, 420, 300, 170, 80, NAVY)
         + f'<path d="M560 420 L600 140 M660 420 L620 140" stroke="{NAVY}" stroke-width="12" stroke-linecap="round"/>'
         + ''.join(f'<path d="M{575+i*6} {380-i*48} h{70-i*2}" stroke="{STEEL}" stroke-width="10" stroke-linecap="round"/>' for i in range(5))
         + f'<rect x="60" y="300" width="80" height="120" rx="8" fill="{STEEL}"/><rect x="72" y="312" width="56" height="30" rx="4" fill="#fff" opacity=".8"/>'
         + f'<path d="M330 300 l60 -60 M390 240 l24 24" stroke="{NAVY}" stroke-width="12" stroke-linecap="round"/><rect x="376" y="216" width="50" height="30" rx="6" transform="rotate(45 401 231)" fill="{NAVY}"/>')
    return _wrap(b, "Home remodeling")


def scene_contracting() -> str:
    b = (_ground(430)
         + f'<rect x="150" y="150" width="500" height="280" rx="8" fill="none" stroke="{NAVY}" stroke-width="10"/>'
         + f'<path d="M150 240 h500 M150 330 h500 M320 150 v280 M480 150 v280" stroke="{STEEL}" stroke-width="8"/>'
         + f'<path d="M150 150 L320 240 M320 150 L480 240 M480 150 L650 240" stroke="{MIST}" stroke-width="6" opacity=".8"/>'
         + f'<rect x="150" y="120" width="500" height="30" rx="6" fill="{NAVY}"/>'
         + f'<path d="M700 120 v300 M700 120 h-60 M700 160 l-50 -40" stroke="{NAVY}" stroke-width="10" stroke-linecap="round"/><circle cx="640" cy="120" r="14" fill="{SKY}"/>'
         + f'<rect x="60" y="360" width="60" height="70" rx="6" fill="{STEEL}"/><rect x="60" y="330" width="60" height="26" rx="6" fill="{NAVY}"/>')
    return _wrap(b, "General contracting")


def scene_tree() -> str:
    b = _sun(690, 100) + _ground(410) + _tree(250, 410, 1.5, STEEL) + _tree(470, 410, 1.1, SKY) + _tree(620, 410, .8, STEEL) + _tree(110, 410, .9, SKY)
    return _wrap(b, "Tree service")


def scene_landscaping() -> str:
    hedge = ''.join(f'<circle cx="{120+i*70}" cy="380" r="34" fill="{"%s" % (STEEL if i % 2 else SKY)}" opacity=".9"/>' for i in range(10))
    b = (_sun(660, 110) + f'<path d="M0 330 Q 300 250 800 330 V500 H0Z" fill="{PAPER2}"/><path d="M0 420 Q 400 360 800 420 V500 H0Z" fill="{LINE}" opacity=".7"/>'
         + hedge + _tree(560, 350, 1.3, STEEL) + _tree(180, 340, 1.0, SKY)
         + f'<path d="M0 470 Q 400 430 800 470" stroke="{MIST}" stroke-width="6" fill="none" opacity=".6"/>')
    return _wrap(b, "Landscaping")


def scene_food() -> str:
    b = (_ground(430)
         + f'<ellipse cx="400" cy="300" rx="190" ry="60" fill="#fff" stroke="{LINE}" stroke-width="4"/><ellipse cx="400" cy="300" rx="130" ry="40" fill="{PAPER2}"/>'
         + f'<circle cx="400" cy="296" r="46" fill="{STEEL}"/><circle cx="360" cy="306" r="18" fill="{SKY}" opacity=".7"/><circle cx="446" cy="308" r="16" fill="{SKY}" opacity=".7"/>'
         + f'<path d="M170 210 v100 M150 210 v40 a20 20 0 0 0 40 0 v-40 M170 310 v70" stroke="{NAVY}" stroke-width="10" stroke-linecap="round"/>'
         + f'<path d="M630 210 c-24 0 -34 40 -34 70 s10 40 34 40 v60" stroke="{NAVY}" stroke-width="10" stroke-linecap="round" fill="none"/>'
         + f'<path d="M560 130 h90 v50 a45 45 0 0 1 -90 0z" fill="#fff" stroke="{NAVY}" stroke-width="8"/><path d="M650 145 h18 a16 16 0 0 1 0 32 h-18" fill="none" stroke="{NAVY}" stroke-width="8"/>'
         + ''.join(f'<path d="M{585+i*20} 118 c 8 -12 -8 -22 0 -34" fill="none" stroke="{MIST}" stroke-width="4" stroke-linecap="round"/>' for i in range(3)))
    return _wrap(b, "Food and beverage")


def scene_towing() -> str:
    b = (_ground(420)
         + f'<path d="M0 425 H800" stroke="{MIST}" stroke-width="4" stroke-dasharray="30 22" opacity=".7"/>'
         + f'<rect x="140" y="300" width="330" height="90" rx="12" fill="{NAVY}"/><path d="M470 390 v-110 h90 l70 60 v50z" fill="{DEEP}"/><rect x="500" y="300" width="55" height="40" rx="6" fill="{SKY}" opacity=".5"/>'
         + f'<path d="M180 300 l-40 -120 M140 180 h30" stroke="{NAVY}" stroke-width="12" stroke-linecap="round"/><path d="M170 180 q0 40 30 40" fill="none" stroke="{STEEL}" stroke-width="8" stroke-linecap="round"/>'
         + f'<rect x="60" y="330" width="120" height="60" rx="10" fill="{STEEL}"/><rect x="80" y="310" width="70" height="30" rx="8" fill="{SKY}" opacity=".6"/>'
         + ''.join(f'<circle cx="{x}" cy="400" r="28" fill="{NAVY}"/><circle cx="{x}" cy="400" r="12" fill="#fff"/>' for x in (220, 400, 580, 110)))
    return _wrap(b, "Towing")


def scene_legal() -> str:
    b = (_ground(430)
         + f'<rect x="330" y="400" width="140" height="30" rx="6" fill="{NAVY}"/><rect x="392" y="150" width="16" height="250" rx="6" fill="{NAVY}"/><rect x="180" y="160" width="440" height="14" rx="7" fill="{NAVY}"/>'
         + f'<circle cx="400" cy="150" r="18" fill="{STEEL}"/>'
         + ''.join(f'<path d="M{x} 170 l-70 110 M{x} 170 l70 110" stroke="{STEEL}" stroke-width="5"/><path d="M{x-80} 280 a80 30 0 0 0 160 0z" fill="{SKY}" opacity=".45" stroke="{STEEL}" stroke-width="5"/>' for x in (200, 600)))
    return _wrap(b, "Legal")


def scene_reporting() -> str:
    bars = ''.join(f'<rect class="bar" x="{170+i*78}" y="{400-h}" width="46" height="{h}" rx="10" fill="{STEEL if i%2 else SKY}" opacity=".9"/>' for i, h in enumerate([120, 180, 150, 230, 200, 280, 260]))
    b = (f'<rect x="100" y="80" width="600" height="360" rx="24" fill="#fff" stroke="{LINE}" stroke-width="3"/>'
         + f'<rect x="130" y="110" width="160" height="18" rx="9" fill="{PAPER2}"/><rect x="130" y="140" width="100" height="12" rx="6" fill="{PAPER2}"/>'
         + f'<path d="M150 400 h520" stroke="{LINE}" stroke-width="3"/>' + bars
         + f'<path class="line-anim" d="M190 330 C 260 300, 300 260, 360 250 S 470 220, 520 170 S 620 120, 660 100" fill="none" stroke="{NAVY}" stroke-width="6" stroke-linecap="round"/>')
    return _wrap(b, "Reporting")


def scene_display() -> str:
    b = (_ground(430)
         + f'<rect x="120" y="90" width="560" height="260" rx="18" fill="{NAVY}"/><rect x="136" y="106" width="528" height="228" rx="12" fill="#fff"/>'
         + f'<rect x="160" y="140" width="220" height="24" rx="12" fill="{NAVY}"/><rect x="160" y="180" width="300" height="14" rx="7" fill="{PAPER2}"/><rect x="160" y="204" width="260" height="14" rx="7" fill="{PAPER2}"/>'
         + f'<rect x="160" y="260" width="140" height="40" rx="20" fill="{SKY}" opacity=".3"/><text x="230" y="286" font-size="16" font-weight="600" fill="{NAVY}" text-anchor="middle" {_FONT}>Book now</text>'
         + f'<rect x="480" y="130" width="160" height="170" rx="16" fill="url(#soft)"/>'
         + f'<rect x="380" y="350" width="40" height="80" fill="{NAVY}"/><rect x="340" y="426" width="120" height="14" rx="7" fill="{NAVY}"/>')
    return _wrap(b, "Display advertising")


def scene_website(label: str = "", square: bool = False) -> str:
    title = f'<text x="400" y="98" font-size="14" font-weight="600" fill="{NAVY}" text-anchor="middle" {_FONT}>{label[:40]}</text>' if label else ""
    if square:
        inner = scene_website(label)
        body = inner[inner.index("</defs>") + 7:inner.rindex("</svg>")]
        body = body.replace(f'<rect width="{W}" height="{H}" fill="url(#sky)"/>', "", 1)
        return _wrap(f'<g transform="translate(0 150)">{body}</g>', label or "Website", w=800, h=800)
    b = (title + f'<rect x="90" y="70" width="620" height="380" rx="22" fill="#fff" stroke="{LINE}" stroke-width="3"/>'
         + f'<rect x="90" y="70" width="620" height="44" rx="22" fill="{PAPER2}"/><rect x="90" y="96" width="620" height="18" fill="{PAPER2}"/>'
         + ''.join(f'<circle cx="{118+i*18}" cy="92" r="5" fill="{MIST}"/>' for i in range(3))
         + f'<rect x="130" y="150" width="240" height="28" rx="8" fill="{NAVY}"/><rect x="130" y="192" width="300" height="12" rx="6" fill="{PAPER2}"/><rect x="130" y="214" width="260" height="12" rx="6" fill="{PAPER2}"/>'
         + f'<rect x="130" y="250" width="130" height="38" rx="19" fill="{SKY}" opacity=".3"/>'
         + f'<rect x="430" y="150" width="240" height="150" rx="14" fill="url(#soft)"/>'
         + ''.join(f'<rect x="{130+i*180}" y="330" width="160" height="90" rx="12" fill="{PAPER}" stroke="{LINE}"/>' for i in range(3)))
    return _wrap(b, "Website")


def scene_search() -> str:
    b = (_ground(440)
         + f'<rect x="140" y="120" width="520" height="72" rx="36" fill="#fff" stroke="{LINE}" stroke-width="3"/><circle cx="190" cy="156" r="16" fill="none" stroke="{STEEL}" stroke-width="6"/><path d="M202 168 l14 14" stroke="{STEEL}" stroke-width="6" stroke-linecap="round"/>'
         + f'<rect x="230" y="146" width="220" height="20" rx="10" fill="{PAPER2}"/><rect x="560" y="140" width="80" height="32" rx="16" fill="{SKY}" opacity=".3"/>'
         + ''.join(f'<rect x="140" y="{224+i*66}" width="520" height="50" rx="14" fill="#fff" stroke="{LINE}" stroke-width="2"/><rect x="164" y="{240+i*66}" width="{260-i*40}" height="10" rx="5" fill="{NAVY if i==0 else PAPER2}"/><rect x="164" y="{256+i*66}" width="{360-i*30}" height="8" rx="4" fill="{PAPER2}"/>' for i in range(3))
         + f'<path d="M700 300 c 0 -40 -30 -70 -70 -70 s -70 30 -70 70 c 0 50 70 110 70 110 s 70 -60 70 -110z" fill="{NAVY}"/><circle cx="630" cy="300" r="22" fill="#fff"/>')
    return _wrap(b, "Search")


def scene_reviews() -> str:
    star = "M0 -22 L6.5 -7 L22 -6 L10 5 L13.5 21 L0 12 L-13.5 21 L-10 5 L-22 -6 L-6.5 -7Z"
    b = (_ground(440)
         + f'<rect x="130" y="110" width="540" height="240" rx="24" fill="#fff" stroke="{LINE}" stroke-width="3"/>'
         + ''.join(f'<path d="{star}" transform="translate({230+i*68} 190) scale(1.6)" fill="{STEEL if i < 4 else SKY}"/>' for i in range(5))
         + f'<rect x="170" y="250" width="380" height="14" rx="7" fill="{PAPER2}"/><rect x="170" y="278" width="300" height="14" rx="7" fill="{PAPER2}"/>'
         + f'<circle cx="190" cy="320" r="14" fill="{NAVY}"/><rect x="216" y="312" width="120" height="14" rx="7" fill="{NAVY}" opacity=".6"/>'
         + f'<path d="{star}" transform="translate(690 120) scale(1.1)" fill="{SKY}" opacity=".6"/><path d="{star}" transform="translate(110 380) scale(.8)" fill="{SKY}" opacity=".5"/>')
    return _wrap(b, "Reviews")


def scene_email() -> str:
    env = lambda x, y, w, h, c: f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="#fff" stroke="{c}" stroke-width="6"/><path d="M{x} {y+10} L{x+w/2} {y+h*0.55} L{x+w} {y+10}" fill="none" stroke="{c}" stroke-width="6" stroke-linejoin="round"/>'
    b = (_ground(440) + env(150, 200, 300, 200, NAVY) + env(520, 130, 180, 120, STEEL) + env(560, 290, 130, 90, SKY)
         + f'<circle cx="440" cy="200" r="30" fill="{SKY}"/><text x="440" y="209" font-size="24" font-weight="700" fill="#fff" text-anchor="middle" {_FONT}>3</text>')
    return _wrap(b, "Email and SMS")


def scene_social() -> str:
    nodes = [(400, 250, 60, NAVY), (200, 160, 36, STEEL), (620, 160, 36, SKY), (180, 360, 30, SKY), (640, 370, 30, STEEL), (400, 90, 26, MIST)]
    lines = ''.join(f'<path d="M400 250 L{x} {y}" stroke="{MIST}" stroke-width="6" stroke-linecap="round" opacity=".8"/>' for x, y, r, c in nodes[1:])
    b = lines + ''.join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{c}"/><circle cx="{x}" cy="{y-r*0.3:.0f}" r="{r*0.35:.0f}" fill="#fff" opacity=".9"/><path d="M{x-r*0.65:.0f} {y+r*0.85:.0f} a{r*0.65:.0f} {r*0.65:.0f} 0 0 1 {r*1.3:.0f} 0z" fill="#fff" opacity=".9"/>' for x, y, r, c in nodes)
    return _wrap(b, "Social media")


def scene_people() -> str:
    b = _ground(440) + ''.join(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{c}"/><circle cx="{x}" cy="{y-r*0.35:.0f}" r="{r*0.42:.0f}" fill="#fff" opacity=".9"/><path d="M{x-r*0.75:.0f} {y+r*0.9:.0f} a{r*0.75:.0f} {r*0.75:.0f} 0 0 1 {r*1.5:.0f} 0z" fill="#fff" opacity=".9"/>' for x, y, r, c in [(400, 250, 110, NAVY), (200, 300, 80, STEEL), (600, 300, 80, SKY)])
    return _wrap(b, "Our team")


def scene_abstract(seed: str = "") -> str:
    h = int(hashlib.md5(seed.encode()).hexdigest()[:6], 16)
    shapes = ""
    for i in range(5):
        x = 80 + ((h >> (i * 4)) % 60) * 11; y = 60 + ((h >> (i * 3)) % 40) * 9; r = 60 + (h >> i) % 90
        shapes += f'<circle cx="{x}" cy="{y}" r="{r}" fill="{[STEEL, SKY, NAVY, MIST, STEEL][i]}" opacity="{.10 + (i % 3) * .06:.2f}"/>'
    b = shapes + f'<path d="M0 360 C 200 300, 300 420, 500 360 S 720 300, 800 340 V500 H0Z" fill="{PAPER2}"/><path d="M0 410 C 260 370, 420 470, 800 400 V500 H0Z" fill="{LINE}" opacity=".7"/>'
    return _wrap(b, "Illustration")


SCENES = {
    "local": scene_local, "hvac": scene_hvac, "plumbing": scene_plumbing, "roofing": scene_roofing, "remodel": scene_remodel,
    "contracting": scene_contracting, "tree": scene_tree, "landscaping": scene_landscaping, "food": scene_food, "towing": scene_towing,
    "legal": scene_legal, "reporting": scene_reporting, "display": scene_display, "website": scene_website, "people": scene_people,
    "search": scene_search, "reviews": scene_reviews, "email": scene_email, "social": scene_social,
}
KEYS = [
    (r"hvac|heating|cooling|air condition|furnace", "hvac"), (r"plumb|drain|water heater", "plumbing"), (r"roof", "roofing"),
    (r"remodel|kitchen|bath|renovat", "remodel"), (r"contract|construct|builder|handyman", "contracting"), (r"\btree|arborist", "tree"),
    (r"landscap|lawn|garden|yard", "landscaping"), (r"restaurant|food|beverage|bakery|caf|catering|dining|pizza|bar\b", "food"),
    (r"tow|auto|car\b|mechanic|truck|tire|body shop|collision|fleet|transport|captain|marine|boat", "towing"), (r"legal|law|attorney", "legal"), (r"report|analytic|dashboard|insight|data", "reporting"),
    (r"display|ads?\b|advert|billboard|banner|ppc|campaign", "display"), (r"seo|search|rank|google business|listing|director|citation|\bai\b|visib", "search"),
    (r"review|reputation|rating|testimonial|trust", "reviews"), (r"email|sms|text message|newsletter|inbox|follow[- ]up|automat", "email"), (r"social|facebook|instagram|linkedin|tiktok", "social"),
    (r"website|web design|site\b|landing|domain|hosting|page speed", "website"),
    (r"team|staff|people|culture|career|employee|office|photo|headshot|portrait", "people"), (r"local|store|shop|retail|business|customer", "local"),
]


def scene_for(*hints: str, default: str = "") -> str:
    text = " ".join(h or "" for h in hints).lower()
    for rx, key in KEYS:
        if re.search(rx, text):
            return SCENES[key]()
    if default in SCENES:
        return SCENES[default]()
    return scene_abstract(text)


# ---------------------------------------------------------------------------
# Map of markets
# ---------------------------------------------------------------------------
US_OUTLINE = [(-124.7, 48.4), (-124.1, 46.9), (-124.0, 45.0), (-124.4, 43.0), (-124.2, 42.0), (-124.1, 40.4), (-123.7, 38.9), (-122.5, 37.6), (-121.9, 36.6), (-120.6, 34.6), (-118.5, 34.0), (-117.2, 32.6),
              (-114.7, 32.7), (-111.0, 31.3), (-108.2, 31.3), (-106.5, 31.8), (-104.5, 29.6), (-103.0, 29.0), (-101.4, 29.8), (-99.5, 27.5), (-97.4, 25.9),
              (-97.2, 27.8), (-96.5, 28.6), (-94.7, 29.4), (-93.3, 29.8), (-91.5, 29.3), (-89.5, 29.0), (-89.0, 30.4), (-87.5, 30.3), (-85.4, 29.7), (-84.0, 30.1), (-82.7, 28.9), (-82.8, 27.5), (-81.8, 26.0), (-81.1, 25.2),
              (-80.4, 25.4), (-80.1, 26.9), (-80.6, 28.5), (-81.4, 30.7), (-80.9, 32.0), (-79.9, 32.8), (-78.5, 33.9), (-76.5, 34.7), (-75.6, 35.5), (-75.9, 36.9), (-75.2, 38.0), (-74.9, 38.9), (-74.0, 40.4), (-72.0, 41.0), (-70.0, 41.6), (-70.7, 42.6), (-70.6, 43.5), (-68.8, 44.4), (-67.0, 44.8), (-67.8, 45.7), (-67.8, 47.1), (-69.2, 47.4), (-70.4, 45.9), (-71.5, 45.0), (-74.8, 45.0), (-76.2, 44.0), (-79.0, 43.3), (-79.0, 42.9),
              (-80.5, 42.2), (-82.4, 41.5), (-83.2, 42.1), (-82.5, 43.0), (-82.7, 44.0), (-83.4, 45.2), (-84.7, 45.8), (-85.5, 45.0), (-86.3, 44.3), (-86.4, 43.0), (-86.8, 42.0), (-87.6, 41.7), (-87.8, 43.0), (-87.2, 44.6), (-88.0, 44.8), (-87.5, 45.5), (-86.7, 45.9), (-84.7, 46.4), (-84.4, 46.5), (-87.5, 46.6), (-88.5, 47.1), (-89.6, 47.0), (-90.5, 46.6), (-92.1, 46.7), (-89.5, 48.0), (-95.2, 49.4), (-104.0, 49.0), (-114.0, 49.0), (-123.3, 49.0)]

CITIES = {  # slug fragment: (label, lat, lon)
    "abilene-tx": ("Abilene, TX", 32.45, -99.73), "albany-ny": ("Albany, NY", 42.65, -73.75), "amarillo-tx": ("Amarillo, TX", 35.22, -101.83), "atlantic-city-cape-may-nj": ("Atlantic City, NJ", 39.36, -74.42),
    "augusta-waterville-me": ("Augusta, ME", 44.31, -69.78), "bangor-me": ("Bangor, ME", 44.80, -68.77), "battle-creek-mi": ("Battle Creek, MI", 42.32, -85.18), "berkshire-ma": ("The Berkshires, MA", 42.45, -73.25),
    "billings-mt": ("Billings, MT", 45.78, -108.50), "binghamton-ny": ("Binghamton, NY", 42.10, -75.91), "bismarck-nd": ("Bismarck, ND", 46.81, -100.78), "boise-id": ("Boise, ID", 43.62, -116.20),
    "bozeman-mt": ("Bozeman, MT", 45.68, -111.04), "buffalo-ny": ("Buffalo, NY", 42.89, -78.88), "butte-mt": ("Butte, MT", 46.00, -112.53), "casper-wy": ("Casper, WY", 42.87, -106.31),
    "cedar-rapids-ia": ("Cedar Rapids, IA", 41.98, -91.67), "charlotte-nc": ("Charlotte, NC", 35.23, -80.84), "cheyenne-wy": ("Cheyenne, WY", 41.14, -104.82), "danbury-ct": ("Danbury, CT", 41.39, -73.45),
    "dubuque-ia": ("Dubuque, IA", 42.50, -90.66), "duluth-mn": ("Duluth, MN", 46.79, -92.10), "el-paso-tx": ("El Paso, TX", 31.76, -106.49), "evansville-in": ("Evansville, IN", 37.97, -87.57),
    "faribault-owatonna-mn": ("Faribault, MN", 44.29, -93.27), "flint-mi": ("Flint, MI", 43.01, -83.69), "fort-collins-co": ("Fort Collins, CO", 40.59, -105.08), "grand-junction-co": ("Grand Junction, CO", 39.06, -108.55),
    "grand-rapids-mi": ("Grand Rapids, MI", 42.96, -85.67), "great-falls-mt": ("Great Falls, MT", 47.50, -111.30), "kalamazoo-mi": ("Kalamazoo, MI", 42.29, -85.59), "killeen-temple-tx": ("Killeen, TX", 31.12, -97.73),
    "lafayette-la": ("Lafayette, LA", 30.22, -92.02), "lake-charles-la": ("Lake Charles, LA", 30.23, -93.22), "lansing-mi": ("Lansing, MI", 42.73, -84.55), "laramie-wy": ("Laramie, WY", 41.31, -105.59),
    "lawton-ok": ("Lawton, OK", 34.60, -98.40), "lubbock-tx": ("Lubbock, TX", 33.58, -101.86), "lufkin-tx": ("Lufkin, TX", 31.34, -94.73), "missoula-mt": ("Missoula, MT", 46.87, -114.00),
    "monmouth-ocean-nj": ("Monmouth, NJ", 40.30, -74.05), "montrose-co": ("Montrose, CO", 38.48, -107.88), "new-bedford-fall-river-ma": ("New Bedford, MA", 41.64, -70.93), "odessa-midland-tx": ("Midland, TX", 31.99, -102.08),
    "oneonta-ny": ("Oneonta, NY", 42.45, -75.06), "owensboro-ky": ("Owensboro, KY", 37.77, -87.11), "phoenix-az": ("Phoenix, AZ", 33.45, -112.07), "portland-me": ("Portland, ME", 43.66, -70.26),
    "portsmouth-nh": ("Portsmouth, NH", 43.07, -70.76), "poughkeepsie-ny": ("Poughkeepsie, NY", 41.70, -73.92), "presque-isle-me": ("Presque Isle, ME", 46.68, -68.02), "quad-cities-ia": ("Quad Cities, IA", 41.52, -90.58),
    "quincy-hannibal-il": ("Quincy, IL", 39.94, -91.41), "richland-kennewick-pasco-wa": ("Tri-Cities, WA", 46.28, -119.28), "rochester-mn": ("Rochester, MN", 44.02, -92.48), "rockford-il": ("Rockford, IL", 42.27, -89.09),
    "san-angelo-tx": ("San Angelo, TX", 31.46, -100.44), "sedalia-mo": ("Sedalia, MO", 38.70, -93.23), "shelby-mt": ("Shelby, MT", 48.51, -111.86), "shreveport-la": ("Shreveport, LA", 32.53, -93.75),
    "sierra-vista-az": ("Sierra Vista, AZ", 31.55, -110.30), "sioux-falls-sd": ("Sioux Falls, SD", 43.55, -96.73), "st-cloud-mn": ("St. Cloud, MN", 45.56, -94.16), "st-george-ut": ("St. George, UT", 37.10, -113.58),
    "texarkana-ar": ("Texarkana", 33.44, -94.04), "trenton-nj": ("Trenton, NJ", 40.22, -74.76), "tuscaloosa-al": ("Tuscaloosa, AL", 33.21, -87.57), "twin-falls-id": ("Twin Falls, ID", 42.56, -114.46),
    "tyler-longview-tx": ("Tyler, TX", 32.35, -95.30), "utica-rome-ny": ("Utica, NY", 43.10, -75.23), "victoria-tx": ("Victoria, TX", 28.81, -97.00), "waterloo-ia": ("Waterloo, IA", 42.49, -92.34),
    "wenatchee-wa": ("Wenatchee, WA", 47.42, -120.31), "wichita-falls-tx": ("Wichita Falls, TX", 33.91, -98.49), "williston-nd": ("Williston, ND", 48.15, -103.62), "yakima-wa": ("Yakima, WA", 46.60, -120.50),
}
_MW, _MH = 960, 600


def _proj(lat: float, lon: float):
    # Equirectangular with latitude scaling — good enough for a stylised map of the lower 48.
    x = (lon + 125.5) / (125.5 - 66.0) * (_MW - 80) + 40
    y = (49.8 - lat) / (49.8 - 24.4) * (_MH - 90) + 30
    return round(x, 1), round(y, 1)


def market_map(links: dict | None = None, stat: tuple[str, str] | None = None) -> str:
    """A real map of the lower 48 with one marker per market. links: slug fragment → href."""
    outline = "M" + " L".join(f"{x} {y}" for x, y in (_proj(lat, lon) for lon, lat in US_OUTLINE)) + "Z"
    dots = []
    for i, (slug, (label, lat, lon)) in enumerate(sorted(CITIES.items(), key=lambda kv: kv[1][2])):
        x, y = _proj(lat, lon)
        href = (links or {}).get(slug)
        body = (f'<circle class="ring" cx="{x}" cy="{y}" r="9" fill="none" stroke="{STEEL}" stroke-width="1.5" style="animation-delay:-{(i * 0.37) % 3.2:.1f}s"/>'
                f'<circle cx="{x}" cy="{y}" r="5.5" fill="{NAVY}" stroke="#fff" stroke-width="2"/><title>{label}</title>')
        dots.append(f'<a href="{href}" class="map-pin">{body}</a>' if href else f'<g class="map-pin">{body}</g>')
    grid = ''.join(f'<path d="M0 {y} H{_MW}" stroke="{LINE}" stroke-width="1" opacity=".6"/>' for y in range(60, _MH, 60)) + ''.join(f'<path d="M{x} 0 V{_MH}" stroke="{LINE}" stroke-width="1" opacity=".6"/>' for x in range(60, _MW, 60))
    stat_html = ""
    if stat:
        stat_html = (f'<g class="type"><rect x="{_MW-330}" y="{_MH-110}" width="300" height="78" rx="18" fill="#fff" stroke="{LINE}"/>'
                     f'<text x="{_MW-306}" y="{_MH-76}" font-size="19" font-weight="700" fill="{NAVY}" {_FONT}>{stat[0]}</text>'
                     f'<text x="{_MW-306}" y="{_MH-50}" font-size="13" fill="#6b7890" {_FONT}>{stat[1]}</text></g>')
    return (f'<svg class="mock map" viewBox="0 0 {_MW} {_MH}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Markets across the United States">'
            f'<rect width="{_MW}" height="{_MH}" rx="26" fill="#fff"/>{grid}'
            f'<path d="{outline}" fill="{PAPER2}" stroke="{MIST}" stroke-width="2" stroke-linejoin="round"/>'
            f'<path d="{outline}" fill="url(#mapfade)" opacity=".5"/>'
            f'<defs><linearGradient id="mapfade" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{SKY}" stop-opacity=".18"/><stop offset="1" stop-color="{SKY}" stop-opacity="0"/></linearGradient></defs>'
            f'{"".join(dots)}{stat_html}</svg>')
