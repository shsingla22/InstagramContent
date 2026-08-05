"""
Story Reel Builder — assembles the 6 AI-generated scenes into a
~30-second Instagram film with a storyline:

    title card → 6 captioned scenes (silent-film style) → outro CTA

Per scene: frame-interpolated 2.25x slow motion, upscale to
1080x1920 with sharpening, vignette + serif caption overlay, and
film-style fade cuts. Vinyl audio bed underneath, H.264+AAC
faststart output.

Run:  python3 -m short_videos.build_story_reel
"""

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
from short_videos.story_generator import STORY_DIR, STORYBOARD

OUT_PATH = "output/short_videos/reel_ai_story_cafe_racer.mp4"

TITLE_SEC = 2.5
OUTRO_SEC = 3.0
SLOW_FACTOR = 2.25          # 49 frames @24fps → ~4.6s per scene
FADE_SEC = 0.3

GOLD = PALETTE["gold"] + (255,)
CREAM = PALETTE["cream"] + (255,)


def _vignette_layer(strength: float = 0.5) -> Image.Image:
    vig = make_vignette(FRAME_WIDTH, FRAME_HEIGHT, strength=strength)[..., 0]
    alpha = ((1.0 - vig) * 255).clip(0, 255).astype("uint8")
    layer = Image.new("RGBA", (FRAME_WIDTH, FRAME_HEIGHT), (5, 3, 2, 255))
    layer.putalpha(Image.fromarray(alpha))
    return layer


def _with_shadow(ov: Image.Image) -> Image.Image:
    shadow = ov.filter(ImageFilter.GaussianBlur(3))
    base = Image.new("RGBA", ov.size, (0, 0, 0, 0))
    base.alpha_composite(shadow)
    base.alpha_composite(ov)
    return base


