---

# Engineering Rules

## 1. Follow the Problem Hint

Always implement the algorithm suggested by the problem statement before considering alternative approaches.

For this project, the canonical workflow is:

```
Binary Mask
→ Contour Tracing
→ Perpendicular Ray Marching
→ Midpoint Extraction
→ Connect Midpoints into Paths
```

Do **not** replace this pipeline with fundamentally different algorithms (e.g. Zhang-Suen thinning, Guo-Hall thinning, Voronoi skeletonization, or Distance-Transform skeletonization) unless the hint-based approach has been thoroughly implemented, tested, and demonstrated to be insufficient.

Any deviation from the challenge hint must be clearly documented and justified.

---

## 2. Test-Driven Development

Maintain an automated comparison tool throughout development.

Requirements:

- Keep `test_compare.py` (or equivalent) up to date.
- Run comparison tests after every significant code change.
- Compare generated SVGs against the provided reference SVGs.
- Verify both topology and visual similarity.
- Do not proceed to the next implementation stage if existing tests fail.

Testing is part of the implementation, not an optional final step.

---

## 3. Per-Shape Configuration

Avoid hard-coded global parameters whenever possible.

If thresholds or tolerances vary between different icons, define them in a configuration dictionary.

Example:

```python
CONFIG = {
    "letter_H": {...},
    "number_6": {...},
    "ampersand": {...},
}
```

The algorithm should first use sensible defaults, then apply per-shape overrides only when necessary.

---

## 4. Project Structure

Organize the implementation into independent modules.

Suggested structure:

```
project/

    png_decode.py          # PNG decoding

    binary_mask.py         # Binarization

    distance_transform.py  # Chamfer Distance Transform

    contour_trace.py       # Moore contour tracing

    geometry.py            # Tangent, normal, vector math

    ray_casting.py         # Perpendicular ray marching

    midpoint.py            # Midpoint extraction & filtering

    topology.py            # Chain building, dedupe, junction handling

    simplify.py            # RDP, smoothing, axis snapping

    svg_writer.py          # SVG generation

    main.py                # CLI entry point

    test_compare.py        # Automated comparison against reference

    compare.html           # Visual comparison

    README.md
```

Avoid placing the entire implementation into a single source file.

Each module should have a single responsibility.

---

## 5. Pure Python Standard Library Only

Only Python's standard library may be used.

Do NOT use external dependencies, including but not limited to:

- numpy
- scipy
- Pillow (PIL)
- OpenCV
- scikit-image
- shapely
- networkx

The implementation must be completely self-contained.

---

## 6. Incremental Development

Implement the pipeline one stage at a time.

For every stage:

1. Design
2. Implement
3. Test
4. Validate against reference
5. Refactor if needed
6. Continue to the next stage

Do not implement multiple major stages simultaneously.

---

## 7. Documentation

Documentation should be written only after:

- implementation is complete,
- tests pass,
- outputs have been verified.

Keep implementation documents in Markdown files rather than embedding large explanations inside source code.

---

## 8. Do Not Change the Core Algorithm Without Approval

The pipeline defined in this document is the canonical implementation.

Do **not** replace or fundamentally alter any stage of the pipeline without explicit approval.

Examples include (but are not limited to):

- replacing contour tracing with thinning
- replacing ray marching with distance-transform skeletonization
- replacing contour-order chaining with nearest-neighbor graph construction
- introducing an entirely different centerline extraction algorithm

If you believe an alternative approach would perform better:

1. Clearly explain the problem with the current approach.
2. Provide evidence (test results, visual comparisons, or measurements).
3. Compare the proposed approach against the current pipeline.
4. Describe the trade-offs (accuracy, complexity, maintainability, performance).
5. Wait for approval before implementing the change.

Never silently replace the intended algorithm simply because another solution appears easier or more familiar.

Small implementation improvements that preserve the algorithm (performance optimizations, bug fixes, code refactoring, parameter tuning, etc.) do **not** require approval.