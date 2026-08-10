"""
Denim Film — "The Rivet That Won the West".

Fully AI-generated (Wan 2.2 A14B via HF Inference Providers), told
as one arc from the article's best material: pockets tore on the
range → a Reno tailor borrowed copper rivets from horse-harness
hardware (1873) → 14-hour saddle days proved them → the 1950s made
the same rivets the uniform of rebellion.

Every riding prompt states pose and orientation explicitly (rider
astride, facing the horse's head / the handlebars, boots in
stirrups) so the model can't stage the rider backwards.

Viral rules: motion + "you"-directed hook in the first second,
brand from frame one, music from the first frame with a crash on
the title card, captions fading before crossfades, loopable ending,
poster thumbnail, faststart.

Run:  HF_TOKEN=... python3 -m short_videos.denim_film
      python3 -m short_videos.denim_film --assemble-only
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

AI_DIR = "output/short_videos/films/denim-wan"
OUT_PATH = ("output/short_videos/films/"
            "denim-and-the-rider-how-jeans-were-born-in-the-saddle.mp4")
THUMB_PATH = ("output/short_videos/films/"
              "denim-and-the-rider-how-jeans-were-born-in-the-saddle_cover.jpg")

WEST = (
    "Cinematic vertical 9:16 video, American West in 1873, shot on 35mm "
    "film, warm dusty Kodachrome colors, film grain, realistic physics "
    "and correct human and horse anatomy, documentary realism, no text "
    "or captions in the image."
)
FIFTIES = (
    "Cinematic vertical 9:16 video, 1950s America, shot on 35mm film, "
    "warm Kodachrome colors, film grain, realistic physics and correct "
    "anatomy, documentary realism, no text or captions in the image."
)

SCENES = [
    {
        "id": "01_range",
        "prompt": (
            "A cowboy rides a chestnut horse at a slow walk across the "
            "open Nevada range at golden dusk, a cattle herd far behind "
            "him in drifting dust. He sits correctly astride the saddle "
            "facing forward in the same direction as the horse's head, "
            "boots in the stirrups, one gloved hand holding the reins. "
            "He glances down at the torn, hanging front pocket of his "
            "denim work trousers. Camera: steady tracking shot from the "
            "side at rider height, slowly pushing in. " + WEST
        ),
        "caption": "Nevada, 1873. Every pair\nof pants tore in the saddle.",
        "eyebrow": "A TRUE STORY • 1873",
    },
    {
        "id": "02_rivet",
        "prompt": (
            "Inside a lamplit 1870s tailor's workshop at night, a "
            "close-up of weathered hands placing a small copper rivet "
            "onto the corner of a denim pocket on a scarred wooden "
            "workbench, a leather horse harness with identical copper "
            "rivets lying beside it. The tailor strikes the rivet once "
            "with a small hammer and it seats into the fabric, gleaming "
            "in the warm lamplight. Camera: slow close orbit over the "
            "hands and the denim. " + WEST
        ),
        "caption": "A tailor stole the fix\nfrom a horse harness.",
        "eyebrow": "RENO, NEVADA",
    },
    {
        "id": "03_drive",
        "prompt": (
            "A cowboy wearing a faded tan cotton work shirt with rolled "
            "sleeves and plain sturdy indigo denim work trousers with "
            "plain undecorated pockets rides his horse at a steady trot "
            "beside a cattle herd across a dusty golden plain at "
            "sunrise. He "
            "sits astride the saddle facing forward over the horse's "
            "neck, boots in the stirrups, reins in his left hand. "
            "Camera: a medium-wide tracking shot that stays level with "
            "the rider, moving with him through the golden dust as the "
            "herd streams past behind. " + WEST
        ),
        "caption": "14-hour days in the saddle.\nThe rivets held.",
        "eyebrow": "THE TEST",
    },
    {
        "id": "04_icon",
        "prompt": (
            "A young man in blue jeans, a white t-shirt and a black "
            "leather jacket sits astride a parked vintage motorcycle on "
            "a quiet 1950s American street at dusk, facing the "
            "handlebars. He kick-starts the engine and rides away down "
            "the street, seated forward with both hands on the "
            "handlebars. Camera: medium shot from the side, panning to "
            "follow as he pulls away. " + FIFTIES
        ),
        "caption": "80 years later, rebellion\nwore the same rivets.",
        "eyebrow": "THE ICON",
        "sfx": ["engine"],
    },
]
SCENES[0]["sfx"] = ["hoofbeats"]
SCENES[1]["sfx"] = ["ticks"]
SCENES[2]["sfx"] = ["hoofbeats", "wind"]


# ── cards / overlays ─────────────────────────────────────────────────

def card_title(path):
    img = Image.new("RGBA", (FRAME_WIDTH, FRAME_HEIGHT), (16, 12, 8, 255))
    d = ImageDraw.Draw(img)
    cy = FRAME_HEIGHT // 2
    draw_tracked_fit(d, (FRAME_WIDTH // 2, cy - 110), "THE RIVET THAT",
                     FONT_SERIF_BOLD, 84, CREAM, tracking=6)
    draw_tracked_fit(d, (FRAME_WIDTH // 2, cy + 5), "WON THE WEST",
                     FONT_SERIF_BOLD, 84, GOLD, tracking=6)
    d.line([(FRAME_WIDTH * 0.3, cy + 95), (FRAME_WIDTH * 0.7, cy + 95)],
           fill=GOLD, width=2)
    draw_plain_fit(d, (FRAME_WIDTH // 2, cy + 150),
                   "Denim & the Rider  •  1873",
                   FONT_SERIF_ITALIC, 40, CREAM)
    img.convert("RGB").save(path)


def card_outro(path):
    img = Image.new("RGBA", (FRAME_WIDTH, FRAME_HEIGHT), (16, 12, 8, 255))
    d = ImageDraw.Draw(img)
    cy = FRAME_HEIGHT // 2
    draw_plain_fit(d, (FRAME_WIDTH // 2, cy - 130),
                   "Your jeans are riding pants.", FONT_SERIF_BOLD, 54, CREAM)
    draw_plain_fit(d, (FRAME_WIDTH // 2, cy - 50),
                   "They never stopped being.", FONT_SERIF_BOLD, 54, GOLD)
    d.line([(FRAME_WIDTH * 0.32, cy + 40), (FRAME_WIDTH * 0.68, cy + 40)],
           fill=GOLD, width=2)
    draw_plain_fit(d, (FRAME_WIDTH // 2, cy + 105),
                   "Story by The Rider's Gang", FONT_SERIF_ITALIC, 36, CREAM)
    draw_plain_fit(d, (FRAME_WIDTH // 2, cy + 170),
                   "The full story — link in bio", FONT_SERIF_ITALIC, 38, GOLD)
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
    g = Image.new("RGBA", (FRAME_WIDTH, grad_h), (5, 3, 2, 255))
    g.putalpha(band)
    ov.alpha_composite(g, (0, FRAME_HEIGHT - grad_h))
    cy = FRAME_HEIGHT - 360
    draw_plain_fit(d, (FRAME_WIDTH // 2, cy), "Look at your jeans.",
                   FONT_SERIF_BOLD, 52, CREAM)
    draw_plain_fit(d, (FRAME_WIDTH // 2, cy + 75),
                   "Those rivets? Horse hardware.", FONT_SERIF_BOLD, 52, GOLD)
    _with_shadow(ov).save(path)


def thumbnail(scene_clip, thumb_path):
    import subprocess
    tmpf = thumb_path + ".src.png"
    subprocess.run(["ffmpeg", "-y", "-ss", "3", "-i", scene_clip,
                    "-frames:v", "1", tmpf], check=True, capture_output=True)
    base = Image.open(tmpf).convert("RGB").resize(
        (FRAME_WIDTH, FRAME_HEIGHT), Image.LANCZOS)
    img = base.convert("RGBA")
    ov = Image.new("RGBA", (FRAME_WIDTH, FRAME_HEIGHT), (0, 0, 0, 0))
    ov.alpha_composite(_vignette_layer(0.5))
    d = ImageDraw.Draw(ov)
    draw_tracked_fit(d, (FRAME_WIDTH // 2, 200), "DENIM & THE RIDER",
                     FONT_SERIF_BOLD, 64, CREAM, tracking=6)
    d.line([(FRAME_WIDTH * 0.34, 265), (FRAME_WIDTH * 0.66, 265)],
           fill=GOLD, width=2)
    cy = FRAME_HEIGHT - 400
    draw_plain_fit(d, (FRAME_WIDTH // 2, cy), "Look at your jeans.",
                   FONT_SERIF_BOLD, 56, CREAM)
    draw_plain_fit(d, (FRAME_WIDTH // 2, cy + 80),
                   "Those rivets? Horse hardware.", FONT_SERIF_BOLD, 52, GOLD)
    draw_plain_fit(d, (FRAME_WIDTH // 2, cy + 165), "EST. 1873",
                   FONT_SERIF_ITALIC, 40, GOLD)
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
        except Exception as e:                    # transient network drops
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
    parser = argparse.ArgumentParser(description="Denim rivet film")
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
             mood="retro_ride", mood_band_idx=1,
             thumb_maker=thumbnail, thumb_scene_idx=2,
             closing_freqs=(110.0, 164.81, 220.0, 277.18))


if __name__ == "__main__":
    main()
