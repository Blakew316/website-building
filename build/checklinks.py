#!/usr/bin/env python3
"""Verify every internal link/asset reference in the generated site resolves to a file."""
import os, re, sys
from collections import Counter
from urllib.parse import urlparse, unquote

root = sys.argv[1] if len(sys.argv) > 1 else "site"
href_rx = re.compile(r'(?:href|src)="([^"]+)"')
missing = Counter(); pages = 0; links = 0
for dp, _, files in os.walk(root):
    for f in files:
        if not f.endswith(".html"):
            continue
        pages += 1
        html = open(os.path.join(dp, f), encoding="utf-8").read()
        for h in href_rx.findall(html):
            if not h.startswith("/") or h.startswith("//"):
                continue
            links += 1
            p = unquote(urlparse(h).path)
            if p.endswith("/"):
                target = os.path.join(root, p.strip("/"), "index.html") if p != "/" else os.path.join(root, "index.html")
            else:
                target = os.path.join(root, p.lstrip("/"))
            if not os.path.exists(target):
                missing[p] += 1
print(f"pages={pages} internal_refs={links} missing_targets={len(missing)}")
for p, n in missing.most_common(40):
    print(f"  {n:5d}  {p}")
