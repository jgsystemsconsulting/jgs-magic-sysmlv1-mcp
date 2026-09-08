# Copyright (c) 2026 JG Systems Consulting Ltd. All Rights Reserved.
# SPDX-License-Identifier: LicenseRef-JGSystemsConsulting-Proprietary
"""Pillow-based image shrink-and-encode utility for MCP image returns.

Shrinks an oversized PNG (base64-encoded) to fit within ``max_px`` on the
longest side, re-encodes as JPEG, and returns the result as a
(base64_string, mime_type) tuple ready for ``mcp.types.ImageContent``.

Environment overrides (clamped to safe ranges):
  JGS_IMAGE_MAX_PX        int  64–8192   default 1024
  JGS_IMAGE_JPEG_QUALITY  int  1–100     default 85

Note: JPEG quality 85 avoids the visible DCT blocking on SysML text labels
that occurs at q=75.

Note: ``Image.MAX_IMAGE_PIXELS`` is set at module level (not inside the
function) to avoid a process-wide race condition when multiple async
coroutines call ``shrink_and_encode`` concurrently. 200 M pixels is the
Pillow default cap — set explicitly here so the intent is clear.
"""
import base64
import io
import os

from PIL import Image, UnidentifiedImageError

_DEFAULT_MAX_PX = 1024
_DEFAULT_JPEG_QUALITY = 85  # 75 causes visible DCT blocking on SysML text labels

# Set once at import — NOT inside shrink_and_encode() — to avoid async races.
Image.MAX_IMAGE_PIXELS = 200_000_000


class ImageDecodeError(ValueError):
    """Raised when the bridge returns an image that cannot be decoded."""


def _max_px() -> int:
    try:
        return max(64, min(int(os.environ.get("JGS_IMAGE_MAX_PX", _DEFAULT_MAX_PX)), 8192))
    except ValueError:
        return _DEFAULT_MAX_PX


def _jpeg_quality() -> int:
    try:
        return max(1, min(int(os.environ.get("JGS_IMAGE_JPEG_QUALITY", _DEFAULT_JPEG_QUALITY)), 100))
    except ValueError:
        return _DEFAULT_JPEG_QUALITY


def shrink_and_encode(b64_png: str, *, max_px: int | None = None, jpeg_quality: int | None = None) -> tuple[str, str]:
    """Shrink a base64-encoded PNG and return ``(b64_jpeg, 'image/jpeg')``.

    Args:
        b64_png: Base64-encoded PNG bytes from the bridge.
        max_px: Override longest-edge pixel cap (default: JGS_IMAGE_MAX_PX or 1024).
        jpeg_quality: Override JPEG quality (default: JGS_IMAGE_JPEG_QUALITY or 85).

    Returns:
        Tuple of (base64_string, mime_type) for use in ImageContent.

    Raises:
        ImageDecodeError: If b64_png is invalid base64 or not a decodable image.
    """
    if max_px is None:
        max_px = _max_px()
    if jpeg_quality is None:
        jpeg_quality = _jpeg_quality()

    try:
        raw = base64.b64decode(b64_png, validate=True)
    except Exception as exc:
        raise ImageDecodeError(f"base64 decode failed: {exc}") from exc

    try:
        img = Image.open(io.BytesIO(raw)).convert("RGB")
    except Image.DecompressionBombError as exc:
        raise ImageDecodeError(f"image too large (decompression bomb): {exc}") from exc
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise ImageDecodeError(f"image decode failed: {exc}") from exc

    w, h = img.size
    longest = max(w, h)
    if longest > max_px:
        scale = max_px / longest
        img = img.resize((round(w * scale), round(h * scale)), Image.Resampling.LANCZOS)

    out = io.BytesIO()
    img.save(out, format="JPEG", quality=jpeg_quality, optimize=True)
    return base64.b64encode(out.getvalue()).decode(), "image/jpeg"
