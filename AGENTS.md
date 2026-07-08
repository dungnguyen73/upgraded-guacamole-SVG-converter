# AGENTS

## Project purpose
This repository extracts centerline SVG paths from solid black PNG icons using a pure Python implementation. The main goal is to recover the medial-axis skeleton of each shape while preserving topology and outputting stroked SVG path geometry.

## Key files
- `source/main.py` — CLI entry point for processing PNGs into SVGs.
- `source/test_compare.py` — automated comparison tests, including reference similarity and reconstruction IoU.
- `source/png_decode.py` — PNG decoder with no external libraries.
- `source/thinning.py` — binary mask creation, chamfer distance transform, contour tracing, midpoint sampling, and centerline path extraction.
- `source/skeleton_graph.py` — path deduplication, junction resolution, topology finalization, and graph cleanup.
- `source/path_fit.py` — simplification, straight-line fitting, resampling, smoothing, and axis snapping.
- `source/svg_writer.py` — SVG output writer.
- `ENGINEERING_RULE.md` — canonical implementation constraints and algorithm rules.
- `PIPELINE.md` — preferred pipeline stages and processing order.

## How to run
- Run from the `source/` directory or pass explicit input/output paths. By
	default CLI output is written to a repository-level `out/`
	folder (created automatically).

```bash
cd source
python main.py input                       # writes SVGs to ../out
python main.py input ../my-out             # write to a custom folder
python test_compare.py
python visualize.py overlay letter_H
```

From the repo root:

```bash
python source/main.py ../input
python source/test_compare.py
```

## Core conventions for AI code changes
- Follow the pipeline in `PIPELINE.md`: `PNG → binary mask → contour trace → perpendicular rays → midpoints → chain → cleanup → SVG`.
- Respect `ENGINEERING_RULE.md`: do not replace the hint-based algorithm with a fundamentally different skeletonization method without explicit approval.
- Keep the implementation pure Python standard library only; do not add third-party dependencies.
- Maintain the current module separation: decoding, masking, contouring, geometry, topology, simplification, and SVG output should remain distinct responsibilities.
- Run `source/test_compare.py` after significant changes and keep the comparison metrics current.

## What AI should avoid
- Replacing the challenge hint algorithm with a different skeletonization pipeline unless the change is documented and justified.
- Adding external libraries such as `numpy`, `scipy`, `Pillow`, `OpenCV`, `shapely`, or `networkx`.
- Hardcoding per-shape parameters unless there is a clear, documented need; prefer defaults with per-shape overrides only when necessary.
- Producing SVGs with filled shapes instead of stroked centerline paths.

## Useful notes for agents
- The repo uses a 3-4 chamfer distance transform in `source/thinning.py` and a centeredness filter that compares midpoint clearance to half the chord length.
-- The output topology is finalized before SVG rendering, so `source/svg_output.py` only formats lines and does not alter connectivity.
- `source/test_compare.py` is the authoritative regression harness and should be updated if the output metrics or comparison strategy changes.

## Suggested follow-up customizations
- Create a `skill` or `AGENT` for shape-specific threshold tuning and quality regression checks.
- Add a `hook` to run `python source/test_compare.py` automatically after edits to `source/*.py`.
- Add a lightweight `README` snippet or root-level doc for the exact developer command to run the project from the repository root.
