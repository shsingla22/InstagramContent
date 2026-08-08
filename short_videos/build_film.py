"""
Film Builder — generates and assembles a complete short film for any
article, following the Ace Cafe formula end to end:

    FLUX photoreal stills → Wan 2.2 animation → captions + title/outro
    cards → mood-matched score with scene SFX → poster thumbnail →
    1080x1920 H.264 faststart MP4

Run:  HF_TOKEN=... python3 -m short_videos.build_film <slug> [--assemble-only]
List: python3 -m short_videos.build_film --list
"""

import argparse
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PIL import Image, ImageDraw

from short_videos import (
    FONT_SERIF_BOLD, FONT_SERIF_ITALIC, FRAME_HEIGHT, FRAME_WIDTH, PALETTE,
)
from short_videos.build_story_reel import (
    CREAM, GOLD, FADE_SEC, _vignette_layer, _with_shadow, card_to_video,
    draw_plain_fit, draw_tracked_fit, preprocess_scene,
)
from short_videos.film_score import build_film_audio
from short_videos.film_scripts import FILMS

FILMS_DIR = "output/short_videos/films"
TITLE_SEC = 2.5
OUTRO_SEC = 3.0
CLIP_SEC = 3.5625


# ── generation (FLUX + Wan via HF Spaces) ────────────────────────────

def generate_scenes(film: dict, film_dir: str) -> bool:
    from gradio_client import Client
    from short_videos.cinematic_generator import (
        FLUX_SPACE, WAN_SPACE, generate_still, animate_still,
    )
    token = os.environ.get("HF_TOKEN")
    if not token:
        print("ERROR: set HF_TOKEN")
        return False
    stills_dir = os.path.join(film_dir, "stills")
    os.makedirs(stills_dir, exist_ok=True)
    flux = Client(FLUX_SPACE, token=token, verbose=False)
    wan = Client(WAN_SPACE, token=token, verbose=False)

    ok = True
    for scene in film["scenes"]:
        print(f"[{scene['id']}]")
        still = os.path.join(stills_dir, f"{scene['id']}.png")
        clip = os.path.join(film_dir, f"scene_{scene['id']}.mp4")
        if not os.path.exists(still):
            if not generate_still(flux, scene, still):
                ok = False
                continue
            time.sleep(3)
        else:
            print("  still cached")
        if not os.path.exists(clip):
            if not animate_still(wan, scene, still, clip):
                ok = False
                continue
            time.sleep(3)
        else:
            print("  clip cached")
    return ok


# ── film-specific cards and thumbnail ────────────────────────────────

