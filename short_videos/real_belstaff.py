"""
Belstaff v3 — real-footage hybrid (Option A+D).

~70% real licensed footage (Wikimedia Commons), AI only where the
story demands staged period shots:

    hook      REAL  dark forest road POV (retro motorcycle)
    brand     CARD  BELSTAFF EST. 1924
    storm     REAL  arcus storm cloud over English houses
    wax       AI    the Stoke-on-Trent wax workshop
    ride      REAL  countryside POV under dramatic clouds + engine
    proof     AI    macro rain beading off the waxed shoulder
    home      REAL  4K candle flame (warmth of arrival)
    heirloom  AI    father hands the jacket to his son
    outro     CARD  BELSTAFF wordmark + credit

Viral-reel rules applied: motion + curiosity hook in the first
second, brand visible from the opening frame, fitted captions that
fade before each crossfade, unified warm grade + grain so real and
AI footage sit in one world, poster thumbnail, faststart.

Run:  python3 -m short_videos.real_belstaff
"""

import os
import subprocess
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PIL import Image, ImageDraw, ImageFilter

from short_videos import (
    FONT_SERIF_BOLD, FONT_SERIF_ITALIC, FRAME_HEIGHT, FRAME_WIDTH, PALETTE,
)
from short_videos.build_film import build_scene_overlay
from short_videos.build_story_reel import (
    CREAM, GOLD, _vignette_layer, _with_shadow, draw_plain_fit,
    draw_tracked_fit,
)
from short_videos.film_score import MOODS, SFX, _env, _pad_chord
from short_videos.rockabilly_score import SR, _add

STOCK = "output/short_videos/stock"
AI_DIR = "output/short_videos/films/belstaff-the-jacket-that-built-a-riding-legend"
OUT_DIR = "output/short_videos/films"
OUT_PATH = os.path.join(OUT_DIR, "belstaff-the-jacket-that-built-a-riding-legend.mp4")
THUMB_PATH = os.path.join(OUT_DIR, "belstaff-the-jacket-that-built-a-riding-legend_cover.jpg")
TMP = os.path.join(AI_DIR, ".assembly_v3")

XF = 0.45

# beat: (name, source, src_start, duration, mode, slow, caption, eyebrow, sfx)
BEATS = [
    ("hook", f"{STOCK}/ride1.webm", 600.0, 2.3, "letterbox", 1.0,
     None, None, ["engine"]),
    ("brand", "CARD_BRAND", 0, 1.8, "card", 1.0, None, None, []),
    ("storm", f"{STOCK}/arcus.webm", 5.0, 3.5, "letterbox", 1.0,
     "England, 1924.\nRain always won.", "A TRUE STORY", ["rain", "wind"]),
    ("wax", f"{AI_DIR}/scene_02_wax.mp4", 0.0, 3.5625, "portrait", 1.0,
     "Until Belstaff taught cotton\nto drink wax.", "STOKE-ON-TRENT", ["ticks"]),
    ("ride", f"{STOCK}/ride1.webm", 420.0, 4.2, "letterbox", 1.0,
     "Riders crossed storms\nand stayed dry.", "THE TRIALMASTER", ["engine"]),
    ("proof", f"{AI_DIR}/scene_04_shedding.mp4", 0.0, 3.5, "portrait", 1.0,
     "The rain rolled off.\nThe rider rode on.", "THE PROOF", ["rain"]),
    ("home", f"{STOCK}/candle.webm", 20.0, 3.2, "portrait", 1.0,
     "Soaked in storm —\ndry at the heart.", "HOME", []),
    ("heirloom", f"{AI_DIR}/scene_06_heirloom.mp4", 0.0, 3.5625, "portrait", 1.0,
     "Forty years on: handed down\nlike land.", "THE HEIRLOOM", []),
    ("outro", "CARD_OUTRO", 0, 2.3, "card", 1.0, None, None, []),
]

