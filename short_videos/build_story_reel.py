"""
Story Reel Builder — assembles the 6 AI-generated scenes into a
~30-second Instagram film with a storyline:

    title card → 6 captioned scenes (silent-film style) → outro CTA

Per scene: frame-interpolated 2.25x slow motion, upscale to
1080x1920 with sharpening and a gentle brightness/contrast lift,
vignette + serif captions (auto-fitted so text never overflows),
and film-style fade cuts. Scene 1 gets a designed "ACE CAFE" neon
sign (diffusion models cannot spell, so the sign is composited).
A designed poster is embedded as the MP4 thumbnail, and the film
opens on a fully visible title card (no black first frame).

Run:  python3 -m short_videos.build_story_reel
"""

import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PIL import Image, ImageDraw, ImageFilter

from short_videos import (
    FONT_SERIF_BOLD,
    FONT_SERIF_ITALIC,
    FRAME_HEIGHT,
    FRAME_WIDTH,
    PALETTE,
)
from short_videos.cinematic_generator import STORY_DIR, STORYBOARD
from short_videos.generator import _load_font
from short_videos.retro_look import make_vignette
from short_videos.rockabilly_score import build_score
from short_videos.sfx_engine import build_engine_track, load_engine_track

OUT_PATH = "output/short_videos/reel_ai_story_cafe_racer.mp4"
THUMB_PATH = "output/short_videos/reel_ai_story_thumbnail.jpg"

TITLE_SEC = 2.5
OUTRO_SEC = 3.0
CLIP_SEC = 3.5625           # Wan clips are ~3.56s at 16fps
SLOW_FACTOR = 1.0           # native speed — racing must feel fast
FADE_SEC = 0.3
MAX_TEXT_WIDTH = int(FRAME_WIDTH * 0.88)   # text must stay inside this

GOLD = PALETTE["gold"] + (255,)
CREAM = PALETTE["cream"] + (255,)


# ── Text helpers (auto-fit: never overflow the frame) ────────────────

def _tracked_width(draw, text, font, tracking):
    widths = [draw.textlength(ch, font=font) for ch in text]
    return sum(widths) + tracking * max(0, len(text) - 1)


def fit_font(draw, text, font_path, size, tracking=0, max_width=MAX_TEXT_WIDTH):
    """Shrink the font size until `text` fits inside max_width."""
    while size > 18:
        font = _load_font(font_path, size)
        if _tracked_width(draw, text, font, tracking) <= max_width:
            return font
        size -= 2
    return _load_font(font_path, 18)


def draw_tracked_fit(draw, xy, text, font_path, size, fill, tracking=0):
    """Letterspaced centered text, auto-shrunk to fit the frame."""
    font = fit_font(draw, text, font_path, size, tracking)
    widths = [draw.textlength(ch, font=font) for ch in text]
    total = sum(widths) + tracking * max(0, len(text) - 1)
    x = xy[0] - total / 2.0
    for ch, w in zip(text, widths):
        draw.text((x, xy[1]), ch, font=font, fill=fill, anchor="lm")
        x += w + tracking


def draw_plain_fit(draw, xy, text, font_path, size, fill):
    """Centered text, auto-shrunk to fit the frame."""
    font = fit_font(draw, text, font_path, size)
    draw.text(xy, text, font=font, fill=fill, anchor="mm")


def _vignette_layer(strength: float = 0.35) -> Image.Image:
    vig = make_vignette(FRAME_WIDTH, FRAME_HEIGHT, strength=strength)[..., 0]
    alpha = ((1.0 - vig) * 255).clip(0, 255).astype("uint8")
    layer = Image.new("RGBA", (FRAME_WIDTH, FRAME_HEIGHT), (5, 3, 2, 255))
    layer.putalpha(Image.fromarray(alpha))
    return layer


def _with_shadow(ov: Image.Image) -> Image.Image:
    shadow = ov.filter(ImageFilter.GaussianBlur(3))
    base = Image.new("RGBA", ov.size, (0, 0, 0, 0))
    base.alpha_composite(shadow)
    base.alpha_composite(ov)
    return base


# ── Designed elements ────────────────────────────────────────────────