def build_title_card(path: str) -> None:
    img = Image.new("RGBA", (FRAME_WIDTH, FRAME_HEIGHT),
                    PALETTE["espresso"] + (255,))
    draw = ImageDraw.Draw(img)
    cy = FRAME_HEIGHT // 2
    eyebrow = _load_font(FONT_SERIF_BOLD, 34)
    _draw_tracked_text(draw, (FRAME_WIDTH // 2, cy - 220),
                       "THE RIDER'S GANG PRESENTS", eyebrow, GOLD, tracking=7)
    draw.line([(FRAME_WIDTH * 0.3, cy - 160), (FRAME_WIDTH * 0.7, cy - 160)],
              fill=GOLD, width=2)
    title = _load_font(FONT_SERIF_BOLD, 88)
    _draw_tracked_text(draw, (FRAME_WIDTH // 2, cy - 50), "THE NIGHT THEY",
                       title, CREAM, tracking=3)
    _draw_tracked_text(draw, (FRAME_WIDTH // 2, cy + 60), "RACED THE JUKEBOX",
                       title, CREAM, tracking=3)
    draw.line([(FRAME_WIDTH * 0.3, cy + 150), (FRAME_WIDTH * 0.7, cy + 150)],
              fill=GOLD, width=2)
    sub = _load_font(FONT_SERIF_ITALIC, 42)
    draw.text((FRAME_WIDTH // 2, cy + 220), "A true story from 1950s London",
              font=sub, fill=CREAM, anchor="mm")
    img.convert("RGB").save(path)


def build_outro_card(path: str) -> None:
    img = Image.new("RGBA", (FRAME_WIDTH, FRAME_HEIGHT),
                    PALETTE["espresso"] + (255,))
    draw = ImageDraw.Draw(img)
    cy = FRAME_HEIGHT // 2
    brand = _load_font(FONT_SERIF_BOLD, 80)
    _draw_tracked_text(draw, (FRAME_WIDTH // 2, cy - 40), "THE RIDER'S GANG",
                       brand, CREAM, tracking=8)
    draw.line([(FRAME_WIDTH * 0.3, cy + 40), (FRAME_WIDTH * 0.7, cy + 40)],
              fill=GOLD, width=3)
    cta = _load_font(FONT_SERIF_ITALIC, 44)
    draw.text((FRAME_WIDTH // 2, cy + 110),
              "The full story — link in bio", font=cta, fill=GOLD, anchor="mm")
    img.convert("RGB").save(path)


def build_scene_overlay(scene: dict, path: str) -> None:
    """Vignette + gold eyebrow + serif caption for one scene."""
    ov = Image.new("RGBA", (FRAME_WIDTH, FRAME_HEIGHT), (0, 0, 0, 0))
    ov.alpha_composite(_vignette_layer())
    draw = ImageDraw.Draw(ov)

    # bottom gradient for caption legibility
    grad_h = 560
    band = Image.new("L", (1, grad_h), 0)
    for i in range(grad_h):
        band.putpixel((0, i), int(190 * (i / grad_h) ** 1.5))
    band = band.resize((FRAME_WIDTH, grad_h))
    gradient = Image.new("RGBA", (FRAME_WIDTH, grad_h), (5, 3, 2, 255))
    gradient.putalpha(band)
    ov.alpha_composite(gradient, (0, FRAME_HEIGHT - grad_h))

    cy = FRAME_HEIGHT - 330
    eyebrow = _load_font(FONT_SERIF_BOLD, 30)
    _draw_tracked_text(draw, (FRAME_WIDTH // 2, cy - 80), scene["eyebrow"],
                       eyebrow, GOLD, tracking=6)
    cap_font = _load_font(FONT_SERIF_BOLD, 52)
    for i, line in enumerate(scene["caption"].split("\n")):
        draw.text((FRAME_WIDTH // 2, cy + i * 68), line,
                  font=cap_font, fill=CREAM, anchor="mm")

    _with_shadow(ov).save(path)


def preprocess_scene(clip: str, overlay: str, out: str) -> None:
    """Slow-mo, upscale, sharpen, caption, and fade one scene."""
    # 54fps interpolation / 2.25x slowdown lands exactly back on 24fps
    dur = 49 / 24 * SLOW_FACTOR
    subprocess.run([
        "ffmpeg", "-y", "-i", clip, "-i", overlay,
        "-filter_complex",
        "[0:v]minterpolate=fps=54:mi_mode=mci:mc_mode=aobmc:vsbmc=1,"
        "setpts=2.25*PTS,"
        "scale=-2:1920:flags=lanczos,crop=1080:1920,"
        "unsharp=5:5:0.6:5:5:0.0[v];"
        f"[v][1:v]overlay=0:0,"
        f"fade=t=in:st=0:d={FADE_SEC},fade=t=out:st={dur - FADE_SEC}:d={FADE_SEC}[outv]",
        "-map", "[outv]", "-r", "24",
        "-c:v", "libx264", "-preset", "fast", "-crf", "16",
        "-pix_fmt", "yuv420p", out,
    ], check=True, capture_output=True)


def card_to_video(png: str, seconds: float, out: str) -> None:
    subprocess.run([
        "ffmpeg", "-y", "-loop", "1", "-t", str(seconds), "-i", png,
        "-vf",
        f"fade=t=in:st=0:d={FADE_SEC},fade=t=out:st={seconds - FADE_SEC}:d={FADE_SEC}",
        "-r", "24", "-c:v", "libx264", "-preset", "fast", "-crf", "16",
        "-pix_fmt", "yuv420p", out,
    ], check=True, capture_output=True)


def main():
    tmp = os.path.join(STORY_DIR, ".assembly")
    os.makedirs(tmp, exist_ok=True)

    # cards
    title_png = os.path.join(tmp, "title.png")
    outro_png = os.path.join(tmp, "outro.png")
    build_title_card(title_png)
    build_outro_card(outro_png)
    segments = []

    print("[Assemble] Title card...")
    title_mp4 = os.path.join(tmp, "seg_00_title.mp4")
    card_to_video(title_png, TITLE_SEC, title_mp4)
    segments.append(title_mp4)

    for i, scene in enumerate(STORYBOARD, 1):
        clip = os.path.join(STORY_DIR, f"scene_{scene['id']}.mp4")
        if not os.path.exists(clip):
            print(f"ERROR: missing scene clip {clip}")
            sys.exit(1)
        print(f"[Assemble] Scene {i}/6: {scene['id']} "
              "(interpolate + upscale + caption)...")
        overlay = os.path.join(tmp, f"ov_{scene['id']}.png")
        build_scene_overlay(scene, overlay)
        seg = os.path.join(tmp, f"seg_{i:02d}_{scene['id']}.mp4")
        preprocess_scene(clip, overlay, seg)
        segments.append(seg)

    print("[Assemble] Outro card...")
    outro_mp4 = os.path.join(tmp, "seg_99_outro.mp4")
    card_to_video(outro_png, OUTRO_SEC, outro_mp4)
    segments.append(outro_mp4)

    # total duration for the audio bed
    scene_dur = 49 / 24 * SLOW_FACTOR
    total = TITLE_SEC + 6 * scene_dur + OUTRO_SEC
    wav = os.path.join(tmp, "bed.wav")
    build_audio_bed(total, "midnight", wav, seed=1959)

    # concat everything + mux audio
    concat_list = os.path.join(tmp, "concat.txt")
    with open(concat_list, "w") as f:
        for s in segments:
            f.write(f"file '{os.path.abspath(s)}'\n")

    print("[Assemble] Final concat + audio...")
    subprocess.run([
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", concat_list,
        "-i", wav,
        "-map", "0:v", "-map", "1:a",
        "-c:v", "libx264", "-preset", "medium", "-crf", "21",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart", "-shortest",
        OUT_PATH,
    ], check=True, capture_output=True)

    size_mb = os.path.getsize(OUT_PATH) / 1024 / 1024
    print(f"\nStory reel saved: {OUT_PATH} ({size_mb:.1f} MB, ~{total:.0f}s)")


if __name__ == "__main__":
    main()
