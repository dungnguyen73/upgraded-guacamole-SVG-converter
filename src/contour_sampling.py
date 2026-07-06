"""
Binary mask to centerline extraction using contour sampling.

Pipeline:
  1. Binarize pixels to mask
  2. Compute chamfer distance transform (3-4 metric)
  3. Trace boundary contours
  4. For each contour: march perpendicular rays across strokes
  5. Sample midpoints and chain them in contour order
  6. Return raw centerline paths (typically 2 per stroke, from both sides)

The key correctness filter is "centeredness": on the true medial axis the
clearance (distance transform value) equals half the perpendicular chord length.
Rays violating this (at junctions, caps) are rejected so chains break cleanly
instead of producing hooks and drift.

Functions:
  - binarize(pixels, width, height, threshold=128) -> mask
  - chamfer_dt(mask, width, height) -> distance_transform
  - trace_all_contours(mask, width, height) -> list of contours
  - extract_centerline_paths(mask, width, height, sample_step=2) -> (paths, dt)
"""

import math


def binarize(pixels, width, height, threshold=128):
    """Convert grayscale pixel rows to binary mask (0=background, 1=shape).
    
    Args:
        pixels: List of grayscale rows (each row is a sequence of 0-255 values)
        width: Image width in pixels
        height: Image height in pixels
        threshold: Grayscale value separating background from shape (default: 128)
    
    Returns:
        2D mask (list of bytearray), where mask[y][x] is 1 for shape pixels
    """
    mask = [bytearray(width) for _ in range(height)]
    for y in range(height):
        row = pixels[y]
        mrow = mask[y]
        for x in range(width):
            mrow[x] = 1 if row[x] < threshold else 0
    return mask


def chamfer_dt(mask, width, height):
    """Compute 3-4 chamfer distance transform (medial axis approximation).
    
    The 3-4 metric uses distances: horizontal/vertical=3, diagonal=4 (units of 1/3 pixel).
    Two passes: forward and backward propagation to converge to approximate Euclidean distances.
    
    Args:
        mask: Binary mask (1=shape, 0=background)
        width: Mask width
        height: Mask height
    
    Returns:
        2D distance transform where dt[y][x] / 3.0 ≈ Euclidean distance to boundary in pixels
    """
    INF = float('inf')
    w, h = width, height
    dt = [[INF] * w for _ in range(h)]
    
    # Initialize: boundary pixels have distance 0
    for y in range(h):
        for x in range(w):
            if mask[y][x] == 0:
                dt[y][x] = 0.0
    
    # Forward pass: propagate from top-left to bottom-right
    for y in range(h):
        for x in range(w):
            if mask[y][x] == 0:
                continue
            best = dt[y][x]
            if y > 0:
                if x > 0 and dt[y - 1][x - 1] + 4 < best:
                    best = dt[y - 1][x - 1] + 4
                if dt[y - 1][x] + 3 < best:
                    best = dt[y - 1][x] + 3
                if x + 1 < w and dt[y - 1][x + 1] + 4 < best:
                    best = dt[y - 1][x + 1] + 4
            if x > 0 and dt[y][x - 1] + 3 < best:
                best = dt[y][x - 1] + 3
            dt[y][x] = best
    
    # Backward pass: propagate from bottom-right to top-left
    for y in range(h - 1, -1, -1):
        for x in range(w - 1, -1, -1):
            if mask[y][x] == 0:
                continue
            best = dt[y][x]
            if y + 1 < h:
                if dt[y + 1][x] + 3 < best:
                    best = dt[y + 1][x] + 3
                if x + 1 < w and dt[y + 1][x + 1] + 4 < best:
                    best = dt[y + 1][x + 1] + 4
                if x > 0 and dt[y + 1][x - 1] + 4 < best:
                    best = dt[y + 1][x - 1] + 4
            if x + 1 < w and dt[y][x + 1] + 3 < best:
                best = dt[y][x + 1] + 3
            dt[y][x] = best
    
    return dt


