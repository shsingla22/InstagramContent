"""
V2 Reel Generator — creates Instagram reels with:
- TTS narration (deep masculine voice — McConaughey-style pacing via
  sentence-by-sentence gTTS + FFmpeg pitch shift, bass boost, deliberate tempo)
- Creative visuals: gradient backgrounds, animated text, Ken Burns on images
- Title intro card + scene-by-scene storytelling timed to audio
- Cross-fade transitions between scenes
- Brand watermark + CTA outro
"""
import os
import sys
import math
import tempfile
import subprocess
from io import BytesIO

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from moviepy import (
    VideoClip, ImageClip, AudioFileClip,
    CompositeVideoClip, concatenate_videoclips, ColorClip
)
from gtts import gTTS

from reel_content import REELS

# ── Config ──────────────────────────────────────────────────
WIDTH, HEIGHT = 1080, 1920
FPS = 24
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))), "output", "videos")
BRAND = "THE RIDER'S GANG"

FADE_DURATION = 0.4  # cross-fade between scenes


def generate_narration(text, output_path):
    """Generate TTS audio with deep, masculine voice — McConaughey-style.

    Uses gTTS (Australian English for deeper base voice) with FFmpeg
    post-processing: pitch shift down 22%, normal tempo, bass boost,
    and high-freq roll-off for warm chest resonance.
    """
    tmp_raw = output_path + ".raw.mp3"
    tts = gTTS(text, lang='en', tld='com.au')  # Australian English — deeper male base
    tts.save(tmp_raw)

    # Deep male voice processing (gTTS outputs at 24kHz):
    # - asetrate=24000*0.78: pitch down 22% for deep masculine register
    # - aresample=44100: resample to standard rate
    # - atempo=1.282: compensate for slowdown so speech is normal pace
    # - Bass boost at 100-200Hz for warm chest resonance
    # - High-freq roll-off for smooth, non-tinny sound
    subprocess.run([
        "ffmpeg", "-y", "-i", tmp_raw,
        "-af", (
            "asetrate=24000*0.78,"
            "aresample=44100,"
            "atempo=1.282,"
            "equalizer=f=100:t=h:w=150:g=7,"
            "equalizer=f=200:t=h:w=200:g=4,"
            "equalizer=f=3500:t=h:w=2000:g=-4,"
            "volume=1.3"
        ),
        "-ar", "44100", "-ac", "1",
        output_path
    ], capture_output=True, check=True)
    os.remove(tmp_raw)
    return output_path


def download_image(url, size=(WIDTH, HEIGHT)):
    """Download image from URL, return PIL Image."""
    import urllib.request
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            img = Image.open(BytesIO(resp.read())).convert("RGB")
        # Smart crop to 9:16
        src_w, src_h = img.size
        target_ratio = size[0] / size[1]
        src_ratio = src_w / src_h
        if src_ratio > target_ratio:
            new_w = int(src_h * target_ratio)
            left = (src_w - new_w) // 2
            img = img.crop((left, 0, left + new_w, src_h))
        elif src_ratio < target_ratio:
            new_h = int(src_w / target_ratio)
            top = (src_h - new_h) // 2
            img = img.crop((0, top, src_w, top + new_h))
        img = img.resize(size, Image.LANCZOS)
        return img
    except Exception as e:
        print(f"  [warn] Could not download {url[:60]}...: {e}")
        return None


def hex_to_rgb(hex_color):
    h = hex_color.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def draw_text_with_shadow(draw, pos, text, font, fill, shadow_color=(0, 0, 0),
                          shadow_offset=3):
    """Draw text with a drop shadow for readability."""
    x, y = pos
    for dx in range(-shadow_offset, shadow_offset + 1):
        for dy in range(-shadow_offset, shadow_offset + 1):
            if dx == 0 and dy == 0:
                continue
            draw.text((x + dx, y + dy), text, font=font, fill=shadow_color)
    draw.text((x, y), text, font=font, fill=fill)


