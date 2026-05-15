# Dense-field example — D30 ASCII complex

Wide, high-detail field rendering (asymmetric composition) across multiple presets.

Source: `D30-ascii-complex-preview.png` (3312×1864) from the hooded-ouroboros-collection. Asymmetric, stipple-dense field with high pixel count and fine texture.

## Renders

| Preset | Scale | Grid | Verdict |
|--------|-------|------|---------|
| stroke-clarity | 1× | 48×24 | high-contrast |
| stroke-clarity | 4× | 192×96 | high-contrast |
| d30-dense | 1× | 48×24 | low-contrast-garble-risk* |
| d30-dense | 4× | 192×96 | low-contrast-garble-risk* |
| braille-detail | 1× | 48×24 | braille-dominant |

*The D30-dense preset applies portrait-style heuristics even on asymmetric fields. Visually it remains strong for dense texture; the diagnostic flag reflects contrast compression from integer downsampling.

All artifacts in `preset-renders/`.

## Usage

```bash
# Dense field rendering with d30-dense at full size
ascii-pipeline render-image \
  --input D30-ascii-complex-preview.png \
  --out dense.txt \
  --preset d30-dense \
  --fullsize
```

## When to use

Dense-field rendering targets scenes with high pixel counts, stippled textures, or complex gradient fields where preserving local detail matters more than binary contrast. The `d30-dense` preset retains varied stroke weight through an expanded 68-glyph palette; expect diagnostic garble-risk flags but often visually compelling results.
