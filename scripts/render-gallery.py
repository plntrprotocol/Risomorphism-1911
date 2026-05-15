#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONT_CANDIDATES = [
    "/System/Library/Fonts/SFNS.ttf",
    "/System/Library/Fonts/Menlo.ttc",
]


def load_font(size: int):
    for candidate in FONT_CANDIDATES:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def parse_item(raw: str) -> tuple[str, Path]:
    if "=" not in raw:
        raise SystemExit(f"Item must be LABEL=path, got: {raw}")
    label, value = raw.split("=", 1)
    return label, Path(value)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    parser.add_argument("items", nargs="+", help="LABEL=path pairs")
    args = parser.parse_args()

    items = [parse_item(item) for item in args.items]
    opened = [(label, Image.open(path).convert("RGB")) for label, path in items]

    title_font = load_font(28)
    label_font = load_font(18)
    margin = 28
    gutter = 18
    label_h = 34
    title_h = 50
    swatch_h = 10

    max_h = max(image.height for _, image in opened)
    total_w = margin * 2 + sum(image.width for _, image in opened) + gutter * (len(opened) - 1)
    total_h = margin * 2 + title_h + label_h + swatch_h + max_h
    canvas = Image.new("RGB", (total_w, total_h), (14, 16, 22))
    draw = ImageDraw.Draw(canvas)

    draw.text((margin, margin), "ASCII Art Pipeline — clarity comparison", fill=(244, 235, 214), font=title_font)

    x = margin
    y = margin + title_h + label_h + swatch_h
    accents = [(90, 180, 255), (255, 110, 110), (240, 200, 90), (140, 220, 160)]
    for idx, (label, image) in enumerate(opened):
        accent = accents[idx % len(accents)]
        draw.rectangle((x, margin + title_h + 8, x + image.width, margin + title_h + 8 + swatch_h), fill=accent)
        draw.text((x, margin + title_h + 18), label, fill=(230, 222, 205), font=label_font)
        canvas.paste(image, (x, y))
        x += image.width + gutter

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out)
    print(out)


if __name__ == "__main__":
    main()
