"""Assemble the self-contained deliverable from the Adastra design system source.

Reads page.template.html and inlines:
  {{FONT:<file>}}      -> base64 woff/ttf data URI from ds/assets/fonts/
  {{ICON:<name>}}      -> inline <svg> from ds/uploads/icon-map.js (fill=currentColor)
  {{LOGO}}             -> the red basic wordmark, inlined as <svg>

Design-system rule: colour is never set on the icon; it inherits via currentColor.
"""
import base64
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).parent
DS = ROOT / "ds"

# ── icons ────────────────────────────────────────────────────────────
ICON_SRC = (DS / "uploads" / "icon-map.js").read_text(encoding="utf-8")
ENTRY_RE = re.compile(r'^  "([a-z0-9-]+)":(\{.*?\}),?$', re.M | re.S)


def load_icons():
    out = {}
    for name, blob in ENTRY_RE.findall(ICON_SRC):
        out[name] = json.loads(blob)
    return out


ICONS = load_icons()


def icon_svg(name):
    if name not in ICONS:
        sys.exit(f"unknown icon: {name}")
    e = ICONS[name]
    return (
        f'<svg class="ico" viewBox="{e["viewBox"]}" fill="currentColor" '
        f'aria-hidden="true" focusable="false">{e["svg"]}</svg>'
    )


# ── fonts ────────────────────────────────────────────────────────────
def font_uri(fname):
    p = DS / "assets" / "fonts" / "figtree" / fname
    b64 = base64.b64encode(p.read_bytes()).decode("ascii")
    return f"data:font/ttf;base64,{b64}"


# ── images (downloaded client logos/photos + bundled stock images) ────
IMG_DIRS = [ROOT / "web-assets", DS / "assets" / "stock-images"]
MIME = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".svg": "image/svg+xml"}


def img_uri(fname):
    for d in IMG_DIRS:
        p = d / fname
        if p.exists():
            mime = MIME[p.suffix.lower()]
            b64 = base64.b64encode(p.read_bytes()).decode("ascii")
            return f"data:{mime};base64,{b64}"
    sys.exit(f"image not found in {IMG_DIRS}: {fname}")


# ── logo ─────────────────────────────────────────────────────────────
def logo_svg():
    raw = (DS / "assets" / "logos" / "adastra_logo_basic_red_RGB.svg").read_text(
        encoding="utf-8"
    )
    body = re.search(r"<g>.*</g>", raw, re.S).group(0)
    body = re.sub(r'\s(id|class)="[^"]*"', "", body)
    body = body.replace("&#x9;", "").replace("&#xA;", " ")
    body = re.sub(r'fill="#F9423A"', 'fill="currentColor"', body)
    return (
        '<svg class="logo" viewBox="0 0 231.1 73.4" fill="currentColor" '
        'role="img" aria-label="Adastra">' + body + "</svg>"
    )


# ── assemble ─────────────────────────────────────────────────────────
def main():
    html = (ROOT / "page.template.html").read_text(encoding="utf-8")
    html = re.sub(r"\{\{ICON:([a-z0-9-]+)\}\}", lambda m: icon_svg(m.group(1)), html)
    html = re.sub(r"\{\{FONT:([\w.-]+)\}\}", lambda m: font_uri(m.group(1)), html)
    html = re.sub(r"\{\{IMG:([\w.-]+)\}\}", lambda m: img_uri(m.group(1)), html)
    html = html.replace("{{LOGO}}", logo_svg())
    leftover = re.findall(r"\{\{[^}]+\}\}", html)
    if leftover:
        sys.exit(f"unresolved placeholders: {sorted(set(leftover))}")
    out = ROOT / "adastra-ai-powered-bank.html"
    out.write_text(html, encoding="utf-8")
    print(f"wrote {out.name} — {out.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
