# PNG → SVG Centerline Extraction

This project extracts centerline (medial-axis) SVG paths from solid black PNG icons
using a pure-Python implementation. It follows the pipeline documented in
`PIPELINE.md` and adheres to the constraints in `ENGINEERING_RULE.md`.

Quick usage

1. Put the input PNGs into the repo-level `input/` folder (create it if needed).
2. Run the converter from the repository root:

```bash
python source/main.py ../input
```

Or run from the `source/` folder (defaults are repo-level):

```bash
cd source
python main.py      # reads ../input and writes ../converted-results
```

By default output SVGs are written to `converted-results/` at the repository root.

Notes
- The implementation is pure Python (no third-party dependencies).
- The canonical comparison harness is `python source/test_compare.py`.

Files
- `PIPELINE.md` — canonical pipeline and guidance
- `ENGINEERING_RULE.md` — project rules and constraints
- `source/` — implementation modules and CLI
