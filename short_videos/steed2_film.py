"""
STEED Film Nº2 — "The Jacket" (the Belstaff story, told by STEED).

Episode two of the STEED series. Character shots are the exact
clips from Nº1 (same concept-art-derived footage, so STEED is
pixel-identical); the story b-roll is the four Belstaff scenes
already generated for the original film; narration is the same
Kokoro am_onyx voice at the same speed. Zero new video generation.

Run:  HF_TOKEN=... python3 -m short_videos.steed2_film --voice
      python3 -m short_videos.steed2_film            (assemble)
"""

import argparse
import os
import subprocess
import sys
import wave as wavmod

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PIL import Image, ImageDraw

from short_videos import (
    FONT_SERIF_BOLD, FONT_SERIF_ITALIC, FRAME_HEIGHT, FRAME_WIDTH,
)
from short_videos.build_story_reel import (
    CREAM, GOLD, _vignette_layer, _with_shadow, draw_plain_fit,
    draw_tracked_fit,
)
from short_videos.film_score import MOODS, SFX, _crash
from short_videos.rockabilly_score import SR, _add, _env
from short_videos.steed_film import (
    VOICE, _caption_png, _cta_png, _load_wav_mono, _watermark,
)

STEED_DIR = "output/short_videos/films/steed-wan"
BELSTAFF_DIR = "output/short_videos/films/belstaff-veo"
VO_DIR = os.path.join(STEED_DIR, ".voice2")
TMP = os.path.join(STEED_DIR, ".assembly2")
OUT_PATH = "output/short_videos/films/steed-02-the-jacket.mp4"
THUMB_PATH = "output/short_videos/films/steed-02-the-jacket_cover.jpg"

BPM = 120
BEAT = 60.0 / BPM

VO_LINES = [
    ("vo1", "They ask me what riders fear. Not speed. Rain."),
    ("vo2", "England, nineteen twenty four. The storms came for every "
            "rider."),
    ("vo3", "In Stoke on Trent, they taught cotton to drink wax."),
    ("vo4", "The rain hit the shoulder... and rolled away. The rider "
            "rode on."),
    ("vo5", "Forty years later, that jacket was handed down like land."),
    ("vo6", "They call it Belstaff. I call it armor."),
    ("vo7", "Follow me. Every legend rides again."),
]

# (dir, source, start, beats, caption, vo id, crop_top) — beats set
# after measuring the narration
SHOTS = [
    (STEED_DIR, "scene_01_awaken", 0.2, 8,
     "What do riders fear? Rain.", "vo1", True),
    (BELSTAFF_DIR, "scene_01_storm", 0.0, 10,
     "England, 1924. The storm.", "vo2", False),
    (BELSTAFF_DIR, "scene_02_wax", 0.4, 9,
     "Cotton, taught to drink wax.", "vo3", False),
    (BELSTAFF_DIR, "scene_03_test", 0.3, 6,
     "The rain hit…", "vo4", False),
    (BELSTAFF_DIR, "scene_03_test", 3.0, 4,
     "…and rolled away.", None, False),
    (BELSTAFF_DIR, "scene_04_gift", 0.3, 9,
     "Handed down like land.", "vo5", False),
    (STEED_DIR, "scene_08_street", 0.4, 8,
     "They call it Belstaff. I call it armor.", "vo6", False),
    (STEED_DIR, "scene_08_street", 1.5, 7, None, "vo7", False),  # CTA
    (STEED_DIR, "scene_01_awaken", 0.2, 4, None, None, True),    # loop
]
CTA_IDX = 7