def build_title_card(film: dict, path: str) -> None:
    img = Image.new("RGBA", (FRAME_WIDTH, FRAME_HEIGHT), PALETTE["espresso"] + (255,))
    draw = ImageDraw.Draw(img)
    cy = FRAME_HEIGHT // 2
    draw_tracked_fit(draw, (FRAME_WIDTH // 2, cy - 220),
                     "THE RIDER'S GANG PRESENTS", FONT_SERIF_BOLD, 32, GOLD,
                     tracking=6)
    draw.line([(FRAME_WIDTH * 0.3, cy - 160), (FRAME_WIDTH * 0.7, cy - 160)],
              fill=GOLD, width=2)
    l1, l2 = film["title_lines"]
    draw_tracked_fit(draw, (FRAME_WIDTH // 2, cy - 50), l1,
                     FONT_SERIF_BOLD, 76, CREAM, tracking=2)
    draw_tracked_fit(draw, (FRAME_WIDTH // 2, cy + 55), l2,
                     FONT_SERIF_BOLD, 76, CREAM, tracking=2)
    draw.line([(FRAME_WIDTH * 0.3, cy + 140), (FRAME_WIDTH * 0.7, cy + 140)],
              fill=GOLD, width=2)
    draw_plain_fit(draw, (FRAME_WIDTH // 2, cy + 205), film["subtitle"],
                   FONT_SERIF_ITALIC, 40, CREAM)
    img.convert("RGB").save(path)


def build_outro_card(path: str) -> None:
    img = Image.new("RGBA", (FRAME_WIDTH, FRAME_HEIGHT), PALETTE["espresso"] + (255,))
    draw = ImageDraw.Draw(img)
    cy = FRAME_HEIGHT // 2
    draw_tracked_fit(draw, (FRAME_WIDTH // 2, cy - 40), "THE RIDER'S GANG",
                     FONT_SERIF_BOLD, 70, CREAM, tracking=6)
    draw.line([(FRAME_WIDTH * 0.3, cy + 40), (FRAME_WIDTH * 0.7, cy + 40)],
              fill=GOLD, width=3)
    draw_plain_fit(draw, (FRAME_WIDTH // 2, cy + 110),
                   "The full story — link in bio", FONT_SERIF_ITALIC, 42, GOLD)
    img.convert("RGB").save(path)


def build_scene_overlay(scene: dict, path: str) -> None:
    ov = Image.new("RGBA", (FRAME_WIDTH, FRAME_HEIGHT), (0, 0, 0, 0))
    ov.alpha_composite(_vignette_layer())
    draw = ImageDraw.Draw(ov)
    grad_h = 520
    band = Image.new("L", (1, grad_h), 0)
    for i in range(grad_h):
        band.putpixel((0, i), int(185 * (i / grad_h) ** 1.5))
    band = band.resize((FRAME_WIDTH, grad_h))
    gradient = Image.new("RGBA", (FRAME_WIDTH, grad_h), (5, 3, 2, 255))
    gradient.putalpha(band)
    ov.alpha_composite(gradient, (0, FRAME_HEIGHT - grad_h))
    cy = FRAME_HEIGHT - 310
    draw_tracked_fit(draw, (FRAME_WIDTH // 2, cy - 75), scene["eyebrow"],
                     FONT_SERIF_BOLD, 28, GOLD, tracking=5)
    for i, line in enumerate(scene["caption"].split("\n")):
        draw_plain_fit(draw, (FRAME_WIDTH // 2, cy + i * 60), line,
                       FONT_SERIF_BOLD, 46, CREAM)
    _with_shadow(ov).save(path)


def build_thumbnail(film: dict, still_path: str, out_path: str) -> None:
    base = Image.open(still_path).convert("RGB")
    base = base.resize((FRAME_WIDTH, FRAME_HEIGHT), Image.LANCZOS)
    img = base.convert("RGBA")
    ov = Image.new("RGBA", (FRAME_WIDTH, FRAME_HEIGHT), (0, 0, 0, 0))
    ov.alpha_composite(_vignette_layer(0.55))
    draw = ImageDraw.Draw(ov)
    for y0, y1, flip in ((0, 420, True), (FRAME_HEIGHT - 700, FRAME_HEIGHT, False)):
        h = y1 - y0
        band = Image.new("L", (1, h), 0)
        for i in range(h):
            p = i / h
            band.putpixel((0, i), int(210 * ((1 - p) if flip else p) ** 1.4))
        band = band.resize((FRAME_WIDTH, h))
        g = Image.new("RGBA", (FRAME_WIDTH, h), (5, 3, 2, 255))
        g.putalpha(band)
        ov.alpha_composite(g, (0, y0))
    draw_tracked_fit(draw, (FRAME_WIDTH // 2, 170), "THE RIDER'S GANG",
                     FONT_SERIF_BOLD, 34, GOLD, tracking=7)
    draw.line([(FRAME_WIDTH * 0.34, 220), (FRAME_WIDTH * 0.66, 220)],
              fill=GOLD, width=2)
    cy = FRAME_HEIGHT - 430
    l1, l2 = film["title_lines"]
    draw_tracked_fit(draw, (FRAME_WIDTH // 2, cy), l1,
                     FONT_SERIF_BOLD, 82, CREAM, tracking=2)
    draw_tracked_fit(draw, (FRAME_WIDTH // 2, cy + 105), l2,
                     FONT_SERIF_BOLD, 82, CREAM, tracking=2)
    draw_plain_fit(draw, (FRAME_WIDTH // 2, cy + 200), film["subtitle"],
                   FONT_SERIF_ITALIC, 42, GOLD)
    img.alpha_composite(_with_shadow(ov))
    img.convert("RGB").save(out_path, quality=90)


# ── assembly ─────────────────────────────────────────────────────────

def assemble(slug: str, film: dict, film_dir: str) -> str:
    tmp = os.path.join(film_dir, ".assembly")
    os.makedirs(tmp, exist_ok=True)
    out_path = os.path.join(FILMS_DIR, f"{slug}.mp4")
    thumb_path = os.path.join(FILMS_DIR, f"{slug}_cover.jpg")

    title_png = os.path.join(tmp, "title.png")
    outro_png = os.path.join(tmp, "outro.png")
    build_title_card(film, title_png)
    build_outro_card(outro_png)

    segments = []
    title_mp4 = os.path.join(tmp, "seg_00_title.mp4")
    card_to_video(title_png, TITLE_SEC, title_mp4, fade_in=False)
    segments.append(title_mp4)

    for i, scene in enumerate(film["scenes"], 1):
        clip = os.path.join(film_dir, f"scene_{scene['id']}.mp4")
        if not os.path.exists(clip):
            print(f"ERROR: missing {clip}")
            sys.exit(1)
        print(f"[Assemble] Scene {i}/{len(film['scenes'])}: {scene['id']}")
        overlay = os.path.join(tmp, f"ov_{scene['id']}.png")
        build_scene_overlay(scene, overlay)
        seg = os.path.join(tmp, f"seg_{i:02d}.mp4")
        preprocess_scene(clip, overlay, seg)
        segments.append(seg)

    outro_mp4 = os.path.join(tmp, "seg_99_outro.mp4")
    card_to_video(outro_png, OUTRO_SEC, outro_mp4)
    segments.append(outro_mp4)

    build_thumbnail(film, os.path.join(film_dir, "stills",
                                       f"{film['thumb_scene']}.png"), thumb_path)

    total = TITLE_SEC + len(film["scenes"]) * CLIP_SEC + OUTRO_SEC
    wav = os.path.join(tmp, "score.wav")
    build_film_audio(film, total, TITLE_SEC, CLIP_SEC, wav)

    concat_list = os.path.join(tmp, "concat.txt")
    with open(concat_list, "w") as f:
        for s in segments:
            f.write(f"file '{os.path.abspath(s)}'\n")

    print("[Assemble] Final concat + audio + thumbnail...")
    no_thumb = os.path.join(tmp, "final_no_thumb.mp4")
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list,
        "-i", wav, "-map", "0:v", "-map", "1:a",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart", "-shortest", no_thumb,
    ], check=True, capture_output=True)
    subprocess.run([
        "ffmpeg", "-y", "-i", no_thumb, "-i", thumb_path,
        "-map", "0", "-map", "1", "-c", "copy", "-c:v:1", "mjpeg",
        "-disposition:v:1", "attached_pic", "-movflags", "+faststart",
        out_path,
    ], check=True, capture_output=True)

    size = os.path.getsize(out_path) / 1024 / 1024
    print(f"\nFilm saved: {out_path} ({size:.1f} MB, ~{total:.0f}s)")
    return out_path


def main():
    parser = argparse.ArgumentParser(description="Generate + assemble a film")
    parser.add_argument("slug", nargs="?", help="Article slug (see --list)")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--assemble-only", action="store_true",
                        help="Skip generation; scenes must already exist")
    args = parser.parse_args()

    if args.list or not args.slug:
        for s in FILMS:
            print(s)
        return

    film = FILMS[args.slug]
    film_dir = os.path.join(FILMS_DIR, args.slug)
    os.makedirs(film_dir, exist_ok=True)

    if not args.assemble_only:
        if not generate_scenes(film, film_dir):
            print("Generation incomplete (quota?) — re-run to resume.")
            sys.exit(1)
    assemble(args.slug, film, film_dir)


if __name__ == "__main__":
    main()
