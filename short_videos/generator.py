"""
Short Video Generator — renders one cinematic MP4 per article.

Pipeline per video:
    1. Download the article's real photographs (oversized, from the
       same sources the posts module uses)
    2. Apply the retro/old-money grade (retro_look.py)
    3. Execute the creative direction (creative_director.py):
       Ken Burns camera moves + serif typography, frame by frame
    4. Add per-frame film grain / flicker / vignette
    5. Crossfade scenes, mux with the vinyl audio bed, encode
       H.264 + AAC with +faststart via ffmpeg

Run:  python3 -m short_videos.generator            # all articles
      python3 -m short_videos.generator --limit 1  # first article only
"""

import argparse
import math
import os
import subprocess
import sys
import urllib.request

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.content_data import get_all_articles
from short_videos import (
    CROSSFADE_SEC,
    FONT_SERIF_BOLD,
    FONT_SERIF_ITALIC,
    FPS,
    FRAME_HEIGHT,
    FRAME_WIDTH,
    PALETTE,
    SHORT_VIDEOS_DIR,
    SOURCE_HEIGHT,
    SOURCE_WIDTH,
)
from short_videos.audio_bed import build_audio_bed
from short_videos.creative_director import SHORT_VIDEO_SCRIPTS
from short_videos.retro_look import apply_film_frame_effects, grade_photo, make_vignette

CACHE_DIR = os.path.join(SHORT_VIDEOS_DIR, ".photo_cache")

# Stable, human-friendly output file names per article slug
SHORT_NAMES = {
    "the-cafe-racer-how-coffee-gave-birth-to-motorcycle-culture": "the-cafe-racer",
    "the-saddlebag-from-horse-leather-to-high-fashion": "the-saddlebag",
    "the-polo-shirt-from-horseback-to-high-street": "the-polo-shirt",
    "denim-and-the-rider-how-jeans-were-born-in-the-saddle": "denim-and-the-rider",
    "the-riding-crop-from-horse-command-to-fashion-icon": "the-riding-crop",
    "hermes-from-horse-harnesses-to-high-fashion": "hermes",
    "belstaff-the-jacket-that-built-a-riding-legend": "belstaff",
    "the-gucci-horsebit-loafer-born-in-the-saddle": "gucci-horsebit",
    "riding-boots-from-cavalry-to-catwalk": "riding-boots",
    "leh-ladakh-the-ride-that-changes-everything": "leh-ladakh",
}


# ── Photo sourcing ───────────────────────────────────────────────────

def _resize_url(url: str) -> str:
    """Rewrite an Unsplash URL to the oversized portrait render size."""
    base = url.split("?")[0]
    return f"{base}?w={SOURCE_WIDTH}&h={SOURCE_HEIGHT}&fit=crop"


def fetch_photo(url: str, cache_name: str) -> Image.Image | None:
    """Download (with cache) and grade one source photograph."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    path = os.path.join(CACHE_DIR, cache_name)
    if not os.path.exists(path):
        try:
            req = urllib.request.Request(
                _resize_url(url), headers={"User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(req, timeout=30) as resp, open(path, "wb") as f:
                f.write(resp.read())
        except Exception as e:
            print(f"    Warning: download failed for {url}: {e}")
            return None
    try:
        img = Image.open(path).convert("RGB")
        if img.size != (SOURCE_WIDTH, SOURCE_HEIGHT):
            img = img.resize((SOURCE_WIDTH, SOURCE_HEIGHT), Image.LANCZOS)
        return grade_photo(img)
    except Exception as e:
        print(f"    Warning: could not open cached photo {path}: {e}")
        return None


def make_outro_card() -> Image.Image:
    """Generated cream brand card used as the final scene's 'photo'."""
    img = Image.new("RGB", (SOURCE_WIDTH, SOURCE_HEIGHT), PALETTE["cream"])
    draw = ImageDraw.Draw(img)
    # faint concentric rules for a letterpress feel
    gold = PALETTE["gold"]
    for inset in (90, 110):
        draw.rectangle(
            [inset, inset, SOURCE_WIDTH - inset, SOURCE_HEIGHT - inset],
            outline=gold, width=3 if inset == 90 else 1,
        )
    return img


# ── Ken Burns camera ─────────────────────────────────────────────────

def _ease(p: float) -> float:
    """Cosine ease-in-out."""
    return 0.5 - 0.5 * math.cos(math.pi * p)