def _is_boundary(mask, x, y, w, h):
    """Check if pixel (x,y) is on the boundary between shape and background."""
    if mask[y][x] == 0:
        return False
    # Boundary if adjacent to background or image edge
    for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            return True
        if mask[ny][nx] == 0:
            return True
    return False


def trace_all_contours(mask, width, height):
    """Trace all boundary contours using Moore-style boundary following.
    
    Returns both outer boundaries and holes. Each contour is a closed loop
    of pixels ordered counter-clockwise (for outer) or clockwise (for holes).
    
    Args:
        mask: Binary mask (1=shape, 0=background)
        width: Mask width
        height: Mask height
    
    Returns:
        List of contours, each a list of (x, y) boundary pixel coordinates
    """
    w, h = width, height
    visited = bytearray(w * h)
    dirs = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]
    contours = []
    
    for y0 in range(h):
        for x0 in range(w):
            if not _is_boundary(mask, x0, y0, w, h) or visited[y0 * w + x0]:
                continue
            
            start = (x0, y0)
            contour = [start]
            visited[start[1] * w + start[0]] = 1
            cx, cy = start
            px, py = -1, -1
            ss = 0
            
            # Moore boundary tracing: follow contour by always turning right
            for _ in range(w * h):
                found = False
                for d in range(8):
                    di = (ss + d) % 8
                    dx, dy = dirs[di]
                    nx, ny = cx + dx, cy + dy
                    if 0 <= nx < w and 0 <= ny < h and _is_boundary(mask, nx, ny, w, h):
                        if (nx, ny) == (px, py):
                            continue
                        if (nx, ny) == start:
                            if len(contour) > 2:
                                found = True
                                break
                            continue
                        contour.append((nx, ny))
                        visited[ny * w + nx] = 1
                        px, py = cx, cy
                        cx, cy = nx, ny
                        ss = (di + 5) % 8
                        found = True
                        break
                if not found or (cx, cy) == start:
                    break
            
            if len(contour) >= 10:
                contours.append(contour)
    
    return contours


def _tangent(contour, i, window):
    """Compute tangent direction at contour index i using a window of neighbors."""
    n = len(contour)
    im = (i - window) % n
    ip = (i + window) % n
    dx = contour[ip][0] - contour[im][0]
    dy = contour[ip][1] - contour[im][1]
    mag = math.hypot(dx, dy)
    return (dx / mag, dy / mag) if mag > 1e-6 else (0.0, 0.0)


def _inward_normal(mask, x, y, tx, ty, w, h):
    """Find inward-pointing perpendicular normal to the tangent.
    
    Of the two perpendiculars to tangent (tx, ty), choose the one pointing
    into the shape by probing which direction reaches deeper into the mask.
    """
    n1x, n1y = -ty, tx
    n2x, n2y = ty, -tx

    def _steps(nx, ny):
        """How many pixels deep can we probe in direction (nx, ny)."""
        fx, fy = float(x) + nx * 2, float(y) + ny * 2
        for s in range(15):
            xi, yi = int(fx), int(fy)
            if xi < 0 or xi >= w or yi < 0 or yi >= h:
                return s
            if mask[yi][xi] == 0:
                return s
            fx += nx
            fy += ny
        return 15

    return (n1x, n1y) if _steps(n1x, n1y) >= _steps(n2x, n2y) else (n2x, n2y)