# unified grade: warm, slightly lifted, real film grain on everything
GRADE = ("eq=gamma=1.04:contrast=1.05:saturation=0.92:gamma_r=1.03,"
         "colorbalance=rs=0.03:rm=0.02:bs=-0.03,"
         "noise=alls=5:allf=t")


# ── designed cards / overlays ────────────────────────────────────────

def card_brand(path):
    img = Image.new("RGBA", (FRAME_WIDTH, FRAME_HEIGHT), (14, 12, 10, 255))
    d = ImageDraw.Draw(img)
    cy = FRAME_HEIGHT // 2
    draw_tracked_fit(d, (FRAME_WIDTH // 2, cy - 60), "BELSTAFF",
                     FONT_SERIF_BOLD, 110, CREAM, tracking=10)
    d.line([(FRAME_WIDTH * 0.3, cy + 30), (FRAME_WIDTH * 0.7, cy + 30)],
           fill=GOLD, width=2)
    draw_tracked_fit(d, (FRAME_WIDTH // 2, cy + 90), "EST. 1924",
                     FONT_SERIF_BOLD, 40, GOLD, tracking=8)
    draw_plain_fit(d, (FRAME_WIDTH // 2, cy + 170),
                   "The jacket that refused the rain",
                   FONT_SERIF_ITALIC, 40, CREAM)
    img.convert("RGB").save(path)


def card_outro(path):
    img = Image.new("RGBA", (FRAME_WIDTH, FRAME_HEIGHT), (14, 12, 10, 255))
    d = ImageDraw.Draw(img)
    cy = FRAME_HEIGHT // 2
    draw_tracked_fit(d, (FRAME_WIDTH // 2, cy - 60), "BELSTAFF",
                     FONT_SERIF_BOLD, 96, CREAM, tracking=9)
    d.line([(FRAME_WIDTH * 0.32, cy + 15), (FRAME_WIDTH * 0.68, cy + 15)],
           fill=GOLD, width=2)
    draw_plain_fit(d, (FRAME_WIDTH // 2, cy + 80),
                   "Story by The Rider's Gang", FONT_SERIF_ITALIC, 36, CREAM)
    draw_plain_fit(d, (FRAME_WIDTH // 2, cy + 145),
                   "The full story — link in bio", FONT_SERIF_ITALIC, 38, GOLD)
    img.convert("RGB").save(path)


def hook_overlay(path):
    """Brand at top + curiosity hook — visible from the first frame."""
    ov = Image.new("RGBA", (FRAME_WIDTH, FRAME_HEIGHT), (0, 0, 0, 0))
    ov.alpha_composite(_vignette_layer(0.45))
    d = ImageDraw.Draw(ov)
    draw_tracked_fit(d, (FRAME_WIDTH // 2, 150), "BELSTAFF",
                     FONT_SERIF_BOLD, 46, CREAM, tracking=9)
    d.line([(FRAME_WIDTH * 0.38, 205), (FRAME_WIDTH * 0.62, 205)],
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
    draw_plain_fit(d, (FRAME_WIDTH // 2, cy), "For 100 years, rain won.",
                   FONT_SERIF_BOLD, 52, CREAM)
    draw_plain_fit(d, (FRAME_WIDTH // 2, cy + 75), "One jacket refused.",
                   FONT_SERIF_BOLD, 52, GOLD)
    _with_shadow(ov).save(path)


# ── beat renderer ────────────────────────────────────────────────────

def render_beat(name, src, start, dur, mode, slow, caption, eyebrow, out):
    if mode == "card":
        png = os.path.join(TMP, f"{name}.png")
        (card_brand if src == "CARD_BRAND" else card_outro)(png)
        subprocess.run([
            "ffmpeg", "-y", "-loop", "1", "-t", str(dur), "-i", png,
            "-vf", GRADE, "-r", "24", "-c:v", "libx264", "-preset", "fast",
            "-crf", "16", "-pix_fmt", "yuv420p", out,
        ], check=True, capture_output=True)
        return

    # overlay: hook gets its special treatment, story beats get captions
    ov_png = os.path.join(TMP, f"ov_{name}.png")
    if name == "hook":
        hook_overlay(ov_png)
    elif caption:
        build_scene_overlay({"caption": caption, "eyebrow": eyebrow}, ov_png)
    else:
        Image.new("RGBA", (FRAME_WIDTH, FRAME_HEIGHT), (0, 0, 0, 0)).save(ov_png)

    if mode == "portrait":
        fit = ("scale=1080:1920:force_original_aspect_ratio=increase:"
               "flags=lanczos,crop=1080:1920")
        vin = "[0:v]" + (f"setpts={slow}*PTS," if slow != 1.0 else "") + fit
    else:  # letterbox: blurred fill behind sharp landscape strip
        vin = (
            "[0:v]split[a][b];"
            "[a]scale=1080:1920:force_original_aspect_ratio=increase,"
            "crop=1080:1920,boxblur=24:2,eq=brightness=-0.12[bg];"
            "[b]scale=1080:-2:flags=lanczos[fg];"
            "[bg][fg]overlay=(W-w)/2:(H-h)/2"
        )

    cap_out = dur - XF - 0.3
    subprocess.run([
        "ffmpeg", "-y", "-ss", str(start), "-t", str(dur * slow + 0.2),
        "-i", src, "-loop", "1", "-t", str(dur), "-i", ov_png,
        "-filter_complex",
        f"{vin},{GRADE},fps=24[v];"
        f"[1:v]format=rgba,fade=t=in:st=0.1:d=0.3:alpha=1,"
        f"fade=t=out:st={cap_out}:d=0.3:alpha=1[ov];"
        "[v][ov]overlay=0:0:shortest=1[outv]",
        "-map", "[outv]", "-r", "24", "-an",
        "-c:v", "libx264", "-preset", "fast", "-crf", "16",
        "-pix_fmt", "yuv420p", out,
    ], check=True, capture_output=True)


# ── audio: storm score + beat-cued SFX at real offsets ───────────────

def build_audio(beat_times, total, wav_path):
    rng = np.random.default_rng(1924)
    n = int(total * SR)
    band_in = beat_times["wax"][0]
    audio = MOODS["storm_heritage"](rng, total, band_in)[:n]
    if len(audio) < n:
        audio = np.concatenate([audio, np.zeros(n - len(audio))])

    for name, _, _, _, _, _, _, _, effects in BEATS:
        if not effects:
            continue
        at, dur = beat_times[name]
        for eff in effects:
            _add(audio, SFX[eff](rng, dur), at)

    ring_at = total - 4.6
    nring = int(3.2 * SR)
    t = np.arange(nring) / SR
    chord = sum(np.sin(2 * np.pi * f * t) for f in (110.0, 138.6, 164.8, 220.0))
    _add(audio, chord * _env(nring, int(0.02 * SR), int(2.6 * SR)) * 0.10, ring_at)

    fade_in = int(0.4 * SR)
    fade_out = int(2.0 * SR)
    audio[:fade_in] *= 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, fade_in))
    audio[-fade_out:] *= 0.5 + 0.5 * np.cos(np.linspace(0, np.pi, fade_out))
    audio = np.tanh(audio * 1.6) / np.tanh(1.6)
    peak = np.abs(audio).max()
    if peak > 0:
        audio = audio / peak * 0.55
    delay = int(0.012 * SR)
    right = np.concatenate([np.zeros(delay), audio[:-delay]])
    stereo = np.stack([audio, right], axis=1)
    import wave as wavmod
    pcm = (stereo * 32767).astype(np.int16)
    with wavmod.open(wav_path, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm.tobytes())


def build_thumbnail():
    frame = os.path.join(TMP, "thumb_src.png")
    subprocess.run(["ffmpeg", "-y", "-ss", "601.5", "-i", f"{STOCK}/ride1.webm",
                    "-frames:v", "1", frame], check=True, capture_output=True)
    base = Image.open(frame).convert("RGB")
    # letterbox-style poster from the landscape frame
    bg = base.resize((FRAME_WIDTH, FRAME_HEIGHT))
    bg = bg.filter(ImageFilter.GaussianBlur(24)).point(lambda v: int(v * 0.55))
    fg_w = FRAME_WIDTH
    fg_h = int(base.height * fg_w / base.width)
    fg = base.resize((fg_w, fg_h), Image.LANCZOS)
    img = bg.convert("RGBA")
    img.paste(fg, (0, (FRAME_HEIGHT - fg_h) // 2))
    ov = Image.new("RGBA", (FRAME_WIDTH, FRAME_HEIGHT), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    draw_tracked_fit(d, (FRAME_WIDTH // 2, 200), "BELSTAFF",
                     FONT_SERIF_BOLD, 92, CREAM, tracking=9)
    d.line([(FRAME_WIDTH * 0.34, 265), (FRAME_WIDTH * 0.66, 265)],
           fill=GOLD, width=2)
    cy = FRAME_HEIGHT - 400
    draw_plain_fit(d, (FRAME_WIDTH // 2, cy), "For 100 years, rain won.",
                   FONT_SERIF_BOLD, 56, CREAM)
    draw_plain_fit(d, (FRAME_WIDTH // 2, cy + 80), "One jacket refused.",
                   FONT_SERIF_BOLD, 56, GOLD)
    draw_plain_fit(d, (FRAME_WIDTH // 2, cy + 165), "EST. 1924",
                   FONT_SERIF_ITALIC, 40, GOLD)
    img.alpha_composite(_with_shadow(ov))
    img.convert("RGB").save(THUMB_PATH, quality=90)


def main():
    os.makedirs(TMP, exist_ok=True)

    segments, durations = [], []
    beat_times = {}
    cum = 0.0
    for i, (name, src, start, dur, mode, slow, cap, eye, sfx) in enumerate(BEATS):
        out = os.path.join(TMP, f"seg_{i:02d}_{name}.mp4")
        print(f"[Beat {i + 1}/{len(BEATS)}] {name}")
        render_beat(name, src, start, dur, mode, slow, cap, eye, out)
        segments.append(out)
        durations.append(dur)
        at = cum if i == 0 else cum - XF
        beat_times[name] = (max(0.0, at), dur)
        cum = at + dur

    total = cum
    wav = os.path.join(TMP, "score.wav")
    build_audio(beat_times, total, wav)

    # crossfade chain
    inputs = []
    for s in segments:
        inputs += ["-i", s]
    graph = []
    cum2 = durations[0]
    prev = "[0:v]"
    for k in range(1, len(segments)):
        offset = cum2 - XF
        outlbl = f"[v{k}]" if k < len(segments) - 1 else "[outv]"
        graph.append(f"{prev}[{k}:v]xfade=transition=fade:duration={XF}:"
                     f"offset={offset:.4f}{outlbl}")
        prev = outlbl
        cum2 = offset + durations[k]

    print("[Final] crossfade concat + audio + thumbnail...")
    no_thumb = os.path.join(TMP, "final_no_thumb.mp4")
    subprocess.run([
        "ffmpeg", "-y", *inputs, "-i", wav,
        "-filter_complex", ";".join(graph),
        "-map", "[outv]", "-map", f"{len(segments)}:a",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart", "-shortest", no_thumb,
    ], check=True, capture_output=True)

    build_thumbnail()
    subprocess.run([
        "ffmpeg", "-y", "-i", no_thumb, "-i", THUMB_PATH,
        "-map", "0", "-map", "1", "-c", "copy", "-c:v:1", "mjpeg",
        "-disposition:v:1", "attached_pic", "-movflags", "+faststart",
        OUT_PATH,
    ], check=True, capture_output=True)

    size = os.path.getsize(OUT_PATH) / 1024 / 1024
    print(f"\nBelstaff v3 saved: {OUT_PATH} ({size:.1f} MB, ~{total:.1f}s)")


if __name__ == "__main__":
    main()
