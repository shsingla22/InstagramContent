"""
Saddlebag Pilot B — stylized animation ("Cavalry Gear", painted).

Same story, narration, grid and score as the photoreal saddlebag
reel, but every scene is generated as an openly hand-painted
animated illustration — testing whether stylized art escapes the
photoreal-AI skip reflex. Nothing pretends to be real footage.

Run:  HF_TOKEN=... python3 -m short_videos.saddlebag_stylized --generate
      python3 -m short_videos.saddlebag_stylized          (assemble)
"""

import argparse
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

PAINT = (
    "Hand-painted animated film still in motion, oil painting texture "
    "with visible brushstrokes, rich warm palette, vintage European "
    "storybook illustration style, painterly light, clearly stylized "
    "and not photorealistic, vertical 9:16 composition, no text or "
    "captions in the image."
)

AI_DIR = "output/short_videos/films/saddlebag-stylized-wan"
OUT_PATH = "output/short_videos/films/saddlebag-pilot-stylized.mp4"
THUMB_PATH = "output/short_videos/films/saddlebag-pilot-stylized_cover.jpg"

SCENES = [
    {"id": "01_paris", "prompt": (
        "A beautiful elegant woman in a cream tailored suit walks along "
        "a golden Paris boulevard, a tan leather saddle-shaped handbag "
        "with a curved flap swinging at her hip, autumn light between "
        "grand facades, she smiles softly toward the viewer. " + PAINT)},
    {"id": "02_cavalry", "prompt": (
        "An ancient Persian cavalry warrior in bronze armor gallops "
        "across a golden desert plain at dawn, leather saddlebags "
        "bouncing at his horse's flanks, dust swirling in painted "
        "strokes, banners of cloud above. " + PAINT)},
    {"id": "03_courier", "prompt": (
        "A hooded medieval courier gallops out of a torch-lit castle "
        "gate into blue dusk, leather saddlebags at the horse's "
        "flanks, sparks from the torches trailing painterly light. "
        + PAINT)},
    {"id": "04_cowboy", "prompt": (
        "A lone cowboy rides through a golden prairie at sunset "
        "beside a river of cattle, tooled leather saddlebags behind "
        "his saddle, long painted shadows and warm dust. " + PAINT)},
    {"id": "05_atelier", "prompt": (
        "Inside a warm Paris leather atelier, an old craftsman "
        "saddle-stitches an elegant leather handbag under a brass "
        "lamp, horse harnesses hanging on the wall behind him, "
        "amber lamplight in thick painted strokes. " + PAINT)},
    {"id": "06_siren", "prompt": (
        "A glamorous 1950s film star with a silk headscarf and dark "
        "sunglasses steps from a cream vintage convertible outside a "
        "Riviera hotel, a structured black handbag on her forearm, "
        "photographers' flashes painted as starbursts. " + PAINT)},
]

# (source, start, beats, caption, vo id, speed) — same grid as photoreal
SHOTS = [
    ("scene_01_paris", 0.2, 6, "That $4,000 Dior bag?", "vo01", 1.0),
    ("scene_02_cavalry", 0.5, 4, "Cavalry gear.", "vo02", 1.0),
    ("scene_02_cavalry", 2.8, 7, "Persia, 500 BC.", "vo03b", 0.62),
    ("scene_03_courier", 0.5, 7, "It carried the royal mail…", "vo04b", 1.0),
    ("scene_03_courier", 3.3, 3, "…before mail existed.", None, 1.0),
    ("scene_04_cowboy", 1.5, 4, "Cowboys lived out of it.", "vo06b", 1.0),
    ("scene_05_atelier", 0.8, 7, "Then cars killed the horse.", "vo07b", 1.0),
    ("scene_06_siren", 1.0, 5, "Grace Kelly, 1956.", "vo08", 1.0),
    ("scene_01_paris", 2.4, 5, "Dior, 1999.", "vo09b", 1.0),
    ("scene_01_paris", 3.6, 7, None, "vo10", 0.62),
    ("scene_01_paris", 0.2, 5, None, "vo11", 1.0),      # loop shot
]


def main():
    parser = argparse.ArgumentParser(description="Stylized saddlebag pilot")
    parser.add_argument("--generate", action="store_true")
    parser.add_argument("--only")
    args = parser.parse_args()
    os.makedirs(AI_DIR, exist_ok=True)

    if args.generate:
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
            for attempt in range(1, 4):
                print(f"  [Wan] {scene['id']} (attempt {attempt})...",
                      flush=True)
                t0 = time.time()
                try:
                    video = client.text_to_video(
                        scene["prompt"], model="Wan-AI/Wan2.2-T2V-A14B",
                        extra_body={"aspect_ratio": "9:16",
                                    "resolution": "720p"})
                except Exception as e:
                    print(f"    failed: {e}", flush=True)
                    if attempt == 3:
                        raise
                    time.sleep(10 * attempt)
                    continue
                with open(out, "wb") as f:
                    f.write(video)
                print(f"    done in {time.time() - t0:.0f}s", flush=True)
                break
        return

    # assembly: reuse the saddlebag pipeline with swapped sources
    import short_videos.saddlebag_film as sf
    sf.SHOTS = [(AI_DIR, src, start, beats, cap, vo, spd)
                for (src, start, beats, cap, vo, spd) in SHOTS]
    sf.CTA_SHOT_IDX = 9
    sf.TMP = os.path.join(AI_DIR, ".assembly")
    sf.OUT_PATH = OUT_PATH
    sf.THUMB_PATH = THUMB_PATH

    def thumb():
        import subprocess
        from PIL import Image, ImageDraw
        from short_videos import (FONT_SERIF_BOLD, FONT_SERIF_ITALIC,
                                  FRAME_HEIGHT, FRAME_WIDTH)
        from short_videos.build_story_reel import (
            CREAM, GOLD, _vignette_layer, _with_shadow, draw_plain_fit,
            draw_tracked_fit)
        tmpf = THUMB_PATH + ".src.png"
        subprocess.run(["ffmpeg", "-y", "-ss", "1.5", "-i",
                        os.path.join(AI_DIR, "scene_02_cavalry.mp4"),
                        "-frames:v", "1", tmpf], check=True,
                       capture_output=True)
        base = Image.open(tmpf).convert("RGB").resize(
            (FRAME_WIDTH, FRAME_HEIGHT), Image.LANCZOS)
        img = base.convert("RGBA")
        ov = Image.new("RGBA", (FRAME_WIDTH, FRAME_HEIGHT), (0, 0, 0, 0))
        ov.alpha_composite(_vignette_layer(0.5))
        d = ImageDraw.Draw(ov)
        draw_tracked_fit(d, (FRAME_WIDTH // 2, 200), "CAVALRY GEAR",
                         FONT_SERIF_BOLD, 84, CREAM, tracking=7)
        cy = FRAME_HEIGHT - 380
        draw_plain_fit(d, (FRAME_WIDTH // 2, cy), "That $4,000 Dior bag?",
                       FONT_SERIF_BOLD, 58, CREAM)
        draw_plain_fit(d, (FRAME_WIDTH // 2, cy + 82), "An animated history.",
                       FONT_SERIF_ITALIC, 44, GOLD)
        img.alpha_composite(_with_shadow(ov))
        img.convert("RGB").save(THUMB_PATH, quality=90)
        os.remove(tmpf)

    sf.build_thumbnail = thumb
    sf.assemble()


if __name__ == "__main__":
    main()
