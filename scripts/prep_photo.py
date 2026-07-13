#!/usr/bin/env python3
"""
prep_photo.py — one-time local image prep.

Removes the background (rembg) and boosts local contrast (CLAHE) so the
subject sits on blank space with real highlights/shadows instead of being a
flat, dark blob once it's converted to ASCII.

Usage:
    python scripts/prep_photo.py path/to/your-photo.jpg source-prepped.png
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image
import cv2
from rembg import remove

# ---- tuning ---------------------------------------------------------------
CLIP_LIMIT = 2.5       # CLAHE strength — higher = punchier local contrast
TILE_GRID = (8, 8)     # CLAHE tile size
TARGET_MAX_DIM = 1200  # downscale huge photos before processing
# -----------------------------------------------------------------------------


def prep(src_path: str, dst_path: str) -> None:
    src = Path(src_path)
    if not src.exists():
        sys.exit(f"error: {src} not found")

    img = Image.open(src).convert("RGBA")

    # downscale if huge — keeps rembg fast and the later ASCII sampling sane
    if max(img.size) > TARGET_MAX_DIM:
        scale = TARGET_MAX_DIM / max(img.size)
        img = img.resize((int(img.width * scale), int(img.height * scale)), Image.LANCZOS)

    # 1. background removal
    no_bg = remove(img)

    # 2. CLAHE local contrast on the RGB channels, alpha preserved
    rgba = np.array(no_bg)
    rgb, alpha = rgba[:, :, :3], rgba[:, :, 3]

    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=CLIP_LIMIT, tileGridSize=TILE_GRID)
    l_channel = clahe.apply(l_channel)
    lab = cv2.merge((l_channel, a_channel, b_channel))
    rgb = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)

    out = np.dstack([rgb, alpha])
    Image.fromarray(out, "RGBA").save(dst_path)
    print(f"wrote {dst_path}  ({out.shape[1]}x{out.shape[0]})")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage: python scripts/prep_photo.py <input photo> <output png>")
    prep(sys.argv[1], sys.argv[2])