def draw_neon_sign(ov: Image.Image, center, text="ACE CAFE") -> None:
    """
    Composite a glowing neon sign. Diffusion models cannot spell, so
    the cafe name is rendered as a designed neon graphic instead.
    """
    cx, cy = center
    draw = ImageDraw.Draw(ov)
    font = _load_font(FONT_SERIF_BOLD, 86)

    # dark backing panel to cover the AI-generated gibberish sign
    w = _tracked_width(draw, text, font, 10)
    pad_x, pad_y = 70, 55
    panel = Image.new("RGBA", (int(w + pad_x * 2), int(140 + pad_y)), (16, 6, 4, 235))
    panel = panel.filter(ImageFilter.GaussianBlur(14))
    ov.alpha_composite(panel, (int(cx - panel.width / 2), int(cy - panel.height / 2)))

    # neon glow: blurred red-orange layers under a hot bright core
    glow = Image.new("RGBA", ov.size, (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    x = cx - w / 2.0
    for ch in text:
        cw = gdraw.textlength(ch, font=font)
        gdraw.text((x, cy), ch, font=font, fill=(255, 60, 20, 255), anchor="lm")
        x += cw + 10
    for radius, alpha in ((18, 130), (8, 180)):
        layer = glow.filter(ImageFilter.GaussianBlur(radius))
        a = layer.getchannel("A").point(lambda v, m=alpha: min(v, m))
        layer.putalpha(a)
        ov.alpha_composite(layer)

    core = Image.new("RGBA", ov.size, (0, 0, 0, 0))
    cdraw = ImageDraw.Draw(core)
    x = cx - w / 2.0
    for ch in text:
        cw = cdraw.textlength(ch, font=font)
        cdraw.text((x, cy), ch, font=font, fill=(255, 210, 150, 255), anchor="lm")
        x += cw + 10
    ov.alpha_composite(core)

    # thin neon border tube around the panel
    bx0 = cx - panel.width / 2 + 18
    by0 = cy - panel.height / 2 + 16
    bx1 = cx + panel.width / 2 - 18
    by1 = cy + panel.height / 2 - 16
    border = Image.new("RGBA", ov.size, (0, 0, 0, 0))
    ImageDraw.Draw(border).rounded_rectangle(
        [bx0, by0, bx1, by1], radius=18, outline=(255, 90, 40, 220), width=4)
    ov.alpha_composite(border.filter(ImageFilter.GaussianBlur(1)))


def build_title_card(path: str) -> None:
    img = Image.new("RGBA", (FRAME_WIDTH, FRAME_HEIGHT),
                    PALETTE["espresso"] + (255,))
    draw = ImageDraw.Draw(img)
    cy = FRAME_HEIGHT // 2
    draw_tracked_fit(draw, (FRAME_WIDTH // 2, cy - 220),
                     "THE RIDER'S GANG PRESENTS", FONT_SERIF_BOLD, 32, GOLD,
                     tracking=6)
    draw.line([(FRAME_WIDTH * 0.3, cy - 160), (FRAME_WIDTH * 0.7, cy - 160)],
              fill=GOLD, width=2)
    draw_tracked_fit(draw, (FRAME_WIDTH // 2, cy - 50), "THE NIGHT THEY",
                     FONT_SERIF_BOLD, 76, CREAM, tracking=2)
    draw_tracked_fit(draw, (FRAME_WIDTH // 2, cy + 55), "RACED THE JUKEBOX",
                     FONT_SERIF_BOLD, 76, CREAM, tracking=2)
    draw.line([(FRAME_WIDTH * 0.3, cy + 140), (FRAME_WIDTH * 0.7, cy + 140)],
              fill=GOLD, width=2)
    draw_plain_fit(draw, (FRAME_WIDTH // 2, cy + 205),
                   "A true story from 1950s London", FONT_SERIF_ITALIC, 40, CREAM)
    img.convert("RGB").save(path)


def build_outro_card(path: str) -> None:
    img = Image.new("RGBA", (FRAME_WIDTH, FRAME_HEIGHT),
                    PALETTE["espresso"] + (255,))
    draw = ImageDraw.Draw(img)
    cy = FRAME_HEIGHT // 2
    draw_tracked_fit(draw, (FRAME_WIDTH // 2, cy - 40), "THE RIDER'S GANG",
                     FONT_SERIF_BOLD, 70, CREAM, tracking=6)
    draw.line([(FRAME_WIDTH * 0.3, cy + 40), (FRAME_WIDTH * 0.7, cy + 40)],
              fill=GOLD, width=3)
    draw_plain_fit(draw, (FRAME_WIDTH // 2, cy + 110),
                   "The full story — link in bio", FONT_SERIF_ITALIC, 42, GOLD)
    img.convert("RGB").save(path)


def build_scene_overlay(scene: dict, path: str) -> None:
    """Vignette + gold eyebrow + serif caption; scene 1 adds the sign."""
    ov = Image.new("RGBA", (FRAME_WIDTH, FRAME_HEIGHT), (0, 0, 0, 0))
    ov.alpha_composite(_vignette_layer())
    draw = ImageDraw.Draw(ov)

    if scene.get("neon_sign"):
        draw_neon_sign(ov, (FRAME_WIDTH // 2, 360))
        draw = ImageDraw.Draw(ov)

    # bottom gradient for caption legibility
    grad_h = 520
    band = Image.new("L", (1, grad_h), 0)
    for i in range(grad_h):
        band.putpixel((0, i), int(185 * (i / grad_h) ** 1.5))
    band = band.resize((FRAME_WIDTH, grad_h))
    gradient = Image.new("RGBA", (FRAME_WIDTH, grad_h), (5, 3, 2, 255))
    gradient.putalpha(band)
    ov.alpha_composite(gradient, (0, FRAME_HEIGHT - grad_h))

    cy = FRAME_HEIGHT - 310
    draw_tracked_fit(draw, (FRAME_WIDTH // 2, cy - 75), scene["eyebrow"],
                     FONT_SERIF_BOLD, 28, GOLD, tracking=5)
    for i, line in enumerate(scene["caption"].split("\n")):
        draw_plain_fit(draw, (FRAME_WIDTH // 2, cy + i * 60), line,
                       FONT_SERIF_BOLD, 46, CREAM)

    _with_shadow(ov).save(path)


def build_thumbnail(scene_frame_path: str) -> None:
    """Designed poster: best scene frame + title + brand, saved as JPG."""
    base = Image.open(scene_frame_path).convert("RGB")
    base = base.resize((FRAME_WIDTH, FRAME_HEIGHT), Image.LANCZOS)
    img = base.convert("RGBA")

    ov = Image.new("RGBA", (FRAME_WIDTH, FRAME_HEIGHT), (0, 0, 0, 0))
    ov.alpha_composite(_vignette_layer(0.55))
    draw = ImageDraw.Draw(ov)

    # top and bottom gradients
    for y0, y1, flip in ((0, 420, True), (FRAME_HEIGHT - 700, FRAME_HEIGHT, False)):
        h = y1 - y0
        band = Image.new("L", (1, h), 0)
        for i in range(h):
            p = i / h
            band.putpixel((0, i), int(210 * ((1 - p) if flip else p) ** 1.4))
        band = band.resize((FRAME_WIDTH, h))
        g = Image.new("RGBA", (FRAME_WIDTH, h), (5, 3, 2, 255))
        g.putalpha(band)
        ov.alpha_composite(g, (0, y0))

    draw_tracked_fit(draw, (FRAME_WIDTH // 2, 170), "THE RIDER'S GANG",
                     FONT_SERIF_BOLD, 34, GOLD, tracking=7)
    draw.line([(FRAME_WIDTH * 0.34, 220), (FRAME_WIDTH * 0.66, 220)],
              fill=GOLD, width=2)

    cy = FRAME_HEIGHT - 430
    draw_tracked_fit(draw, (FRAME_WIDTH // 2, cy), "THE NIGHT THEY",
                     FONT_SERIF_BOLD, 82, CREAM, tracking=2)
    draw_tracked_fit(draw, (FRAME_WIDTH // 2, cy + 105), "RACED THE JUKEBOX",
                     FONT_SERIF_BOLD, 82, CREAM, tracking=2)
    draw_plain_fit(draw, (FRAME_WIDTH // 2, cy + 200),
                   "A true story from 1950s London", FONT_SERIF_ITALIC, 42, GOLD)

    img.alpha_composite(_with_shadow(ov))
    img.convert("RGB").save(THUMB_PATH, quality=90)
    print(f"[Thumb] Saved: {THUMB_PATH}")


# ── Video segment builders ───────────────────────────────────────────

def preprocess_scene(clip: str, overlay: str, out: str) -> None:
    """Slow-mo, upscale, brighten, sharpen, caption, and fade one scene."""
    # 54fps interpolation / 2.25x slowdown lands exactly back on 24fps
    dur = CLIP_SEC * SLOW_FACTOR
    subprocess.run([
        "ffmpeg", "-y", "-i", clip, "-i", overlay,
        "-filter_complex",
        "[0:v]minterpolate=fps=24:mi_mode=mci:mc_mode=aobmc:vsbmc=1,"
        "scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,"
        "crop=1080:1920,"
        "eq=gamma=1.03:contrast=1.04:saturation=1.05,"
        "cas=0.3[v];"
        f"[v][1:v]overlay=0:0,"
        f"fade=t=in:st=0:d={FADE_SEC},fade=t=out:st={dur - FADE_SEC}:d={FADE_SEC}[outv]",
        "-map", "[outv]", "-r", "24",
        "-c:v", "libx264", "-preset", "fast", "-crf", "16",
        "-pix_fmt", "yuv420p", out,
    ], check=True, capture_output=True)


def card_to_video(png: str, seconds: float, out: str, fade_in: bool = True) -> None:
    fades = f"fade=t=out:st={seconds - FADE_SEC}:d={FADE_SEC}"
    if fade_in:
        fades = f"fade=t=in:st=0:d={FADE_SEC}," + fades
    subprocess.run([
        "ffmpeg", "-y", "-loop", "1", "-t", str(seconds), "-i", png,
        "-vf", fades,
        "-r", "24", "-c:v", "libx264", "-preset", "fast", "-crf", "16",
        "-pix_fmt", "yuv420p", out,
    ], check=True, capture_output=True)


def main():
    tmp = os.path.join(STORY_DIR, ".assembly")
    os.makedirs(tmp, exist_ok=True)

    # cards
    title_png = os.path.join(tmp, "title.png")
    outro_png = os.path.join(tmp, "outro.png")
    build_title_card(title_png)
    build_outro_card(outro_png)
    segments = []

    print("[Assemble] Title card...")
    title_mp4 = os.path.join(tmp, "seg_00_title.mp4")
    # no fade-in: the film (and its default preview frame) opens visible
    card_to_video(title_png, TITLE_SEC, title_mp4, fade_in=False)
    segments.append(title_mp4)

    for i, scene in enumerate(STORYBOARD, 1):
        clip = os.path.join(STORY_DIR, f"scene_{scene['id']}.mp4")
        if not os.path.exists(clip):
            print(f"ERROR: missing scene clip {clip}")
            sys.exit(1)
        print(f"[Assemble] Scene {i}/{len(STORYBOARD)}: {scene['id']} "
              "(interpolate + upscale + caption)...")
        overlay = os.path.join(tmp, f"ov_{scene['id']}.png")
        build_scene_overlay(scene, overlay)
        seg = os.path.join(tmp, f"seg_{i:02d}_{scene['id']}.mp4")
        preprocess_scene(clip, overlay, seg)
        segments.append(seg)

    print("[Assemble] Outro card...")
    outro_mp4 = os.path.join(tmp, "seg_99_outro.mp4")
    card_to_video(outro_png, OUTRO_SEC, outro_mp4)
    segments.append(outro_mp4)

    # thumbnail from the race scene (the most dramatic frame)
    build_thumbnail(os.path.join(STORY_DIR, "stills", "01_cafe.png"))

    # story-synced score: band kicks in at the jukebox scene,
    # engine rumble under launch through the final straight
    scene_dur = CLIP_SEC * SLOW_FACTOR
    total = TITLE_SEC + len(STORYBOARD) * scene_dur + OUTRO_SEC
    band_in = TITLE_SEC + 1 * scene_dur          # scene 2: the coin drop
    race_span = (TITLE_SEC + 2 * scene_dur,      # scenes 3-6: the race
                 TITLE_SEC + 6 * scene_dur)
    wav = os.path.join(tmp, "bed.wav")
    engine_raw = os.path.join(tmp, "engines.f32")
    build_engine_track(total, race_span, engine_raw)
    engines = load_engine_track(engine_raw, int(total * 44100))
    build_score(total, wav, band_in_sec=band_in, race_span=race_span,
                engine_track=engines)

    # concat everything + mux audio
    concat_list = os.path.join(tmp, "concat.txt")
    with open(concat_list, "w") as f:
        for s in segments:
            f.write(f"file '{os.path.abspath(s)}'\n")

    print("[Assemble] Final concat + audio...")
    no_thumb = os.path.join(tmp, "final_no_thumb.mp4")
    subprocess.run([
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0", "-i", concat_list,
        "-i", wav,
        "-map", "0:v", "-map", "1:a",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart", "-shortest",
        no_thumb,
    ], check=True, capture_output=True)

    # embed the poster as cover art via stream-copy remux
    print("[Assemble] Embedding thumbnail...")
    subprocess.run([
        "ffmpeg", "-y", "-i", no_thumb, "-i", THUMB_PATH,
        "-map", "0", "-map", "1",
        "-c", "copy", "-c:v:1", "mjpeg",
        "-disposition:v:1", "attached_pic",
        "-movflags", "+faststart",
        OUT_PATH,
    ], check=True, capture_output=True)

    size_mb = os.path.getsize(OUT_PATH) / 1024 / 1024
    print(f"\nStory reel saved: {OUT_PATH} ({size_mb:.1f} MB, ~{total:.0f}s)")


if __name__ == "__main__":
    main()
