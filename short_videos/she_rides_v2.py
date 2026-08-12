"""
She Rides vNº2 — the feed-native re-edit of "Never Assume".

Structural inversion of v1 per the skip-rate analysis: the wheelie
IS frame zero (cold open), 13 hard cuts on a 132 BPM beat grid, no
early title card, watermark branding, the visor-snap as the drop,
the dead-stop reveal kept, a follow CTA overlaid on the held reveal
shot, and a seamless loop back into the opening wheelie.

Only two new scenes (burnout circle, paddock reaction) — the rest
re-cuts v1 footage. Score built fresh: full-band hard rock from
sample one, double-time after the visor drop, engine layers under
the stunts, dead stop, final chord on the smirk, and a drum fill
that hands off into the loop shot.

Run:  HF_TOKEN=... python3 -m short_videos.she_rides_v2 --generate
      python3 -m short_videos.she_rides_v2            (assemble)
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
from short_videos.film_score import (
    SFX, _crash, _lead_note, _power_chord, _slapback,
)
from short_videos.rockabilly_score import (
    SR, _add, _bass_note, _env, _hat, _kick, _snare,
)
from short_videos.she_rides_film import BIKE, STYLE

AI_DIR = "output/short_videos/films/she-rides-wan"
OUT_PATH = "output/short_videos/films/she-rides-never-assume-v2.mp4"
THUMB_PATH = "output/short_videos/films/she-rides-never-assume-v2_cover.jpg"
TMP = os.path.join(AI_DIR, ".v2_assembly")

BPM = 132
BEAT = 60.0 / BPM

NEW_SCENES = [
    {
        "id": "06_burnout",
        "prompt": (
            f"A professional motorcycle racer in fitted black-and-gold "
            f"racing leathers and a full black helmet performs a "
            f"controlled circular burnout on {BIKE} on racetrack "
            f"asphalt, the rear tire spinning and pouring thick white "
            f"smoke as the bike pivots in a tight circle, rider seated "
            f"astride with both hands on the handlebars and one boot "
            f"braced on the tarmac. Camera: low tracking arc around "
            f"the smoke circle. " + STYLE
        ),
    },
    {
        "id": "07_reaction",
        "prompt": (
            f"Three motorcycle mechanics in dark team shirts stand "
            f"behind a pit lane fence watching the racetrack with "
            f"stunned expressions, one slowly lowering his phone, "
            f"another pulling off his cap, superbikes parked behind "
            f"them in golden hour light. Camera: slow push-in on "
            f"their faces. " + STYLE
        ),
    },
]

# (source scene file, source start sec, beats, text or None)
SHOTS = [
    ("scene_04_wheelie", 2.2, 3, "They laughed at her."),
    ("scene_01_paddock", 1.8, 3, "She didn't say a word."),
    ("scene_02_suitup", 0.6, 3, None),
    ("scene_02_suitup", 2.0, 3, None),          # visor — drop at its end
    ("scene_03_apex", 0.4, 4, None),
    ("scene_03_apex", 3.0, 3, "160 km/h."),
    ("scene_04_wheelie", 0.2, 4, None),
    ("scene_04_wheelie", 3.3, 3, None),
    ("scene_06_burnout", 0.5, 3, None),
    ("scene_06_burnout", 2.8, 3, None),
    ("scene_07_reaction", 1.0, 3, "Not laughing now."),
]
REVEAL_SRC, REVEAL_START, REVEAL_DUR = "scene_05_reveal", 0.3, 4.6
LOOP_SHOT = ("scene_04_wheelie", 2.2, 3)        # mirrors the cold open

DROP_BEAT = 12                                  # end of the visor shot


def _shot_overlay(text, path, big=False):
    ov = Image.new("RGBA", (FRAME_WIDTH, FRAME_HEIGHT), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    grad_h = 430
    band = Image.new("L", (1, grad_h), 0)
    for i in range(grad_h):
        band.putpixel((0, i), int(165 * (i / grad_h) ** 1.5))
    band = band.resize((FRAME_WIDTH, grad_h))
    g = Image.new("RGBA", (FRAME_WIDTH, grad_h), (3, 3, 5, 255))
    g.putalpha(band)
    ov.alpha_composite(g, (0, FRAME_HEIGHT - grad_h))
    draw_plain_fit(d, (FRAME_WIDTH // 2, FRAME_HEIGHT - 300), text,
                   FONT_SERIF_BOLD, 72 if big else 62, CREAM)
    _with_shadow(ov).save(path)


def _watermark(path):
    ov = Image.new("RGBA", (FRAME_WIDTH, FRAME_HEIGHT), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    draw_tracked_fit(d, (FRAME_WIDTH // 2, 96), "THE RIDER'S GANG",
                     FONT_SERIF_BOLD, 26, (238, 232, 218, 132), tracking=7)
    ov.save(path)


def _reveal_overlays():
    p1 = os.path.join(TMP, "ov_never.png")
    ov = Image.new("RGBA", (FRAME_WIDTH, FRAME_HEIGHT), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    draw_plain_fit(d, (FRAME_WIDTH // 2, FRAME_HEIGHT - 560), "Never assume.",
                   FONT_SERIF_BOLD, 80, CREAM)
    _with_shadow(ov).save(p1)

    p2 = os.path.join(TMP, "ov_cta.png")
    ov = Image.new("RGBA", (FRAME_WIDTH, FRAME_HEIGHT), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    grad_h = 480
    band = Image.new("L", (1, grad_h), 0)
    for i in range(grad_h):
        band.putpixel((0, i), int(180 * (i / grad_h) ** 1.5))
    band = band.resize((FRAME_WIDTH, grad_h))
    g = Image.new("RGBA", (FRAME_WIDTH, grad_h), (3, 3, 5, 255))
    g.putalpha(band)
    ov.alpha_composite(g, (0, FRAME_HEIGHT - grad_h))
    draw_plain_fit(d, (FRAME_WIDTH // 2, FRAME_HEIGHT - 380),
                   "Follow — Nº2: THE NIGHT RIDE", FONT_SERIF_BOLD, 46, GOLD)
    draw_plain_fit(d, (FRAME_WIDTH // 2, FRAME_HEIGHT - 300),
                   "The Apex Series", FONT_SERIF_ITALIC, 36, CREAM)
    draw_plain_fit(d, (FRAME_WIDTH // 2, FRAME_HEIGHT - 150),
                   "Professional rider. Closed track.",
                   FONT_SERIF_ITALIC, 26, (150, 145, 135, 220))
    _with_shadow(ov).save(p2)
    return p1, p2


BASE_VF = ("scale=1080:1920:force_original_aspect_ratio=increase:"
           "flags=lanczos,crop=1080:1920,fps=24,"
           "eq=gamma=1.02:contrast=1.04:saturation=1.02")


def _render_cut(src, start, dur, text, out):
    cmd = ["ffmpeg", "-y", "-ss", f"{start:.3f}", "-i",
           os.path.join(AI_DIR, f"{src}.mp4")]
    if text:
        png = os.path.join(TMP, f"txt_{abs(hash(text)) % 99999}.png")
        _shot_overlay(text, png)
        cmd += ["-loop", "1", "-t", f"{dur:.3f}", "-i", png,
                "-filter_complex",
                f"[0:v]{BASE_VF}[v];"
                f"[1:v]format=rgba,fade=t=in:st=0.12:d=0.18:alpha=1[ov];"
                f"[v][ov]overlay=0:0:shortest=1[outv]",
                "-map", "[outv]"]
    else:
        cmd += ["-vf", BASE_VF]
    cmd += ["-t", f"{dur:.3f}", "-r", "24", "-an", "-c:v", "libx264",
            "-preset", "fast", "-crf", "16", "-pix_fmt", "yuv420p", out]
    subprocess.run(cmd, check=True, capture_output=True)


def _render_reveal(out):
    p1, p2 = _reveal_overlays()
    subprocess.run([
        "ffmpeg", "-y", "-ss", f"{REVEAL_START:.3f}", "-i",
        os.path.join(AI_DIR, f"{REVEAL_SRC}.mp4"),
        "-loop", "1", "-t", f"{REVEAL_DUR:.3f}", "-i", p1,
        "-loop", "1", "-t", f"{REVEAL_DUR:.3f}", "-i", p2,
        "-filter_complex",
        f"[0:v]{BASE_VF}[v];"
        f"[1:v]format=rgba,fade=t=in:st=1.1:d=0.3:alpha=1,"
        f"fade=t=out:st=2.3:d=0.3:alpha=1[o1];"
        f"[2:v]format=rgba,fade=t=in:st=2.6:d=0.35:alpha=1[o2];"
        f"[v][o1]overlay=0:0:shortest=1[m];[m][o2]overlay=0:0:shortest=1[outv]",
        "-map", "[outv]", "-t", f"{REVEAL_DUR:.3f}", "-r", "24", "-an",
        "-c:v", "libx264", "-preset", "fast", "-crf", "16",
        "-pix_fmt", "yuv420p", out], check=True, capture_output=True)


# ── score ────────────────────────────────────────────────────────────

def build_audio(total, drop_at, stop_at, loop_at, wav_path):
    rng = np.random.default_rng(132)
    n = int(total * SR)
    audio = np.zeros(n)
    E, G, A_ = 82.41, 98.0, 110.0
    PROG = [E, E, G, A_]
    bar = 4 * BEAT

    def band(t0, t1, double_time):
        t, bar_i = t0, 0
        while t < t1 - 0.05:
            root = PROG[bar_i % len(PROG)]
            _add(audio, _power_chord(root, BEAT * 2.0, drive=4.6) * 0.6, t)
            for e8 in (4, 5, 6, 7):
                at = t + e8 * BEAT / 2
                if at < t1:
                    _add(audio, _power_chord(root, BEAT * 0.5, mute=True,
                                             drive=4.6) * 0.42, at)
            for e8 in range(8):
                at = t + e8 * BEAT / 2
                if at < t1:
                    _add(audio, _bass_note(root / 2, BEAT * 0.45) * 0.85, at)
            t += bar
            bar_i += 1
        t, beat_i = t0, 0
        while t < t1 - 0.05:
            _add(audio, _hat(rng) * 0.9, t)
            _add(audio, _hat(rng) * 0.6, t + BEAT / 2)
            if double_time:
                _add(audio, _kick() * 1.1, t)
                if beat_i % 2 == 1:
                    _add(audio, _snare(rng) * 1.2, t)
            else:
                if beat_i % 2 == 0:
                    _add(audio, _kick() * 1.1, t)
                else:
                    _add(audio, _snare(rng) * 1.15, t)
            t += BEAT
            beat_i += 1

    band(0.0, drop_at, double_time=False)
    band(drop_at + BEAT * 0.5, stop_at, double_time=True)   # one-beat gap
    _add(audio, _crash(rng), 0.0)
    _add(audio, _kick() * 1.4, drop_at + BEAT * 0.5)
    _add(audio, _crash(rng) * 0.9, drop_at + BEAT * 0.5)

    # lead answers through the stunt section
    E4, G4, A4, B4, D5, E5, G5 = (329.63, 392.0, 440.0, 493.88,
                                  587.33, 659.26, 783.99)
    LICK = [(0.0, E5, 0.5, None), (0.5, D5, 0.5, None), (1.0, B4, 0.5, None),
            (1.5, D5, 0.5, E5), (2.5, G5, 1.2, None),
            (4.0, B4, 0.5, None), (4.5, A4, 0.5, None), (5.0, G4, 0.5, None),
            (5.5, A4, 1.2, B4), (7.0, E4, 0.8, None)]
    t = drop_at + BEAT * 0.5 + 2 * bar
    while t + 2 * bar <= stop_at:
        for off, f0, ndur, f1 in LICK:
            _add(audio, _lead_note(f0, ndur * BEAT, f1, 0.42), t + off * BEAT)
        t += 2 * bar

    # engine: scream at frame zero, layer under the stunts
    eng = SFX["engine"](rng, 2.2)
    _add(audio, eng * 1.1, 0.0)
    _add(audio, SFX["engine"](rng, stop_at - drop_at) * 0.5, drop_at)

    # dead stop → wind → final chord on the smirk
    i0, i1 = int(stop_at * SR), int((stop_at + 0.3) * SR)
    edge = int(0.008 * SR)
    audio[i0 - edge:i0] *= np.linspace(1, 0, edge)
    audio[i0:] = 0.0
    wind = rng.normal(0, 1, int(3.0 * SR))
    wind = np.convolve(wind, np.ones(260) / 260.0, mode="same") * 2.2
    _add(audio, wind * _env(len(wind), int(0.3 * SR), int(0.8 * SR)),
         stop_at + 0.15)
    smirk_at = stop_at + 1.3
    _add(audio, _crash(rng) * 0.8, smirk_at)
    _add(audio, _power_chord(E, 3.0, drive=4.6) * 0.75, smirk_at)

    # drum fill → loop hit riding out to the end
    fill_at = loop_at - 0.45
    for k in range(6):
        _add(audio, _snare(rng) * (0.6 + 0.1 * k), fill_at + k * 0.075)
    _add(audio, _crash(rng), loop_at)
    _add(audio, _kick() * 1.3, loop_at)
    t = loop_at
    while t < total - 0.1:
        _add(audio, _power_chord(E, BEAT * 0.5, mute=True, drive=4.6) * 0.5, t)
        _add(audio, _bass_note(E / 2, BEAT * 0.45) * 0.8, t)
        _add(audio, _hat(rng) * 0.8, t)
        t += BEAT / 2
    _add(audio, SFX["engine"](rng, total - loop_at) * 0.7, loop_at)

    audio = np.tanh(audio * 1.6) / np.tanh(1.6)
    peak = np.abs(audio).max()
    if peak > 0:
        audio = audio / peak * 0.44    # headroom for AAC transient overshoot
    delay = int(0.012 * SR)
    right = np.concatenate([np.zeros(delay), audio[:-delay]])
    stereo = np.stack([audio, right], axis=1)
    pcm = (stereo * 32767).astype(np.int16)
    with wavmod.open(wav_path, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm.tobytes())


def build_thumbnail(thumb_path):
    tmpf = thumb_path + ".src.png"
    subprocess.run(["ffmpeg", "-y", "-ss", "2.4", "-i",
                    os.path.join(AI_DIR, "scene_04_wheelie.mp4"),
                    "-frames:v", "1", tmpf], check=True, capture_output=True)
    base = Image.open(tmpf).convert("RGB").resize(
        (FRAME_WIDTH, FRAME_HEIGHT), Image.LANCZOS)
    img = base.convert("RGBA")
    ov = Image.new("RGBA", (FRAME_WIDTH, FRAME_HEIGHT), (0, 0, 0, 0))
    ov.alpha_composite(_vignette_layer(0.5))
    d = ImageDraw.Draw(ov)
    draw_tracked_fit(d, (FRAME_WIDTH // 2, 200), "SHE RIDES",
                     FONT_SERIF_BOLD, 96, CREAM, tracking=9)
    d.line([(FRAME_WIDTH * 0.34, 272), (FRAME_WIDTH * 0.66, 272)],
           fill=GOLD, width=2)
    cy = FRAME_HEIGHT - 360
    draw_plain_fit(d, (FRAME_WIDTH // 2, cy), "They laughed at her.",
                   FONT_SERIF_BOLD, 62, CREAM)
    draw_plain_fit(d, (FRAME_WIDTH // 2, cy + 90), "APEX SERIES • Nº1",
                   FONT_SERIF_ITALIC, 38, GOLD)
    img.alpha_composite(_with_shadow(ov))
    img.convert("RGB").save(thumb_path, quality=90)
    os.remove(tmpf)


def assemble():
    os.makedirs(TMP, exist_ok=True)
    segs, cursor = [], 0.0
    for i, (src, start, beats, text) in enumerate(SHOTS):
        dur = beats * BEAT
        out = os.path.join(TMP, f"cut_{i:02d}.mp4")
        print(f"[v2] cut {i + 1}/{len(SHOTS) + 2}")
        _render_cut(src, start, dur, text, out)
        segs.append(out)
        cursor += dur
    stop_at = cursor

    out = os.path.join(TMP, "cut_reveal.mp4")
    print("[v2] reveal")
    _render_reveal(out)
    segs.append(out)
    cursor += REVEAL_DUR
    loop_at = cursor

    src, start, beats = LOOP_SHOT
    out = os.path.join(TMP, "cut_loop.mp4")
    print("[v2] loop shot")
    _render_cut(src, start, beats * BEAT, None, out)
    segs.append(out)
    total = cursor + beats * BEAT

    drop_at = DROP_BEAT * BEAT
    print(f"[v2] audio: drop {drop_at:.2f}s stop {stop_at:.2f}s "
          f"loop {loop_at:.2f}s total {total:.2f}s")
    wav = os.path.join(TMP, "mix.wav")
    build_audio(total, drop_at, stop_at, loop_at, wav)

    wm = os.path.join(TMP, "watermark.png")
    _watermark(wm)
    inputs = []
    for s in segs:
        inputs += ["-i", s]
    concat_labels = "".join(f"[{k}:v]" for k in range(len(segs)))
    no_thumb = os.path.join(TMP, "final_no_thumb.mp4")
    subprocess.run([
        "ffmpeg", "-y", *inputs,
        "-loop", "1", "-t", f"{total:.3f}", "-i", wm, "-i", wav,
        "-filter_complex",
        f"{concat_labels}concat=n={len(segs)}:v=1:a=0[cat];"
        f"[{len(segs)}:v]format=rgba[wm];"
        f"[cat][wm]overlay=0:0:shortest=1,noise=alls=4:allf=t[outv]",
        "-map", "[outv]", "-map", f"{len(segs) + 1}:a",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "256k",
        "-movflags", "+faststart", "-shortest", no_thumb,
    ], check=True, capture_output=True)

    build_thumbnail(THUMB_PATH)
    subprocess.run([
        "ffmpeg", "-y", "-i", no_thumb, "-i", THUMB_PATH,
        "-map", "0", "-map", "1", "-c", "copy", "-c:v:1", "mjpeg",
        "-disposition:v:1", "attached_pic", "-movflags", "+faststart",
        OUT_PATH,
    ], check=True, capture_output=True)
    size = os.path.getsize(OUT_PATH) / 1024 / 1024
    print(f"\nv2 reel saved: {OUT_PATH} ({size:.1f} MB, {total:.1f}s)")


def main():
    parser = argparse.ArgumentParser(description="She Rides v2 re-edit")
    parser.add_argument("--generate", action="store_true",
                        help="generate the two new scenes first")
    args = parser.parse_args()

    if args.generate:
        from huggingface_hub import InferenceClient
        from short_videos.she_rides_film import generate_scene
        client = InferenceClient(provider="fal-ai",
                                 token=os.environ["HF_TOKEN"], timeout=560)
        for scene in NEW_SCENES:
            out = os.path.join(AI_DIR, f"scene_{scene['id']}.mp4")
            if os.path.exists(out):
                print(f"  {scene['id']}: cached")
                continue
            generate_scene(client, scene, out)
        return
    assemble()


if __name__ == "__main__":
    main()
