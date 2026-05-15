# Portrait example — D34 alchemist-robe.observatory

Square (1:1) character portrait rendered at multiple quality tiers.

Source: `D34-alchemist-robe.observatory.png` (1024×1024) from the hooded-ouroboros-collection. Square composition, centered figure with textured robe detail.

## Renders

| Preset | Scale | Grid | Verdict |
|--------|-------|------|---------|
| stroke-clarity | 1× | 48×24 | high-contrast |
| stroke-clarity | 4× | 192×96 | high-contrast |
| d30-dense | 1× | 48×24 | portrait-suited |
| d30-dense | 4× | 192×96 | portrait-suited |
| braille-detail | 1× | 48×24 | braille-dominant |

All artifacts in `preset-renders/`:
- `.txt` — raw ASCII grid
- `.png` — preview render (Menlo 18pt)
- `.json` — quality diagnostics

## Usage

```bash
# Base resolution
ascii-pipeline render-image \
  --input D34-alchemist-robe.observatory.png \
  --out stroke-clarity.txt \
  --preset stroke-clarity

# Full-size showcase
ascii-pipeline render-image \
  --input D34-alchemist-robe.observatory.png \
  --out stroke-clarity.txt \
  --preset stroke-clarity \
  --fullsize
```

## When to use

- **stroke-clarity** — clean silhouette, maximal readability; ideal for quick previews and clear character outlines.
- **d30-dense** — varied stroke weight, cyber-noir density; excels on portrait compositions with subtle gradients and textured surfaces.
- **braille-detail** — 4× spot density through Braille blocks; best for fine detail when glyph count is secondary.
