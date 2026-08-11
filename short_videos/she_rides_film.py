"""
She Rides — "Never Assume". The Apex Series stunt reel.

Fully AI-generated (Wan 2.2 A14B). Subverted-expectation arc: the
paddock assumes she's a spectator → she suits up, drops the visor,
and owns the track (knee-down apex, wheelie) → helmet-off reveal
and a smirk that loops back to the opening walk.

Character consistency: every prompt carries the same rider and bike
description (black-and-gold leathers, black-and-gold superbike),
matching the approved FLUX previews.

Music: apex_rock — coiled chug under the walk, full-band detonation
on the SHE RIDES card, dead-stop silence right before the reveal.

Run:  HF_TOKEN=... python3 -m short_videos.she_rides_film
      python3 -m short_videos.she_rides_film --assemble-only
      HF_TOKEN=... python3 -m short_videos.she_rides_film --only 03_apex
"""

import argparse
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PIL import Image, ImageDraw

from short_videos import (
    FONT_SERIF_BOLD, FONT_SERIF_ITALIC, FRAME_HEIGHT, FRAME_WIDTH,
)
from short_videos.build_story_reel import (
    CREAM, GOLD, _vignette_layer, _with_shadow, draw_plain_fit,
    draw_tracked_fit,
)

AI_DIR = "output/short_videos/films/she-rides-wan"
OUT_PATH = "output/short_videos/films/she-rides-never-assume.mp4"
THUMB_PATH = "output/short_videos/films/she-rides-never-assume_cover.jpg"

RIDER = (
    "a strikingly beautiful young woman with a stunning athletic "
    "figure and long dark wavy hair, wearing fitted black-and-gold "
    "one-piece motorcycle racing leathers"
)
BIKE = "a black and gold liter-class superbike with aggressive race fairings"
STYLE = (
    "Cinematic vertical 9:16 video, shot on 35mm film, cinematic color "
    "grade, film grain, realistic physics and correct human anatomy, "
    "golden hour light at a racetrack, documentary realism, no text or "
    "captions in the image."
)

SCENES = [
    {
        "id": "01_paddock",
        "prompt": (
            f"{RIDER}, the racing suit zipped over a black athletic "
            f"crew-neck top visible at the collar, "
            f"carrying a racing helmet under one arm, walks in slow "
            f"confident slow-motion stride through a race paddock past "
            f"rows of parked superbikes, mechanics glancing up as she "
            f"passes, her hair moving as she walks. Camera: smooth "
            f"tracking shot moving backward in front of her. " + STYLE
        ),
        "caption": "Everyone thought\nshe came to watch.",
        "eyebrow": "APEX SERIES • Nº1",
    },
    {
        "id": "02_suitup",
        "prompt": (
            f"{RIDER} standing beside {BIKE} in a pit lane zips her "
            f"racing leathers closed to the collar, pulls on her black "
            f"racing helmet, then swings her leg over the motorcycle "
            f"and sits astride it correctly, facing the handlebars, "
            f"both hands gripping the bars. Camera: medium shot, slow "
            f"push-in as she mounts. " + STYLE
        ),
        "caption": "She came to ride.",
        "eyebrow": "THE ANSWER",
        "sfx": ["engine"],
    },
    {
        "id": "03_apex",
        "prompt": (
            f"A professional motorcycle racer in fitted black-and-gold "
            f"racing leathers and a full black helmet rides {BIKE} "
            f"through a fast sweeping racetrack corner at extreme lean "
            f"angle, body hanging off the inside of the bike in correct "
            f"racing posture, knee slider skimming the tarmac, both "
            f"hands on the handlebars, background motion-blurred. "
            f"Camera: low tracking shot alongside the bike through the "
            f"corner. " + STYLE
        ),
        "caption": "Knee down.\n160 km/h.",
        "eyebrow": "THE APEX",
        "sfx": ["engine"],
    },
    {
        "id": "04_wheelie",
        "prompt": (
            f"A professional motorcycle racer in fitted black-and-gold "
            f"racing leathers and a full black helmet lifts the front "
            f"wheel of {BIKE} into a controlled high wheelie down a "
            f"racetrack main straight, seated correctly astride the "
            f"bike, both hands on the handlebars, tire smoke and heat "
            f"haze trailing behind. Camera: dramatic low angle tracking "
            f"from the side. " + STYLE
        ),
        "caption": "The track\nbelongs to her.",
        "eyebrow": "THE STUNT",
        "sfx": ["engine"],
    },
    {
        "id": "05_reveal",
        "prompt": (
            f"{RIDER} sits astride {BIKE}, stopped on the racetrack at "
            f"sunset. She pulls off her black racing helmet with both "
            f"hands, shakes her long dark hair loose, and gives the "
            f"camera a slow confident smirk. Camera: slow push-in from "
            f"medium to close-up on her face. " + STYLE
        ),
        "caption": "Never assume.",
        "eyebrow": "THE REVEAL",
    },
]


