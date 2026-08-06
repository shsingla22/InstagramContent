"""
Story Generator — multi-scene AI video via LTX-Video 2B.

Renders the storyboard for "The Night They Raced the Jukebox", the
best narrative from the café racer article: at the Ace Cafe in 1950s
London, riders dropped a coin in the jukebox and raced to hit
100 mph and return before the record ended.

Efficiency: the text encoder is loaded once to embed ALL scene
prompts, then freed; the transformer is loaded once and generates
every scene in sequence. Quality over the first single-clip attempt:
512x896 resolution (vs 448x800) and 35 denoising steps (vs 20).

Run:  python3 -m short_videos.story_generator
"""

import argparse
import gc
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

MODEL_ID = "Lightricks/LTX-Video"

WIDTH = 576
HEIGHT = 1024          # exact 9:16, higher detail than the 512x896 pass
NUM_FRAMES = 49
FPS = 24

STYLE = (
    "1950s London, evening, cinematic 35mm film footage, warm golden "
    "streetlight and neon glow, well-lit subjects, sharp focus, highly "
    "detailed, crisp clear image, smooth camera motion"
)

NEGATIVE_PROMPT = (
    "worst quality, inconsistent motion, blurry, jittery, distorted, deformed, "
    "watermark, text, logo, cartoon, animation, illustration, low resolution, "
    "modern cars, daylight, dark, underexposed, murky, out of focus, "
    "soft focus, low contrast"
)

# The storyboard — each scene is one AI generation plus the caption
# that tells the story over it (silent-film style).
STORYBOARD = [
    {
        "id": "01_cafe",
        "seed": 111,
        "prompt": (
            "Exterior of a brightly lit vintage British roadside cafe in the "
            "evening, large glowing red neon sign above the entrance, a row "
            "of classic motorcycles clearly visible parked out front, riders "
            "in leather jackets by the door, warm light from the windows, "
            "slow push-in camera move, " + STYLE
        ),
        "caption": "London, 1959.\nThe Ace Cafe never slept.",
        "eyebrow": "A TRUE STORY",
    },
    {
        "id": "02_jukebox",
        "seed": 212,
        "prompt": (
            "Close-up of a brightly glowing vintage 1950s jukebox, chrome trim "
            "and colorful light tubes clearly visible, a vinyl record spinning "
            "on the turntable, warm cafe interior with soft lamplight behind, "
            "slow orbiting camera move, " + STYLE
        ),
        "caption": "Inside, a rider drops\na coin in the jukebox.",
        "eyebrow": "THE BET",
    },
    {
        "id": "03_kickstart",
        "seed": 313,
        "prompt": (
            "A rider in a black leather jacket sitting on a vintage cafe racer "
            "motorcycle under a bright streetlamp at night, kick-starting the "
            "engine, chrome tank gleaming in warm lamplight, headlight glowing "
            "bright, well-lit scene, clearly visible rider and motorcycle, "
            + STYLE
        ),
        "caption": "Reach 100 mph — and be back\nbefore the record ends.",
        "eyebrow": "THREE MINUTES. ONE SONG.",
    },
    {
        "id": "04_race",
        "seed": 414,
        "prompt": (
            "A vintage cafe racer motorcycle speeding down a city street lined "
            "with bright streetlights in the evening, rider in black leather "
            "tucked low over the chrome fuel tank, motorcycle clearly visible "
            "and well-lit, tracking shot alongside the motorcycle, " + STYLE
        ),
        "caption": "They called it\n“doing the ton.”",
        "eyebrow": "100 MPH",
    },
    {
        "id": "05_corner",
        "seed": 515,
        "prompt": (
            "A vintage motorcycle with a bright glowing headlight leaning into "
            "a bend on a well-lit city street at night, rider clearly visible "
            "in leather jacket, rows of streetlights illuminating wet asphalt, "
            "low tracking camera following the motorcycle, " + STYLE
        ),
        "caption": "No second chances.\nNo slowing down.",
        "eyebrow": "FLAT OUT",
    },
    {
        "id": "06_return",
        "seed": 616,
        "prompt": (
            "A rider on a vintage motorcycle pulling up outside a brightly "
            "neon-lit cafe and coming to a stop, other riders clearly visible "
            "cheering and raising their hands, faces lit by warm cafe light, "
            "triumphant mood, " + STYLE
        ),
        "caption": "The ones who made it back\nbecame legends.",
        "eyebrow": "THE TON-UP BOYS",
    },
]

