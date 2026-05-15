#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ascii_pipeline.diagnostics import diagnose_path, load_frames_from_path
from ascii_pipeline.preview import FONT_CANDIDATES
from ascii_pipeline.video_modes import build_eikon_from_frames

SOURCE = Path(__file__).resolve().parent / "source" / "cosmic-pyramid.jpg"
GENERATED = Path(__file__).resolve().parent / "generated"
FRAMES_DIR = GENERATED / "scene-eikon-frames"
PREVIEW_DIR = GENERATED / "preview-frames"
EIKON_OUT = REPO_ROOT / "examples" / "eikon" / "cosmic-pyramid-fullsize-192x96.eikon"
GIF_OUT = REPO_ROOT / "gallery" / "fullsize" / "cosmic-pyramid-animated-preview.gif"
BOARD_OUT = REPO_ROOT / "gallery" / "fullsize" / "cosmic-pyramid-animated-3frame-board.png"
SUMMARY_OUT = GENERATED / "animated-scene-summary.json"

STATE_COUNTS = {"idle": 20, "thinking": 16, "speaking": 16}
FULLSIZE_GRID = (192, 96)
COLLAPSE_GRID = "48x24"
FONT_SIZE = 10
MARGIN = 18
LINE_SPACING = 1
BG = (16, 18, 24)
FG = (235, 225, 205)


def load_font(size: int) -> ImageFont.ImageFont:
    for candidate in FONT_CANDIDATES:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def render_lines_to_image(lines: Iterable[str], font: ImageFont.ImageFont) -> Image.Image:
    rendered = [str(line) for line in lines]
    width = max((len(line) for line in rendered), default=1)
    normalized = [line.ljust(width) for line in rendered] or [""]
    bbox = font.getbbox("M")
    char_width = max(1, bbox[2] - bbox[0])
    try:
        ascent, descent = font.getmetrics()
        char_height = max(1, ascent + descent)
    except AttributeError:
        char_height = max(1, bbox[3] - bbox[1])
    image_width = MARGIN * 2 + char_width * width
    image_height = MARGIN * 2 + len(normalized) * (char_height + LINE_SPACING)
    canvas = Image.new("RGB", (image_width, image_height), BG)
    draw = ImageDraw.Draw(canvas)
    for row, line in enumerate(normalized):
        draw.text((MARGIN, MARGIN + row * (char_height + LINE_SPACING)), line, fill=FG, font=font)
    return canvas


def build_board(items: list[tuple[str, Path]], out_path: Path) -> Path:
    opened = [(label, Image.open(path).convert("RGB")) for label, path in items]
    title_font = load_font(28)
    label_font = load_font(18)
    margin = 28
    gutter = 18
    label_h = 34
    title_h = 50
    swatch_h = 10
    accents = [(90, 180, 255), (255, 110, 110), (240, 200, 90), (140, 220, 160)]

    max_h = max(image.height for _, image in opened)
    total_w = margin * 2 + sum(image.width for _, image in opened) + gutter * (len(opened) - 1)
    total_h = margin * 2 + title_h + label_h + swatch_h + max_h
    canvas = Image.new("RGB", (total_w, total_h), (14, 16, 22))
    draw = ImageDraw.Draw(canvas)
    draw.text((margin, margin), "ASCII Art Pipeline — animated scene eikon", fill=(244, 235, 214), font=title_font)

    x = margin
    y = margin + title_h + label_h + swatch_h
    for idx, (label, image) in enumerate(opened):
        accent = accents[idx % len(accents)]
        draw.rectangle((x, margin + title_h + 8, x + image.width, margin + title_h + 8 + swatch_h), fill=accent)
        draw.text((x, margin + title_h + 18), label, fill=(230, 222, 205), font=label_font)
        canvas.paste(image, (x, y))
        x += image.width + gutter

    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path)
    return out_path


def crop_zoom(im: Image.Image, scale: float, dx: float = 0.0, dy: float = 0.0) -> Image.Image:
    width, height = im.size
    crop_w = max(1, int(width / scale))
    crop_h = max(1, int(height / scale))
    center_x = width / 2 + dx * width
    center_y = height / 2 + dy * height
    left = int(round(center_x - crop_w / 2))
    top = int(round(center_y - crop_h / 2))
    left = max(0, min(width - crop_w, left))
    top = max(0, min(height - crop_h, top))
    return im.crop((left, top, left + crop_w, top + crop_h)).resize((width, height), Image.LANCZOS)


