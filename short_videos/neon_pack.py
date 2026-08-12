"""
Neon Pack — the short-form volume formats.

A. NEON GARAGE loops (~8 s each): one bike, night, drenched in
   color — slow orbit with a speed-ramp snap, palindrome edit for a
   perfect loop, dark phonk + engine, model name small at the
   bottom. Three reels: cafe racer (amber), cruiser (crimson/gold),
   superbike (magenta/cyan).

B. PICK YOUR GANG (~15 s): the versus reel — velvet round, venom
   round, rapid-fire ping-pong, vote card. Phonk flips from
   halftime to double-time when the superbikes arrive. Reuses the
   She Rides apex/wheelie shots for the venom side.

Run:  HF_TOKEN=... python3 -m short_videos.neon_pack --generate
      python3 -m short_videos.neon_pack --loops
      python3 -m short_videos.neon_pack --versus
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
    CREAM, GOLD, _with_shadow, draw_plain_fit, draw_tracked_fit,
)
from short_videos.film_score import SFX
from short_videos.rockabilly_score import SR, _add
from short_videos.studio import glue, master, phonk_track

AI_DIR = "output/short_videos/films/neon-wan"
SHERIDES_DIR = "output/short_videos/films/she-rides-wan"
OUT_DIR = "output/short_videos/films"
TMP = os.path.join(AI_DIR, ".assembly")

NEON = (
    "Cinematic vertical 9:16 video at night, ultra vivid neon "
    "lighting, wet asphalt reflections, glowing light flares and "
    "haze, deep blacks, high contrast cinematic color grade, "
    "photorealistic detail, no people, no text or logos in the image."
)
SUNSET = (
    "Cinematic vertical 9:16 video at golden sunset, warm lens "
    "flares, rich cinematic color grade, film grain, realistic "
    "physics and correct anatomy, no text or logos in the image."
)

SCENES = [
    {"id": "n1_cafe", "prompt": (
        "A modern high-end cafe racer motorcycle with a round "
        "headlight and cowled tail parked in a narrow city alley "
        "drenched in amber and gold neon light, steam drifting "
        "through the light beams, reflections rippling on wet "
        "asphalt. Camera: slow half-circle orbit around the "
        "motorcycle. " + NEON)},
    {"id": "n2_cruiser", "prompt": (
        "A massive modern power cruiser motorcycle with sweeping "
        "chrome, a low muscular stance and a wide rear tire, parked "
        "under crimson and warm gold neon signs, light blooming off "
        "the chrome, mist drifting through the glow. Camera: slow "
        "half-circle orbit around the motorcycle. " + NEON)},
    {"id": "n3_super", "prompt": (
        "An aggressive modern racing superbike with sharp fairings "
        "and aerodynamic winglets parked in a dark underground "
        "garage flooded with magenta and cyan neon, reflections "
        "sliding across the glossy fairings, haze in the light "
        "beams. Camera: slow half-circle orbit around the "
        "motorcycle. " + NEON)},
    {"id": "v1_canyon", "prompt": (
        "A rider in an open-face helmet and brown leather jacket "
        "rides a modern cafe racer motorcycle along a winding "
        "coastal canyon road at golden sunset, seated astride "
        "facing forward, warm light flaring across the frame. "
        "Camera: tracking alongside the motorcycle. " + SUNSET)},
    {"id": "v2_chrome", "prompt": (
        "Extreme close-up gliding over a modern cafe racer "
        "motorcycle at sunset: round glowing headlight, brushed "
        "aluminum fuel tank, chrome exhaust pipe releasing a small "
        "flame burst as the engine revs, heat shimmer. Camera: slow "
        "macro dolly along the machine. " + SUNSET)},
]

LOOPS = [
    ("n1_cafe", "neon-loop-cafe-racer", "CAFE RACER",
     "colorbalance=rs=.12:gs=.03:bs=-.12:rm=.10:bm=-.06"),
    ("n2_cruiser", "neon-loop-cruiser", "POWER CRUISER",
     "colorbalance=rs=.15:gs=-.02:bs=-.05:rm=.10:bm=.02"),
    ("n3_super", "neon-loop-superbike", "SUPERBIKE",
     "colorbalance=rs=.10:gs=-.05:bs=.14:rm=.06:bm=.10"),
]


def _loop_overlay(label, path):
    ov = Image.new("RGBA", (FRAME_WIDTH, FRAME_HEIGHT), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    draw_tracked_fit(d, (FRAME_WIDTH // 2, FRAME_HEIGHT - 170), label,
                     FONT_SERIF_BOLD, 40, CREAM, tracking=8)
    draw_tracked_fit(d, (FRAME_WIDTH // 2, 96), "THE RIDER'S GANG",
                     FONT_SERIF_BOLD, 24, (238, 232, 218, 120), tracking=7)
    _with_shadow(ov).save(path)


def build_loop(scene_id, out_name, label, balance):
    """Palindrome speed-ramp: 3.5 s forward (slow-snap-slow) + fast
    reverse back to frame one = a seamless ~8 s loop."""
    os.makedirs(TMP, exist_ok=True)
    src = os.path.join(AI_DIR, f"scene_{scene_id}.mp4")
    grade = (f"scale=1080:1920:force_original_aspect_ratio=increase:"
             f"flags=lanczos,crop=1080:1920,"
             f"eq=contrast=1.18:saturation=1.55:gamma=0.98,{balance},"
             f"vignette=PI/4.4")
    fwd = os.path.join(TMP, f"{scene_id}_fwd.mp4")
    subprocess.run([
        "ffmpeg", "-y", "-t", "3.5", "-i", src,
        "-filter_complex",
        f"[0:v]{grade},split=3[a][b][c];"
        "[a]trim=0:1.6,setpts=(PTS-STARTPTS)/0.72[sa];"
        "[b]trim=1.6:2.2,setpts=(PTS-STARTPTS)/1.9[sb];"
        "[c]trim=2.2:3.5,setpts=(PTS-STARTPTS)/0.72[sc];"
        "[sa][sb][sc]concat=n=3:v=1:a=0,fps=30[outv]",
        "-map", "[outv]",
        "-an", "-c:v", "libx264", "-preset", "fast", "-crf", "17",
        "-pix_fmt", "yuv420p", fwd], check=True, capture_output=True)
    rev = os.path.join(TMP, f"{scene_id}_rev.mp4")
    subprocess.run([
        "ffmpeg", "-y", "-i", fwd, "-vf", "reverse,setpts=PTS/1.6,fps=30",
        "-an", "-c:v", "libx264", "-preset", "fast", "-crf", "17",
        "-pix_fmt", "yuv420p", rev], check=True, capture_output=True)

    ov = os.path.join(TMP, f"{scene_id}_ov.png")
    _loop_overlay(label, ov)
    joined = os.path.join(TMP, f"{scene_id}_joined.mp4")
    subprocess.run([
        "ffmpeg", "-y", "-i", fwd, "-i", rev, "-loop", "1", "-i", ov,
        "-filter_complex",
        "[0:v][1:v]concat=n=2:v=1:a=0[cat];"
        "[cat][2:v]overlay=0:0:shortest=1,noise=alls=3:allf=t[outv]",
        "-map", "[outv]", "-an", "-c:v", "libx264", "-preset", "medium",
        "-crf", "19", "-pix_fmt", "yuv420p", joined],
        check=True, capture_output=True)

    dur = float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", joined], capture_output=True, text=True,
        check=True).stdout.strip())
    rng = np.random.default_rng(hash(scene_id) % 2 ** 31)
    audio = phonk_track(rng, dur)
    _add(audio, SFX["engine"](rng, min(2.5, dur - 1)) * 0.5, dur * 0.35)
    audio = master(glue(audio, 0.3, 2.0), target_rms_db=-15.0)
    delay = int(0.012 * SR)
    right = np.concatenate([np.zeros(delay), audio[:-delay]])
    stereo = np.stack([audio, right], axis=1)
    wav = os.path.join(TMP, f"{scene_id}.wav")
    pcm = (np.clip(stereo, -1, 1) * 32767).astype(np.int16)
    with wavmod.open(wav, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm.tobytes())

    out = os.path.join(OUT_DIR, f"{out_name}.mp4")
    thumb = os.path.join(OUT_DIR, f"{out_name}_cover.jpg")
    subprocess.run(["ffmpeg", "-y", "-ss", "1.0", "-i", joined,
                    "-frames:v", "1", thumb], check=True,
                   capture_output=True)
    subprocess.run([
        "ffmpeg", "-y", "-i", joined, "-i", wav, "-i", thumb,
        "-map", "0:v", "-map", "1:a", "-map", "2",
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-c:v:1", "mjpeg", "-disposition:v:1", "attached_pic",
        "-movflags", "+faststart", "-shortest", out],
        check=True, capture_output=True)
    print(f"  loop saved: {out} ({dur:.1f}s)")


# ── versus reel ──────────────────────────────────────────────────────

V_GRADE = ("scale=1080:1920:force_original_aspect_ratio=increase:"
           "flags=lanczos,crop=1080:1920,fps=30,"
           "eq=contrast=1.14:saturation=1.4:gamma=0.99")

# (dir, src, start, dur, speed, big text or None, small text or None)
V_SHOTS = [
    (SHERIDES_DIR, "scene_03_apex", 1.8, 1.0, 1.6, "TWO GANGS.", None),
    (AI_DIR, "scene_v2_chrome", 2.2, 1.1, 1.0, "PICK YOURS.", None),
    (AI_DIR, "scene_v1_canyon", 0.5, 1.6, 1.0, None, "TRIUMPH THRUXTON RS"),
    (AI_DIR, "scene_v2_chrome", 0.2, 1.5, 1.0, None, "105 HP • ALL TORQUE"),
    (AI_DIR, "scene_n1_cafe", 0.8, 1.4, 1.0, "MADE FOR SUNSETS.", None),
    (SHERIDES_DIR, "scene_03_apex", 0.4, 1.5, 1.3, None,
     "DUCATI PANIGALE V4S"),
    (SHERIDES_DIR, "scene_04_wheelie", 0.3, 1.4, 1.3, None,
     "215 HP • 15,000 RPM"),
    (AI_DIR, "scene_n3_super", 1.0, 1.3, 1.0, "MADE FOR APEXES.", None),
    (AI_DIR, "scene_v1_canyon", 2.4, 0.8, 1.4, "SUNSET", None),
    (SHERIDES_DIR, "scene_04_wheelie", 2.6, 0.8, 1.6, "APEX", None),
    (AI_DIR, "scene_n2_cruiser", 1.2, 0.8, 1.4, "HEART", None),
    (SHERIDES_DIR, "scene_03_apex", 3.2, 0.8, 1.6, "ADRENALINE", None),
]
VOTE_SEC = 2.6
DOUBLE_AT = 5              # venom round starts at shot index 5


def _big_text(text, path):
    ov = Image.new("RGBA", (FRAME_WIDTH, FRAME_HEIGHT), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    draw_plain_fit(d, (FRAME_WIDTH // 2, FRAME_HEIGHT // 2 - 40), text,
                   FONT_SERIF_BOLD, 96, CREAM)
    _with_shadow(ov).save(path)


def _small_text(text, path):
    ov = Image.new("RGBA", (FRAME_WIDTH, FRAME_HEIGHT), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    draw_tracked_fit(d, (FRAME_WIDTH // 2, FRAME_HEIGHT - 240), text,
                     FONT_SERIF_BOLD, 44, GOLD, tracking=4)
    _with_shadow(ov).save(path)


def _vote_card(path):
    img = Image.new("RGBA", (FRAME_WIDTH, FRAME_HEIGHT), (8, 8, 12, 255))
    d = ImageDraw.Draw(img)
    cy = FRAME_HEIGHT // 2
    draw_plain_fit(d, (FRAME_WIDTH // 2, cy - 190), "COMMENT:",
                   FONT_SERIF_BOLD, 60, CREAM)
    draw_plain_fit(d, (FRAME_WIDTH // 2, cy - 70), "VELVET",
                   FONT_SERIF_BOLD, 110, GOLD)
    draw_plain_fit(d, (FRAME_WIDTH // 2, cy + 40), "or", FONT_SERIF_ITALIC,
                   48, CREAM)
    draw_plain_fit(d, (FRAME_WIDTH // 2, cy + 150), "VENOM",
                   FONT_SERIF_BOLD, 110, (196, 66, 244, 255))
    draw_plain_fit(d, (FRAME_WIDTH // 2, cy + 290),
                   "Follow The Rider's Gang  •  AI cinema",
                   FONT_SERIF_ITALIC, 32, (200, 193, 178, 235))
    img.convert("RGB").save(path)


def build_versus():
    os.makedirs(TMP, exist_ok=True)
    segs, starts, cursor = [], [], 0.0
    for i, (d_, src, start, dur, speed, big, small) in enumerate(V_SHOTS):
        out = os.path.join(TMP, f"v_{i:02d}.mp4")
        vf = V_GRADE if speed == 1.0 else f"setpts=PTS/{speed},{V_GRADE}"
        cmd = ["ffmpeg", "-y", "-ss", f"{start:.2f}", "-i",
               os.path.join(d_, f"{src}.mp4")]
        if big or small:
            png = os.path.join(TMP, f"vt_{i:02d}.png")
            (_big_text if big else _small_text)(big or small, png)
            cmd += ["-loop", "1", "-t", f"{dur:.2f}", "-i", png,
                    "-filter_complex",
                    f"[0:v]{vf}[v];[1:v]format=rgba[t];"
                    f"[v][t]overlay=0:0:shortest=1[outv]",
                    "-map", "[outv]"]
        else:
            cmd += ["-vf", vf]
        cmd += ["-t", f"{dur:.2f}", "-r", "30", "-an", "-c:v", "libx264",
                "-preset", "fast", "-crf", "17", "-pix_fmt", "yuv420p", out]
        subprocess.run(cmd, check=True, capture_output=True)
        segs.append(out)
        starts.append(cursor)
        cursor += dur

    vote_png = os.path.join(TMP, "vote.png")
    _vote_card(vote_png)
    vote = os.path.join(TMP, "v_vote.mp4")
    subprocess.run(["ffmpeg", "-y", "-loop", "1", "-t", str(VOTE_SEC),
                    "-i", vote_png, "-vf", "noise=alls=4:allf=t,fps=30",
                    "-c:v", "libx264", "-preset", "fast", "-crf", "17",
                    "-pix_fmt", "yuv420p", vote], check=True,
                   capture_output=True)
    segs.append(vote)
    total = cursor + VOTE_SEC

    rng = np.random.default_rng(215)
    double_from = starts[DOUBLE_AT]
    audio = phonk_track(rng, total,
                        sections=[(0, double_from, "half"),
                                  (double_from, total, "double")])
    _add(audio, SFX["engine"](rng, 2.0) * 0.6, 0.0)
    _add(audio, SFX["engine"](rng, 2.5) * 0.55, double_from)
    audio = master(glue(audio, 0.3, 2.0), target_rms_db=-15.0)
    delay = int(0.012 * SR)
    right = np.concatenate([np.zeros(delay), audio[:-delay]])
    stereo = np.stack([audio, right], axis=1)
    wav = os.path.join(TMP, "versus.wav")
    pcm = (np.clip(stereo, -1, 1) * 32767).astype(np.int16)
    with wavmod.open(wav, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm.tobytes())

    inputs = []
    for s in segs:
        inputs += ["-i", s]
    concat = "".join(f"[{k}:v]" for k in range(len(segs)))
    out = os.path.join(OUT_DIR, "pick-your-gang-velvet-vs-venom.mp4")
    thumb = os.path.join(OUT_DIR, "pick-your-gang-velvet-vs-venom_cover.jpg")
    no_thumb = os.path.join(TMP, "versus_nothumb.mp4")
    subprocess.run([
        "ffmpeg", "-y", *inputs, "-i", wav,
        "-filter_complex", f"{concat}concat=n={len(segs)}:v=1:a=0[outv]",
        "-map", "[outv]", "-map", f"{len(segs)}:a",
        "-c:v", "libx264", "-preset", "medium", "-crf", "19",
        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart", "-shortest", no_thumb],
        check=True, capture_output=True)
    subprocess.run(["ffmpeg", "-y", "-ss", "6.5", "-i", no_thumb,
                    "-frames:v", "1", thumb], check=True,
                   capture_output=True)
    subprocess.run([
        "ffmpeg", "-y", "-i", no_thumb, "-i", thumb, "-map", "0",
        "-map", "1", "-c", "copy", "-c:v:1", "mjpeg",
        "-disposition:v:1", "attached_pic", "-movflags", "+faststart",
        out], check=True, capture_output=True)
    print(f"  versus saved: {out} ({total:.1f}s)")


def main():
    parser = argparse.ArgumentParser(description="Neon pack")
    parser.add_argument("--generate", action="store_true")
    parser.add_argument("--loops", action="store_true")
    parser.add_argument("--versus", action="store_true")
    args = parser.parse_args()
    os.makedirs(AI_DIR, exist_ok=True)

    if args.generate:
        import time

        from huggingface_hub import InferenceClient
        client = InferenceClient(provider="fal-ai",
                                 token=os.environ["HF_TOKEN"], timeout=560)
        for scene in SCENES:
            out = os.path.join(AI_DIR, f"scene_{scene['id']}.mp4")
            if os.path.exists(out):
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

    if args.loops:
        for scene_id, out_name, label, balance in LOOPS:
            print(f"[loop] {out_name}")
            build_loop(scene_id, out_name, label, balance)
        return

    if args.versus:
        build_versus()


if __name__ == "__main__":
    main()
