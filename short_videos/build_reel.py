"""
Reel Builder — turns a raw AI-generated clip into a finished
Instagram reel engineered for retention:

    - Motion from frame zero (no static intro — stops the scroll)
    - Curiosity hook text visible in the first second
    - Slow-motion (2x frame-interpolated) so the AI footage breathes
    - Boomerang loop (forward + reverse) — the reel loops seamlessly,
      driving rewatches, which the algorithm rewards
    - Brand serif typography + vignette (old-money look)
    - Vinyl-crackle audio bed
    - 1080x1920 H.264 + AAC, faststart

Run:  python3 -m short_videos.build_reel \
          --clip output/short_videos/ai_clip_cafe_racer.mp4 \
          --out  output/short_videos/reel_ai_cafe_racer.mp4
"""

import argparse
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PIL import Image, ImageDraw, ImageFilter

from short_videos import (
    FONT_SERIF_BOLD,
    FONT_SERIF_ITALIC,
    FRAME_HEIGHT,
    FRAME_WIDTH,
    PALETTE,
)
from short_videos.audio_bed import build_audio_bed
from short_videos.generator import _draw_tracked_text, _load_font
from short_videos.retro_look import make_vignette


def build_hook_overlay(path: str) -> None:
    """
    Full-duration overlay: vignette + brand eyebrow at top + curiosity
    hook at the bottom. Rendered once, composited over every frame.
    """
    import numpy as np

    ov = Image.new("RGBA", (FRAME_WIDTH, FRAME_HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(ov)
    gold = PALETTE["gold"] + (255,)
    cream = PALETTE["cream"] + (255,)

    # vignette as alpha-black so the AI footage gets the old-money edge
    vig = make_vignette(FRAME_WIDTH, FRAME_HEIGHT, strength=0.5)[..., 0]
    vig_alpha = ((1.0 - vig) * 255).clip(0, 255).astype("uint8")
    black = Image.new("RGBA", (FRAME_WIDTH, FRAME_HEIGHT), (5, 3, 2, 255))
    black.putalpha(Image.fromarray(vig_alpha))
    ov.alpha_composite(black)

    # top brand eyebrow
    eyebrow_font = _load_font(FONT_SERIF_BOLD, 32)
    _draw_tracked_text(draw, (FRAME_WIDTH // 2, 150), "THE RIDER'S GANG",
                       eyebrow_font, gold, tracking=8)
    draw.line([(FRAME_WIDTH * 0.36, 200), (FRAME_WIDTH * 0.64, 200)],
              fill=gold, width=2)

    # bottom text block: dark gradient + hook
    grad_h = 640
    band = Image.new("L", (1, grad_h), 0)
    for i in range(grad_h):
        band.putpixel((0, i), int(200 * (i / grad_h) ** 1.5))
    band = band.resize((FRAME_WIDTH, grad_h))
    gradient = Image.new("RGBA", (FRAME_WIDTH, grad_h), (5, 3, 2, 255))
    gradient.putalpha(band)
    ov.alpha_composite(gradient, (0, FRAME_HEIGHT - grad_h))

    cy = FRAME_HEIGHT - 400
    eyebrow2 = _load_font(FONT_SERIF_BOLD, 30)
    _draw_tracked_text(draw, (FRAME_WIDTH // 2, cy - 90), "LONDON • 1950s",
                       eyebrow2, gold, tracking=6)
    title_font = _load_font(FONT_SERIF_BOLD, 84)
    _draw_tracked_text(draw, (FRAME_WIDTH // 2, cy), "THE CAFÉ RACER",
                       title_font, cream, tracking=3)
    hook_font = _load_font(FONT_SERIF_ITALIC, 44)
    draw.text((FRAME_WIDTH // 2, cy + 90),
              "They raced jukebox songs at 100 mph.",
              font=hook_font, fill=cream, anchor="mm")
    hook2_font = _load_font(FONT_SERIF_ITALIC, 38)
    draw.text((FRAME_WIDTH // 2, cy + 150),
              "The full story — link in bio",
              font=hook2_font, fill=gold, anchor="mm")

    # soft shadow for legibility
    shadow = ov.filter(ImageFilter.GaussianBlur(3))
    base = Image.new("RGBA", ov.size, (0, 0, 0, 0))
    base.alpha_composite(shadow)
    base.alpha_composite(ov)
    base.save(path)


def build_reel(clip_path: str, out_path: str) -> None:
    workdir = os.path.dirname(out_path)
    overlay_path = os.path.join(workdir, ".reel_overlay.png")
    slow_path = os.path.join(workdir, ".reel_slow.mp4")
    wav_path = os.path.join(workdir, ".reel_audio.wav")

    build_hook_overlay(overlay_path)

    # 1) frame-interpolate 24→48fps, slow 2x, upscale to 1080x1920
    print("[Reel] Interpolating + upscaling (this is CPU-heavy)...")
    subprocess.run([
        "ffmpeg", "-y", "-i", clip_path,
        "-vf",
        "minterpolate=fps=48:mi_mode=mci:mc_mode=aobmc:vsbmc=1,"
        "setpts=2.0*PTS,"
        "scale=1080:1929:flags=lanczos,crop=1080:1920",
        "-r", "24",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-pix_fmt", "yuv420p", slow_path,
    ], check=True, capture_output=True)

    # duration of the slowed clip → boomerang doubles it
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", slow_path],
        capture_output=True, text=True, check=True,
    )
    slow_dur = float(probe.stdout.strip())
    total_dur = slow_dur * 2.0

    # 2) audio bed for the final duration
    build_audio_bed(total_dur, "midnight", wav_path, seed=1950)

    # 3) boomerang (forward + reverse), overlay typography, mux audio
    print("[Reel] Building boomerang loop + typography + audio...")
    subprocess.run([
        "ffmpeg", "-y",
        "-i", slow_path,
        "-i", overlay_path,
        "-i", wav_path,
        "-filter_complex",
        # reverse-first boomerang: the reel opens on the clip's final
        # (most dramatic) frame, pulls away, then returns — and the
        # last frame equals the first, so the loop is seamless
        "[0:v]split[fwd][t];"
        "[t]reverse[rev];"
        "[rev][fwd]concat=n=2:v=1:a=0[loop];"
        "[loop][1:v]overlay=0:0[outv]",
        "-map", "[outv]", "-map", "2:a",
        "-c:v", "libx264", "-preset", "medium", "-crf", "22",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart", "-shortest",
        out_path,
    ], check=True, capture_output=True)

    for p in (overlay_path, slow_path, wav_path):
        if os.path.exists(p):
            os.remove(p)

    size_mb = os.path.getsize(out_path) / 1024 / 1024
    print(f"[Reel] Saved: {out_path} ({size_mb:.1f} MB, {total_dur:.1f}s loop)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build Instagram reel from AI clip")
    parser.add_argument("--clip", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    build_reel(args.clip, args.out)
