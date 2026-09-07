"""Real map of the contiguous United States (state boundaries from GeoJSON, Albers equal-area
projection) with a linked marker for every market. Used by build/illustrations.market_map."""
from __future__ import annotations

import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
NAVY, STEEL, SKY, MIST, PAPER2, LINE = "#0b1f3f", "#2a5a9c", "#4f86c6", "#8a9bbb", "#eceef4", "#dfe4ee"
_FONT = 'font-family="-apple-system,BlinkMacSystemFont,Inter,Helvetica,Arial,sans-serif"'
W, H = 960, 600
SKIP = {"Alaska", "Hawaii", "Puerto Rico"}

# Albers equal-area conic, standard parallels 29.5° / 45.5°, centred on 96°W (the usual US projection)
_p1, _p2, _lon0, _lat0 = math.radians(29.5), math.radians(45.5), math.radians(-96), math.radians(38)
_n = (math.sin(_p1) + math.sin(_p2)) / 2
_C = math.cos(_p1) ** 2 + 2 * _n * math.sin(_p1)
_rho0 = math.sqrt(_C - 2 * _n * math.sin(_lat0)) / _n


def _albers(lon: float, lat: float):
    lam, phi = math.radians(lon), math.radians(lat)
    rho = math.sqrt(_C - 2 * _n * math.sin(phi)) / _n
    th = _n * (lam - _lon0)
    return rho * math.sin(th), _rho0 - rho * math.cos(th)


_states = None
_bbox = None


def _load():
    global _states, _bbox
    if _states is not None:
        return
    g = json.load(open(os.path.join(HERE, "data", "us-states.json"), encoding="utf-8"))
    _states = []
    xs, ys = [], []
    for f in g["features"]:
        name = f["properties"].get("name", "")
        if name in SKIP:
            continue
        geom = f["geometry"]
        polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
        rings = []
        for poly in polys:
            for ring in poly:
                pts = [_albers(lon, lat) for lon, lat in ring]
                rings.append(pts)
                xs.extend(p[0] for p in pts); ys.extend(p[1] for p in pts)
        _states.append((name, rings))
    _bbox = (min(xs), min(ys), max(xs), max(ys))


def _fit():
    x0, y0, x1, y1 = _bbox
    pad = 28
    s = min((W - 2 * pad) / (x1 - x0), (H - 2 * pad) / (y1 - y0))
    ox = (W - (x1 - x0) * s) / 2 - x0 * s
    oy = (H - (y1 - y0) * s) / 2 - y0 * s
    return lambda p: (round(p[0] * s + ox, 1), round(H - (p[1] * s + oy) + 0, 1))


def project(lat: float, lon: float):
    _load()
    fit = _fit()
    x, y = fit(_albers(lon, lat))
    return x, y


def svg(markers: list[tuple[str, float, float, str]], stat: tuple[str, str] | None = None) -> str:
    """markers: (label, lat, lon, href). Returns a complete SVG."""
    _load()
    fit = _fit()
    paths = []
    for name, rings in _states:
        d = ""
        for ring in rings:
            pts = [fit(p) for p in ring]
            d += "M" + " L".join(f"{x} {y}" for x, y in pts) + "Z"
        paths.append(f'<path d="{d}" fill="{PAPER2}" stroke="#fff" stroke-width="1.6" stroke-linejoin="round"><title>{name}</title></path>')
    outline = "".join(paths)
    pins = []
    for i, (label, lat, lon, href) in enumerate(sorted(markers, key=lambda m: m[2])):
        x, y = fit(_albers(lon, lat))
        body = (f'<circle class="ring" cx="{x}" cy="{y}" r="10" fill="none" stroke="{STEEL}" stroke-width="1.5" style="animation-delay:-{(i * 0.37) % 3.2:.1f}s"/>'
                f'<circle cx="{x}" cy="{y}" r="5.5" fill="{NAVY}" stroke="#fff" stroke-width="2"/><title>{label}</title>')
        pins.append(f'<a href="{href}" class="map-pin">{body}</a>' if href else f'<g class="map-pin">{body}</g>')
    stat_html = ""
    if stat:
        stat_html = (f'<g class="type"><rect x="{W-320}" y="{H-104}" width="292" height="76" rx="18" fill="#fff" stroke="{LINE}"/>'
                     f'<text x="{W-298}" y="{H-72}" font-size="18" font-weight="700" fill="{NAVY}" {_FONT}>{stat[0]}</text>'
                     f'<text x="{W-298}" y="{H-47}" font-size="12.5" fill="#6b7890" {_FONT}>{stat[1]}</text></g>')
    return (f'<svg class="mock map" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Markets across the United States">'
            f'<defs><filter id="mapshadow" x="-5%" y="-5%" width="110%" height="115%"><feDropShadow dx="0" dy="6" stdDeviation="8" flood-color="{NAVY}" flood-opacity=".12"/></filter></defs>'
            f'<rect width="{W}" height="{H}" rx="26" fill="#fff"/>'
            f'<g filter="url(#mapshadow)">{outline}</g>{"".join(pins)}{stat_html}</svg>')
