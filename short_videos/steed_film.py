"""
STEED Film Nº1 — "The Ton" (the Ace Cafe story, told by STEED).

The debut of STEED, The Rider's Gang's digital creator: a mechanical
horse-motorcycle who narrates riding history in first person (deep
voice, Kokoro am_onyx). Character shots are animated from the
approved concept art via Wan image-to-video so STEED stays on-model;
story b-roll is text-to-video; the bed is the in-house rockabilly
score ducked under his voice. Feed rules: character cold open with a
hook line, beat-locked cuts, captions for muted viewing, watermark,
CTA + loop, disclosed AI (a talking machine-horse discloses itself).

Run:  HF_TOKEN=... python3 -m short_videos.steed_film --generate
      HF_TOKEN=... python3 -m short_videos.steed_film --voice
      python3 -m short_videos.steed_film            (assemble)
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
from short_videos.film_score import MOODS, SFX, _crash
from short_videos.rockabilly_score import SR, _add, _env

AI_DIR = "output/short_videos/films/steed-wan"
VO_DIR = os.path.join(AI_DIR, ".voice")
TMP = os.path.join(AI_DIR, ".assembly")
OUT_PATH = "output/short_videos/films/steed-01-the-ton.mp4"
THUMB_PATH = "output/short_videos/films/steed-01-the-ton_cover.jpg"
CONCEPT_PNG = ("/tmp/claude-0/-home-user-InstagramContent/"
               "7b927874-4269-534e-b24b-e54c1786f3cf/scratchpad/"
               "creators/02_steed.png")

BPM = 120
BEAT = 60.0 / BPM

FIFTIES = (
    "Cinematic vertical 9:16 video, London 1952 at night, shot on 35mm "
    "film, moody neon and sodium light, rain-wet streets, film grain, "
    "realistic physics and correct anatomy, documentary realism, no "
    "text or captions in the image."
)

T2V_SCENES = [
    {"id": "02_cafe", "prompt": (
        "Exterior of a 1950s London transport cafe at night in light "
        "rain, warm windows glowing, a soft neon sign reflected in the "
        "wet asphalt, rows of vintage cafe racer motorcycles parked "
        "outside, young men in leather jackets talking beside them. "
        "Camera: slow dolly along the parked bikes. " + FIFTIES)},
    {"id": "03_boys", "prompt": (
        "Inside a smoky 1950s London cafe at night, young rockers in "
        "leather jackets lean on the counter with mugs of tea, one "
        "spins a coin on the formica table, all glancing toward the "
        "jukebox. Camera: handheld medium shot drifting past their "
        "faces. " + FIFTIES)},
    {"id": "04_jukebox", "prompt": (
        "Extreme close-up of a hand dropping a sixpence coin into the "
        "slot of a glowing 1950s jukebox, the mechanism lifting a "
        "vinyl record into place and the record starting to spin, "
        "warm neon colors reflecting on chrome. Camera: slow close "
        "push. " + FIFTIES)},
    {"id": "05_race", "prompt": (
        "Two 1950s cafe racer motorcycles race side by side down a "
        "dark wet London arterial road at night, riders in leather "
        "jackets crouched low over the tanks, correctly astride "
        "facing forward, headlight beams streaking on the wet "
        "asphalt, lampposts flashing past. Camera: low tracking shot "
        "alongside. " + FIFTIES)},
    {"id": "06_speedo", "prompt": (
        "Close-up over a rider's shoulder of a vintage motorcycle "
        "speedometer at night, the needle sweeping up toward one "
        "hundred miles per hour, gloved hand on the throttle, the "
        "dark road rushing beneath, dial glowing amber. Camera: "
        "locked close shot, slight vibration. " + FIFTIES)},
    {"id": "07_legends", "prompt": (
        "Young riders pull their vintage motorcycles back in to the "
        "1950s London cafe at night and pull off their helmets, "
        "laughing, steam rising from the engines in the cool air, "
        "friends clapping them on the shoulder, warm cafe light. "
        "Camera: medium tracking as they arrive. " + FIFTIES)},
]

STEED2_FLUX_PROMPT = (
    "A magnificent mechanical horse fused with a vintage cafe racer "
    "motorcycle: sculpted chrome and matte-black horse head as the "
    "fairing, flowing mane of copper cables, fuel tank body with gold "
    "pinstripes, wheels where hooves would be, glowing amber eyes, "
    "standing on a rain-wet 1950s London street at night outside a "
    "glowing transport cafe, neon light reflecting on the chrome, "
    "character concept portrait, cinematic lighting, rich detail, "
    "vertical 9:16 composition, no text")

I2V_SCENES = [
    {"id": "01_awaken", "src": "concept",
     "prompt": ("The mechanical horse-motorcycle stands in the dark "
                "workshop. Its amber eyes slowly ignite and glow "
                "brighter, the copper cable mane sways gently, subtle "
                "steam vents from its nostrils, warm rim light "
                "flickers. Camera: very slow push-in toward the "
                "glowing eyes. Cinematic, moody.")},
    {"id": "08_street", "src": "steed2",
     "prompt": ("The mechanical horse-motorcycle stands on the "
                "rain-wet night street, neon light flickering on its "
                "chrome, rain falling softly, the copper cable mane "
                "swaying, amber eyes glowing steadily. Camera: slow "
                "orbit around the machine. Cinematic, moody.")},
]

VO_LINES = [
    ("vo1", "They ask why my heart sounds like hoofbeats."),
    ("vo2", "London, nineteen fifty two. The Ace Cafe never slept."),
    ("vo3", "Boys with fast bikes dropped a coin in the jukebox,"),
    ("vo4", "and raced the record. Out and back, before the song ended."),
    ("vo5", "One hundred miles an hour. They called it the ton."),
    ("vo6", "The ones who came back became legends."),
    ("vo7", "They called themselves cafe racers."),
    ("vo8", "I call them family."),
    ("vo9", "Follow me. Every legend rides again."),
]
VOICE = {"voice": "am_onyx", "speed": 0.92}

# (source, start, beats, caption, vo id, crop_top)
# beats sized to the measured narration lines (deep voice, 0.92 speed)
SHOTS = [
    ("scene_01_awaken", 0.2, 7, "Why does my heart sound like hoofbeats?",
     "vo1", True),
    ("scene_02_cafe", 0.0, 10, "London, 1952. The Ace Cafe.", "vo2", False),
    ("scene_03_boys", 0.8, 4, "A coin in the jukebox…", "vo3", False),
    ("scene_04_jukebox", 1.0, 4, None, None, False),
    ("scene_05_race", 0.5, 9, "…and race the record.", "vo4", False),
    ("scene_06_speedo", 0.8, 8, "100 mph. The ton.", "vo5", False),
    ("scene_07_legends", 0.6, 7, "Make it back — become a legend.",
     "vo6", False),
    ("scene_08_street", 0.4, 7, "They called themselves cafe racers.",
     "vo7", False),
    ("scene_01_awaken", 2.5, 5, "I call them family.", "vo8", True),
    ("scene_08_street", 1.5, 7, None, "vo9", False),      # CTA hold
    ("scene_01_awaken", 0.2, 4, None, None, True),        # loop
]
CTA_IDX = 9


def _caption_png(text, path):
    ov = Image.new("RGBA", (FRAME_WIDTH, FRAME_HEIGHT), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    grad_h = 340
    band = Image.new("L", (1, grad_h), 0)
    for i in range(grad_h):
        band.putpixel((0, i), int(150 * (i / grad_h) ** 1.5))
    band = band.resize((FRAME_WIDTH, grad_h))
    g = Image.new("RGBA", (FRAME_WIDTH, grad_h), (3, 3, 5, 255))
    g.putalpha(band)
    ov.alpha_composite(g, (0, FRAME_HEIGHT - grad_h))
    draw_plain_fit(d, (FRAME_WIDTH // 2, FRAME_HEIGHT - 235), text,
                   FONT_SERIF_BOLD, 52, CREAM)
    _with_shadow(ov).save(path)


def _cta_png(path):
    ov = Image.new("RGBA", (FRAME_WIDTH, FRAME_HEIGHT), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    grad_h = 500
    band = Image.new("L", (1, grad_h), 0)
    for i in range(grad_h):
        band.putpixel((0, i), int(180 * (i / grad_h) ** 1.5))
    band = band.resize((FRAME_WIDTH, grad_h))
    g = Image.new("RGBA", (FRAME_WIDTH, grad_h), (3, 3, 5, 255))
    g.putalpha(band)
    ov.alpha_composite(g, (0, FRAME_HEIGHT - grad_h))
    draw_tracked_fit(d, (FRAME_WIDTH // 2, FRAME_HEIGHT - 400), "STEED",
                     FONT_SERIF_BOLD, 72, CREAM, tracking=10)
    draw_plain_fit(d, (FRAME_WIDTH // 2, FRAME_HEIGHT - 300),
                   "Follow — every legend rides again",
                   FONT_SERIF_BOLD, 40, GOLD)
    draw_plain_fit(d, (FRAME_WIDTH // 2, FRAME_HEIGHT - 225),
                   "The Rider's Gang  •  AI cinema",
                   FONT_SERIF_ITALIC, 32, (200, 193, 178, 235))
    _with_shadow(ov).save(path)


def _watermark(path):
    ov = Image.new("RGBA", (FRAME_WIDTH, FRAME_HEIGHT), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    draw_tracked_fit(d, (FRAME_WIDTH // 2, 96), "STEED • THE RIDER'S GANG",
                     FONT_SERIF_BOLD, 26, (238, 232, 218, 130), tracking=6)
    ov.save(path)


def _render_cut(idx, src, start, dur, caption, crop_top, out):
    # crop_top trims the lower fifth (the concept art's tank lettering)
    base = ("crop=iw:ih*0.82:0:0," if crop_top else "")
    vf = (f"{base}scale=1080:1920:force_original_aspect_ratio=increase:"
          "flags=lanczos,crop=1080:1920,fps=24,"
          "eq=gamma=1.02:contrast=1.05:saturation=0.98")
    cmd = ["ffmpeg", "-y", "-ss", f"{start:.3f}", "-i",
           os.path.join(AI_DIR, f"{src}.mp4")]
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


def _load_wav_mono(path):
    out = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-ac", "1",
         "-ar", str(SR), "-"], capture_output=True, check=True)
    return np.frombuffer(out.stdout, dtype=np.float32).astype(np.float64)


def build_audio(shot_starts, total, wav_path):
    rng = np.random.default_rng(1952)
    n = int(total * SR)

    vo = np.zeros(n)
    prev_end = 0.0
    for (src, start, beats, cap, vo_id, crop), at in zip(SHOTS, shot_starts):
        if not vo_id:
            continue
        seg = _load_wav_mono(os.path.join(VO_DIR, f"{vo_id}.wav"))
        rms = np.sqrt((seg ** 2).mean())
        if rms > 0:
            seg = seg / rms * 0.215          # voice out front
        vo_at = max(at + 0.1, prev_end + 0.2)
        _add(vo, seg, vo_at)
        prev_end = vo_at + len(seg) / SR

    from short_videos.studio import THEME_SECONDS, steed_bed, steed_theme
    music = np.zeros(n)
    _add(music, steed_theme(), 0.0)                      # the sonic logo
    bed = steed_bed(rng, total - THEME_SECONDS + 0.4)
    edge = int(0.3 * SR)
    bed[:edge] *= np.linspace(0, 1, edge)
    _add(music, bed, THEME_SECONDS - 0.4)
    _add(music, _crash(rng) * 0.6, shot_starts[1])       # into the story
    # engine layer under the race and speedo shots
    race_at, race_end = shot_starts[4], shot_starts[6]
    _add(music, SFX["engine"](rng, race_end - race_at) * 0.45, race_at)
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
    duck = 1.0 - 0.55 * env              # music stays bold under the voice
    smooth = int(0.05 * SR)
    duck = np.convolve(duck, np.ones(smooth) / smooth, mode="same")
    music *= duck

    from short_videos.studio import master
    audio = master(music + vo)
    fade_in = int(0.1 * SR)
    audio[:fade_in] *= np.linspace(0, 1, fade_in)
    fade_out = int(0.8 * SR)
    audio[-fade_out:] *= 0.5 + 0.5 * np.cos(np.linspace(0, np.pi, fade_out))
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
                    os.path.join(AI_DIR, "scene_01_awaken.mp4"),
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
                   "Why does my heart", FONT_SERIF_BOLD, 56, CREAM)
    draw_plain_fit(d, (FRAME_WIDTH // 2, cy + 80),
                   "sound like hoofbeats?", FONT_SERIF_BOLD, 56, GOLD)
    draw_plain_fit(d, (FRAME_WIDTH // 2, cy + 165), "Nº1 • THE TON",
                   FONT_SERIF_ITALIC, 38, GOLD)
    img.alpha_composite(_with_shadow(ov))
    img.convert("RGB").save(THUMB_PATH, quality=90)
    os.remove(tmpf)


def assemble():
    os.makedirs(TMP, exist_ok=True)
    segs, starts, cursor = [], [], 0.0
    for i, (src, start, beats, cap, vo_id, crop) in enumerate(SHOTS):
        dur = beats * BEAT
        print(f"[steed] cut {i + 1}/{len(SHOTS)}")
        out = os.path.join(TMP, f"cut_{i:02d}.mp4")
        _render_cut(i, src, start, dur, cap, crop, out)
        segs.append(out)
        starts.append(cursor)
        cursor += dur
    total = cursor

    print(f"[steed] audio: total {total:.2f}s")
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
    print(f"\nSTEED Nº1 saved: {OUT_PATH} ({size:.1f} MB, {total:.1f}s)")


def main():
    parser = argparse.ArgumentParser(description="STEED film Nº1")
    parser.add_argument("--generate", action="store_true")
    parser.add_argument("--voice", action="store_true")
    parser.add_argument("--only")
    args = parser.parse_args()
    os.makedirs(AI_DIR, exist_ok=True)

    if args.generate:
        from huggingface_hub import InferenceClient
        client = InferenceClient(provider="fal-ai",
                                 token=os.environ["HF_TOKEN"], timeout=560)
        # STEED street still → i2v
        steed2_png = os.path.join(AI_DIR, "steed2_still.png")
        if not os.path.exists(steed2_png):
            from gradio_client import Client
            print("  [FLUX] steed street still...", flush=True)
            flux = Client("black-forest-labs/FLUX.1-Krea-dev",
                          token=os.environ["HF_TOKEN"], verbose=False)
            result = flux.predict(prompt=STEED2_FLUX_PROMPT, seed=72,
                                  randomize_seed=False, width=576,
                                  height=1024, guidance_scale=4.5,
                                  num_inference_steps=28, api_name="/infer")
            img = result[0] if isinstance(result, (list, tuple)) else result
            if isinstance(img, dict):
                img = img.get("path") or img.get("url")
            import shutil
            shutil.copy(img, steed2_png)
        for scene in I2V_SCENES:
            out = os.path.join(AI_DIR, f"scene_{scene['id']}.mp4")
            if os.path.exists(out) and not args.only:
                print(f"  {scene['id']}: cached")
                continue
            if args.only and scene["id"] != args.only:
                continue
            src = CONCEPT_PNG if scene["src"] == "concept" else steed2_png
            print(f"  [Wan-I2V] {scene['id']}...", flush=True)
            video = client.image_to_video(
                open(src, "rb").read(), prompt=scene["prompt"],
                model="Wan-AI/Wan2.2-I2V-A14B")
            with open(out, "wb") as f:
                f.write(video)
            print(f"    done ({len(video) / 1e6:.1f} MB)", flush=True)
        for scene in T2V_SCENES:
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
            audio = client.text_to_speech(text, model="hexgrad/Kokoro-82M",
                                          extra_body=VOICE)
            with open(out, "wb") as f:
                f.write(audio)
        return

    assemble()


if __name__ == "__main__":
    main()
