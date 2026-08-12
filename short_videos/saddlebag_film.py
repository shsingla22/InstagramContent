"""
Saddlebag Film — "Cavalry Gear" (story lane, feed-native, narrated).

The first reel built fully under the repositioned playbook:
voiceover narration (Kokoro TTS) carrying 11 hard cuts on a 120 BPM
grid, face-led cold open, the beauty-to-warhorse smash cut at 1.5s,
small synced captions for muted viewing, watermark branding, no
cards, seamless loop, elegant ducked score. Posted as disclosed AI.

Story: the $4,000 Dior Saddle bag is 2,500-year-old cavalry gear —
Persia → medieval mail → cowboys → Hermès → Grace Kelly → Dior.
The shape never changed. It never needed to.

Run:  HF_TOKEN=... python3 -m short_videos.saddlebag_film --generate
      HF_TOKEN=... python3 -m short_videos.saddlebag_film --voice
      python3 -m short_videos.saddlebag_film            (assemble)
"""

import argparse
import os
import subprocess
import sys
import time
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
from short_videos.film_score import _crash, _pad_chord, _pluck, _slapback
from short_videos.rockabilly_score import (
    SR, _add, _bass_note, _env, _hat, _kick, _snare,
)

AI_DIR = "output/short_videos/films/saddlebag-wan"
DENIM_DIR = "output/short_videos/films/denim-wan"
VO_DIR = os.path.join(AI_DIR, ".voice")
TMP = os.path.join(AI_DIR, ".assembly")
OUT_PATH = ("output/short_videos/films/"
            "the-saddlebag-from-horse-leather-to-high-fashion.mp4")
THUMB_PATH = ("output/short_videos/films/"
              "the-saddlebag-from-horse-leather-to-high-fashion_cover.jpg")

BPM = 120
BEAT = 60.0 / BPM

WOMAN = (
    "a strikingly beautiful young woman with long chestnut hair, "
    "wearing an elegant cream tailored suit, a structured tan leather "
    "saddle-shaped handbag with a curved flap and brass buckle at her hip"
)
LUX = (
    "Cinematic vertical 9:16 video, shot on 35mm film, warm elegant "
    "color grade, film grain, realistic physics and correct human and "
    "horse anatomy, documentary realism, no text or captions in the "
    "image."
)

SCENES = [
    {"id": "01_paris", "prompt": (
        f"{WOMAN}, walking along a Paris street of stone facades at "
        f"golden hour, confident relaxed stride, and near the end she "
        f"glances at the camera with a soft smile. Camera: smooth "
        f"tracking shot moving backward in front of her. " + LUX)},
    {"id": "02_cavalry", "prompt": (
        "An ancient Persian cavalry rider in bronze and leather armor "
        "gallops across a dusty plain at dawn, worn leather saddlebags "
        "with flaps bouncing at his horse's flanks, the rider astride "
        "facing forward over the horse's neck. Camera: low tracking "
        "shot alongside the gallop, dust trailing. " + LUX)},
    {"id": "03_letter", "prompt": (
        "Close-up of a weathered hand sliding a folded parchment "
        "letter sealed with red wax under the buckled flap of a worn "
        "leather saddlebag hanging from a horse's saddle, candlelit "
        "stone stable at night. Camera: slow close push-in. " + LUX)},
    {"id": "04_courier", "prompt": (
        "A medieval courier in a hooded cloak gallops on horseback "
        "out of a torch-lit castle gate at dusk, leather saddlebags "
        "at the horse's flanks, the rider astride facing forward. "
        "Camera: tracking from the side as he passes. " + LUX)},
    {"id": "05_atelier", "prompt": (
        "In a 1920s Paris leather atelier, weathered hands "
        "saddle-stitch an elegant trapezoid leather handbag with an "
        "awl and two needles, horse harnesses and bridles hanging on "
        "the wall behind, warm work lamp. Camera: slow close orbit "
        "over the hands and the bag. " + LUX)},
    {"id": "06_siren", "prompt": (
        "A breathtakingly beautiful 1950s film star with red "
        "lipstick, a silk headscarf and cat-eye sunglasses steps out "
        "of a cream vintage convertible in front of a Riviera grand "
        "hotel, a structured black leather handbag on her forearm, "
        "photographers' flashbulbs going off behind her. Camera: "
        "medium shot, slow push-in as she rises from the car. " + LUX)},
    {"id": "07_bagclose", "prompt": (
        f"Extreme close-up of the curved tan leather flap and brass "
        f"buckle of a saddle-shaped luxury handbag swaying at the hip "
        f"of {WOMAN} as she walks, then the camera tilts up to her "
        f"soft smile. Golden hour Paris street. " + LUX)},
]