# each move maps progress → (zoom, center_x_offset, center_y_offset)
# offsets are fractions of the available slack
MOVES = {
    "zoom_in":  lambda p: (1.02 + 0.11 * p, 0.0, 0.0),
    "zoom_out": lambda p: (1.13 - 0.11 * p, 0.0, 0.0),
    "pan_left": lambda p: (1.10, 0.9 - 1.8 * p, 0.05),
    "pan_right": lambda p: (1.10, -0.9 + 1.8 * p, 0.05),
    "drift_up": lambda p: (1.06 + 0.04 * p, 0.0, 0.55 - 1.1 * p),
}


def ken_burns_frame(src: Image.Image, move: str, progress: float) -> Image.Image:
    """Crop one 1080x1920 frame out of the oversized source."""
    zoom, ox, oy = MOVES[move](_ease(progress))
    crop_w = SOURCE_WIDTH / zoom
    crop_h = SOURCE_HEIGHT / zoom
    slack_x = (SOURCE_WIDTH - crop_w) / 2.0
    slack_y = (SOURCE_HEIGHT - crop_h) / 2.0
    cx = SOURCE_WIDTH / 2.0 + ox * slack_x
    cy = SOURCE_HEIGHT / 2.0 + oy * slack_y
    left = max(0.0, min(SOURCE_WIDTH - crop_w, cx - crop_w / 2.0))
    top = max(0.0, min(SOURCE_HEIGHT - crop_h, cy - crop_h / 2.0))
    box = (int(left), int(top), int(left + crop_w), int(top + crop_h))
    return src.crop(box).resize((FRAME_WIDTH, FRAME_HEIGHT), Image.BILINEAR)


# ── Typography overlays ──────────────────────────────────────────────

