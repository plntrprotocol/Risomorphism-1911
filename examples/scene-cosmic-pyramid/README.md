# Cosmic Pyramid Full-Size Scene Example

Source image:
- `source/cosmic-pyramid.jpg`

This example tests a square, high-contrast illustration with:
- strong geometric architecture (pyramid + staircase)
- a small robed human figure
- dense stippled cosmic sky / nebula texture
- a bright focal star at the apex

## Why this example matters

It expands the showcase beyond portraits and avatars.

This scene stresses a different part of the pipeline:
- sharp perspective lines
- small foreground figure readability
- atmospheric, punctuated sky texture
- large dark-field / bright-structure contrast

## Still-image commands used

### Full-size dense reference
```bash
/Users/johann/go/bin/ascii-image-converter source/cosmic-pyramid.jpg \
  -d 192,96 \
  -m '@$#MHAGXS532;:,. ' \
  --save-txt dense-ref-192x96 \
  --save-img dense-ref-192x96 \
  --only-save
```

### Full-size D30
```bash
/Users/johann/go/bin/ascii-image-converter source/cosmic-pyramid.jpg \
  -d 192,96 \
  -m ".,'`^\",:;Il!i><~+_-?][}{1)|/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$" \
  --save-txt d30-192x96 \
  --save-img d30-192x96 \
  --only-save
```

### Collapsed baseline
```bash
/Users/johann/go/bin/ascii-image-converter source/cosmic-pyramid.jpg \
  -d 48,24 \
  -m '@$#MHAGXS532;:,. ' \
  --save-txt dense-ref-48x24 \
  --save-img dense-ref-48x24 \
  --only-save
```

## Still-image diagnostics summary

### dense-ref 192x96
- verdict: `high-contrast`
- unique glyphs: `16`
- fill ratio: `0.9988`
- heavy ratio: `0.4422`
- light ratio: `0.1764`

### d30 192x96
- verdict: `low-contrast-garble-risk`
- unique glyphs: `67`
- fill ratio: `1.0`
- heavy ratio: `0.0406`
- light ratio: `0.3038`

### dense-ref 48x24
- verdict: `high-contrast`
- unique glyphs: `16`
- fill ratio: `1.0`
- heavy ratio: `0.4340`
- light ratio: `0.1649`

## Important still-image finding

This example shows that **portrait-derived metrics are not the whole story**.

- The `dense-ref 192x96` render is the strongest tactile / engraved full-size artifact.
- The `d30 192x96` render preserves more atmospheric linework and sky drama visually, even though the current portrait-centric diagnostic heuristic flags it as risky.
- The `48x24` version works as a collapsed derivative, but loses too much of the cosmic scene's atmosphere to be the canonical showcase artifact.

### First-class `render-image` CLI expansion

The published still-image path now avoids `chafa` entirely.

Use the repo CLI instead of raw converter invocations when you want a reproducible public preset render:

```bash
python3 -m ascii_pipeline.cli render-image \
  --input examples/scene-cosmic-pyramid/source/cosmic-pyramid.jpg \
  --preset stroke-clarity \
  --out examples/scene-cosmic-pyramid/preset-renders/stroke-clarity.txt \
  --preview-out examples/scene-cosmic-pyramid/preset-renders/stroke-clarity.png \
  --diagnostics-out examples/scene-cosmic-pyramid/preset-renders/stroke-clarity.json
```

Also generated:

```bash
python3 -m ascii_pipeline.cli render-image --input examples/scene-cosmic-pyramid/source/cosmic-pyramid.jpg --preset d30-dense --out examples/scene-cosmic-pyramid/preset-renders/d30-dense.txt --preview-out examples/scene-cosmic-pyramid/preset-renders/d30-dense.png --diagnostics-out examples/scene-cosmic-pyramid/preset-renders/d30-dense.json
python3 -m ascii_pipeline.cli render-image --input examples/scene-cosmic-pyramid/source/cosmic-pyramid.jpg --preset braille-detail --out examples/scene-cosmic-pyramid/preset-renders/braille-detail.txt --preview-out examples/scene-cosmic-pyramid/preset-renders/braille-detail.png --diagnostics-out examples/scene-cosmic-pyramid/preset-renders/braille-detail.json
```

For showcase-tier full-size outputs (192×96 dense-field), add `--fullsize` (equivalent to `--scale 4`):

```bash
python3 -m ascii_pipeline.cli render-image \
  --input examples/scene-cosmic-pyramid/source/cosmic-pyramid.jpg \
  --preset stroke-clarity \
  --fullsize \
  --out examples/scene-cosmic-pyramid/preset-renders/fullsize-stroke-clarity.txt \
  --preview-out examples/scene-cosmic-pyramid/preset-renders/fullsize-stroke-clarity.png \
  --diagnostics-out examples/scene-cosmic-pyramid/preset-renders/fullsize-stroke-clarity.json
```

Higher resolutions are available via `--scale N` (where base grid is 48×24). For example, `--scale 8` yields a 384×192 grid, and `--scale 16` yields 768×384:

```bash
# High-resolution showcase: stroke-clarity (direct path — safe up to scale 16)
python3 -m ascii_pipeline.cli render-image \
  --input examples/scene-cosmic-pyramid/source/cosmic-pyramid.jpg \
  --preset stroke-clarity \
  --scale 8 \
  --out examples/scene-cosmic-pyramid/preset-renders/scale8-stroke-clarity.txt \
  --preview-out examples/scene-cosmic-pyramid/preset-renders/scale8-stroke-clarity.png

