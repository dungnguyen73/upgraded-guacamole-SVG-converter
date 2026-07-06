"""
Pure-Python PNG decoder for standard 8-bit image formats.

Supports common icon PNG formats (no interlacing, 8-bit depth):
  - Color type 0: Grayscale
  - Color type 2: RGB
  - Color type 4: Grayscale + Alpha
  - Color type 6: RGBA

Transparent and alpha-blended pixels are composited over white background.

Functions:
  - decode_png(filepath) -> (width, height, pixels)
    Returns grayscale pixel rows (list of lists)
"""

import struct
import zlib


class PNGDecodeError(Exception):
    """Raised when PNG parsing or decompression fails."""
    pass


def _paeth_predictor(a, b, c):
    """Paeth predictor function for PNG filter type 4 (Paeth).
    
    Selects the color value (a, b, or c) that is closest to p = a + b - c.
    Used to reverse the PNG filter prediction during decompression.
    """
    p = a + b - c
    pa = abs(p - a)
    pb = abs(p - b)
    pc = abs(p - c)
    
    if pa <= pb and pa <= pc:
        return a
    if pb <= pc:
        return b
    return c


def _unfilter_scanline(filter_type, scanline, prev_scanline, bpp):
    """Reverse PNG filtering on a scanline.
    
    PNG stores scanlines with a filter byte indicating how the row was
    compressed relative to neighboring rows and prior bytes.
    This function reverses that filtering.
    
    Args:
        filter_type: Filter type byte (0-4)
        scanline: Filtered scanline bytes
        prev_scanline: Previous scanline (for filters that reference it)
        bpp: Bytes per pixel (needed for "Sub" filter)
    
    Returns:
        Unfiltered scanline as bytearray
    """
    line = bytearray(scanline)
    
    if filter_type == 0:  # None: no filter
        return line
    
    if filter_type == 1:  # Sub: pixel = filtered + left
        for i in range(len(line)):
            left = line[i - bpp] if i >= bpp else 0
            line[i] = (line[i] + left) & 0xFF
        return line
    
    if filter_type == 2:  # Up: pixel = filtered + above
        for i in range(len(line)):
            up = prev_scanline[i] if prev_scanline is not None else 0
            line[i] = (line[i] + up) & 0xFF
        return line
    
    if filter_type == 3:  # Average: pixel = filtered + average(left, above)
        for i in range(len(line)):
            left = line[i - bpp] if i >= bpp else 0
            up = prev_scanline[i] if prev_scanline is not None else 0
            line[i] = (line[i] + (left + up) // 2) & 0xFF
        return line
    
    if filter_type == 4:  # Paeth: pixel = filtered + paeth(left, above, upleft)
        for i in range(len(line)):
            left = line[i - bpp] if i >= bpp else 0
            up = prev_scanline[i] if prev_scanline is not None else 0
            upleft = prev_scanline[i - bpp] if (prev_scanline is not None and i >= bpp) else 0
            line[i] = (line[i] + _paeth_predictor(left, up, upleft)) & 0xFF
        return line
    
    raise PNGDecodeError(f"Unknown filter type: {filter_type}")


def _bytes_per_pixel(color_type):
    """Return bytes per pixel for a given PNG color type."""
    if color_type == 0:
        return 1  # Grayscale
    if color_type == 2:
        return 3  # RGB
    if color_type == 4:
        return 2  # Grayscale + Alpha
    if color_type == 6:
        return 4  # RGBA
    raise PNGDecodeError(f"Unsupported color type: {color_type}")


def _to_gray(row, x, color_type):
    """Convert pixel at column x in row to grayscale value.
    
    For color images, computes average of R, G, B.
    For alpha-channel images, composites over white background.
    
    Args:
        row: Pixel data row
        x: Column index (pixel number, not byte offset)
        color_type: PNG color type
    
    Returns:
        Grayscale value 0-255
    """
    if color_type == 0:
        return row[x]
    
    if color_type == 2:  # RGB
        off = x * 3
        return (row[off] + row[off + 1] + row[off + 2]) // 3
    
    if color_type == 4:  # Grayscale + Alpha
        off = x * 2
        g, a = row[off], row[off + 1]
        # Composite over white background: result = g * (a/255) + 255 * (1 - a/255)
        return (g * a + 255 * (255 - a)) // 255
    
    if color_type == 6:  # RGBA
        off = x * 4
        r, g, b, a = row[off], row[off + 1], row[off + 2], row[off + 3]
        gray = (r + g + b) // 3
        # Composite over white background
        return (gray * a + 255 * (255 - a)) // 255
    
    raise PNGDecodeError(f"Unsupported color type: {color_type}")


def decode_png(filepath):
    """Decode a PNG file to grayscale pixel rows.
    
    Reads PNG chunks, decompresses IDAT data, unfilters scanlines,
    and converts to grayscale. Transparent pixels are composited over white.
    
    Args:
        filepath: Path to PNG file
    
    Returns:
        (width, height, pixels) where pixels is a list of grayscale rows,
        each row a list of 0-255 intensity values
    
    Raises:
        PNGDecodeError: If PNG is invalid, unsupported, or corrupted
    """
    with open(filepath, 'rb') as f:
        data = f.read()

    # Verify PNG signature
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        raise PNGDecodeError("Not a valid PNG file")

    # Parse PNG chunks
    pos = 8
    idat_chunks = []
    width = height = bit_depth = color_type = interlace = None

    while pos < len(data):
        if pos + 8 > len(data):
            raise PNGDecodeError("Truncated PNG chunk header")
        
        length = struct.unpack('>I', data[pos:pos + 4])[0]
        pos += 4
        chunk_type = data[pos:pos + 4].decode('ascii', errors='replace')
        pos += 4
        chunk_data = data[pos:pos + length]
        pos += length
        pos += 4  # CRC (skip validation)

        if chunk_type == 'IHDR':
            if length != 13:
                raise PNGDecodeError(f"IHDR length != 13: {length}")
            width = struct.unpack('>I', chunk_data[0:4])[0]
            height = struct.unpack('>I', chunk_data[4:8])[0]
            bit_depth = chunk_data[8]
            color_type = chunk_data[9]
            interlace = chunk_data[12]
            if bit_depth != 8:
                raise PNGDecodeError(f"Unsupported bit depth: {bit_depth} (expected 8)")
            if color_type not in (0, 2, 4, 6):
                raise PNGDecodeError(f"Unsupported color type: {color_type}")
            if interlace != 0:
                raise PNGDecodeError(f"Unsupported interlace: {interlace} (expected 0)")
        
        elif chunk_type == 'IDAT':
            idat_chunks.append(chunk_data)
        
        elif chunk_type == 'IEND':
            break

    if width is None or height is None:
        raise PNGDecodeError("No IHDR chunk found")

    # Decompress IDAT data
    try:
        raw_data = zlib.decompress(b''.join(idat_chunks))
    except zlib.error as e:
        raise PNGDecodeError(f"zlib decompression failed: {e}")

    # Unfilter and convert to grayscale
    bpp = _bytes_per_pixel(color_type)
    stride = 1 + width * bpp  # 1 byte filter type + width bytes of pixels
    expected_size = height * stride
    if len(raw_data) < expected_size:
        raise PNGDecodeError(f"Decompressed data too short: {len(raw_data)} < {expected_size}")

    pixels = []
    prev_row = None
    
    for y in range(height):
        offset = y * stride
        filter_type = raw_data[offset]
        scanline = raw_data[offset + 1:offset + stride]
        
        unfiltered = _unfilter_scanline(filter_type, scanline, prev_row, bpp)
        gray_row = [_to_gray(unfiltered, x, color_type) for x in range(width)]
        pixels.append(gray_row)
        prev_row = unfiltered

    return width, height, pixels
