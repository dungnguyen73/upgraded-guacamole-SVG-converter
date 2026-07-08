# PNG → SVG Centerline Extraction

This repository contains a pure-Python pipeline for turning PNG icons into thin centerline SVG paths. The goal is to recover the medial axis of each shape so it can be rendered as a clean skeleton instead of an outline.

For quickly looking up the results, see [PNG → SVG Centerline Extraction](https://dungnguyen73.github.io/upgraded-guacamole-SVG-converter/). 

## Offered features

- Batch conversion from PNG inputs to SVG outputs
- Single-file conversion with preview output
- Overlay diagnostics for comparing reference and generated paths
- A browser dashboard for visual review
- An upload server for converting uploaded PNG files on demand
- A metric harness for comparing outputs against the reference set

## How to use the source code

Requirements:
- Python 3.10 or newer
- No third-party dependencies are required; the pipeline uses the Python standard library

From the repository root:

```bash
python src/main.py <input-file-or-directory>
```

Examples:

```bash
python src/main.py input/letter_H.png
python src/main.py ../input
```

To generate overlay visuals:

```bash
python src/visualize.py overlay
```

To launch the review dashboard:

```bash
python src/upload_server.py
```

Then open http://localhost:8000/index.html.

## Approach

The implementation follows a defined pipeline (see [PIPELINE.md](PIPELINE.md)):

```mermaid
flowchart LR
    A[PNG input] --> B[Decode and binarize]
    B --> C[Build distance transform and trace contours]
    C --> D[March rays and filter midpoints]
    D --> E[Chain and clean candidate paths]
    E --> F[Resolve topology and finalize skeleton]
    F --> G[Simplify, snap, smooth, and write SVG]
```

The main steps are:

1. Input preparation and binarization
   - Decode the PNG and convert it into a binary mask.
2. Geometry extraction
   - Compute a chamfer distance transform and trace the contours while estimating tangent and inward-normal directions.
3. Midpoint sampling
   - March perpendicular rays across the stroke, then keep only midpoint candidates that pass the centeredness filter.
4. Path construction and cleanup
   - Chain the accepted samples into candidate paths, split on clearance jumps, and remove duplicate or covered fragments.
5. Topology resolution
   - Resolve junctions and finalize the skeleton graph so branches and loops are represented consistently.
6. Final rendering
   - Simplify the paths, fit straight segments where appropriate, snap them to axes, smooth the geometry, and write the final SVG output.

## Project structure and documentation

```text
png2svg_centerline_extraction/
├── README.md                     # Overview, usage, and project summary
├── PIPELINE.md                   # Canonical processing order and stage descriptions
├── ENGINEERING_RULE.md           # Implementation constraints and rules for future changes
├── TOPIC.md                      # Original challenge brief and evaluation context
├── TESTING_RESULTS.md            # Verified metrics and interpretation of the current output
├── src/                          # Pure-Python implementation modules
│   ├── main.py                   # CLI entry point
│   ├── thinning.py               # Masking, transforms, and contour tracing
│   ├── skeleton_graph.py         # Topology cleanup and path resolution
│   ├── path_fit.py               # Simplification, smoothing, and fitting
│   ├── svg_writer.py             # SVG output generation
│   ├── visualize.py              # Overlay and diagnostic generation
│   └── test_compare.py           # Metric comparison harness
├── input/                       # Sample input PNGs
├── reference/                   # Reference SVGs used for comparison
└── out/                         # Generated SVG outputs from the sample pipeline run
```

## What I would improve with more time
- Interactive Parameter Tuning: Extend the local web dashboard to allow real-time adjustment of algorithm parameters (e.g. stroke width , RDP epsilon, smoothing window) with live SVG previews.
- Better junction and topology handling for crossings and branch points
- Adaptive sampling that responds to local stroke width and shape complexity
- More shape-specific heuristics so difficult glyphs behave more like the reference

## Where the output diverges from the reference

The current pipeline favors a geometric centerline that reconstructs the original shape well. The reference SVGs are human-authored, so some differences are expected:

- path decomposition may differ at junctions or small branches
- stroke placement can be slightly offset from the exact medial axis
- the algorithm may simplify or merge strokes differently than the reference

For full testing details and metric output, see [TESTING_RESULTS.md](TESTING_RESULTS.md).
