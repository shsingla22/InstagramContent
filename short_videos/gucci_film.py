"""
Gucci Film — "The Bit That Built Gucci".

Fully AI-generated (Wan 2.2 A14B). The arc, from the article's best
material: the gold ornament on every Gucci loafer is a snaffle bit —
horse tack — miniaturized in gold by Aldo Gucci in 1953; it sold
84,000 pairs a year, dressed Hepburn and Kennedy, and in 1985 became
the only shoe in the Met's permanent collection. The film closes
with "Style Notes Nº1": three classic-luxury pairings that fade in
one after another — the community segment.

Music: original velvet blues-rock (old money x riding), full band
from frame one, crash on the GUCCI title card, lead guitar sits out
under the style notes.

Run:  HF_TOKEN=... python3 -m short_videos.gucci_film
      python3 -m short_videos.gucci_film --assemble-only
      HF_TOKEN=... python3 -m short_videos.gucci_film --only 03_golden
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

AI_DIR = "output/short_videos/films/gucci-wan"
OUT_PATH = ("output/short_videos/films/"
            "the-gucci-horsebit-loafer-born-in-the-saddle.mp4")
THUMB_PATH = ("output/short_videos/films/"
              "the-gucci-horsebit-loafer-born-in-the-saddle_cover.jpg")

LUX = (
    "Cinematic vertical 9:16 video, shot on 35mm film, warm elegant "
    "color grade, film grain, realistic physics and correct anatomy, "
    "quiet old-money luxury aesthetic, documentary realism, no text "
    "or captions in the image."
)

STYLE_NOTES = [
    "Black horsebit + charcoal suit,\nno socks — the boardroom.",
    "Brown suede + ecru chinos\n+ navy blazer — the Riviera.",
    "Loafers + raw denim\n+ white tee — the '60s off-duty.",
]

SCENES = [
    {
        "id": "01_horse",
        "prompt": (
            "In the stable of an English manor estate at golden morning "
            "light, a groom in a tweed vest gently fits a leather bridle "
            "onto a calm bay horse, the polished metal snaffle bit "
            "gleaming as he lifts it toward the horse's mouth. The "
            "horse's head is relaxed, anatomy natural and correct. "
            "Camera: slow push-in from medium to close on the gleaming "
            "bit and bridle rings. Dust motes drift in the light. " + LUX
        ),
        "caption": "That gold bar on Gucci loafers?\nIt belongs in a horse's mouth.",
        "eyebrow": "A TRUE STORY",
        "sfx": ["hoofbeats"],
    },
    {
        "id": "02_atelier",
        "prompt": (
            "In a 1950s Italian shoemaker's atelier, a close-up of a "
            "craftsman's hands holding an elegant black calfskin "
            "leather loafer decorated with simple geometric gold "
            "hardware across the vamp: two small round gold rings "
            "joined by a straight gold bar, like a miniature horse "
            "snaffle bit. He polishes the leather with a soft cloth "
            "and turns the shoe slowly so the gold rings catch the "
            "light of the warm work lamp, leather tools and polish "
            "tins on the scarred wooden workbench. Camera: slow close "
            "orbit over the hands and the shoe. " + LUX
        ),
        "caption": "1953. Aldo Gucci shrank\na horse's bit into gold.",
        "eyebrow": "NEW YORK → FLORENCE",
        "sfx": ["ticks"],
    },
    {
        "id": "03_golden",
        "prompt": (
            "An elegant couple in 1960s evening wear steps out of a "
            "vintage black car in front of a grand hotel entrance at "
            "dusk, warm lamplight on marble steps. Both wear polished "
            "black leather loafers with small gold horsebit ornaments. "
            "Camera: starts at medium height on the couple, then glides "
            "smoothly down to their loafers stepping onto the marble, "
            "gold hardware catching the light. " + LUX
        ),
        "caption": "Hepburn. Kennedy.\n84,000 pairs a year.",
        "eyebrow": "THE ICON",
    },
    {
        "id": "04_museum",
        "prompt": (
            "A single black calfskin loafer with a gold horsebit "
            "ornament stands on a lit pedestal inside a dark museum "
            "gallery, a soft spotlight from above, subtle reflections "
            "on the polished stone floor. Camera: very slow orbit "
            "around the pedestal, the gold horsebit gleaming against "
            "the black leather. Quiet, reverent, minimal. " + LUX
        ),
        "caption": "1985: the Met made it art.\nThe only shoe ever.",
        "eyebrow": "THE MUSEUM",
    },
    {
        "id": "05_style",
        "prompt": (
            "A slow gliding camera moves across a classic luxury "
            "dressing room in warm lamplight: two pairs of horsebit "
            "loafers, one black leather and one brown suede, lined up "
            "on a wooden valet stand beside neatly folded charcoal "
            "tailored trousers, a navy blazer on a hanger, folded raw "
            "denim jeans, and a vintage watch on a leather tray. "
            "Camera: smooth lateral dolly along the arrangement, "
            "shallow depth of field. " + LUX
        ),
        "overlays_maker": None,        # set below — style notes sequence
    },
]


# ── cards / overlays ─────────────────────────────────────────────────

def card_title(path):
    img = Image.new("RGBA", (FRAME_WIDTH, FRAME_HEIGHT), (12, 12, 14, 255))
    d = ImageDraw.Draw(img)
    cy = FRAME_HEIGHT // 2
    draw_tracked_fit(d, (FRAME_WIDTH // 2, cy - 80), "GUCCI",
                     FONT_SERIF_BOLD, 130, CREAM, tracking=12)
    d.line([(FRAME_WIDTH * 0.3, cy + 25), (FRAME_WIDTH * 0.7, cy + 25)],
           fill=GOLD, width=2)
    draw_tracked_fit(d, (FRAME_WIDTH // 2, cy + 85), "THE HORSEBIT LOAFER",
                     FONT_SERIF_BOLD, 44, GOLD, tracking=6)
    draw_plain_fit(d, (FRAME_WIDTH // 2, cy + 165), "Born in the saddle  •  1953",
                   FONT_SERIF_ITALIC, 40, CREAM)
    img.convert("RGB").save(path)


def card_outro(path):
    img = Image.new("RGBA", (FRAME_WIDTH, FRAME_HEIGHT), (12, 12, 14, 255))
    d = ImageDraw.Draw(img)
    cy = FRAME_HEIGHT // 2
    draw_plain_fit(d, (FRAME_WIDTH // 2, cy - 150),
                   "Born in the stable.", FONT_SERIF_BOLD, 56, CREAM)
    draw_plain_fit(d, (FRAME_WIDTH // 2, cy - 70),
                   "At home everywhere.", FONT_SERIF_BOLD, 56, GOLD)
    d.line([(FRAME_WIDTH * 0.32, cy + 20), (FRAME_WIDTH * 0.68, cy + 20)],
           fill=GOLD, width=2)
    draw_plain_fit(d, (FRAME_WIDTH // 2, cy + 85),
                   "Follow The Rider's Gang", FONT_SERIF_BOLD, 42, CREAM)
    draw_plain_fit(d, (FRAME_WIDTH // 2, cy + 150),
                   "New Style Notes every week", FONT_SERIF_ITALIC, 38, GOLD)
    draw_plain_fit(d, (FRAME_WIDTH // 2, cy + 215),
                   "The full story — link in bio", FONT_SERIF_ITALIC, 34, CREAM)
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
    g = Image.new("RGBA", (FRAME_WIDTH, grad_h), (4, 4, 6, 255))
    g.putalpha(band)
    ov.alpha_composite(g, (0, FRAME_HEIGHT - grad_h))
    cy = FRAME_HEIGHT - 360
    draw_plain_fit(d, (FRAME_WIDTH // 2, cy), "That gold bar on Gucci loafers?",
                   FONT_SERIF_BOLD, 50, CREAM)
    draw_plain_fit(d, (FRAME_WIDTH // 2, cy + 75),
                   "It belongs in a horse's mouth.", FONT_SERIF_BOLD, 50, GOLD)
    _with_shadow(ov).save(path)


def style_overlays(tmp):
    """Three style-note overlays that fade in one after another."""
    paths = []
    base_y = FRAME_HEIGHT - 520
    for i, note in enumerate(STYLE_NOTES):
        ov = Image.new("RGBA", (FRAME_WIDTH, FRAME_HEIGHT), (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        if i == 0:
            grad_h = 640
            band = Image.new("L", (1, grad_h), 0)
            for j in range(grad_h):
                band.putpixel((0, j), int(195 * (j / grad_h) ** 1.5))
            band = band.resize((FRAME_WIDTH, grad_h))
            g = Image.new("RGBA", (FRAME_WIDTH, grad_h), (4, 4, 6, 255))
            g.putalpha(band)
            ov.alpha_composite(g, (0, FRAME_HEIGHT - grad_h))
            ov.alpha_composite(_vignette_layer(0.35))
            draw_tracked_fit(d, (FRAME_WIDTH // 2, base_y - 95),
                             "STYLE NOTES  •  Nº1", FONT_SERIF_BOLD, 34,
                             GOLD, tracking=6)
        lines = note.split("\n")
        y = base_y + i * 150
        for k, line in enumerate(lines):
            draw_plain_fit(d, (FRAME_WIDTH // 2, y + k * 58), line,
                           FONT_SERIF_BOLD, 41,
                           CREAM if i != 1 else (232, 220, 188, 255))
        p = os.path.join(tmp, f"ov_style_{i}.png")
        _with_shadow(ov).save(p)
        paths.append((p, 0.4 + i * 1.35))
    return paths


SCENES[4]["overlays_maker"] = style_overlays


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
    draw_tracked_fit(d, (FRAME_WIDTH // 2, 200), "GUCCI",
                     FONT_SERIF_BOLD, 100, CREAM, tracking=11)
    d.line([(FRAME_WIDTH * 0.34, 275), (FRAME_WIDTH * 0.66, 275)],
           fill=GOLD, width=2)
    cy = FRAME_HEIGHT - 400
    draw_plain_fit(d, (FRAME_WIDTH // 2, cy), "That gold bar on the loafer?",
                   FONT_SERIF_BOLD, 52, CREAM)
    draw_plain_fit(d, (FRAME_WIDTH // 2, cy + 78),
                   "It belongs in a horse's mouth.", FONT_SERIF_BOLD, 50, GOLD)
    draw_plain_fit(d, (FRAME_WIDTH // 2, cy + 160), "EST. 1953",
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
    parser = argparse.ArgumentParser(description="Gucci horsebit film")
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
             mood="velvet_rock", mood_band_idx=1,
             thumb_maker=thumbnail, thumb_scene_idx=3,
             closing_freqs=(110.0, 138.59, 164.81, 220.0))


if __name__ == "__main__":
    main()
