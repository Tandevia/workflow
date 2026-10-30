#!/usr/bin/env python3
"""Generates the Tandevia Workflow marks and lockup into packages/web/public.

Needs Pillow and the macOS system fonts (Didot for the wordmark, SF for the product
name): the wordmark is never retyped in another face, so it ships as a rendered PNG
rather than as SVG text that would fall back on machines without Didot.

    python3 -m venv /tmp/brand && /tmp/brand/bin/pip install pillow
    /tmp/brand/bin/python tandevia/generate-brand.py

The Workflow mark follows the product identity system (Workspace = four blocks, one
lit; Gateway = two posts and an arrow): three blocks stepping down, joined by the
connectors a flow draws between its steps, the last one lit. On a filled ink tile,
which is what the system specifies below 16px.
"""
import pathlib
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
PUBLIC = ROOT / 'packages/web/public'
INK, VIOLET, WHITE, RULE = '#12172B', '#3A28E0', '#FFFFFF', '#C9CCD6'

# 64-unit grid, the same as the gateway's tab icons.
BLOCKS = [(7, 7), (25, 25), (43, 43)]
SIZE, RADIUS = 14, 4.5
CONNECTORS = [((21, 14), (32, 14), (32, 25)), ((39, 32), (50, 32), (50, 43))]


def mark_svg() -> str:
    blocks = [
        f'<rect x="{x}" y="{y}" width="{SIZE}" height="{SIZE}" rx="{RADIUS}" fill="{VIOLET if i == 2 else WHITE}"/>'
        for i, (x, y) in enumerate(BLOCKS)
    ]
    paths = [
        f'<path d="M{a[0]} {a[1]}H{b[0]}V{c[1]}" fill="none" stroke="{WHITE}" stroke-width="3.5" '
        'stroke-linecap="round" stroke-linejoin="round"/>'
        for a, b, c in CONNECTORS
    ]
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-label="Tandevia Workflow">\n'
        f'  <rect width="64" height="64" rx="14" fill="{INK}"/>\n  '
        + '\n  '.join(paths + blocks)
        + '\n</svg>\n'
    )


def mark_png(px: int, tile: bool = True) -> Image.Image:
    s = 8  # supersample, then downsample for clean edges
    k = px * s / 64
    img = Image.new('RGBA', (px * s, px * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if tile:
        d.rounded_rectangle([0, 0, px * s - 1, px * s - 1], radius=14 * k, fill=INK)
    w = 3.5 * k
    for a, b, c in CONNECTORS:
        pts = [(a[0] * k, a[1] * k), (b[0] * k, b[1] * k), (c[0] * k, c[1] * k)]
        d.line(pts, fill=WHITE, width=round(w), joint='curve')
        for x, y in pts:
            d.ellipse([x - w / 2, y - w / 2, x + w / 2, y + w / 2], fill=WHITE)
    for i, (x, y) in enumerate(BLOCKS):
        d.rounded_rectangle([x * k, y * k, (x + SIZE) * k, (y + SIZE) * k], radius=RADIUS * k,
                            fill=VIOLET if i == 2 else WHITE)
    return img.resize((px, px), Image.LANCZOS)


def product_font(size: int) -> ImageFont.FreeTypeFont:
    try:
        f = ImageFont.truetype('/System/Library/Fonts/SFNS.ttf', size)
        f.set_variation_by_name('Semibold')
        return f
    except Exception:
        return ImageFont.truetype('/System/Library/Fonts/HelveticaNeue.ttc', size, index=10)


def lockup(color: str, rule: str) -> Image.Image:
    """Horizontal lockup, 'Tandevia | Workflow', at 2x of the Workspace sign-in size."""
    scale = 2
    wordmark = ImageFont.truetype('/System/Library/Fonts/Supplemental/Didot.ttc', 64 * scale, index=0)
    product = product_font(26 * scale)
    gap, rule_w = 22 * scale, 1 * scale
    wb = wordmark.getbbox('Tandevia')
    pb = product.getbbox('Workflow')
    ww, wh = wb[2] - wb[0], wb[3] - wb[1]
    pw, ph = pb[2] - pb[0], pb[3] - pb[1]
    rule_h = round(ww * 0.145)
    pad = 6 * scale
    h = max(wh, rule_h, ph) + 2 * pad
    w = ww + gap + rule_w + gap + pw + 2 * pad
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    mid = h / 2
    d.text((pad - wb[0], mid - wh / 2 - wb[1]), 'Tandevia', font=wordmark, fill=color)
    x = pad + ww + gap
    d.rectangle([x, mid - rule_h / 2, x + rule_w - 1, mid + rule_h / 2], fill=rule)
    x += rule_w + gap
    d.text((x - pb[0], mid - ph / 2 - pb[1]), 'Workflow', font=product, fill=color)
    return img


def main() -> None:
    (PUBLIC / 'logo.svg').write_text(mark_svg())
    mark_png(180).save(PUBLIC / 'logo-180.png', optimize=True)
    mark_png(192).save(PUBLIC / 'logo-192.png', optimize=True)
    mark_png(256).save(PUBLIC / 'favicon.ico', sizes=[(16, 16), (32, 32), (48, 48)])
    brand = PUBLIC / 'tandevia'
    brand.mkdir(exist_ok=True)
    lockup(INK, RULE).save(brand / 'full-logo.png', optimize=True)
    lockup(WHITE, '#4A5068').save(brand / 'full-logo-dark.png', optimize=True)
    print('written to', PUBLIC)


if __name__ == '__main__':
    main()