def _render_cut(idx, src_dir, src, start, dur, caption, crop_top, out):
    base = ("crop=iw:ih*0.82:0:0," if crop_top else "")
    vf = (f"{base}scale=1080:1920:force_original_aspect_ratio=increase:"
          "flags=lanczos,crop=1080:1920,fps=24,"
          "eq=gamma=1.02:contrast=1.05:saturation=0.98")
    cmd = ["ffmpeg", "-y", "-ss", f"{start:.3f}", "-i",
           os.path.join(src_dir, f"{src}.mp4")]
    overlays = []
    if caption:
        png = os.path.join(TMP, f"cap_{idx:02d}.png")
        _caption_png(caption, png)
        overlays.append((png, 0.1))
    if idx == CTA_IDX:
        png = os.path.join(TMP, "cta.png")
        _cta_png(png)
        overlays.append((png, 0.5))
    if overlays:
        for png, _ in overlays:
            cmd += ["-loop", "1", "-t", f"{dur:.3f}", "-i", png]
        graph = f"[0:v]{vf}[v0]"
        prev = "[v0]"
        for k, (_, t_in) in enumerate(overlays):
            graph += (f";[{k + 1}:v]format=rgba,"
                      f"fade=t=in:st={t_in}:d=0.22:alpha=1[o{k}]")
            nxt = f"[m{k}]" if k < len(overlays) - 1 else "[outv]"
            graph += f";{prev}[o{k}]overlay=0:0:shortest=1{nxt}"
            prev = nxt
        cmd += ["-filter_complex", graph, "-map", "[outv]"]
    else:
        cmd += ["-vf", vf]
    cmd += ["-t", f"{dur:.3f}", "-r", "24", "-an", "-c:v", "libx264",
            "-preset", "fast", "-crf", "16", "-pix_fmt", "yuv420p", out]
    subprocess.run(cmd, check=True, capture_output=True)


def build_audio(shot_starts, total, wav_path):
    rng = np.random.default_rng(1924)
    n = int(total * SR)

    vo = np.zeros(n)
    prev_end = 0.0
    for (d_, src, start, beats, cap, vo_id, crop), at in zip(SHOTS,
                                                             shot_starts):
        if not vo_id:
            continue
        seg = _load_wav_mono(os.path.join(VO_DIR, f"{vo_id}.wav"))
        rms = np.sqrt((seg ** 2).mean())
        if rms > 0:
            seg = seg / rms * 0.165
        vo_at = max(at + 0.1, prev_end + 0.2)
        _add(vo, seg, vo_at)
        prev_end = vo_at + len(seg) / SR

    music = MOODS["rockabilly"](rng, total, 0.0)[:n] * 0.8
    if len(music) < n:
        music = np.concatenate([music, np.zeros(n - len(music))])
    _add(music, _crash(rng) * 0.5, shot_starts[1])
    # weather + machine under the story: rain through the storm and
    # test scenes, engine under the night ride
    _add(music, SFX["rain"](rng, shot_starts[3] - shot_starts[1]),
         shot_starts[1])
    _add(music, SFX["rain"](rng, shot_starts[5] - shot_starts[3]),
         shot_starts[3])
    _add(music, SFX["engine"](rng, shot_starts[5] - shot_starts[3]) * 0.4,
         shot_starts[3])
    ring_at = total - 2.4
    nring = int(2.2 * SR)
    tt = np.arange(nring) / SR
    ring = sum(np.sin(2 * np.pi * f * tt)
               for f in (110.0, 164.81, 220.0, 277.18))
    _add(music, ring * _env(nring, int(0.02 * SR), int(1.8 * SR)) * 0.08,
         ring_at)

    env = np.abs(vo)
    win = int(0.06 * SR)
    env = np.convolve(env, np.ones(win) / win, mode="same")
    env = np.minimum(env / 0.04, 1.0)
    duck = 1.0 - 0.62 * env
    smooth = int(0.05 * SR)
    duck = np.convolve(duck, np.ones(smooth) / smooth, mode="same")
    music *= duck

    audio = music + vo
    fade_in = int(0.1 * SR)
    audio[:fade_in] *= np.linspace(0, 1, fade_in)
    fade_out = int(0.8 * SR)
    audio[-fade_out:] *= 0.5 + 0.5 * np.cos(np.linspace(0, np.pi, fade_out))
    audio = np.tanh(audio * 1.4) / np.tanh(1.4)
    peak = np.abs(audio).max()
    if peak > 0:
        audio = audio / peak * 0.5
    delay = int(0.012 * SR)
    right = np.concatenate([np.zeros(delay), audio[:-delay]])
    stereo = np.stack([audio, right], axis=1)
    pcm = (stereo * 32767).astype(np.int16)
    with wavmod.open(wav_path, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm.tobytes())


