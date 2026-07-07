# PIPELINE.md

# PNG → SVG Centerline Extraction Pipeline

This document defines the canonical processing pipeline for extracting centerlines from PNG icons and generating SVG paths. All implementations should follow this pipeline unless there is a documented justification for deviating.

---

# Guiding Principles

- Follow the challenge hint as closely as possible:
  > PNG → Binary Mask → Chamfer Distance Transform → Contour Trace → Tangent/Normal Estimation → Perpendicular Rays → Midpoints → Connect into Paths.
- Prioritize geometric correctness over heuristics.
- Preserve topology (endpoints, branches, loops, junctions).
- Keep the centerline centered within the stroke.
- Produce smooth, compact SVG paths.

---

# Pipeline Overview

```
PNG
    ↓
Decode and Binarize
    ↓
Distance Transform
    ↓
Contour Trace and Geometry Estimation
    ↓
Perpendicular Ray Marching
    ↓
Centeredness Filtering
    ↓
Midpoint Chaining
    ↓
Split, Dedupe, and Prune
    ↓
Junction Resolution and Topology Finalization
    ↓
Simplify, Snap, Smooth, and Write SVG
```

---

# Stage 1 — Decode PNG and Normalize Input

## Goal

Load the PNG image without external CV libraries and prepare it for later processing.

## Sub-steps

- Support 1024×1024 PNG files.
- Decode RGB/RGBA images.
- Reconstruct PNG scanlines.
- Produce a raster image as `Image[y][x]`.

---

# Stage 2 — Binarize the Image

## Goal

Convert the decoded image into a binary mask.

```
mask[y][x]

1 = foreground (shape)
0 = background
```

## Sub-steps

- Handle white or transparent backgrounds.
- Produce a clean binary mask.
- Optionally pad the mask with one pixel of background to simplify contour tracing.

---

# Stage 3 — Compute the Chamfer Distance Transform

## Goal

Estimate local clearance from every foreground pixel to the nearest boundary.

```
distance[y][x]
```

## Sub-steps

- Use a 3-4 chamfer metric as an approximate distance field.
- Store local clearance values for later centeredness checks.
- Use the distance map to verify whether midpoint candidates are truly centered.

---

# Stage 4 — Trace Contours and Estimate Geometry

## Goal

Recover the boundary geometry of the shape and estimate the local orientation at each contour point.

## Sub-steps

- Trace every connected component with Moore-style contour following.
- Track outer contours and holes.
- Estimate the local tangent at each contour sample.
- Derive an inward-pointing normal from the tangent and the mask.

---

# Stage 5 — March Perpendicular Rays

## Goal

Cast a ray from each contour point inward to find the opposite boundary.

## Sub-steps

- March along the inward normal until leaving the foreground.
- Record the entry and exit points of the chord.
- Compute the midpoint and half-width of each chord.

---

# Stage 6 — Filter Centeredness and Sample Midpoints

## Goal

Keep only midpoint candidates that are plausible medial-axis points.

## Sub-steps

- Compare the actual clearance from the distance transform with the expected half-chord length.
- Reject rays that stop too early, cross diagonally, or occur in unstable junction regions.
- Keep the remaining samples as valid midpoint candidates.

---

# Stage 7 — Chain Midpoints into Candidate Paths

## Goal

Turn the accepted samples into continuous centerline candidates.

## Sub-steps

- Preserve contour order.
- Connect consecutive valid midpoint samples into chains.
- Allow wrap-around linking when a contour closes back on itself.

---

# Stage 8 — Split, Dedupe, and Prune Fragments

## Goal

Clean up the raw chains before topology is finalized.

## Sub-steps

- Split a chain when the clearance changes abruptly, which often indicates a junction or a bad correspondence.
- Merge duplicate midpoint chains from opposite sides of the same stroke.
- Remove fragments that are fully covered by a longer, stronger path.

---

# Stage 9 — Resolve Junctions and Finalize Topology

## Goal

Reconstruct the skeleton graph so branches, loops, and junctions are represented consistently.

## Sub-steps

- Detect junctions such as T-, Y-, and X-shaped intersections.
- Reconnect broken branches through explicit graph nodes.
- Preserve loops and branch topology in the final skeleton graph.

---

# Stage 10 — Simplify, Snap, Smooth, and Write SVG

## Goal

Turn the finalized topology into clean, compact SVG paths.

## Sub-steps

- Apply Ramer–Douglas–Peucker simplification and fit straight segments where appropriate.
- Snap near-horizontal and near-vertical segments to exact axes.
- Resample and smooth the polylines while preserving endpoints and junctions.
- Write the final SVG output with the chosen stroke width.

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