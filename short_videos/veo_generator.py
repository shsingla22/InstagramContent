"""
Veo Film Generator — Option B: top-tier fully-AI generation.

Uses Google Veo 3.1 via the Gemini API. Each scene is a single
8-second 1080p vertical clip with NATIVE AUDIO generated with the
picture (rain, thunder, engine, cloth — no synthetic SFX needed),
in-scene camera direction, and far stronger physics and temporal
consistency than the previous Wan pipeline.

Belstaff storyboard — one storm, one jacket, one inheritance,
told in four 8s scenes:

    1. THE STORM   rider mounts as the storm breaks (hook scene)
    2. THE WAX     the Stoke-on-Trent workshop
    3. THE TEST    night ride through rain → close on rain beading
                   off the waxed shoulder (one continuous camera move)
    4. THE GIFT    forty years later: father hands the jacket to his son

Viral rules: motion + hook text in the first second, BELSTAFF wordmark
from frame one, brand card, fitted captions fading before crossfades,
poster thumbnail, faststart, ~30s.

Requires GEMINI_API_KEY in the environment.

Run:  GEMINI_API_KEY=... python3 -m short_videos.veo_generator
      GEMINI_API_KEY=... python3 -m short_videos.veo_generator --assemble-only
"""

import argparse
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

VEO_MODEL = "veo-3.1-generate-preview"
FALLBACK_MODEL = "veo-3.0-generate-001"

AI_DIR = "output/short_videos/films/belstaff-veo"
OUT_PATH = "output/short_videos/films/belstaff-the-jacket-that-built-a-riding-legend.mp4"
THUMB_PATH = "output/short_videos/films/belstaff-the-jacket-that-built-a-riding-legend_cover.jpg"

STYLE = (
    "Cinematic vertical 9:16 video, 1920s England, shot on 35mm film, "
    "muted Kodachrome colors, film grain, realistic physics, documentary "
    "realism, no text or captions in the image."
)

SCENES = [
    {
        "id": "01_storm",
        "prompt": (
            "A rider in a belted waxed-cotton jacket swings his leg over a "
            "vintage motorcycle outside a stone cottage as a massive storm "
            "front rolls in over the English moors. Wind whips the grass "
            "flat, the first heavy raindrops begin to fall, he kicks the "
            "engine to life and pulls away. Camera: slow push-in from wide "
            "to medium as he mounts, then pans to follow him leaving. "
            "Audio: deep thunder rumble, rising wind, first raindrops "
            "hitting waxed fabric, a single-cylinder engine kicking to "
            "life and pulling away. " + STYLE
        ),
        "caption": "England, 1924.\nThe storm came for him.",
        "eyebrow": "BELSTAFF • A TRUE STORY",
    },
    {
        "id": "02_wax",
        "prompt": (
            "Inside a dim Stoke-on-Trent mill workshop, weathered hands "
            "brush warm amber wax into heavy cotton cloth on a scarred "
            "wooden workbench, tins of wax and a single work lamp nearby. "
            "The fabric darkens and gleams as the wax soaks in. Camera: "
            "slow close orbit around the hands and cloth. Audio: soft "
            "brush strokes on fabric, rain drumming on the workshop "
            "windows, quiet room tone. " + STYLE
        ),
        "caption": "Belstaff taught cotton\nto drink wax.",
        "eyebrow": "STOKE-ON-TRENT",
    },
    {
        "id": "03_test",
        "prompt": (
            "A motorcyclist in a belted waxed-cotton jacket rides through "
            "heavy night rain on a dark moorland road, headlight beam "
            "cutting through sheets of rain. Camera: starts as a tracking "
            "shot alongside the motorcycle, then moves close onto his "
            "shoulder where raindrops bead and stream off the waxed "
            "cotton, then pulls back as he rides on. Audio: hard rain, "
            "steady engine under the storm, wind, water hissing off "
            "tires. " + STYLE
        ),
        "caption": "The rain rolled off.\nThe rider rode on.",
        "eyebrow": "THE PROOF",
    },
    {
        "id": "04_gift",
        "prompt": (
            "In a warm lamplit workshop forty years later, an elderly man "
            "with weathered hands passes his worn waxed-cotton jacket — "
            "decades of patina and repairs visible — into the hands of his "
            "adult son. The son takes its weight, both men hold the moment, "
            "the father nods once. Camera: slow push-in from medium to "
            "close on the jacket between their hands. Audio: quiet rain "
            "outside, the soft heavy sound of waxed fabric, a crackling "
            "fire, no dialogue. " + STYLE
        ),
        "caption": "Forty years on: handed down\nlike land.",
        "eyebrow": "THE HEIRLOOM",
    },
]


def generate_scene(client, scene, out_path: str) -> bool:
    from google.genai import types
    print(f"  [Veo] generating {scene['id']} (8s, native audio)...")
    t0 = time.time()
    try:
        op = client.models.generate_videos(
            model=VEO_MODEL,
            prompt=scene["prompt"],
            config=types.GenerateVideosConfig(
                aspect_ratio="9:16",
                resolution="1080p",
            ),
        )
        while not op.done:
            time.sleep(10)
            op = client.operations.get(op)
        video = op.response.generated_videos[0]
        client.files.download(file=video.video)
        video.video.save(out_path)
        print(f"    done in {time.time() - t0:.0f}s → {out_path}")
        return True
    except Exception as e:
        print(f"    ERROR: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Veo Belstaff film")
    parser.add_argument("--assemble-only", action="store_true")
    args = parser.parse_args()

    os.makedirs(AI_DIR, exist_ok=True)

    if not args.assemble_only:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            print("ERROR: set GEMINI_API_KEY")
            sys.exit(1)
        from google import genai
        client = genai.Client(api_key=api_key)
        failed = []
        for scene in SCENES:
            out = os.path.join(AI_DIR, f"scene_{scene['id']}.mp4")
            if os.path.exists(out):
                print(f"  {scene['id']}: cached")
                continue
            if not generate_scene(client, scene, out):
                failed.append(scene["id"])
        if failed:
            print(f"Failed: {failed} — re-run to resume")
            sys.exit(1)

    # assembly is done by veo_assemble (kept separate so mixing and
    # timing can be tuned without regenerating)
    from short_videos.veo_assemble import assemble
    assemble(SCENES, AI_DIR, OUT_PATH, THUMB_PATH)


if __name__ == "__main__":
    main()
