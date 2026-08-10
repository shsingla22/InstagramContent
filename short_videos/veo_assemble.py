"""
Film Assembly — stitches the AI-generated scenes (Wan 2.2 A14B,
video-only) into the finished Instagram reel.

Timeline:  scene1(hook) → BELSTAFF card → scene2 → scene3 → scene4
           → outro card

Video: crossfades between all segments; captions fade out before
each transition. Audio: fully synthesized — a classic-rock riding
score carries the film with the full band playing from the very
first frame (crash on the downbeat, E–D–A power chords, driving
backbeat, anthemic lead melody), with per-scene SFX (rain, wind,
the real engine recording) cued at each scene's actual start time.
Poster thumbnail embedded.
"""

import os
import subprocess
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PIL import Image

from short_videos import FRAME_HEIGHT, FRAME_WIDTH
from short_videos.build_film import build_scene_overlay
from short_videos.build_story_reel import (
    CREAM, GOLD, _vignette_layer, _with_shadow, draw_plain_fit,
    draw_tracked_fit,
)
from short_videos.film_score import MOODS, SFX
from short_videos.real_belstaff import card_brand, card_outro, hook_overlay
from short_videos.rockabilly_score import SR, _add, _env

XF = 0.45
BRAND_SEC = 1.6
OUTRO_SEC = 2.2


