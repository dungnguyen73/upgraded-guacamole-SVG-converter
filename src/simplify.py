"""
Path simplification, fitting, and refinement utilities.

Handles:
  - RDP simplification: reduce points while maintaining shape fidelity
  - Straight-line fitting: detect and replace nearly-linear segments
  - Resampling: normalize point spacing
  - Smoothing: reduce noise via moving average
  - Axis snapping: align nearly horizontal/vertical lines to exact axes
  - Spike removal: eliminate short back-and-forth wiggles

Functions:
  - rdp_simplify(poly, epsilon=2.0) -> simplified polyline
  - is_almost_straight(poly, max_error=3.0) -> bool
  - fit_line_if_straight(poly, max_error=3.0) -> polyline
  - resample_polyline(poly, spacing=4.0) -> polyline
  - smooth_polyline(poly, window=3) -> polyline
  - snap_axis_aligned(poly, ratio=4.0, max_error=6.0) -> polyline
  - remove_spikes(poly, min_leg=10.0, angle_thresh=0.45) -> polyline
  - polyline_length(poly) -> float
"""

import math


def resample_polyline(poly, spacing=4.0):
    """Resample polyline to uniform point spacing while preserving endpoints.
    
    Redistributes points along the polyline at regular arc-length intervals.
    Useful for preparing paths for rendering or further processing.
    
    Args:
        poly: Polyline as list of (x, y) tuples
        spacing: Target distance between consecutive samples (default: 4.0 pixels)
    
    Returns:
        Resampled polyline with uniform spacing
    """
    if len(poly) < 2:
        return poly
    
    # Compute cumulative arc length
    dists = [0.0]
    for i in range(1, len(poly)):
        dx = poly[i][0] - poly[i - 1][0]
        dy = poly[i][1] - poly[i - 1][1]
        dists.append(dists[-1] + math.hypot(dx, dy))
    
    total = dists[-1]
    if total < spacing:
        return [poly[0], poly[-1]]
    
    result = [poly[0]]
    pos = spacing
    si = 0
    
    while pos < total:
        # Find the segment containing this position
        while si < len(dists) - 1 and dists[si + 1] < pos:
            si += 1
        if si >= len(poly) - 1:
            break
        
        # Interpolate
        t = (pos - dists[si]) / (dists[si + 1] - dists[si]) if dists[si + 1] > dists[si] else 0
        x = poly[si][0] + t * (poly[si + 1][0] - poly[si][0])
        y = poly[si][1] + t * (poly[si + 1][1] - poly[si][1])
        result.append((x, y))
        pos += spacing
    
    result.append(poly[-1])
    return result


def smooth_polyline(poly, window=3):
    """Apply moving-average smoothing while preserving endpoints.
    
    Each interior point is averaged with its neighbors. Endpoints are unchanged.
    Useful for reducing noise and high-frequency jitter.
    
    Args:
        poly: Polyline as list of (x, y) tuples
        window: Averaging window size (default: 3)
    
    Returns:
        Smoothed polyline with same length as input
    """
    if window <= 1 or len(poly) <= 2 or len(poly) <= window:
        return poly
    
    result = [poly[0]]
    half = window // 2
    
    for i in range(1, len(poly) - 1):
        s = max(0, i - half)
        e = min(len(poly), i + half + 1)
        sx = sum(p[0] for p in poly[s:e])
        sy = sum(p[1] for p in poly[s:e])
        n = e - s
        result.append((sx / n, sy / n))
    
    result.append(poly[-1])
    return result


def _perp_distance(px, py, ax, ay, bx, by):
    """Perpendicular distance from point P to line segment AB.
    
    Used by RDP simplification to measure deviation from the simplified line.
    """
    vx, vy = bx - ax, by - ay
    wx, wy = px - ax, py - ay
    vv = vx * vx + vy * vy
    
    if vv < 1e-12:
        return math.hypot(px - ax, py - ay)
    
    t = (wx * vx + wy * vy) / vv
    if t <= 0:
        return math.hypot(px - ax, py - ay)
    if t >= 1:
        return math.hypot(px - bx, py - by)
    
    qx = ax + t * vx
    qy = ay + t * vy
    return math.hypot(px - qx, py - qy)


def _rdp(poly, epsilon, start, end, result):
    """Recursive Ramer-Douglas-Peucker simplification helper."""
    dmax = 0
    imax = start
    
    for i in range(start + 1, end):
        d = _perp_distance(poly[i][0], poly[i][1],
                           poly[start][0], poly[start][1],
                           poly[end][0], poly[end][1])
        if d > dmax:
            dmax = d
            imax = i
    
    if dmax > epsilon:
        _rdp(poly, epsilon, start, imax, result)
        _rdp(poly, epsilon, imax, end, result)
    else:
        result.append(poly[end])


def rdp_simplify(poly, epsilon=2.0):
    """Ramer-Douglas-Peucker polyline simplification.
    
    Recursively removes points that lie within epsilon distance of the
    simplified line segment. Preserves overall shape while reducing point count.
    
    Args:
        poly: Polyline as list of (x, y) tuples
        epsilon: Maximum allowed perpendicular distance (default: 2.0 pixels)
    
    Returns:
        Simplified polyline
    """
    if len(poly) < 3:
        return poly
    result = [poly[0]]
    _rdp(poly, epsilon, 0, len(poly) - 1, result)
    return result