def _load_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def _draw_tracked_text(draw, xy, text, font, fill, tracking=0, anchor="mm"):
    """Draw text with letterspacing (tracking, in px between glyphs)."""
    if tracking <= 0:
        draw.text(xy, text, font=font, fill=fill, anchor=anchor)
        return
    widths = [draw.textlength(ch, font=font) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = xy[0] - total / 2.0
    for ch, w in zip(text, widths):
        draw.text((x, xy[1]), ch, font=font, fill=fill, anchor="lm")
        x += w + tracking


def build_overlay(scene: dict) -> Image.Image:
    """
    Pre-render one scene's typography as an RGBA overlay. Includes a
    soft dark gradient behind the text so it stays readable over any
    photograph.
    """
    ov = Image.new("RGBA", (FRAME_WIDTH, FRAME_HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(ov)
    kind = scene["kind"]
    gold = PALETTE["gold"] + (255,)
    cream = PALETTE["cream"] + (255,)
    espresso = PALETTE["espresso"] + (255,)

    def gradient(y0, y1, max_alpha=170):
        band = Image.new("L", (1, y1 - y0), 0)
        for i in range(y1 - y0):
            p = i / max(1, y1 - y0 - 1)
            band.putpixel((0, i), int(max_alpha * _ease(p)))
        band = band.resize((FRAME_WIDTH, y1 - y0))
        black = Image.new("RGBA", (FRAME_WIDTH, y1 - y0), (5, 3, 2, 255))
        black.putalpha(band)
        ov.alpha_composite(black, (0, y0))

    if kind == "title":
        gradient(int(FRAME_HEIGHT * 0.45), FRAME_HEIGHT, 215)
        cy = int(FRAME_HEIGHT * 0.72)
        eyebrow_font = _load_font(FONT_SERIF_BOLD, 30)
        _draw_tracked_text(draw, (FRAME_WIDTH // 2, cy - 130), scene["eyebrow"],
                           eyebrow_font, gold, tracking=6)
        # gold rules flanking the eyebrow
        draw.line([(FRAME_WIDTH * 0.22, cy - 90), (FRAME_WIDTH * 0.78, cy - 90)],
                  fill=gold, width=2)
        title_font = _load_font(FONT_SERIF_BOLD, 92)
        for i, line in enumerate(scene["text"].split("\n")):
            _draw_tracked_text(draw, (FRAME_WIDTH // 2, cy + i * 105), line,
                               title_font, cream, tracking=3)
        n_lines = len(scene["text"].split("\n"))
        foot_font = _load_font(FONT_SERIF_ITALIC, 40)
        draw.text((FRAME_WIDTH // 2, cy + n_lines * 105 + 30), scene["footnote"],
                  font=foot_font, fill=cream, anchor="mm")

    elif kind == "beat":
        gradient(int(FRAME_HEIGHT * 0.52), FRAME_HEIGHT, 205)
        cy = int(FRAME_HEIGHT * 0.78)
        eyebrow_font = _load_font(FONT_SERIF_BOLD, 30)
        _draw_tracked_text(draw, (FRAME_WIDTH // 2, cy - 110), scene["eyebrow"],
                           eyebrow_font, gold, tracking=6)
        body_font = _load_font(FONT_SERIF_BOLD, 52)
        for i, line in enumerate(scene["text"].split("\n")):
            draw.text((FRAME_WIDTH // 2, cy + i * 68), line,
                      font=body_font, fill=cream, anchor="mm")

    elif kind == "quote":
        # full-frame dim + centered italic quote between gold rules
        dim = Image.new("RGBA", (FRAME_WIDTH, FRAME_HEIGHT), (5, 3, 2, 150))
        ov.alpha_composite(dim)
        cy = FRAME_HEIGHT // 2
        quote_font = _load_font(FONT_SERIF_ITALIC, 54)
        lines = scene["text"].split("\n")
        start_y = cy - (len(lines) - 1) * 38
        draw.line([(FRAME_WIDTH * 0.3, start_y - 110), (FRAME_WIDTH * 0.7, start_y - 110)],
                  fill=gold, width=2)
        for i, line in enumerate(lines):
            draw.text((FRAME_WIDTH // 2, start_y + i * 76), line,
                      font=quote_font, fill=cream, anchor="mm")
        end_y = start_y + (len(lines) - 1) * 76
        draw.line([(FRAME_WIDTH * 0.3, end_y + 110), (FRAME_WIDTH * 0.7, end_y + 110)],
                  fill=gold, width=2)

    elif kind == "outro":
        cy = FRAME_HEIGHT // 2
        brand_font = _load_font(FONT_SERIF_BOLD, 76)
        _draw_tracked_text(draw, (FRAME_WIDTH // 2, cy - 40), scene["text"],
                           brand_font, espresso, tracking=8)
        draw.line([(FRAME_WIDTH * 0.3, cy + 40), (FRAME_WIDTH * 0.7, cy + 40)],
                  fill=gold, width=3)
        foot_font = _load_font(FONT_SERIF_ITALIC, 42)
        draw.text((FRAME_WIDTH // 2, cy + 110), scene["footnote"],
                  font=foot_font, fill=espresso, anchor="mm")

    # soft shadow pass for legibility over busy photos
    if kind != "outro":
        shadow = ov.filter(ImageFilter.GaussianBlur(3))
        base = Image.new("RGBA", ov.size, (0, 0, 0, 0))
        base.alpha_composite(shadow)
        base.alpha_composite(ov)
        return base
    return ov


# ── Scene frame production ───────────────────────────────────────────

def scene_frame(src, scene, overlay, idx, n_frames, vignette, rng):
    """Render frame `idx` of a scene as a uint8 HxWx3 array."""
    progress = idx / max(1, n_frames - 1)
    frame = ken_burns_frame(src, scene["move"], progress)

    # text fades in over the first 0.5s of the scene
    fade = min(1.0, idx / (FPS * 0.5))
    if fade >= 1.0:
        frame.paste(overlay, (0, 0), overlay)
    elif fade > 0:
        faded = overlay.copy()
        alpha = faded.getchannel("A").point(lambda a: int(a * fade))
        faded.putalpha(alpha)
        frame.paste(faded, (0, 0), faded)

    arr = np.asarray(frame)
    return apply_film_frame_effects(arr, vignette, rng)


# ── Per-article rendering ────────────────────────────────────────────

def render_short_video(article, script, out_path: str) -> bool:
    """Render one article's short video to out_path. Returns success."""
    sources = {
        "hero": fetch_photo(article.hero_image, f"{article.slug}_hero.jpg"),
        "alt1": fetch_photo(article.additional_images[0], f"{article.slug}_alt1.jpg"),
        "alt2": fetch_photo(article.additional_images[1], f"{article.slug}_alt2.jpg"),
        "outro": make_outro_card(),
    }
    # fall back to hero for any failed download
    if sources["hero"] is None:
        print("    ERROR: hero image unavailable; skipping article")
        return False
    for key in ("alt1", "alt2"):
        if sources[key] is None:
            sources[key] = sources["hero"]

    scenes = script["scenes"]
    xfade_frames = int(CROSSFADE_SEC * FPS)
    scene_frames = [int(s["duration"] * FPS) for s in scenes]
    total_frames = sum(scene_frames) - xfade_frames * (len(scenes) - 1)
    duration = total_frames / FPS

    # audio bed
    wav_path = out_path.replace(".mp4", ".wav")
    build_audio_bed(duration, script["mood"], wav_path,
                    seed=abs(hash(article.slug)) % 10000)

    overlays = [build_overlay(s) for s in scenes]
    vignette = make_vignette(FRAME_WIDTH, FRAME_HEIGHT)
    rng = np.random.default_rng(abs(hash(article.slug)) % 10000)

    ffmpeg = subprocess.Popen(
        [
            "ffmpeg", "-y",
            "-f", "rawvideo", "-pix_fmt", "rgb24",
            "-s", f"{FRAME_WIDTH}x{FRAME_HEIGHT}", "-r", str(FPS), "-i", "-",
            "-i", wav_path,
            "-c:v", "libx264", "-preset", "medium", "-crf", "26",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "128k",
            "-movflags", "+faststart", "-shortest",
            out_path,
        ],
        stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )

    try:
        # stream scenes with crossfade blending between them
        pending = None  # tail frames of previous scene for blending
        for si, scene in enumerate(scenes):
            src = sources[scene["image"]]
            n = scene_frames[si]
            overlay = overlays[si]
            is_last = si == len(scenes) - 1
            tail_start = n - xfade_frames if not is_last else n

            for idx in range(n):
                frame = scene_frame(src, scene, overlay, idx, n, vignette, rng)
                if pending is not None and idx < xfade_frames:
                    # blend previous scene's tail into this scene's head
                    t = _ease((idx + 1) / xfade_frames)
                    frame = (
                        pending[idx].astype(np.float32) * (1 - t)
                        + frame.astype(np.float32) * t
                    ).astype(np.uint8)
                if idx >= tail_start:
                    # buffer tail frames for the next scene's blend
                    if idx == tail_start:
                        tail_buf = []
                    tail_buf.append(frame)
                    continue  # do not emit yet
                ffmpeg.stdin.write(frame.tobytes())
            pending = tail_buf if not is_last else None

        ffmpeg.stdin.close()
        ffmpeg.wait(timeout=300)
    except Exception as e:
        print(f"    ERROR during render: {e}")
        ffmpeg.kill()
        return False
    finally:
        if os.path.exists(wav_path):
            os.remove(wav_path)

    ok = ffmpeg.returncode == 0 and os.path.exists(out_path)
    if ok:
        size_mb = os.path.getsize(out_path) / 1024 / 1024
        print(f"    Saved: {out_path} ({size_mb:.1f} MB, {duration:.1f}s)")
    else:
        print(f"    ERROR: ffmpeg failed for {out_path}")
    return ok


def generate_all_short_videos(limit: int | None = None) -> dict:
    """Render short videos for all scripted articles. Returns manifest."""
    os.makedirs(SHORT_VIDEOS_DIR, exist_ok=True)
    articles = {a.slug: a for a in get_all_articles()}
    manifest = {}

    slugs = list(SHORT_VIDEO_SCRIPTS.keys())
    if limit:
        slugs = slugs[:limit]

    print(f"=== Short Video Module — rendering {len(slugs)} video(s) ===\n")
    for i, slug in enumerate(slugs, 1):
        article = articles.get(slug)
        if article is None:
            print(f"[{i}] SKIP: no article data for {slug}")
            continue
        out_path = os.path.join(
            SHORT_VIDEOS_DIR, f"short_{i:02d}_{SHORT_NAMES[slug]}.mp4"
        )
        print(f"[{i}/{len(slugs)}] {article.title}")
        if render_short_video(article, SHORT_VIDEO_SCRIPTS[slug], out_path):
            manifest[slug] = out_path

    import json
    manifest_path = os.path.join(SHORT_VIDEOS_DIR, "short_video_manifest.json")
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"\nManifest saved: {manifest_path}")
    print(f"Rendered {len(manifest)}/{len(slugs)} videos.")
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Render short videos")
    parser.add_argument("--limit", type=int, default=None,
                        help="Only render the first N videos")
    args = parser.parse_args()
    generate_all_short_videos(limit=args.limit)