def build_thumbnail():
    tmpf = THUMB_PATH + ".src.png"
    subprocess.run(["ffmpeg", "-y", "-ss", "4.0", "-i",
                    os.path.join(STEED_DIR, "scene_01_awaken.mp4"),
                    "-frames:v", "1", tmpf], check=True, capture_output=True)
    base = Image.open(tmpf).convert("RGB")
    w, h = base.size
    base = base.crop((0, 0, w, int(h * 0.82))).resize(
        (FRAME_WIDTH, FRAME_HEIGHT), Image.LANCZOS)
    img = base.convert("RGBA")
    ov = Image.new("RGBA", (FRAME_WIDTH, FRAME_HEIGHT), (0, 0, 0, 0))
    ov.alpha_composite(_vignette_layer(0.5))
    d = ImageDraw.Draw(ov)
    draw_tracked_fit(d, (FRAME_WIDTH // 2, 200), "STEED",
                     FONT_SERIF_BOLD, 110, CREAM, tracking=12)
    d.line([(FRAME_WIDTH * 0.34, 282), (FRAME_WIDTH * 0.66, 282)],
           fill=GOLD, width=2)
    cy = FRAME_HEIGHT - 400
    draw_plain_fit(d, (FRAME_WIDTH // 2, cy),
                   "What do riders fear?", FONT_SERIF_BOLD, 56, CREAM)
    draw_plain_fit(d, (FRAME_WIDTH // 2, cy + 80),
                   "Rain.", FONT_SERIF_BOLD, 60, GOLD)
    draw_plain_fit(d, (FRAME_WIDTH // 2, cy + 165), "Nº2 • THE JACKET",
                   FONT_SERIF_ITALIC, 38, GOLD)
    img.alpha_composite(_with_shadow(ov))
    img.convert("RGB").save(THUMB_PATH, quality=90)
    os.remove(tmpf)


def assemble():
    os.makedirs(TMP, exist_ok=True)
    segs, starts, cursor = [], [], 0.0
    for i, (d_, src, start, beats, cap, vo_id, crop) in enumerate(SHOTS):
        dur = beats * BEAT
        print(f"[steed2] cut {i + 1}/{len(SHOTS)}")
        out = os.path.join(TMP, f"cut_{i:02d}.mp4")
        _render_cut(i, d_, src, start, dur, cap, crop, out)
        segs.append(out)
        starts.append(cursor)
        cursor += dur
    total = cursor

    print(f"[steed2] audio: total {total:.2f}s")
    wav = os.path.join(TMP, "mix.wav")
    build_audio(starts, total, wav)

    wm = os.path.join(TMP, "watermark.png")
    _watermark(wm)
    inputs = []
    for s in segs:
        inputs += ["-i", s]
    concat = "".join(f"[{k}:v]" for k in range(len(segs)))
    no_thumb = os.path.join(TMP, "final_no_thumb.mp4")
    subprocess.run([
        "ffmpeg", "-y", *inputs,
        "-loop", "1", "-t", f"{total:.3f}", "-i", wm, "-i", wav,
        "-filter_complex",
        f"{concat}concat=n={len(segs)}:v=1:a=0[cat];"
        f"[{len(segs)}:v]format=rgba[wm];"
        f"[cat][wm]overlay=0:0:shortest=1,noise=alls=4:allf=t[outv]",
        "-map", "[outv]", "-map", f"{len(segs) + 1}:a",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
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
    print(f"\nSTEED Nº2 saved: {OUT_PATH} ({size:.1f} MB, {total:.1f}s)")


def main():
    parser = argparse.ArgumentParser(description="STEED film Nº2")
    parser.add_argument("--voice", action="store_true")
    args = parser.parse_args()

    if args.voice:
        from huggingface_hub import InferenceClient
        os.makedirs(VO_DIR, exist_ok=True)
        client = InferenceClient(provider="fal-ai",
                                 token=os.environ["HF_TOKEN"], timeout=180)
        for vo_id, text in VO_LINES:
            out = os.path.join(VO_DIR, f"{vo_id}.wav")
            if os.path.exists(out):
                print(f"  {vo_id}: cached")
                continue
            print(f"  [VO] {vo_id}: {text!r}", flush=True)
            audio = client.text_to_speech(text, model="hexgrad/Kokoro-82M",
                                          extra_body=VOICE)
            with open(out, "wb") as f:
                f.write(audio)
        return

    assemble()


if __name__ == "__main__":
    main()