# ── cards / overlays ─────────────────────────────────────────────────

def card_title(path):
    img = Image.new("RGBA", (FRAME_WIDTH, FRAME_HEIGHT), (10, 10, 12, 255))
    d = ImageDraw.Draw(img)
    cy = FRAME_HEIGHT // 2
    draw_tracked_fit(d, (FRAME_WIDTH // 2, cy - 70), "SHE RIDES",
                     FONT_SERIF_BOLD, 120, CREAM, tracking=10)
    d.line([(FRAME_WIDTH * 0.3, cy + 35), (FRAME_WIDTH * 0.7, cy + 35)],
           fill=GOLD, width=2)
    draw_tracked_fit(d, (FRAME_WIDTH // 2, cy + 95), "APEX SERIES",
                     FONT_SERIF_BOLD, 46, GOLD, tracking=8)
    draw_plain_fit(d, (FRAME_WIDTH // 2, cy + 175),
                   "The Rider's Gang", FONT_SERIF_ITALIC, 40, CREAM)
    img.convert("RGB").save(path)


def card_outro(path):
    img = Image.new("RGBA", (FRAME_WIDTH, FRAME_HEIGHT), (10, 10, 12, 255))
    d = ImageDraw.Draw(img)
    cy = FRAME_HEIGHT // 2
    draw_plain_fit(d, (FRAME_WIDTH // 2, cy - 120),
                   "Ride with The Rider's Gang", FONT_SERIF_BOLD, 50, CREAM)
    d.line([(FRAME_WIDTH * 0.32, cy - 40), (FRAME_WIDTH * 0.68, cy - 40)],
           fill=GOLD, width=2)
    draw_plain_fit(d, (FRAME_WIDTH // 2, cy + 25),
                   "Follow — the Apex Series", FONT_SERIF_BOLD, 44, GOLD)
    draw_plain_fit(d, (FRAME_WIDTH // 2, cy + 95),
                   "The full story — link in bio", FONT_SERIF_ITALIC, 36, CREAM)
    draw_plain_fit(d, (FRAME_WIDTH // 2, FRAME_HEIGHT - 160),
                   "Professional rider. Closed track.",
                   FONT_SERIF_ITALIC, 28, (150, 145, 135, 255))
    img.convert("RGB").save(path)


def hook_overlay(path):
    ov = Image.new("RGBA", (FRAME_WIDTH, FRAME_HEIGHT), (0, 0, 0, 0))
    ov.alpha_composite(_vignette_layer(0.45))
    d = ImageDraw.Draw(ov)
    draw_tracked_fit(d, (FRAME_WIDTH // 2, 150), "THE RIDER'S GANG",
                     FONT_SERIF_BOLD, 42, CREAM, tracking=8)
    d.line([(FRAME_WIDTH * 0.36, 205), (FRAME_WIDTH * 0.64, 205)],
           fill=GOLD, width=2)
    grad_h = 560
    band = Image.new("L", (1, grad_h), 0)
    for i in range(grad_h):
        band.putpixel((0, i), int(200 * (i / grad_h) ** 1.5))
    band = band.resize((FRAME_WIDTH, grad_h))
    g = Image.new("RGBA", (FRAME_WIDTH, grad_h), (3, 3, 5, 255))
    g.putalpha(band)
    ov.alpha_composite(g, (0, FRAME_HEIGHT - grad_h))
    cy = FRAME_HEIGHT - 360
    draw_plain_fit(d, (FRAME_WIDTH // 2, cy), "Everyone thought",
                   FONT_SERIF_BOLD, 54, CREAM)
    draw_plain_fit(d, (FRAME_WIDTH // 2, cy + 78), "she came to watch.",
                   FONT_SERIF_BOLD, 54, GOLD)
    _with_shadow(ov).save(path)


def thumbnail(scene_clip, thumb_path):
    import subprocess
    tmpf = thumb_path + ".src.png"
    subprocess.run(["ffmpeg", "-y", "-ss", "2.5", "-i", scene_clip,
                    "-frames:v", "1", tmpf], check=True, capture_output=True)
    base = Image.open(tmpf).convert("RGB").resize(
        (FRAME_WIDTH, FRAME_HEIGHT), Image.LANCZOS)
    img = base.convert("RGBA")
    ov = Image.new("RGBA", (FRAME_WIDTH, FRAME_HEIGHT), (0, 0, 0, 0))
    ov.alpha_composite(_vignette_layer(0.5))
    d = ImageDraw.Draw(ov)
    draw_tracked_fit(d, (FRAME_WIDTH // 2, 200), "SHE RIDES",
                     FONT_SERIF_BOLD, 96, CREAM, tracking=9)
    d.line([(FRAME_WIDTH * 0.34, 272), (FRAME_WIDTH * 0.66, 272)],
           fill=GOLD, width=2)
    cy = FRAME_HEIGHT - 400
    draw_plain_fit(d, (FRAME_WIDTH // 2, cy), "Everyone thought",
                   FONT_SERIF_BOLD, 56, CREAM)
    draw_plain_fit(d, (FRAME_WIDTH // 2, cy + 80), "she came to watch.",
                   FONT_SERIF_BOLD, 56, GOLD)
    draw_plain_fit(d, (FRAME_WIDTH // 2, cy + 165), "APEX SERIES • Nº1",
                   FONT_SERIF_ITALIC, 38, GOLD)
    img.alpha_composite(_with_shadow(ov))
    img.convert("RGB").save(thumb_path, quality=90)
    os.remove(tmpf)


# ── generation + assembly ────────────────────────────────────────────

def generate_scene(client, scene, out_path, attempts=3):
    for attempt in range(1, attempts + 1):
        print(f"  [Wan] generating {scene['id']} "
              f"(attempt {attempt})...", flush=True)
        t0 = time.time()
        try:
            video = client.text_to_video(
                scene["prompt"],
                model="Wan-AI/Wan2.2-T2V-A14B",
                extra_body={"aspect_ratio": "9:16", "resolution": "720p"},
            )
        except Exception as e:
            print(f"    failed: {e}", flush=True)
            if attempt == attempts:
                raise
            time.sleep(10 * attempt)
            continue
        with open(out_path, "wb") as f:
            f.write(video)
        print(f"    done in {time.time() - t0:.0f}s "
              f"({len(video) / 1e6:.1f} MB)", flush=True)
        return


def main():
    parser = argparse.ArgumentParser(description="She Rides stunt reel")
    parser.add_argument("--assemble-only", action="store_true")
    parser.add_argument("--only", help="generate a single scene id")
    args = parser.parse_args()

    os.makedirs(AI_DIR, exist_ok=True)

    if not args.assemble_only:
        from huggingface_hub import InferenceClient
        client = InferenceClient(provider="fal-ai",
                                 token=os.environ["HF_TOKEN"], timeout=560)
        for scene in SCENES:
            out = os.path.join(AI_DIR, f"scene_{scene['id']}.mp4")
            if args.only and scene["id"] != args.only:
                continue
            if os.path.exists(out) and not args.only:
                print(f"  {scene['id']}: cached")
                continue
            generate_scene(client, scene, out)
        if args.only:
            return

    from short_videos.veo_assemble import assemble
    assemble(SCENES, AI_DIR, OUT_PATH, THUMB_PATH,
             cards=(card_title, card_outro), hook=hook_overlay,
             mood="apex_rock", mood_band_idx=1,
             thumb_maker=thumbnail, thumb_scene_idx=2,
             closing_freqs=(82.41, 123.47, 164.81, 207.65))


if __name__ == "__main__":
    main()
