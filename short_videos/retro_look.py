"""
Retro / old-money color grade for real photographs.

The grade is deliberately subtle — the photos must still read as real
footage. Applied once to each oversized source image before the Ken
Burns pass; per-frame film grain and flicker are added at render time
so the grain moves like real film stock.
"""

import numpy as np
from PIL import Image, ImageEnhance

from short_videos import PALETTE


def grade_photo(img: Image.Image) -> Image.Image:
    """Apply the warm old-money grade to a source photograph."""
    img = img.convert("RGB")

    # Gentle desaturation — old Kodachrome, not black-and-white
    img = ImageEnhance.Color(img).enhance(0.82)
    img = ImageEnhance.Contrast(img).enhance(1.06)

    arr = np.asarray(img).astype(np.float32)

    # Warm tone curve: lift shadows toward espresso brown, pull
    # highlights toward cream. Blended at low strength so skin,
    # chrome, and leather keep their natural color.
    luma = arr.mean(axis=2, keepdims=True) / 255.0
    shadow_tint = np.array(PALETTE["espresso"], dtype=np.float32)
    highlight_tint = np.array(PALETTE["cream"], dtype=np.float32)
    tint = shadow_tint * (1.0 - luma) + highlight_tint * luma
    arr = arr * 0.88 + tint * 0.12

    # Slight warmth push in the channels themselves
    arr[..., 0] *= 1.04   # red up
    arr[..., 2] *= 0.94   # blue down

    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


def make_vignette(width: int, height: int, strength: float = 0.40) -> np.ndarray:
    """Radial darkening mask (float32 multiplier, HxWx1)."""
    yy, xx = np.mgrid[0:height, 0:width].astype(np.float32)
    cx, cy = width / 2.0, height / 2.0
    # normalized distance from center, corners ~1.0
    dist = np.sqrt(((xx - cx) / cx) ** 2 + ((yy - cy) / cy) ** 2) / np.sqrt(2.0)
    mask = 1.0 - strength * np.clip(dist - 0.35, 0.0, 1.0) ** 2 / (0.65 ** 2)
    return mask[..., np.newaxis]


def apply_film_frame_effects(
    frame: np.ndarray,
    vignette: np.ndarray,
    rng: np.random.Generator,
    grain_strength: float = 3.5,
) -> np.ndarray:
    """
    Per-frame film effects: moving grain, vignette, and a faint
    exposure flicker. `frame` is uint8 HxWx3; returns uint8.
    """
    out = frame.astype(np.float32)

    # Exposure flicker (±1%) — the heartbeat of projected film
    out *= rng.uniform(0.99, 1.01)

    # Vignette
    out *= vignette

    # Film grain — coarse noise upsampled so it reads as grain, not
    # digital noise. Generated at quarter resolution so it stays
    # soft, filmic, and compressible.
    h, w = frame.shape[:2]
    grain = rng.normal(0.0, grain_strength, size=(h // 4, w // 4, 1)).astype(np.float32)
    grain = np.repeat(np.repeat(grain, 4, axis=0), 4, axis=1)[:h, :w]
    out += grain

    return np.clip(out, 0, 255).astype(np.uint8)