# narration lines (id, text) — written to fit a 26s runtime
VO_LINES = [
    ("vo01", "That four thousand dollar Dior bag?"),
    ("vo02", "Cavalry gear."),
    ("vo03b", "Persia invented it twenty five hundred years ago."),
    ("vo04b", "It carried the royal mail, before mail existed."),
    ("vo06b", "Cowboys lived out of it."),
    ("vo07b", "When cars killed the horse, Hermes stitched handbags."),
    ("vo08", "Grace Kelly made it famous."),
    ("vo09b", "Dior just copied the saddle."),
    ("vo10", "Five thousand years. The shape never changed."),
    ("vo11", "It never needed to."),
]

# (dir, source, start, beats, caption, vo id or None, speed)
# beats are sized to each narration line; speed<1 = slow motion
SHOTS = [
    (AI_DIR, "scene_01_paris", 0.2, 6, "That $4,000 Dior bag?", "vo01", 1.0),
    (AI_DIR, "scene_02_cavalry", 0.5, 4, "Cavalry gear.", "vo02", 1.0),
    (AI_DIR, "scene_02_cavalry", 2.8, 7, "Persia, 500 BC.", "vo03b", 0.62),
    (AI_DIR, "scene_03_letter", 1.0, 7, "It carried the royal mail…",
     "vo04b", 1.0),
    (AI_DIR, "scene_04_courier", 1.5, 3, "…before mail existed.", None, 1.0),
    (DENIM_DIR, "scene_03_drive", 1.5, 4, "Cowboys lived out of it.",
     "vo06b", 1.0),
    (AI_DIR, "scene_05_atelier", 0.8, 7, "Then cars killed the horse.",
     "vo07b", 1.0),
    (AI_DIR, "scene_06_siren", 1.0, 5, "Grace Kelly, 1956.", "vo08", 1.0),
    (AI_DIR, "scene_01_paris", 2.4, 5, "Dior, 1999.", "vo09b", 1.0),
    (AI_DIR, "scene_07_bagclose", 1.2, 7, None, "vo10", 1.0),
    (AI_DIR, "scene_01_paris", 0.2, 5, None, "vo11", 1.0),  # loop shot
]
CTA_SHOT_IDX = 9          # overlays land on the bag-close shot