def create_title_frame(reel_data, t, duration):
    """Create the title/intro card frame."""
    accent = hex_to_rgb(reel_data["color_accent"])
    img = Image.new("RGB", (WIDTH, HEIGHT), (15, 10, 8))
    draw = ImageDraw.Draw(img)

    progress = min(1.0, t / duration) if duration > 0 else 1.0

    # Decorative top line
    line_w = int(400 * min(1.0, progress * 3))
    draw.rectangle([(WIDTH - line_w) // 2, 680,
                     (WIDTH + line_w) // 2, 684], fill=accent)

    # Brand name
    try:
        brand_font = ImageFont.truetype(FONT_REGULAR, 26)
    except:
        brand_font = ImageFont.load_default()
    bb = draw.textbbox((0, 0), BRAND, font=brand_font)
    bw = bb[2] - bb[0]
    draw.text(((WIDTH - bw) // 2, 640), BRAND, font=brand_font, fill=accent)

    # Title — big and bold
    try:
        title_font = ImageFont.truetype(FONT_BOLD, 88)
    except:
        title_font = ImageFont.load_default()

    title = reel_data["title"]
    title_lines = title.split('\n')
    line_h = 100
    total_h = len(title_lines) * line_h
    start_y = 720

    # Slide-in effect
    offset_x = int(40 * max(0, 1.0 - progress * 3))

    for i, line in enumerate(title_lines):
        bb = draw.textbbox((0, 0), line, font=title_font)
        tw = bb[2] - bb[0]
        x = (WIDTH - tw) // 2 + offset_x
        y = start_y + i * line_h
        draw_text_with_shadow(draw, (x, y), line, title_font, (255, 255, 255))

    # Subtitle — smaller
    try:
        sub_font = ImageFont.truetype(FONT_REGULAR, 36)
    except:
        sub_font = ImageFont.load_default()

    subtitle = reel_data["subtitle"]
    sub_lines = subtitle.split('\n')
    sub_start_y = start_y + total_h + 40

    # Fade in subtitle
    sub_alpha = min(1.0, max(0, (progress - 0.3) * 3))
    sub_color = (
        int(accent[0] * sub_alpha + 15 * (1 - sub_alpha)),
        int(accent[1] * sub_alpha + 10 * (1 - sub_alpha)),
        int(accent[2] * sub_alpha + 8 * (1 - sub_alpha)),
    )

    for i, line in enumerate(sub_lines):
        bb = draw.textbbox((0, 0), line, font=sub_font)
        tw = bb[2] - bb[0]
        x = (WIDTH - tw) // 2
        y = sub_start_y + i * 46
        draw.text((x, y), line, font=sub_font, fill=sub_color)

    # Bottom line
    draw.rectangle([(WIDTH - line_w) // 2, sub_start_y + len(sub_lines) * 46 + 30,
                     (WIDTH + line_w) // 2, sub_start_y + len(sub_lines) * 46 + 34],
                    fill=accent)

    return np.array(img)


def create_scene_frame(scene_text, reel_data, scene_idx, bg_image=None,
                       t=0.0, duration=1.0):
    """Create a single frame for a scene with animated text and visuals."""
    accent = hex_to_rgb(reel_data["color_accent"])
    progress = min(1.0, t / duration) if duration > 0 else 1.0

    # Background with Ken Burns effect
    if bg_image is not None:
        scale = 1.0 + 0.12 * progress
        img = bg_image.copy()
        new_w = int(WIDTH * scale)
        new_h = int(HEIGHT * scale)
        img = img.resize((new_w, new_h), Image.LANCZOS)
        # Alternate pan direction by scene
        if scene_idx % 2 == 0:
            pan_x = int((new_w - WIDTH) * progress)
            pan_y = int((new_h - HEIGHT) * 0.3)
        else:
            pan_x = int((new_w - WIDTH) * (1 - progress))
            pan_y = int((new_h - HEIGHT) * 0.6)
        pan_x = max(0, min(pan_x, new_w - WIDTH))
        pan_y = max(0, min(pan_y, new_h - HEIGHT))
        img = img.crop((pan_x, pan_y, pan_x + WIDTH, pan_y + HEIGHT))
        # Dark gradient overlay — darker at center for text
        overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        for y in range(HEIGHT):
            # Darkest in center band where text appears
            dist_from_center = abs(y - HEIGHT // 2) / (HEIGHT // 2)
            alpha = int(180 - 60 * dist_from_center)
            overlay_draw.line([(0, y), (WIDTH, y)], fill=(0, 0, 0, alpha))
        img = img.convert("RGBA")
        img = Image.alpha_composite(img, overlay).convert("RGB")
    else:
        dark = (20, 14, 10)
        img = Image.new("RGB", (WIDTH, HEIGHT), dark)

    draw = ImageDraw.Draw(img)

    # ── Animated main text ──
    # Fade in + slight upward slide
    text_progress = min(1.0, progress * 2.5)
    y_slide = int(30 * (1.0 - text_progress))

    try:
        main_font = ImageFont.truetype(FONT_BOLD, 82)
    except:
        main_font = ImageFont.load_default()

    lines = scene_text.split('\n')
    line_h = 96
    total_h = len(lines) * line_h
    start_y = (HEIGHT // 2) - (total_h // 2) + y_slide

    for i, line in enumerate(lines):
        bb = draw.textbbox((0, 0), line, font=main_font)
        tw = bb[2] - bb[0]
        x = (WIDTH - tw) // 2
        y = start_y + i * line_h
        # White text with heavy shadow
        draw_text_with_shadow(draw, (x, y), line, main_font, (255, 255, 255),
                              shadow_offset=4)

    # Accent underline — grows in
    line_w = int(min(300, WIDTH * 0.3) * min(1.0, progress * 2.0))
    ul_y = start_y + total_h + 16
    draw.rectangle([(WIDTH - line_w) // 2, ul_y,
                     (WIDTH + line_w) // 2, ul_y + 5], fill=accent)

    # ── Brand watermark top ──
    try:
        brand_font = ImageFont.truetype(FONT_REGULAR, 22)
    except:
        brand_font = ImageFont.load_default()
    bb = draw.textbbox((0, 0), BRAND, font=brand_font)
    bw = bb[2] - bb[0]
    draw_text_with_shadow(draw, ((WIDTH - bw) // 2, 55), BRAND, brand_font,
                          accent, shadow_offset=2)

    # ── Scene counter dots at bottom ──
    num_scenes = len(reel_data["scenes"])
    dot_y = HEIGHT - 100
    dot_spacing = 20
    total_dots_w = num_scenes * dot_spacing
    dot_start_x = (WIDTH - total_dots_w) // 2
    for i in range(num_scenes):
        cx = dot_start_x + i * dot_spacing + 5
        if i == scene_idx:
            draw.ellipse([cx - 5, dot_y - 5, cx + 5, dot_y + 5], fill=accent)
        else:
            draw.ellipse([cx - 3, dot_y - 3, cx + 3, dot_y + 3],
                         fill=(100, 100, 100))

    return np.array(img)


def create_outro_frame(reel_data, t, duration):
    """Create outro/CTA card."""
    accent = hex_to_rgb(reel_data["color_accent"])
    img = Image.new("RGB", (WIDTH, HEIGHT), (15, 10, 8))
    draw = ImageDraw.Draw(img)
    progress = min(1.0, t / duration) if duration > 0 else 1.0

    # Brand
    try:
        brand_font = ImageFont.truetype(FONT_BOLD, 44)
    except:
        brand_font = ImageFont.load_default()
    bb = draw.textbbox((0, 0), BRAND, font=brand_font)
    bw = bb[2] - bb[0]
    draw.text(((WIDTH - bw) // 2, HEIGHT // 2 - 80), BRAND, font=brand_font,
              fill=(255, 255, 255))

    # Accent line
    line_w = int(300 * min(1.0, progress * 2))
    draw.rectangle([(WIDTH - line_w) // 2, HEIGHT // 2,
                     (WIDTH + line_w) // 2, HEIGHT // 2 + 4], fill=accent)

    # CTA
    try:
        cta_font = ImageFont.truetype(FONT_REGULAR, 32)
    except:
        cta_font = ImageFont.load_default()
    cta = "Follow for more riding stories"
    bb = draw.textbbox((0, 0), cta, font=cta_font)
    cw = bb[2] - bb[0]
    cta_alpha = min(1.0, max(0, (progress - 0.3) * 3))
    cta_color = (int(180 * cta_alpha), int(170 * cta_alpha), int(160 * cta_alpha))
    draw.text(((WIDTH - cw) // 2, HEIGHT // 2 + 40), cta, font=cta_font,
              fill=cta_color)

    return np.array(img)


def apply_crossfade(clips, fade_dur=FADE_DURATION):
    """Concatenate clips with cross-fade transitions."""
    if len(clips) <= 1:
        return clips[0] if clips else ColorClip((WIDTH, HEIGHT), (0, 0, 0), duration=1)

    result_clips = []
    for i, clip in enumerate(clips):
        c = clip
        if i > 0:
            c = c.with_effects([])  # placeholder — we'll use compositing
        result_clips.append(c)

    # Simple approach: crossfade via concatenate
    return concatenate_videoclips(result_clips, method="compose",
                                  padding=-fade_dur)


def generate_reel(reel_data, index):
    """Generate a complete reel video with audio and visuals."""
    slug = reel_data["slug"]
    print(f"\n{'='*60}")
    print(f"  Generating Reel #{index+1}: {reel_data['title'].replace(chr(10), ' ')}")
    print(f"{'='*60}")

    # 1. Generate narration audio
    print("  [1/4] Generating narration audio...")
    audio_path = os.path.join(OUTPUT_DIR, f"{slug}_audio.mp3")
    generate_narration(reel_data["narration"], audio_path)
    audio = AudioFileClip(audio_path)
    narration_duration = audio.duration
    print(f"        Narration: {narration_duration:.1f}s")

    # Time budget: intro (2.5s) + scenes (narration) + outro (2s)
    intro_dur = 2.5
    outro_dur = 2.0
    total_duration = intro_dur + narration_duration + outro_dur

    # 2. Download images for backgrounds
    print("  [2/4] Downloading background images...")
    bg_images = []
    for url in reel_data.get("images", []):
        img = download_image(url)
        if img:
            bg_images.append(img)
    if not bg_images:
        bg_images = [None]
    print(f"        Downloaded {len(bg_images)} images")

    # 3. Build clips
    print("  [3/4] Building video clips...")

    # Intro card
    def make_intro(t):
        return create_title_frame(reel_data, t, intro_dur)
    intro_clip = VideoClip(make_intro, duration=intro_dur).with_fps(FPS)

    # Scene clips — each scene gets equal portion of narration time
    scenes = reel_data["scenes"]
    num_scenes = len(scenes)
    scene_dur = narration_duration / num_scenes

    scene_clips = []
    for i, scene in enumerate(scenes):
        bg_img = bg_images[i % len(bg_images)] if bg_images[0] is not None else None

        def make_scene(t, _s=scene, _i=i, _bg=bg_img, _d=scene_dur):
            return create_scene_frame(_s["text"], reel_data, _i,
                                      bg_image=_bg, t=t, duration=_d)

        clip = VideoClip(make_scene, duration=scene_dur).with_fps(FPS)
        scene_clips.append(clip)

    # Outro card
    def make_outro(t):
        return create_outro_frame(reel_data, t, outro_dur)
    outro_clip = VideoClip(make_outro, duration=outro_dur).with_fps(FPS)

    # 4. Combine all clips with crossfades
    print("  [4/4] Rendering final video...")
    all_clips = [intro_clip] + scene_clips + [outro_clip]
    video = concatenate_videoclips(all_clips, method="compose",
                                   padding=-FADE_DURATION)

    # Add audio: silence for intro, then narration, silence for outro
    # Create a silent pad before narration starts
    from moviepy import AudioClip
    silence_intro = AudioClip(lambda t: [0], duration=intro_dur - FADE_DURATION / 2,
                               fps=44100).with_fps(44100)

    from moviepy import concatenate_audioclips
    silence_outro = AudioClip(lambda t: [0], duration=outro_dur, fps=44100).with_fps(44100)
    full_audio = concatenate_audioclips([silence_intro, audio, silence_outro])

    # Trim audio/video to match
    final_dur = min(video.duration, full_audio.duration)
    video = video.subclipped(0, final_dur)
    full_audio = full_audio.subclipped(0, final_dur)
    video = video.with_audio(full_audio)

    output_path = os.path.join(OUTPUT_DIR, f"{slug}.mp4")
    video.write_videofile(
        output_path,
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        preset="fast",
        logger=None,
        threads=4,
    )

    # Faststart for web
    tmp_path = output_path + ".tmp.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-i", output_path,
        "-c", "copy", "-movflags", "+faststart", tmp_path
    ], capture_output=True)
    os.replace(tmp_path, output_path)

    # Cleanup
    if os.path.exists(audio_path):
        os.remove(audio_path)
    audio.close()
    video.close()
    for c in all_clips:
        c.close()

    file_size = os.path.getsize(output_path)
    print(f"  Done: {output_path} ({file_size/1024/1024:.1f}MB)")
    return output_path


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    if len(sys.argv) > 1:
        indices = [int(x) - 1 for x in sys.argv[1:]]
    else:
        indices = range(len(REELS))

    results = []
    for i in indices:
        if 0 <= i < len(REELS):
            path = generate_reel(REELS[i], i)
            results.append(path)

    print(f"\n{'='*60}")
    print(f"  Generated {len(results)} reels")
    for p in results:
        print(f"  {p}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