def radial_overlay(size: tuple[int, int], center: tuple[int, int], radius: int, alpha: int, color=(255, 255, 240)) -> Image.Image:
    width, height = size
    mask = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius), fill=max(0, min(255, int(alpha))))
    mask = mask.filter(ImageFilter.GaussianBlur(radius=max(1, int(radius * 0.4))))
    overlay = Image.new("RGB", (width, height), color)
    out = Image.new("RGB", (width, height))
    out.paste(overlay, (0, 0), mask)
    return out


def cross_flare(draw: ImageDraw.ImageDraw, center: tuple[int, int], arm: int, brightness: int) -> None:
    x, y = center
    fill = (brightness, brightness, min(255, brightness))
    draw.line((x - arm, y, x + arm, y), fill=fill, width=1)
    draw.line((x, y - arm, x, y + arm), fill=fill, width=1)
    half = max(1, arm // 2)
    draw.line((x - half, y - half, x + half, y + half), fill=fill, width=1)
    draw.line((x - half, y + half, x + half, y - half), fill=fill, width=1)


def build_frame(base: Image.Image, global_t: float, state: str, state_t: float) -> Image.Image:
    width, height = base.size
    star = (int(width * 0.50), int(height * 0.31))
    nebula = (int(width * 0.56), int(height * 0.17))
    figure = (int(width * 0.31), int(height * 0.59))
    twinkle_points = [
        (int(width * x), int(height * y), r)
        for x, y, r in [
            (0.14, 0.09, 1), (0.24, 0.16, 1), (0.29, 0.07, 1), (0.40, 0.11, 1), (0.67, 0.08, 1),
            (0.79, 0.15, 1), (0.72, 0.24, 1), (0.12, 0.22, 1), (0.18, 0.31, 1), (0.83, 0.27, 1),
            (0.90, 0.18, 1), (0.61, 0.05, 1), (0.51, 0.09, 1), (0.36, 0.18, 1), (0.44, 0.21, 1),
        ]
    ]

    if state == "idle":
        zoom = 1.022 + 0.012 * math.sin(2 * math.pi * global_t)
        dx = 0.004 * math.sin(2 * math.pi * global_t)
        dy = -0.010 + 0.005 * math.cos(2 * math.pi * global_t)
        nebula_alpha = 42 + 24 * (0.5 + 0.5 * math.sin(2 * math.pi * global_t))
        flare_arm = 5 + int(2 * (0.5 + 0.5 * math.sin(2 * math.pi * global_t)))
        flare_brightness = 235
        contrast = 1.04
        brightness = 1.02
    elif state == "thinking":
        zoom = 1.030 + 0.018 * math.sin(2 * math.pi * state_t)
        dx = 0.006 * math.sin(2 * math.pi * state_t)
        dy = -0.015 + 0.006 * math.cos(2 * math.pi * state_t)
        nebula_alpha = 58 + 32 * (0.5 + 0.5 * math.sin(4 * math.pi * state_t))
        flare_arm = 6 + int(3 * (0.5 + 0.5 * math.sin(4 * math.pi * state_t)))
        flare_brightness = 248
        contrast = 1.08
        brightness = 1.035
    else:
        zoom = 1.040 + 0.020 * math.sin(2 * math.pi * state_t)
        dx = 0.008 * math.sin(2 * math.pi * state_t)
        dy = -0.018 + 0.008 * math.cos(2 * math.pi * state_t)
        nebula_alpha = 68 + 38 * (0.5 + 0.5 * math.sin(4 * math.pi * state_t + math.pi / 4))
        flare_arm = 7 + int(4 * (0.5 + 0.5 * math.sin(4 * math.pi * state_t + math.pi / 3)))
        flare_brightness = 255
        contrast = 1.12
        brightness = 1.045

    frame = crop_zoom(base, zoom, dx=dx, dy=dy)
    overlay = radial_overlay(frame.size, nebula, radius=int(width * 0.12), alpha=int(nebula_alpha), color=(255, 255, 245))
    frame = Image.blend(frame, overlay, alpha=0.13)
    frame = ImageEnhance.Contrast(frame).enhance(contrast)
    frame = ImageEnhance.Brightness(frame).enhance(brightness)
    frame = frame.filter(ImageFilter.UnsharpMask(radius=1.5, percent=110, threshold=2))
    draw = ImageDraw.Draw(frame)
    cross_flare(draw, star, flare_arm, flare_brightness)
    glint = 18 + int(14 * (0.5 + 0.5 * math.sin(2 * math.pi * state_t + math.pi / 5)))
    draw.ellipse((figure[0] - 10, figure[1] - 7, figure[0] + 10, figure[1] + 7), outline=(90 + glint, 110 + glint, 120 + glint), width=1)
    for idx, (sx, sy, radius) in enumerate(twinkle_points):
        phase = 2 * math.pi * ((idx % 7) / 7)
        amp = 0.5 + 0.5 * math.sin(2 * math.pi * global_t * 1.7 + phase)
        if amp > 0.72:
            bright = 210 + int(45 * amp)
            draw.ellipse((sx - radius, sy - radius, sx + radius, sy + radius), fill=(bright, bright, bright))
    return frame


def main() -> None:
    source = Image.open(SOURCE).convert("RGB")
    FRAMES_DIR.mkdir(parents=True, exist_ok=True)
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    GENERATED.mkdir(parents=True, exist_ok=True)

    for path in FRAMES_DIR.glob("*.png"):
        path.unlink()
    for path in PREVIEW_DIR.glob("*.png"):
        path.unlink()

    total_frames = sum(STATE_COUNTS.values())
    frame_counter = 1
    for state, count in STATE_COUNTS.items():
        for state_index in range(count):
            global_t = (frame_counter - 1) / max(1, total_frames - 1)
            state_t = state_index / max(1, count - 1)
            frame = build_frame(source, global_t, state, state_t)
            out = FRAMES_DIR / f"{state}_frame_{frame_counter:04d}.png"
            frame.save(out)
            frame_counter += 1

    result = build_eikon_from_frames(
        FRAMES_DIR,
        EIKON_OUT,
        grid=f"{FULLSIZE_GRID[0]}x{FULLSIZE_GRID[1]}",
        charset="dense-ref",
        collapse_to=COLLAPSE_GRID,
        eikon_id="cosmic-pyramid-fullsize-192x96",
    )

    full_diag = diagnose_path(EIKON_OUT, expected_width=FULLSIZE_GRID[0], expected_height=FULLSIZE_GRID[1])
    collapse_diag = diagnose_path(result["collapse_eikon"], expected_width=48, expected_height=24)
    frames = load_frames_from_path(EIKON_OUT)
    font = load_font(FONT_SIZE)
    rendered = []
    for frame in frames:
        img = render_lines_to_image(frame.lines, font)
        rendered.append(img)
    GIF_OUT.parent.mkdir(parents=True, exist_ok=True)
    rendered[0].save(
        GIF_OUT,
        save_all=True,
        append_images=rendered[1:],
        duration=90,
        loop=0,
        optimize=False,
        disposal=2,
    )

    key_frames = [(0, "idle-0"), (26, "thinking-26"), (44, "speaking-44")]
    board_inputs: list[tuple[str, Path]] = []
    for frame_index, label in key_frames:
        image_path = PREVIEW_DIR / f"{label}.png"
        render_lines_to_image(frames[frame_index].lines, font).save(image_path)
        board_inputs.append((label, image_path))
    build_board(board_inputs, BOARD_OUT)

    summary = {
        "source": str(SOURCE),
        "frames_dir": str(FRAMES_DIR),
        "full_size_eikon": result["full_size_eikon"],
        "collapse_eikon": result["collapse_eikon"],
        "preview_gif": str(GIF_OUT),
        "preview_board": str(BOARD_OUT),
        "diagnostics": {
            "full_size": full_diag,
            "collapsed": collapse_diag,
        },
    }
    SUMMARY_OUT.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
