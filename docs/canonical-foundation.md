# Canonical Foundation

## Core decisions frozen

### Canonical motion pipeline
- Source script baseline: `/Users/johann/projects/herm/scripts/generate_eikon_scratch.py`
- Canonical use case: subtle-motion portrait eikons
- Current winning settings:
  - source scale: `384x384`
  - output grid: `48x24`
  - backend: `chafa --format=symbols`
  - frame extraction: `10 fps`
  - state split: `idle/thinking/speaking`

### Canonical 52-frame Herm legacy pipeline
- Source script baseline: `/Users/johann/projects/herm/scripts/video_to_eikon.py`
- Strong for classic Herm eikons with bounded frame budgets
- Current winning settings:
  - source scale: `192x192`
  - output grid: `48x24`
  - backend: `chafa --format=symbols`
  - state counts: `20 / 16 / 16`

### Preview-render baseline
- Source helper: `/Users/johann/projects/herm/scripts/render_hires_eikons.py`
- Role: visual QA, gallery material, side-by-side comparisons

## Canonical vs experimental

### Canonical
- `generate_eikon_scratch.py` style motion pipeline
- `video_to_eikon.py` style bounded legacy Herm pipeline
- high-res preview rendering of eikon outputs
- glyph-quality diagnostics as a first-class release gate

### Experimental / archive material
- `video_derived_ascii_skill_v2` through `v8_edge`
- factor-16 / oversized-source experiments that produced unreadable outputs
- one-off comparison sheets generated only for local diagnosis

## Migration note
The new standalone repo should not inherit every historical experiment. It should inherit the winning rules, the diagnostic logic, and a small curated showcase set.