def _caption_png(text, path):
    ov = Image.new("RGBA", (FRAME_WIDTH, FRAME_HEIGHT), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    grad_h = 340
    band = Image.new("L", (1, grad_h), 0)
    for i in range(grad_h):
        band.putpixel((0, i), int(150 * (i / grad_h) ** 1.5))
    band = band.resize((FRAME_WIDTH, grad_h))
    g = Image.new("RGBA", (FRAME_WIDTH, grad_h), (4, 3, 3, 255))
    g.putalpha(band)
    ov.alpha_composite(g, (0, FRAME_HEIGHT - grad_h))
    draw_plain_fit(d, (FRAME_WIDTH // 2, FRAME_HEIGHT - 235), text,
                   FONT_SERIF_BOLD, 52, CREAM)
    _with_shadow(ov).save(path)


def _cta_overlays():
    p1 = os.path.join(TMP, "ov_shape.png")
    ov = Image.new("RGBA", (FRAME_WIDTH, FRAME_HEIGHT), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    grad_h = 470
    band = Image.new("L", (1, grad_h), 0)
    for i in range(grad_h):
        band.putpixel((0, i), int(175 * (i / grad_h) ** 1.5))
    band = band.resize((FRAME_WIDTH, grad_h))
    g = Image.new("RGBA", (FRAME_WIDTH, grad_h), (4, 3, 3, 255))
    g.putalpha(band)
    ov.alpha_composite(g, (0, FRAME_HEIGHT - grad_h))
    draw_plain_fit(d, (FRAME_WIDTH // 2, FRAME_HEIGHT - 360),
                   "It never needed to.", FONT_SERIF_BOLD, 62, CREAM)
    draw_plain_fit(d, (FRAME_WIDTH // 2, FRAME_HEIGHT - 240),
                   "Follow — new heritage films weekly",
                   FONT_SERIF_BOLD, 40, GOLD)
    draw_plain_fit(d, (FRAME_WIDTH // 2, FRAME_HEIGHT - 165),
                   "The Rider's Gang  •  AI cinema",
                   FONT_SERIF_ITALIC, 32, (200, 193, 178, 235))
    _with_shadow(ov).save(p1)
    return p1


def _watermark(path):
    ov = Image.new("RGBA", (FRAME_WIDTH, FRAME_HEIGHT), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    draw_tracked_fit(d, (FRAME_WIDTH // 2, 96), "THE RIDER'S GANG",
                     FONT_SERIF_BOLD, 26, (238, 232, 218, 130), tracking=7)
    ov.save(path)


BASE_VF = ("scale=1080:1920:force_original_aspect_ratio=increase:"
           "flags=lanczos,crop=1080:1920,fps=24,"
           "eq=gamma=1.02:contrast=1.03:saturation=1.0")


def _render_cut(idx, src_dir, src, start, dur, caption, out, speed=1.0):
    base_vf = BASE_VF
    if speed != 1.0:
        base_vf = f"setpts=PTS/{speed},{BASE_VF}"
    cmd = ["ffmpeg", "-y", "-ss", f"{start:.3f}", "-i",
           os.path.join(src_dir, f"{src}.mp4")]
    overlays = []
    if caption:
        png = os.path.join(TMP, f"cap_{idx:02d}.png")
        _caption_png(caption, png)
        overlays.append((png, 0.1, None))
    if idx == CTA_SHOT_IDX:
        overlays.append((_cta_overlays(), 0.7, None))
    if overlays:
        for png, _, _ in overlays:
            cmd += ["-loop", "1", "-t", f"{dur:.3f}", "-i", png]
        graph = f"[0:v]{base_vf}[v0]"
        prev = "[v0]"
        for k, (_, t_in, _) in enumerate(overlays):
            graph += (f";[{k + 1}:v]format=rgba,"
                      f"fade=t=in:st={t_in}:d=0.22:alpha=1[o{k}]")
            nxt = f"[m{k}]" if k < len(overlays) - 1 else "[outv]"
            graph += f";{prev}[o{k}]overlay=0:0:shortest=1{nxt}"
            prev = nxt
        cmd += ["-filter_complex", graph, "-map", "[outv]"]
    else:
        cmd += ["-vf", base_vf]
    cmd += ["-t", f"{dur:.3f}", "-r", "24", "-an", "-c:v", "libx264",
            "-preset", "fast", "-crf", "16", "-pix_fmt", "yuv420p", out]
    subprocess.run(cmd, check=True, capture_output=True)


def _load_wav_mono(path):
    out = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-ac", "1",
         "-ar", str(SR), "-"], capture_output=True, check=True)
    return np.frombuffer(out.stdout, dtype=np.float32).astype(np.float64)


def build_audio(shot_starts, total, wav_path):
    rng = np.random.default_rng(1837)
    n = int(total * SR)

    # ── voiceover track: sequential, never overlapping ───────────
    vo = np.zeros(n)
    prev_end = 0.0
    for (dir_, src, start, beats, cap, vo_id, spd), at in zip(SHOTS,
                                                              shot_starts):
        if not vo_id:
            continue
        seg = _load_wav_mono(os.path.join(VO_DIR, f"{vo_id}.wav"))
        rms = np.sqrt((seg ** 2).mean())
        if rms > 0:
            seg = seg / rms * 0.16
        vo_at = max(at + 0.12, prev_end + 0.18)
        _add(vo, seg, vo_at)
        prev_end = vo_at + len(seg) / SR

    # ── elegant heritage bed (A major, plucked, brushed) ─────────
    music = np.zeros(n)
    bar = 4 * BEAT
    PROG = [(110.0, [220.0, 277.18, 329.63, 440.0]),
            (82.41, [164.81, 246.94, 329.63, 415.30]),
            (92.5, [185.0, 277.18, 369.99, 440.0]),
            (73.42, [146.83, 220.0, 293.66, 369.99])]
    groove_end = total - 1.6
    t, bar_i = 0.0, 0
    while t < groove_end:
        root, chord = PROG[bar_i % len(PROG)]
        _add(music, _pad_chord([root, root * 2], bar + 0.3, 0.04), t)
        _add(music, _bass_note(root, BEAT * 1.9) * 0.7, t)
        _add(music, _bass_note(root * 1.5, BEAT * 1.9) * 0.55, t + 2 * BEAT)
        for k, f in enumerate(chord):                 # gentle arpeggio
            at = t + k * BEAT
            if at < groove_end:
                _add(music, _slapback(_pluck(f, BEAT * 1.6, 0.6), 0.12, 0.3)
                     * 0.34, at)
        t += bar
        bar_i += 1
    t, beat_i = 0.0, 0
    while t < groove_end:
        _add(music, _hat(rng) * 0.45, t)
        _add(music, _hat(rng) * 0.28, t + BEAT / 2)
        if beat_i % 2 == 0:
            _add(music, _kick() * 0.55, t)
        else:
            _add(music, _snare(rng) * 0.35, t)
        t += BEAT
        beat_i += 1
    _add(music, _crash(rng) * 0.35, shot_starts[1])   # the smash cut
    chord_at = total - 2.4
    nring = int(2.2 * SR)
    tt = np.arange(nring) / SR
    ring = sum(np.sin(2 * np.pi * f * tt)
               for f in (110.0, 164.81, 220.0, 277.18))
    _add(music, ring * _env(nring, int(0.02 * SR), int(1.8 * SR)) * 0.09,
         chord_at)

    # ── duck music under the voice ───────────────────────────────
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
    subprocess.run(["ffmpeg", "-y", "-ss", "1.5", "-i",
                    os.path.join(AI_DIR, "scene_02_cavalry.mp4"),
                    "-frames:v", "1", tmpf], check=True, capture_output=True)
    base = Image.open(tmpf).convert("RGB").resize(
        (FRAME_WIDTH, FRAME_HEIGHT), Image.LANCZOS)
    img = base.convert("RGBA")
    ov = Image.new("RGBA", (FRAME_WIDTH, FRAME_HEIGHT), (0, 0, 0, 0))
    ov.alpha_composite(_vignette_layer(0.5))
    d = ImageDraw.Draw(ov)
    draw_tracked_fit(d, (FRAME_WIDTH // 2, 200), "CAVALRY GEAR",
                     FONT_SERIF_BOLD, 84, CREAM, tracking=7)
    d.line([(FRAME_WIDTH * 0.34, 268), (FRAME_WIDTH * 0.66, 268)],
           fill=GOLD, width=2)
    cy = FRAME_HEIGHT - 400
    draw_plain_fit(d, (FRAME_WIDTH // 2, cy), "That $4,000 Dior bag?",
                   FONT_SERIF_BOLD, 58, CREAM)
    draw_plain_fit(d, (FRAME_WIDTH // 2, cy + 82),
                   "It's 2,500-year-old cavalry gear.",
                   FONT_SERIF_BOLD, 50, GOLD)
    img.alpha_composite(_with_shadow(ov))
    img.convert("RGB").save(THUMB_PATH, quality=90)
    os.remove(tmpf)


def assemble():
    os.makedirs(TMP, exist_ok=True)
    segs, starts, cursor = [], [], 0.0
    for i, (dir_, src, start, beats, cap, vo_id, spd) in enumerate(SHOTS):
        dur = beats * BEAT
        out = os.path.join(TMP, f"cut_{i:02d}.mp4")
        print(f"[saddlebag] cut {i + 1}/{len(SHOTS)}")
        _render_cut(i, dir_, src, start, dur, cap, out, speed=spd)
        segs.append(out)
        starts.append(cursor)
        cursor += dur
    total = cursor

    print(f"[saddlebag] audio: total {total:.2f}s")
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
    print(f"\nSaddlebag reel saved: {OUT_PATH} ({size:.1f} MB, {total:.1f}s)")


def main():
    parser = argparse.ArgumentParser(description="Saddlebag reel")
    parser.add_argument("--generate", action="store_true")
    parser.add_argument("--voice", action="store_true")
    parser.add_argument("--only", help="generate a single scene id")
    args = parser.parse_args()

    os.makedirs(AI_DIR, exist_ok=True)

    if args.generate:
        from huggingface_hub import InferenceClient
        client = InferenceClient(provider="fal-ai",
                                 token=os.environ["HF_TOKEN"], timeout=560)
        for scene in SCENES:
            out = os.path.join(AI_DIR, f"scene_{scene['id']}.mp4")
            if args.only and scene["id"] != args.only:
                continue
            if os.path.exists(out) and not args.only:
                print(f"  {scene['id']}: cached")
                continue
            for attempt in range(1, 4):
                print(f"  [Wan] {scene['id']} (attempt {attempt})...",
                      flush=True)
                t0 = time.time()
                try:
                    video = client.text_to_video(
                        scene["prompt"], model="Wan-AI/Wan2.2-T2V-A14B",
                        extra_body={"aspect_ratio": "9:16",
                                    "resolution": "720p"})
                except Exception as e:
                    print(f"    failed: {e}", flush=True)
                    if attempt == 3:
                        raise
                    time.sleep(10 * attempt)
                    continue
                with open(out, "wb") as f:
                    f.write(video)
                print(f"    done in {time.time() - t0:.0f}s", flush=True)
                break
        return

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
            audio = client.text_to_speech(text, model="hexgrad/Kokoro-82M")
            with open(out, "wb") as f:
                f.write(audio)
        return

    assemble()


if __name__ == "__main__":
    main()
