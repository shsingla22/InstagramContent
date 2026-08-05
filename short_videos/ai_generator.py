"""
AI Video Generation — LTX-Video 2B (open source, Lightricks).

Generates real AI video (text-to-video diffusion) on CPU. The model
is loaded in two stages so the T5-XXL text encoder and the DiT
transformer never occupy RAM at the same time:

    Stage 1: load T5 text encoder → encode prompt → save embeddings
             → free the encoder
    Stage 2: load transformer + VAE → denoise → decode → export

Output is a raw clip; build_reel.py turns it into a finished
Instagram reel (typography, audio, 1080x1920).

Run:  python3 -m short_videos.ai_generator --steps 20
"""

import argparse
import gc
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

MODEL_ID = "Lightricks/LTX-Video"

# Portrait, divisible by 32, close to 9:16
WIDTH = 448
HEIGHT = 800
NUM_FRAMES = 49          # LTX requires 8k+1 frames; 49 ≈ 2s at 24fps
FPS = 24

PROMPT = (
    "A vintage cafe racer motorcycle riding down an empty city street at dusk, "
    "1960s London, rider in a black leather jacket and open-face helmet leaning "
    "forward over the fuel tank, warm golden hour light, long shadows, shallow "
    "depth of field, film grain, cinematic 35mm footage, smooth tracking shot "
    "following the motorcycle, headlight glowing, wet asphalt reflections"
)

NEGATIVE_PROMPT = (
    "worst quality, inconsistent motion, blurry, jittery, distorted, "
    "watermark, text, logo, cartoon, animation, illustration, low resolution"
)


def stage1_encode_prompt(embeds_path: str) -> None:
    """Encode the prompt with T5-XXL, save embeddings, free the model."""
    import torch
    from diffusers import LTXPipeline

    print("[Stage 1] Loading T5 text encoder...")
    pipe = LTXPipeline.from_pretrained(
        MODEL_ID,
        transformer=None,
        vae=None,
        torch_dtype=torch.bfloat16,
    )

    print("[Stage 1] Encoding prompt...")
    with torch.no_grad():
        (
            prompt_embeds,
            prompt_attention_mask,
            negative_prompt_embeds,
            negative_prompt_attention_mask,
        ) = pipe.encode_prompt(
            prompt=PROMPT,
            negative_prompt=NEGATIVE_PROMPT,
            do_classifier_free_guidance=True,
        )

    torch.save(
        {
            "prompt_embeds": prompt_embeds,
            "prompt_attention_mask": prompt_attention_mask,
            "negative_prompt_embeds": negative_prompt_embeds,
            "negative_prompt_attention_mask": negative_prompt_attention_mask,
        },
        embeds_path,
    )
    print(f"[Stage 1] Embeddings saved to {embeds_path}")

    del pipe
    gc.collect()


def stage2_generate(embeds_path: str, out_path: str, steps: int, seed: int) -> None:
    """Denoise with the DiT transformer and decode with the VAE."""
    import torch
    from diffusers import LTXPipeline
    from diffusers.utils import export_to_video

    print("[Stage 2] Loading transformer + VAE...")
    pipe = LTXPipeline.from_pretrained(
        MODEL_ID,
        text_encoder=None,
        tokenizer=None,
        torch_dtype=torch.bfloat16,
    )

    embeds = torch.load(embeds_path)

    print(f"[Stage 2] Generating {NUM_FRAMES} frames at {WIDTH}x{HEIGHT}, "
          f"{steps} steps (CPU — this takes a while)...")
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
        generator=torch.Generator().manual_seed(seed),
    )
    frames = result.frames[0]
    print(f"[Stage 2] Denoise+decode took {(time.time() - t0) / 60:.1f} min")

    export_to_video(frames, out_path, fps=FPS)
    print(f"[Stage 2] Raw AI clip saved: {out_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate AI video with LTX-Video")
    parser.add_argument("--steps", type=int, default=20)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out", default="output/short_videos/ai_clip_cafe_racer.mp4")
    parser.add_argument("--skip-encode", action="store_true",
                        help="Reuse previously saved prompt embeddings")
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    embeds_path = os.path.join(os.path.dirname(args.out), ".prompt_embeds.pt")

    if not args.skip_encode or not os.path.exists(embeds_path):
        stage1_encode_prompt(embeds_path)
    stage2_generate(embeds_path, args.out, args.steps, args.seed)


if __name__ == "__main__":
    main()