def is_almost_straight(poly, max_error=3.0):
    """Check if polyline approximates a straight line within tolerance.
    
    All points must be within max_error perpendicular distance from the
    start-end line segment.
    
    Args:
        poly: Polyline as list of (x, y) tuples
        max_error: Maximum perpendicular distance (default: 3.0 pixels)
    
    Returns:
        True if polyline is nearly straight, False otherwise
    """
    if len(poly) < 3:
        return True
    
    ax, ay = poly[0]
    bx, by = poly[-1]
    
    for i in range(1, len(poly) - 1):
        if _perp_distance(poly[i][0], poly[i][1], ax, ay, bx, by) > max_error:
            return False
    
    return True


def fit_line_if_straight(poly, max_error=3.0):
    """Replace nearly-straight polylines with a single line segment.
    
    If all points lie within max_error of the start-end line, return just
    the endpoints. Otherwise return the original polyline unchanged.
    
    Args:
        poly: Polyline as list of (x, y) tuples
        max_error: Tolerance for straightness (default: 3.0 pixels)
    
    Returns:
        Two-point line if straight, otherwise original polyline
    """
    if len(poly) < 3:
        return poly
    if is_almost_straight(poly, max_error):
        return [poly[0], poly[-1]]
    return poly


def _axis_span(poly):
    """Return (horizontal_span, vertical_span) of the polyline bounding box."""
    xs = [p[0] for p in poly]
    ys = [p[1] for p in poly]
    return max(xs) - min(xs), max(ys) - min(ys)


def snap_axis_aligned(poly, ratio=4.0, max_error=6.0):
    """Snap nearly-horizontal or nearly-vertical polylines to exact axes.
    
    If the polyline is predominantly aligned with an axis (width >> height or
    vice versa) and all points are within max_error of the axis, snap them to
    a constant coordinate along that axis.
    
    Args:
        poly: Polyline as list of (x, y) tuples
        ratio: Aspect ratio threshold (default: 4.0 means 4:1 favors axis snapping)
        max_error: Max distance from axis before snapping fails (default: 6.0 pixels)
    
    Returns:
        Axis-aligned polyline if criteria met, otherwise original polyline
    """
    if len(poly) < 2:
        return poly
    
    hx, vy = _axis_span(poly)
    if hx < 1e-6 and vy < 1e-6:
        return poly
    
    # Snap horizontal: height much smaller than width
    if hx >= ratio * vy:
        avg_y = sum(p[1] for p in poly) / len(poly)
        if all(abs(p[1] - avg_y) <= max_error for p in poly):
            return [(p[0], avg_y) for p in poly]
    
    # Snap vertical: width much smaller than height
    if vy >= ratio * hx:
        avg_x = sum(p[0] for p in poly) / len(poly)
        if all(abs(p[0] - avg_x) <= max_error for p in poly):
            return [(avg_x, p[1]) for p in poly]
    
    return poly


def remove_spikes(poly, min_leg=10.0, angle_thresh=0.45):
    """Remove short back-and-forth wiggles (spikes) from polylines.
    
    Detects points where both legs are short and the angle is a sharp
    U-turn, indicating a spike or temporary deviation. Such points are dropped.
    Common near junction blobs in the centerline extraction.
    
    Args:
        poly: Polyline as list of (x, y) tuples
        min_leg: Maximum segment length to consider a "short leg" (default: 10.0)
        angle_thresh: Cosine threshold for spike detection (default: 0.45, ~63°)
    
    Returns:
        Polyline with spikes removed
    """
    if len(poly) < 4:
        return poly
    
    out = [poly[0]]
    
    for i in range(1, len(poly) - 1):
        ax, ay = out[-1]
        bx, by = poly[i]
        cx, cy = poly[i + 1]
        
        ab = math.hypot(bx - ax, by - ay)
        bc = math.hypot(cx - bx, cy - by)
        
        # Check for spike: both legs short and sharp turn
        if ab < min_leg and bc < min_leg:
            v1x, v1y = bx - ax, by - ay
            v2x, v2y = cx - bx, cy - by
            m1 = math.hypot(v1x, v1y)
            m2 = math.hypot(v2x, v2y)
            
            if m1 > 1e-6 and m2 > 1e-6:
                cos_a = (v1x * v2x + v1y * v2y) / (m1 * m2)
                if cos_a < -angle_thresh:  # Sharp U-turn (angle > 117°)
                    continue
        
        out.append((bx, by))
    
    out.append(poly[-1])
    return out


def polyline_length(poly):
    """Compute total arc length of a polyline.
    
    Args:
        poly: Polyline as list of (x, y) tuples
    
    Returns:
        Total distance along the polyline
    """
    if len(poly) < 2:
        return 0.0
    return sum(math.hypot(poly[i][0] - poly[i - 1][0],
                          poly[i][1] - poly[i - 1][1])
               for i in range(1, len(poly)))