def extract_centerline_paths(mask, width, height, sample_step=2):
    """Extract centerline paths from binary mask using the contour sampling pipeline.
    
    Processes each contour by:
      1. Sampling points at regular intervals along the boundary
      2. Marching perpendicular chords across the stroke
      3. Filtering by centeredness criterion (clearance ≈ half chord length)
      4. Chaining consecutive samples and refining to medial axis
    
    **Important**: Each stroke yields typically TWO nearly identical tracks (one per side).
    Deduplication happens in the topology module.
    
    Args:
        mask: Binary mask (1=shape, 0=background)
        width: Mask width
        height: Mask height
        sample_step: Interval (in pixels) along contours for sampling (default: 2)
    
    Returns:
        (paths, dt) where:
          - paths: list of polylines, each a list of (x, y) coordinates
          - dt: distance transform array (for later use in topology/simplification)
    """
    w, h = width, height
    dt = chamfer_dt(mask, w, h)
    contours = trace_all_contours(mask, w, h)
    print(f"  Contours: {len(contours)} ({sum(len(c) for c in contours)} pts)")

    max_igap = sample_step * 8  # Max index gap between consecutive samples
    max_sgap = 25.0  # Max spatial gap (pixels) between consecutive samples
    paths = []

    for contour in contours:
        n = len(contour)
        window = max(4, min(12, n // 100))
        samples = []  # (contour_index, mx, my, clearance)

        # Sample along the contour
        for idx in range(0, n, sample_step):
            x, y = contour[idx]
            tx, ty = _tangent(contour, idx, window)
            if tx == 0 and ty == 0:
                continue
            nx, ny = _inward_normal(mask, x, y, tx, ty, w, h)

            # March the perpendicular chord across the stroke
            fx, fy = float(x), float(y)
            hit = False
            for _ in range(300):
                fx += nx
                fy += ny
                xi, yi = int(fx), int(fy)
                if xi < 0 or xi >= w or yi < 0 or yi >= h:
                    break
                if mask[yi][xi] == 0:
                    hit = True
                    break
            if not hit:
                continue

            # Midpoint of the chord
            ox, oy = fx - nx, fy - ny  # last point still inside
            mx = (x + ox) / 2.0
            my = (y + oy) / 2.0
            chord = math.hypot(ox - x, oy - y)
            if chord < 4.0:
                continue
            
            mxi, myi = int(mx), int(my)
            if not (0 <= mxi < w and 0 <= myi < h and mask[myi][mxi]):
                continue

            # Centeredness filter: clearance must match half chord
            half = chord / 2.0
            clearance = dt[myi][mxi] / 3.0
            if abs(half - clearance) > max(2.5, 0.15 * half):
                continue

            # Refine: slide to max clearance along the chord (medial axis ridge)
            best_c = clearance
            bx, by = mx, my
            steps = int(chord)
            for s in range(steps + 1):
                t = s / max(steps, 1)
                px_ = x + t * (ox - x)
                py_ = y + t * (oy - y)
                pxi, pyi = int(px_), int(py_)
                if 0 <= pxi < w and 0 <= pyi < h:
                    c = dt[pyi][pxi] / 3.0
                    if c > best_c:
                        best_c = c
                        bx, by = px_, py_

            samples.append((idx, bx, by, best_c))

        if len(samples) < 3:
            continue

        # Chain consecutive samples; break on gaps
        chains = [[samples[0]]]
        for k in range(1, len(samples)):
            pidx, px_, py_, _ = chains[-1][-1]
            cidx, cx_, cy_, _ = samples[k]
            if (cidx - pidx) > max_igap or math.hypot(cx_ - px_, cy_ - py_) > max_sgap:
                chains.append([samples[k]])
            else:
                chains[-1].append(samples[k])

        # Handle contour wrap-around: last chain may connect to first
        def _wrap_connects(tail, head):
            igap = head[0][0] + n - tail[-1][0]
            sgap = math.hypot(head[0][1] - tail[-1][1], head[0][2] - tail[-1][2])
            return igap <= max_igap and sgap <= max_sgap

        closed = False
        if len(chains) > 1 and _wrap_connects(chains[-1], chains[0]):
            chains[0] = chains.pop() + chains[0]
        elif len(chains) == 1 and _wrap_connects(chains[0], chains[0]):
            closed = True

        # Convert chains to paths
        for ch in chains:
            if len(ch) < 3:
                continue
            pts = [(mx, my) for _, mx, my, _ in ch]
            if closed:
                pts.append(pts[0])
            paths.append(pts)

    print(f"  Raw midpoint tracks: {len(paths)}")
    return paths, dt
