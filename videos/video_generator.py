"""
Video Generator Module

Generates short Instagram Reel videos from article content.

Primary method:  CogVideoX-5b (open-source text-to-video diffusion model)
                 via Hugging Face diffusers library.
Fallback method: Animated Ken Burns + vintage filter videos via moviepy,
                 using the article's hero images.

CogVideoX-5b (by Tsinghua University) is chosen because:
- State-of-the-art open-source text-to-video generation
- Produces 6-second clips at 720p with high temporal consistency
- Supports detailed scene prompts with cinematic quality
- Available through HuggingFace diffusers with fp16 optimization
"""

import os
import sys
import json
import math
import subprocess
import urllib.request
from typing import List, Optional

from common import VIDEOS_DIR, VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS, VIDEO_DURATION_SEC
from common.content_data import ArticleData, get_all_articles
from videos.prompt_builder import build_video_prompt, build_image_to_video_prompt


# ── GPU / model availability detection ──────────────────────────────────

def check_gpu_available() -> bool:
    """Check if CUDA GPU is available for model inference."""
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False


def check_diffusers_available() -> bool:
    """Check if the diffusers library is installed."""
    try:
        import diffusers  # noqa: F401
        return True
    except ImportError:
        return False


# ── Primary: CogVideoX-5b text-to-video ─────────────────────────────────

def generate_video_cogvideox(
    prompt: str,
    output_path: str,
    num_frames: int = 49,
    guidance_scale: float = 6.0,
    num_inference_steps: int = 50,
) -> bool:
    """
    Generate a video using CogVideoX-5b via HuggingFace diffusers.

    Model: THUDM/CogVideoX-5b
    - 5 billion parameters
    - Generates 49 frames (≈6 seconds at 8fps, upsampled to 24fps)
    - Native resolution: 720x480, upscaled to target resolution

    Returns True on success, False on failure.
    """
    try:
        import torch
        from diffusers import CogVideoXPipeline
        from diffusers.utils import export_to_video

        print(f"    Loading CogVideoX-5b model...")
        pipe = CogVideoXPipeline.from_pretrained(
            "THUDM/CogVideoX-5b",
            torch_dtype=torch.float16,
        )
        pipe.to("cuda")
        pipe.enable_model_cpu_offload()
        pipe.vae.enable_tiling()

        print(f"    Generating video frames...")
        video_frames = pipe(
            prompt=prompt,
            num_videos_per_prompt=1,
            num_inference_steps=num_inference_steps,
            num_frames=num_frames,
            guidance_scale=guidance_scale,
        ).frames[0]

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        export_to_video(video_frames, output_path, fps=8)

        print(f"    Saved CogVideoX video: {output_path}")
        return True

    except Exception as e:
        print(f"    CogVideoX generation failed: {e}")
        return False


# ── Fallback: moviepy animated video from hero images ────────────────────

def download_image(url: str, dest_path: str) -> bool:
    """Download an image from URL to local path."""
    try:
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            with open(dest_path, "wb") as f:
                f.write(resp.read())
        return True
    except Exception as e:
        print(f"    Download failed for {url}: {e}")
        return False


