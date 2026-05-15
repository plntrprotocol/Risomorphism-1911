from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps

from .diagnostics import diagnose_path
from .eikon import ASCII_IMAGE_CONVERTER, normalize_lines
from . import downsampling
from .presets import PRESETS, Preset
from .preview import render_lines_to_image


class RenderImageError(RuntimeError):
    pass


def _apply_preprocess(
    image: Image.Image,
    preset: Preset,
    *,
    source_scale_override: tuple[int, int] | None = None,
) -> Image.Image:
    working = image.convert("L") if "grayscale" in preset.preprocess else image.convert("RGB")
    if "autocontrast" in preset.preprocess:
        working = ImageOps.autocontrast(working)
    if "equalize" in preset.preprocess:
        working = ImageOps.equalize(working)
    if "contrast+10%" in preset.preprocess:
        working = ImageEnhance.Contrast(working).enhance(1.10)
    target_scale = source_scale_override if source_scale_override else preset.source_scale
    if target_scale:
        working = working.resize(target_scale, Image.LANCZOS)
    return working.convert("RGB")


def _run_converter(image_path: Path, args: list[str]) -> list[str]:
    if not ASCII_IMAGE_CONVERTER.exists():
        raise FileNotFoundError(f"{ASCII_IMAGE_CONVERTER} not found")
    cmd = [str(ASCII_IMAGE_CONVERTER), str(image_path), *args]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RenderImageError(proc.stderr.strip() or proc.stdout.strip() or f"converter failed: {' '.join(cmd)}")
    return proc.stdout.splitlines()


def _render_with_preset(
    image_path: Path,
    preset: Preset,
    *,
    force_grid: tuple[int, int] | None = None,
    force_intermediate: tuple[int, int] | None = None,
) -> list[str]:
    target_width, target_height = force_grid if force_grid else preset.target
    if preset.braille:
        lines = _run_converter(image_path, ["-d", f"{target_width},{target_height}", "-b", "--dither"])
        return normalize_lines(lines, target_width, target_height)

    charset = preset.charset
    if not charset:
        raise RenderImageError(f"Preset {preset.name} is missing charset")

    interm_width, interm_height = (
        force_intermediate if force_intermediate else preset.intermediate_grid
    ) if preset.intermediate_grid else (None, None)

    if preset.intermediate_grid:
        # Use (possibly overridden) intermediate grid
        lines = _run_converter(image_path, ["-d", f"{interm_width},{interm_height}", "-m", charset])
        normalized = normalize_lines(lines, interm_width, interm_height)
        # Select downsampling method based on preset
        method = getattr(preset, "downsample", "majority")
        factor_y = interm_height // target_height
        factor_x = interm_width // target_width
        if factor_x != factor_y:
            raise ValueError(f"Non-square block factors not supported: fx={factor_x}, fy={factor_y}")
        if method == "edge-aware":
            return downsampling.edge_aware_downsample(normalized, factor_y)
        elif method == "clahe":
            return downsampling.clahe_downsample(normalized, factor_y)
        else:  # majority
            return downsampling.majority_vote(normalized, factor_y)

    lines = _run_converter(image_path, ["-d", f"{target_width},{target_height}", "-m", charset])
    return normalize_lines(lines, target_width, target_height)


def render_image(
    input_path: str | Path,
    out_path: str | Path,
    *,
    preset_name: str = "stroke-clarity",
    preview_out: str | Path | None = None,
    diagnostics_out: str | Path | None = None,
    scale: int = 1,
) -> dict[str, object]:
    if preset_name not in PRESETS:
        raise KeyError(f"Unknown preset: {preset_name}")

    if scale < 1:
        raise ValueError(f"Scale must be >= 1, got {scale}")
    if scale > 16:
        raise ValueError(f"Scale capped at 16 for performance; got {scale}")

    preset = PRESETS[preset_name]
    source = Path(input_path)
    if not source.exists():
        raise FileNotFoundError(source)

    # Compute scaled dimensions
    base_w, base_h = preset.target
    target_grid = (base_w * scale, base_h * scale)

    # Intermediate grid (if preset defines one) scales identically
    force_intermediate: tuple[int, int] | None = None
    if preset.intermediate_grid:
        interm_w, interm_h = preset.intermediate_grid
        force_intermediate = (interm_w * scale, interm_h * scale)

    # Source-scale override: scale preset.source_scale the same way to maintain pixel coverage
    source_scale_override: tuple[int, int] | None = None
    if preset.source_scale:
        src_w, src_h = preset.source_scale
        source_scale_override = (src_w * scale, src_h * scale)

    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        preprocessed = tmpdir / "preprocessed.png"
        image = Image.open(source)
        _apply_preprocess(image, preset, source_scale_override=source_scale_override).save(preprocessed)
        lines = _render_with_preset(
            preprocessed,
            preset,
            force_grid=target_grid,
            force_intermediate=force_intermediate,
        )

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")

    preview_path: str | None = None
    if preview_out:
        preview = render_lines_to_image(lines, preview_out, font_size=preset.preview_font_size)
        preview_path = str(preview)

    diagnostics = diagnose_path(out, expected_width=target_grid[0], expected_height=target_grid[1])
    if diagnostics_out:
        diag_path = Path(diagnostics_out)
        diag_path.parent.mkdir(parents=True, exist_ok=True)
        diag_path.write_text(json.dumps(diagnostics, indent=2), encoding="utf-8")

    return {
        "input": str(source),
        "preset": preset.name,
        "output": str(out),
        "preview": preview_path,
        "diagnostics": diagnostics,
    }