python3 -m ascii_pipeline.cli render-image \
  --input examples/scene-cosmic-pyramid/source/cosmic-pyramid.jpg \
  --preset stroke-clarity \
  --scale 16 \
  --out examples/scene-cosmic-pyramid/preset-renders/scale16-stroke-clarity.txt \
  --preview-out examples/scene-cosmic-pyramid/preset-renders/scale16-stroke-clarity.png

# D30 dense variant (block-mode — recommended scale ≤ 8)
python3 -m ascii_pipeline.cli render-image \
  --input examples/scene-cosmic-pyramid/source/cosmic-pyramid.jpg \
  --preset d30-dense \
  --scale 8 \
  --out examples/scene-cosmic-pyramid/preset-renders/scale8-d30-dense.txt \
  --preview-out examples/scene-cosmic-pyramid/preset-renders/scale8-d30-dense.png
```

**Performance note:** `d30-dense` uses an intermediate block downsampling step; at `--scale 8` the intermediate grid becomes 3072×1536 which is resource-intensive but manageable; at `--scale 16` it becomes 6144×3072 and may exceed practical limits. Prefer `stroke-clarity` for very high-resolution showcase work.

Preset outputs:
- `preset-renders/stroke-clarity.txt`
- `preset-renders/stroke-clarity.png`
- `preset-renders/stroke-clarity.json`
- `preset-renders/d30-dense.txt`
- `preset-renders/d30-dense.png`
- `preset-renders/d30-dense.json`
- `preset-renders/braille-detail.txt`
- `preset-renders/braille-detail.png`
- `preset-renders/braille-detail.json`
- comparison board:
  - `preset-renders/preset-board.png`

### Preset verdicts on this source

#### `stroke-clarity`
- verdict: `high-contrast`
- best role: **published default**
- why: the pyramid silhouette reads immediately and the preview is robust

#### `d30-dense`
- verdict: `low-contrast-garble-risk`
- best role: optional atmospheric / texture-forward mode
- why: it carries more glyph variety, but on this source it is not the safest default

#### `braille-detail`
- verdict: `braille-dominant`
- best role: detail mode when Unicode Braille rendering is acceptable
- caveat: terminal/font support matters; preview PNGs avoid that ambiguity

## Animated scene expansion

This example now includes a **slow animated scene eikon** synthesized from the still image.

The animation is intentionally subtle:
- slight breathing zoom / drift
- pulsing apex star flare
- nebula glow breathing
- sparse star-field twinkle
- tiny figure-area glint so the human anchor survives in motion

### Build command

From repo root:

```bash
python3 examples/scene-cosmic-pyramid/build_animated_scene.py
```

### Generated animated outputs

- Full-size eikon:
  - `../eikon/cosmic-pyramid-fullsize-192x96.eikon`
- Collapsed derivative:
  - `../eikon/cosmic-pyramid-fullsize-192x96-48x24.eikon`
- Generated motion source frames:
  - `generated/scene-eikon-frames/`
- Rendered preview frames:
  - `generated/preview-frames/`
- Animated preview GIF:
  - `../../gallery/fullsize/cosmic-pyramid-animated-preview.gif`
- Three-frame motion board:
  - `../../gallery/fullsize/cosmic-pyramid-animated-3frame-board.png`
- Build/diagnostics summary:
  - `generated/animated-scene-summary.json`

## Animated diagnostics summary

### Full-size animated eikon (`192x96`)
- frames: `52`
- state counts: `idle 20`, `thinking 16`, `speaking 16`
- verdict: `high-contrast`
- unique glyphs mean: `16.0`
- heavy ratio mean: `0.4711`
- light ratio mean: `0.1189`
- motion char diff mean: `0.2754`
- motion char diff max: `0.5124`

### Collapsed animated derivative (`48x24`)
- frames: `52`
- verdict: `high-contrast`
- unique glyphs mean: `15.54`
- heavy ratio mean: `0.4850`
- light ratio mean: `0.1361`
- motion char diff mean: `0.2362`
- motion char diff max: `0.3889`

## Animated showcase verdict

The motion path works.

- The scene stays recognizable as a cosmic pyramid instead of collapsing into glyph churn.
- The strongest changes occur in the atmospheric field and interior texture rather than destroying the silhouette.
- The full-size animated eikon is the canonical master.
- The `48x24` animated version is a deployment-sized derivative, not the showcase artifact.

## Recommended showcase assets

Still:
- `dense-ref-192x96/cosmic-pyramid-ascii-art.png`
- `d30-192x96/cosmic-pyramid-ascii-art.png`
- `../../gallery/fullsize/cosmic-pyramid-board.png`

Motion:
- `../../gallery/fullsize/cosmic-pyramid-animated-preview.gif`
- `../../gallery/fullsize/cosmic-pyramid-animated-3frame-board.png`
- `../eikon/cosmic-pyramid-fullsize-192x96.eikon`

Interpretation:
- `dense-ref 192x96` = strongest dense tactile poster artifact
- `d30 192x96` = strongest atmospheric linework variant
- animated `192x96` eikon = strongest full-size scene-motion showcase
- `48x24` still/animated variants = deployment-sized fallbacks, not the masters