STORY_DIR = "output/short_videos/story"


def stage1_encode_all(embeds_dir: str) -> None:
    """Encode every scene prompt with T5, save embeddings, free model."""
    import torch
    from diffusers import LTXPipeline

    print("[Stage 1] Loading T5 text encoder...")
    pipe = LTXPipeline.from_pretrained(
        MODEL_ID, transformer=None, vae=None, torch_dtype=torch.bfloat16,
    )

    os.makedirs(embeds_dir, exist_ok=True)
    for scene in STORYBOARD:
        path = os.path.join(embeds_dir, f"{scene['id']}.pt")
        if os.path.exists(path):
            print(f"[Stage 1] {scene['id']}: embeddings cached")
            continue
        print(f"[Stage 1] Encoding: {scene['id']}")
        with torch.no_grad():
            pe, pam, ne, nam = pipe.encode_prompt(
                prompt=scene["prompt"],
                negative_prompt=NEGATIVE_PROMPT,
                do_classifier_free_guidance=True,
            )
        torch.save(
            {"prompt_embeds": pe, "prompt_attention_mask": pam,
             "negative_prompt_embeds": ne, "negative_prompt_attention_mask": nam},
            path,
        )

    del pipe
    gc.collect()


def stage2_generate_all(embeds_dir: str, steps: int) -> None:
    """Load the transformer once and render every scene."""
    import torch
    from diffusers import LTXPipeline
    from diffusers.utils import export_to_video

    print("[Stage 2] Loading transformer + VAE...")
    pipe = LTXPipeline.from_pretrained(
        MODEL_ID, text_encoder=None, tokenizer=None, torch_dtype=torch.bfloat16,
    )

    for i, scene in enumerate(STORYBOARD, 1):
        out_path = os.path.join(STORY_DIR, f"scene_{scene['id']}.mp4")
        if os.path.exists(out_path):
            print(f"[{i}/{len(STORYBOARD)}] {scene['id']}: already rendered")
            continue
        embeds = torch.load(os.path.join(embeds_dir, f"{scene['id']}.pt"))
        print(f"[{i}/{len(STORYBOARD)}] Generating {scene['id']} "
              f"({WIDTH}x{HEIGHT}, {steps} steps)...")
        t0 = time.time()
        result = pipe(
            prompt_embeds=embeds["prompt_embeds"],
            prompt_attention_mask=embeds["prompt_attention_mask"],
            negative_prompt_embeds=embeds["negative_prompt_embeds"],
            negative_prompt_attention_mask=embeds["negative_prompt_attention_mask"],
            width=WIDTH,
            height=HEIGHT,
            num_frames=NUM_FRAMES,
            num_inference_steps=steps,
            guidance_scale=3.0,
            generator=torch.Generator().manual_seed(scene["seed"]),
        )
        export_to_video(result.frames[0], out_path, fps=FPS)
        print(f"    done in {(time.time() - t0) / 60:.1f} min → {out_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate story scenes")
    parser.add_argument("--steps", type=int, default=45)
    args = parser.parse_args()

    os.makedirs(STORY_DIR, exist_ok=True)
    embeds_dir = os.path.join(STORY_DIR, ".embeds")
    stage1_encode_all(embeds_dir)
    stage2_generate_all(embeds_dir, args.steps)
    print("\nAll scenes rendered.")


if __name__ == "__main__":
    main()