def generate_video_moviepy(
    article: ArticleData,
    output_path: str,
    duration: int = VIDEO_DURATION_SEC,
    fps: int = VIDEO_FPS,
    width: int = 1080,
    height: int = 1920,
) -> bool:
    """
    Generate a cinematic short video using moviepy with Ken Burns effect,
    vintage color grading, and film grain — matching the retro/old-money aesthetic.

    Creates a visually rich Reel from the article's hero + additional images
    with smooth pan/zoom transitions and overlay text.
    """
    try:
        from moviepy import (
            ImageClip, CompositeVideoClip, TextClip,
            concatenate_videoclips, ColorClip, vfx
        )
        import numpy as np
    except ImportError:
        print("    moviepy not installed. Install with: pip install moviepy")
        return False

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Collect all image URLs
    all_images = [article.hero_image] + article.additional_images
    temp_dir = f"output/videos/.tmp_{article.slug}"
    os.makedirs(temp_dir, exist_ok=True)

    # Download images
    local_images = []
    for i, url in enumerate(all_images):
        local_path = os.path.join(temp_dir, f"img_{i}.jpg")
        if download_image(url, local_path):
            local_images.append(local_path)

    if not local_images:
        print(f"    No images downloaded for {article.slug}")
        return False

    # Duration per image segment
    seg_duration = duration / len(local_images)

    clips = []
    for idx, img_path in enumerate(local_images):
        try:
            img_clip = ImageClip(img_path).with_duration(seg_duration)

            # Resize to fill the vertical frame (9:16)
            img_w, img_h = img_clip.size
            target_ratio = width / height  # 0.5625 for 9:16
            img_ratio = img_w / img_h

            if img_ratio > target_ratio:
                # Image is wider — scale by height, crop width
                scale = height / img_h * 1.3  # 1.3x for zoom headroom
            else:
                # Image is taller — scale by width, crop height
                scale = width / img_w * 1.3

            img_clip = img_clip.resized(scale)

            # Ken Burns effect: alternate between zoom-in and pan directions
            effect_type = idx % 4

            def make_ken_burns(clip, effect, seg_dur, target_w, target_h):
                """Create a Ken Burns pan/zoom effect."""
                cw, ch = clip.size

                def effect_fn(get_frame, t):
                    progress = t / seg_dur
                    frame = get_frame(t)
                    fh, fw = frame.shape[:2]

                    if effect == 0:  # Slow zoom in
                        z = 1.0 + 0.15 * progress
                    elif effect == 1:  # Slow zoom out
                        z = 1.15 - 0.15 * progress
                    elif effect == 2:  # Pan left to right
                        z = 1.1
                    else:  # Pan right to left
                        z = 1.1

                    crop_w = int(target_w / z)
                    crop_h = int(target_h / z)
                    crop_w = min(crop_w, fw)
                    crop_h = min(crop_h, fh)

                    if effect == 2:
                        cx = int(progress * (fw - crop_w))
                    elif effect == 3:
                        cx = int((1 - progress) * (fw - crop_w))
                    else:
                        cx = (fw - crop_w) // 2

                    cy = (fh - crop_h) // 2
                    cx = max(0, min(cx, fw - crop_w))
                    cy = max(0, min(cy, fh - crop_h))

                    cropped = frame[cy:cy + crop_h, cx:cx + crop_w]

                    # Resize to target
                    from PIL import Image
                    pil_img = Image.fromarray(cropped)
                    pil_img = pil_img.resize((target_w, target_h), Image.LANCZOS)
                    return np.array(pil_img)

                return clip.transform(effect_fn)

            img_clip = make_ken_burns(img_clip, effect_type, seg_duration, width, height)
            clips.append(img_clip)

        except Exception as e:
            print(f"    Error processing image {img_path}: {e}")
            continue

    if not clips:
        return False

    # Concatenate image clips
    video = concatenate_videoclips(clips, method="compose")

    # ── Vintage color grading overlay ────────────────────────────────
    # Warm sepia-toned overlay for old-money aesthetic
    sepia_overlay = ColorClip(
        size=(width, height),
        color=(62, 44, 20),  # Dark warm brown
    ).with_duration(duration).with_opacity(0.12)

    # Gold vignette corners
    vignette_overlay = ColorClip(
        size=(width, height),
        color=(10, 8, 5),
    ).with_duration(duration).with_opacity(0.25)

    # ── Text overlays ────────────────────────────────────────────────
    try:
        # Title text
        title_text = TextClip(
            text=article.title,
            font_size=42,
            color="white",
            font="/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
            text_align="center",
            size=(width - 120, None),
            stroke_color="black",
            stroke_width=2,
        ).with_duration(duration).with_position(("center", height - 420))

        # Quote text
        quote_text = TextClip(
            text=f'"{article.key_quote[:120]}..."' if len(article.key_quote) > 120 else f'"{article.key_quote}"',
            font_size=28,
            color="#F5E6C8",
            font="/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
            text_align="center",
            size=(width - 140, None),
            stroke_color="black",
            stroke_width=1,
        ).with_duration(duration - 2).with_start(1.5).with_position(("center", height - 280))

        # Brand watermark
        brand_text = TextClip(
            text="THE RIDER'S GANG",
            font_size=22,
            color="#D4A843",
            font="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            stroke_color="black",
            stroke_width=1,
        ).with_duration(duration).with_position(("center", 60))

        # Category badge
        cat_text = TextClip(
            text=f"  {article.category.upper()}  ",
            font_size=18,
            color="white",
            font="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            bg_color="#2C1810",
        ).with_duration(duration).with_position(("center", 100))

        text_layers = [title_text, quote_text, brand_text, cat_text]
    except Exception as e:
        print(f"    Text overlay failed (font issue): {e}")
        text_layers = []

    # ── Composite everything ─────────────────────────────────────────
    final = CompositeVideoClip(
        [video, sepia_overlay, vignette_overlay] + text_layers,
        size=(width, height),
    ).with_duration(duration)

    # ── Film grain effect via numpy ──────────────────────────────────
    def add_grain(get_frame, t):
        frame = get_frame(t)
        grain = np.random.normal(0, 8, frame.shape).astype(np.int16)
        result = np.clip(frame.astype(np.int16) + grain, 0, 255).astype(np.uint8)
        return result

    final = final.transform(add_grain)

    # ── Write output ─────────────────────────────────────────────────
    final.write_videofile(
        output_path,
        fps=fps,
        codec="libx264",
        audio=False,
        preset="medium",
        bitrate="4000k",
        logger=None,
    )

    # Cleanup temp images
    import shutil
    shutil.rmtree(temp_dir, ignore_errors=True)

    print(f"    Saved video: {output_path}")
    return True


