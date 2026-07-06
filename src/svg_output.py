"""
SVG output utilities — cleaner, well-documented and robust writer.

Provides `write_svg_file()` which ensures the destination directory exists
and writes one stroked <path> element per polyline. Paths are written with
consistent formatting and numeric precision suitable for diffs.
"""

import os
from typing import Iterable, Sequence, Tuple


Point = Tuple[float, float]


def _format_path_d(points: Sequence[Point]) -> str:
    if len(points) < 2:
        return ""
    parts = [f'M{points[0][0]:.3f} {points[0][1]:.3f}']
    for x, y in points[1:]:
        parts.append(f'L{x:.3f} {y:.3f}')
    return ' '.join(parts)


def write_svg_file(filepath: str,
                   polylines: Iterable[Sequence[Point]],
                   width: int = 1024,
                   height: int = 1024,
                   stroke_width: float = 45.0,
                   stroke_color: str = '#000000') -> None:
    """Write polylines to `filepath` as stroked SVG paths.

    Ensures parent directory exists. Each polyline becomes a separate
    `<path>` with `fill="none"` and rounded caps/joins.
    """
    # Ensure destination directory.
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" preserveAspectRatio="xMidYMid meet">',
        '  <g id="centerline-shapes">',
    ]

    for idx, poly in enumerate(polylines):
        if len(poly) < 2:
            continue
        d = _format_path_d(poly)
        lines.append(
            f'    <path id="path-{idx+1}" d="{d}" stroke="{stroke_color}" '
            f'stroke-width="{stroke_width:.2f}" fill="none" '
            f'stroke-linecap="round" stroke-linejoin="round" />'
        )

    lines.append('  </g>')
    lines.append('</svg>')

    with open(filepath, 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(lines) + '\n')
