"""
GPU Scene Generator — renders the storyboard through the official
Lightricks LTX-Video 13B distilled Space on Hugging Face ZeroGPU.

Same storyboard as story_generator.py, but scenes render on a real
GPU in ~1 minute each instead of ~80 minutes on this host's CPU —
and the 13B model is dramatically sharper than the local 2B one.

Requires HF_TOKEN in the environment (free Hugging Face account).

Run:  HF_TOKEN=... python3 -m short_videos.gpu_generator
      HF_TOKEN=... python3 -m short_videos.gpu_generator --only 04_race
"""

import argparse
import os
import shutil
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from short_videos.story_generator import NEGATIVE_PROMPT, STORY_DIR, STORYBOARD

SPACE = "Lightricks/ltx-video-distilled"
WIDTH = 512
HEIGHT = 896
DURATION_SEC = 3


def generate_scene(client, scene: dict, out_path: str) -> bool:
    print(f"  Generating {scene['id']} on GPU...")
    t0 = time.time()
    try:
        result = client.predict(
            prompt=scene["prompt"],
            negative_prompt=NEGATIVE_PROMPT,
            input_image_filepath=None,
            input_video_filepath=None,
            height_ui=HEIGHT,
            width_ui=WIDTH,
            mode="text-to-video",
            duration_ui=DURATION_SEC,
            ui_frames_to_use=9,
            seed_ui=scene["seed"],
            randomize_seed=False,
            ui_guidance_scale=1,
            improve_texture_flag=True,
            api_name="/text_to_video",
        )
    except Exception as e:
        print(f"  ERROR for {scene['id']}: {e}")
        return False
    video_path = result[0]["video"] if isinstance(result[0], dict) else result[0]
    shutil.copy(video_path, out_path)
    print(f"  done in {time.time() - t0:.0f}s → {out_path}")
    return True


def main():
    parser = argparse.ArgumentParser(description="Generate scenes on HF ZeroGPU")
    parser.add_argument("--only", type=str, default=None,
                        help="Comma-separated scene ids to (re)generate")
    args = parser.parse_args()

    from gradio_client import Client
    token = os.environ.get("HF_TOKEN")
    if not token:
        print("ERROR: set HF_TOKEN")
        sys.exit(1)
    client = Client(SPACE, token=token, verbose=False)

    scenes = STORYBOARD
    if args.only:
        wanted = set(args.only.split(","))
        scenes = [s for s in STORYBOARD if s["id"] in wanted]

    os.makedirs(STORY_DIR, exist_ok=True)
    failed = []
    for scene in scenes:
        out_path = os.path.join(STORY_DIR, f"scene_{scene['id']}.mp4")
        if not generate_scene(client, scene, out_path):
            failed.append(scene["id"])
        time.sleep(5)   # be gentle with the queue between calls

    if failed:
        print(f"\nFailed (likely quota): {failed}")
        print("Re-run later with:  --only " + ",".join(failed))
        sys.exit(1)
    print("\nAll scenes generated on GPU.")


if __name__ == "__main__":
    main()