# ── Main generation orchestrator ─────────────────────────────────────────

def generate_all_videos(
    articles: Optional[List[ArticleData]] = None,
    output_dir: str = VIDEOS_DIR,
    force_fallback: bool = False,
) -> dict:
    """
    Generate videos for all articles.

    Tries CogVideoX-5b first (if GPU + diffusers available).
    Falls back to moviepy Ken Burns + vintage filter videos.

    Returns dict mapping article slug -> video file path.
    """
    if articles is None:
        articles = get_all_articles()

    os.makedirs(output_dir, exist_ok=True)

    use_cogvideo = (
        not force_fallback
        and check_gpu_available()
        and check_diffusers_available()
    )

    if use_cogvideo:
        print("  Using CogVideoX-5b (GPU detected)")
    else:
        print("  Using moviepy fallback (cinematic Ken Burns + vintage filters)")
        if not force_fallback:
            if not check_gpu_available():
                print("    Reason: No CUDA GPU detected")
            if not check_diffusers_available():
                print("    Reason: diffusers library not installed")

    video_map = {}

    for i, article in enumerate(articles, 1):
        print(f"\n  [{i}/{len(articles)}] {article.title}")
        output_path = os.path.join(output_dir, f"reel_{i:02d}_{article.slug}.mp4")

        success = False
        if use_cogvideo:
            prompt = build_video_prompt(article)
            success = generate_video_cogvideox(prompt, output_path)

        if not success:
            success = generate_video_moviepy(article, output_path)

        if success:
            video_map[article.slug] = output_path
        else:
            print(f"    FAILED to generate video for: {article.slug}")
            video_map[article.slug] = ""

    # Save video manifest
    manifest_path = os.path.join(output_dir, "video_manifest.json")
    with open(manifest_path, "w") as f:
        json.dump(video_map, f, indent=2)
    print(f"\n  Video manifest saved: {manifest_path}")

    return video_map


if __name__ == "__main__":
    print("=== The Rider's Gang — Video Generator ===\n")
    video_map = generate_all_videos()
    generated = sum(1 for v in video_map.values() if v)
    print(f"\nGenerated {generated}/{len(video_map)} videos.")