def _clip_duration(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", path], capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def _render_video_segment(src, dur, overlay_png, out, is_card=False):
    if is_card:
        subprocess.run([
            "ffmpeg", "-y", "-loop", "1", "-t", str(dur), "-i", src,
            "-vf", "noise=alls=4:allf=t", "-r", "24",
            "-c:v", "libx264", "-preset", "fast", "-crf", "16",
            "-pix_fmt", "yuv420p", out], check=True, capture_output=True)
        return
    cap_out = dur - XF - 0.5   # caption fully out before the crossfade
    subprocess.run([
        "ffmpeg", "-y", "-i", src, "-loop", "1", "-t", str(dur),
        "-i", overlay_png,
        "-filter_complex",
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase:"
        "flags=lanczos,crop=1080:1920,fps=24,"
        "eq=gamma=1.02:contrast=1.03:saturation=0.96,"
        "noise=alls=4:allf=t[v];"
        f"[1:v]format=rgba,fade=t=in:st=0.2:d=0.4:alpha=1,"
        f"fade=t=out:st={cap_out}:d=0.35:alpha=1[ov];"
        "[v][ov]overlay=0:0:shortest=1[outv]",
        "-map", "[outv]", "-r", "24", "-an",
        "-c:v", "libx264", "-preset", "fast", "-crf", "16",
        "-pix_fmt", "yuv420p", out], check=True, capture_output=True)


def build_thumbnail(scene_clip, thumb_path):
    tmpf = thumb_path + ".src.png"
    subprocess.run(["ffmpeg", "-y", "-ss", "4", "-i", scene_clip,
                    "-frames:v", "1", tmpf], check=True, capture_output=True)
    from PIL import ImageDraw
    base = Image.open(tmpf).convert("RGB").resize(
        (FRAME_WIDTH, FRAME_HEIGHT), Image.LANCZOS)
    img = base.convert("RGBA")
    ov = Image.new("RGBA", (FRAME_WIDTH, FRAME_HEIGHT), (0, 0, 0, 0))
    ov.alpha_composite(_vignette_layer(0.5))
    d = ImageDraw.Draw(ov)
    draw_tracked_fit(d, (FRAME_WIDTH // 2, 200), "BELSTAFF",
                     None or __import__("short_videos").FONT_SERIF_BOLD,
                     92, CREAM, tracking=9)
    d.line([(FRAME_WIDTH * 0.34, 265), (FRAME_WIDTH * 0.66, 265)],
           fill=GOLD, width=2)
    from short_videos import FONT_SERIF_BOLD, FONT_SERIF_ITALIC
    cy = FRAME_HEIGHT - 400
    draw_plain_fit(d, (FRAME_WIDTH // 2, cy), "For 100 years, rain won.",
                   FONT_SERIF_BOLD, 56, CREAM)
    draw_plain_fit(d, (FRAME_WIDTH // 2, cy + 80), "One jacket refused.",
                   FONT_SERIF_BOLD, 56, GOLD)
    draw_plain_fit(d, (FRAME_WIDTH // 2, cy + 165), "EST. 1924",
                   FONT_SERIF_ITALIC, 40, GOLD)
    img.alpha_composite(_with_shadow(ov))
    img.convert("RGB").save(thumb_path, quality=90)
    os.remove(tmpf)


def assemble(scenes, ai_dir, out_path, thumb_path):
    tmp = os.path.join(ai_dir, ".assembly")
    os.makedirs(tmp, exist_ok=True)

    # timeline: scene1, brand card, scene2..4, outro
    brand_png = os.path.join(tmp, "brand.png")
    outro_png = os.path.join(tmp, "outro.png")
    card_brand(brand_png)
    card_outro(outro_png)

    entries = []       # (src, dur, sfx list or None, meta)
    s1 = os.path.join(ai_dir, f"scene_{scenes[0]['id']}.mp4")
    entries.append((s1, min(8.0, _clip_duration(s1)),
                    scenes[0].get("sfx"), "hook"))
    entries.append((brand_png, BRAND_SEC, None, "card"))
    for sc in scenes[1:]:
        p = os.path.join(ai_dir, f"scene_{sc['id']}.mp4")
        entries.append((p, min(8.0, _clip_duration(p)), sc.get("sfx"), sc))
    entries.append((outro_png, OUTRO_SEC, None, "card"))

    # render video segments
    segments, durations, metas = [], [], []
    for i, (src, dur, sfx, meta) in enumerate(entries):
        out = os.path.join(tmp, f"seg_{i:02d}.mp4")
        print(f"[Assemble] segment {i + 1}/{len(entries)}")
        if meta == "card":
            _render_video_segment(src, dur, None, out, is_card=True)
        elif meta == "hook":
            ov = os.path.join(tmp, "ov_hook.png")
            hook_overlay(ov)
            _render_video_segment(src, dur, ov, out)
        else:
            ov = os.path.join(tmp, f"ov_{meta['id']}.png")
            build_scene_overlay(meta, ov)
            _render_video_segment(src, dur, ov, out)
        segments.append(out)
        durations.append(dur)
        metas.append((sfx, dur))

    # audio timeline: storm-heritage score + SFX cued per scene
    starts = [0.0]
    for k in range(1, len(durations)):
        starts.append(starts[-1] + durations[k - 1] - XF)
    total = starts[-1] + durations[-1]

    n = int(total * SR)
    rng = np.random.default_rng(1924)
    audio = MOODS["classic_rock"](rng, total, 0.0)[:n]
    if len(audio) < n:
        audio = np.concatenate([audio, np.zeros(n - len(audio))])

    SFX_GAIN = {"engine": 0.4}     # keep the bike well under the music
    for (sfx, dur), at in zip(metas, starts):
        for effect in sfx or []:
            seg = SFX[effect](rng, dur) * SFX_GAIN.get(effect, 1.0)
            f = int(XF * SR)
            if len(seg) > 2 * f:
                seg[:f] *= np.linspace(0, 1, f)
                seg[-f:] *= np.linspace(1, 0, f)
            _add(audio, seg, at)

    # closing chord under the outro card
    ring_at = max(0.0, total - OUTRO_SEC - 1.2)
    nring = int(3.0 * SR)
    t = np.arange(nring) / SR
    chord = sum(np.sin(2 * np.pi * f * t)
                for f in (82.41, 123.47, 164.81, 207.65))
    _add(audio, chord * _env(nring, int(0.02 * SR), int(2.4 * SR)) * 0.10,
         ring_at)

    fade_in = int(0.12 * SR)   # just enough to avoid a click — the
                               # band hits from the very first frame
    audio[:fade_in] *= 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, fade_in))
    fade_out = int(1.8 * SR)
    audio[-fade_out:] *= 0.5 + 0.5 * np.cos(np.linspace(0, np.pi, fade_out))
    audio = np.tanh(audio * 1.6) / np.tanh(1.6)
    peak = np.abs(audio).max()
    if peak > 0:
        audio = audio / peak * 0.5     # headroom for AAC encoder overshoot
    delay = int(0.012 * SR)
    right = np.concatenate([np.zeros(delay), audio[:-delay]])
    stereo = np.stack([audio, right], axis=1)
    wav = os.path.join(tmp, "mix.wav")
    import wave as wavmod
    pcm = (stereo * 32767).astype(np.int16)
    with wavmod.open(wav, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm.tobytes())

    # video crossfade chain + mux
    inputs = []
    for s in segments:
        inputs += ["-i", s]
    graph, cum, prev = [], durations[0], "[0:v]"
    for k in range(1, len(segments)):
        offset = cum - XF
        outlbl = f"[v{k}]" if k < len(segments) - 1 else "[outv]"
        graph.append(f"{prev}[{k}:v]xfade=transition=fade:duration={XF}:"
                     f"offset={offset:.4f}{outlbl}")
        prev = outlbl
        cum = offset + durations[k]

    print("[Assemble] final mux...")
    no_thumb = os.path.join(tmp, "final_no_thumb.mp4")
    subprocess.run([
        "ffmpeg", "-y", *inputs, "-i", wav,
        "-filter_complex", ";".join(graph),
        "-map", "[outv]", "-map", f"{len(segments)}:a",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
        "-movflags", "+faststart", "-shortest", no_thumb,
    ], check=True, capture_output=True)

    build_thumbnail(os.path.join(ai_dir, f"scene_{scenes[2]['id']}.mp4"),
                    thumb_path)
    subprocess.run([
        "ffmpeg", "-y", "-i", no_thumb, "-i", thumb_path,
        "-map", "0", "-map", "1", "-c", "copy", "-c:v:1", "mjpeg",
        "-disposition:v:1", "attached_pic", "-movflags", "+faststart",
        out_path,
    ], check=True, capture_output=True)

    size = os.path.getsize(out_path) / 1024 / 1024
    print(f"\nVeo film saved: {out_path} ({size:.1f} MB, ~{cum:.1f}s)")
