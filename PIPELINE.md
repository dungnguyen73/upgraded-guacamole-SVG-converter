# PIPELINE.md

# PNG → SVG Centerline Extraction Pipeline

This document defines the canonical processing pipeline for extracting centerlines from PNG icons and generating SVG paths. All implementations should follow this pipeline unless there is a documented justification for deviating.

---

# Guiding Principles

- Follow the challenge hint as closely as possible:
  > PNG → Binary Mask → Contour Trace → Perpendicular Rays → Midpoints → Connect into Paths.
- Prioritize geometric correctness over heuristics.
- Preserve topology (endpoints, branches, loops, junctions).
- Keep the centerline centered within the stroke.
- Produce smooth, compact SVG paths.

---

# Pipeline Overview

```
PNG
    ↓
Decode
    ↓
Binarize
    ↓
Chamfer Distance Transform
    ↓
Contour Trace
    ↓
Perpendicular Ray Marching
    ↓
Midpoint Samples
    ↓
Chain by Contour Order
    ↓
Clearance Jump Split
    ↓
Dedupe
    ↓
Junction Resolution
    ↓
Topology Split / Connect
    ↓
RDP Simplification
    ↓
Axis Snap
    ↓
Resample & Smooth
    ↓
SVG
```

---

# Stage 1 — Decode PNG

## Goal

Load the PNG image without external CV libraries.

## Requirements

- Support 1024×1024 PNG files.
- Decode RGB/RGBA images.
- Reconstruct PNG scanlines.
- Produce a raster image.

Output:

```
Image[y][x]
```

---

# Stage 2 — Binarization

## Goal

Convert the decoded image into a binary mask.

```
mask[y][x]

1 = foreground (shape)
0 = background
```

Requirements:

- Handle white or transparent backgrounds.
- Produce a clean binary mask.
- Optionally pad the mask with one pixel of background to simplify contour tracing.

---

# Stage 3 — Chamfer Distance Transform

## Goal

Compute an approximate Euclidean distance from every foreground pixel to the nearest boundary.

```
distance[y][x]
```

Each foreground pixel stores its local clearance.

Example:

```
1111111
1222221
1233321
1222221
1111111
```

The distance field is later used to verify whether midpoint samples are truly centered.

---

# Stage 4 — Contour Tracing

## Goal

Extract all contours using Moore Neighbor tracing.

Requirements:

- Trace every connected component.
- Trace outer contours.
- Trace inner contours (holes).
- Preserve contour ordering.

Output:

```
Contour

[
    p0,
    p1,
    p2,
    ...
]
```

Each contour is an ordered list of boundary pixels.

---

# Stage 5 — Tangent & Normal Estimation

For each contour point:

1. Estimate the tangent using finite differences over a local window.
2. Rotate the tangent by 90°.
3. Determine the inward direction by checking the binary mask.
4. Normalize to a unit vector.

Output:

```
Point
Tangent
Inward Normal
```

---

# Stage 6 — Perpendicular Ray Marching

## Goal

Cast a ray from each contour point inward.

Procedure:

1. March along the inward normal.
2. Continue until leaving the foreground.
3. Record the opposite boundary.
4. Compute:

```
Chord
Midpoint
Half Width
```

Definitions:

```
Chord = entry → exit

Midpoint = (entry + exit)/2

HalfWidth = chord_length / 2
```

Each successful ray produces one midpoint sample.

---

# Stage 7 — Centeredness Filter

Not every ray is valid.

For every midpoint:

```
expected_clearance = half_chord_length

actual_clearance = chamfer_distance(midpoint)
```

Accept the midpoint only if:

```
actual_clearance ≈ expected_clearance
```

Reject rays that:

- stop too early
- cross diagonally
- intersect adjacent branches
- occur near sharp caps
- occur inside unstable junction regions

This stage greatly improves robustness around junctions.

---

# Stage 8 — Chain Midpoints by Contour Order

Instead of constructing an immediate proximity graph:

- preserve contour order
- connect consecutive valid midpoint samples

Result:

```
Contour

↓

Midpoint Chain
```

This naturally forms continuous centerline candidates.

---

# Stage 9 — Clearance Jump Split

A sudden clearance change usually indicates:

- junction
- corner
- stroke transition
- invalid correspondence

If:

```
|clearance(i+1)-clearance(i)| > threshold
```

split the chain.

This prevents unrelated stroke regions from remaining connected.

---

# Stage 10 — Dedupe

Each stroke is sampled twice:

- once from each contour side.

Duplicate midpoint chains should be merged.

Requirements:

- compare overlapping chains
- keep the longest consistent chain
- remove duplicate tracks

Do not merge unrelated branches.

---

# Stage 11 — Junction Resolution

This stage reconstructs topology.

Goals:

- detect T-junctions
- detect Y-junctions
- detect X-junctions
- reconnect broken branches
- create stable junction nodes

Junctions should be treated as explicit graph nodes rather than relying solely on nearest-neighbor proximity.

---

# Stage 12 — Topology Split / Connect

Convert midpoint chains into the final graph.

Operations include:

- split paths at junction hubs
- reconnect neighboring branches
- insert short connector paths where necessary
- preserve loops
- preserve branch topology

Output:

```
Skeleton Graph

Nodes
Edges
Ordered Paths
```

---

# Stage 13 — RDP Simplification

Apply the Ramer–Douglas–Peucker algorithm.

Goals:

- reduce vertex count
- preserve shape
- maintain topology

---

# Stage 14 — Axis Snap

Many icons contain perfectly horizontal or vertical strokes.

After simplification:

- detect nearly horizontal segments
- detect nearly vertical segments

Snap them to exact axes when within tolerance.

This improves SVG cleanliness and visual quality.

---

# Stage 15 — Resample & Smooth

Apply optional smoothing:

- moving average
- Gaussian smoothing
- spline interpolation (if appropriate)

Requirements:

- preserve endpoints
- preserve junctions
- avoid oversmoothing corners

---

# Stage 16 — SVG Generation

Generate SVG paths.

Requirements:

- preserve graph topology
- preserve path ordering
- emit separate paths for junction connectors if needed

Output format:

```xml
<svg viewBox="0 0 1024 1024">
    <path
        fill="none"
        stroke="black"
        stroke-width="45"
        stroke-linecap="round"
        stroke-linejoin="round"
        d="..."
    />
</svg>
```

---

# Expected Properties

A correct implementation should:

- preserve topology
- produce centered centerlines
- correctly handle loops
- correctly handle junctions
- correctly handle stroke caps
- reject invalid rays
- produce compact SVG paths
- closely match the provided reference SVGs

---

# Implementation Notes

The implementation should remain modular.

Avoid placing the entire implementation in a single source file.

Each stage should be independently testable.