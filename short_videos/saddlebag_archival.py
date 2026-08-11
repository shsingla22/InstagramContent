"""
Saddlebag Pilot A — archival documentary ("Cavalry Gear", real).

Same story and narration as the photoreal reel, but built entirely
from real public-domain artifacts (see saddlebag-archive/
ATTRIBUTION.md): the 1956 Hepburn/Kelly backstage photograph, the
Achaemenid cavalry of the Alexander Sarcophagus, a Codex Manesse
illumination, the 1861 Pony Express poster, Remington's cowboy,
and Thierry Hermès himself — animated only with Ken Burns moves.
Nothing AI-generated on screen; testing whether authentic imagery
escapes the AI skip reflex.

Run:  python3 -m short_videos.saddlebag_archival
"""

import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PIL import Image, ImageDraw

from short_videos import (
    FONT_SERIF_BOLD, FONT_SERIF_ITALIC, FRAME_HEIGHT, FRAME_WIDTH,
)
from short_videos.build_story_reel import (
    CREAM, GOLD, _vignette_layer, _with_shadow, draw_plain_fit,
    draw_tracked_fit,
)

IMG_DIR = "output/short_videos/films/saddlebag-archive"
TMP = os.path.join(IMG_DIR, ".assembly")
OUT_PATH = "output/short_videos/films/saddlebag-pilot-archival.mp4"
THUMB_PATH = "output/short_videos/films/saddlebag-pilot-archival_cover.jpg"

BPM = 120
BEAT = 60.0 / BPM

# (image, beats, caption, vo id, zoom_start, zoom_end, pan_x 0..1)
# pan_x: horizontal drift of the crop window center, -1 left → +1 right
SHOTS = [
    ("hepburn_kelly", 6, "That $4,000 Dior bag?", "vo01", 1.0, 1.18, 0.3),
    ("cavalry3", 4, "Cavalry gear.", "vo02", 1.35, 1.12, 0.0),
    ("cavalry3", 7, "Persia, 500 BC.", "vo03b", 1.12, 1.28, -0.5),
    ("medieval", 7, "It carried the royal mail…", "vo04b", 1.0, 1.22, 0.2),
    ("ponyexpress", 3, "…before mail existed.", None, 1.15, 1.35, 0.0),
    ("cowboy", 4, "Cowboys lived out of it.", "vo06b", 1.1, 1.28, -0.3),
    ("hermes", 7, "Then cars killed the horse.", "vo07b", 1.0, 1.25, 0.0),
    ("hepburn_kelly", 5, "Grace Kelly, 1956.", "vo08", 1.35, 1.6, 0.5),
    ("leather", 5, None, "vo09b", 1.0, 1.12, 0.0),          # big text
    ("cowboy", 7, None, "vo10", 1.35, 1.1, 0.4),            # thesis + CTA
    ("hepburn_kelly", 5, None, "vo11", 1.0, 1.1, 0.3),      # loop
]
BIGTEXT_IDX = 8
CTA_IDX = 9


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


def _bigtext_png(path):
    ov = Image.new("RGBA", (FRAME_WIDTH, FRAME_HEIGHT), (0, 0, 0, 100))
    d = ImageDraw.Draw(ov)
    cy = FRAME_HEIGHT // 2
    draw_tracked_fit(d, (FRAME_WIDTH // 2, cy - 90), "DIOR",
                     FONT_SERIF_BOLD, 130, CREAM, tracking=12)
    d.line([(FRAME_WIDTH * 0.32, cy + 15), (FRAME_WIDTH * 0.68, cy + 15)],
           fill=GOLD, width=2)
    draw_tracked_fit(d, (FRAME_WIDTH // 2, cy + 70), "1999",
                     FONT_SERIF_BOLD, 72, GOLD, tracking=10)
    draw_plain_fit(d, (FRAME_WIDTH // 2, cy + 170),
                   "It just copied the saddle.", FONT_SERIF_ITALIC, 42, CREAM)
    _with_shadow(ov).save(path)


def _cta_png(path):
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
                   "Follow — real history, weekly", FONT_SERIF_BOLD, 40, GOLD)
    draw_plain_fit(d, (FRAME_WIDTH // 2, FRAME_HEIGHT - 165),
                   "The Rider's Gang  •  Archive", FONT_SERIF_ITALIC, 32,
                   (200, 193, 178, 235))
    _with_shadow(ov).save(path)


def _watermark(path):
    ov = Image.new("RGBA", (FRAME_WIDTH, FRAME_HEIGHT), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    draw_tracked_fit(d, (FRAME_WIDTH // 2, 96), "THE RIDER'S GANG",
                     FONT_SERIF_BOLD, 26, (238, 232, 218, 130), tracking=7)
    ov.save(path)


def _prep_image(name, out_png):
    """Fit source onto a 1080x1920 canvas: cover-crop for portrait-ish
    sources, blurred-fill letterbox for wide or text-bearing ones."""
    src = Image.open(os.path.join(IMG_DIR, f"{name}.jpg")).convert("RGB")
    w, h = src.size
    target = FRAME_WIDTH / FRAME_HEIGHT
    if name in ("ponyexpress", "medieval", "cowboy"):
        # keep whole artifact visible on a blurred backdrop
        from PIL import ImageFilter
        bg = src.resize((FRAME_WIDTH, FRAME_HEIGHT), Image.LANCZOS)
        bg = bg.filter(ImageFilter.GaussianBlur(40))
        scale = min(FRAME_WIDTH / w, FRAME_HEIGHT / h) * 0.98
        fg = src.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
        bg.paste(fg, ((FRAME_WIDTH - fg.width) // 2,
                      (FRAME_HEIGHT - fg.height) // 2))
        canvas = bg
    else:
        if w / h > target:
            nw = int(h * target)
            canvas = src.crop(((w - nw) // 2, 0, (w + nw) // 2, h))
        else:
            nh = int(w / target)
            canvas = src.crop((0, (h - nh) // 2, w, (h + nh) // 2))
        canvas = canvas.resize((FRAME_WIDTH, FRAME_HEIGHT), Image.LANCZOS)
    # oversize 1.5x so zoompan has room to move without upscaling blur
    canvas = canvas.resize((int(FRAME_WIDTH * 1.5), int(FRAME_HEIGHT * 1.5)),
                           Image.LANCZOS)
    canvas.save(out_png)


def _render_shot(idx, name, dur, caption, zs, ze, pan):
    frames = max(2, int(round(dur * 24)))
    src_png = os.path.join(TMP, f"src_{name}.png")
    if not os.path.exists(src_png):
        _prep_image(name, src_png)
    zoom = (f"{zs}+({ze}-{zs})*on/{frames - 1}")
    x = (f"(iw-iw/zoom)/2+({pan})*(iw-iw/zoom)/2*on/{frames - 1}")
    y = "(ih-ih/zoom)/2"
    vf = (f"zoompan=z='{zoom}':x='{x}':y='{y}':d={frames}:"
          f"s={FRAME_WIDTH}x{FRAME_HEIGHT}:fps=24,"
          "eq=gamma=1.02:contrast=1.04:saturation=0.98")
    out = os.path.join(TMP, f"cut_{idx:02d}.mp4")
    cmd = ["ffmpeg", "-y", "-loop", "1", "-t", f"{dur:.3f}",
           "-i", src_png]
    overlays = []
    if caption:
        png = os.path.join(TMP, f"cap_{idx:02d}.png")
        _caption_png(caption, png)
        overlays.append((png, 0.1))
    if idx == BIGTEXT_IDX:
        png = os.path.join(TMP, "bigtext.png")
        _bigtext_png(png)
        overlays.append((png, 0.2))
    if idx == CTA_IDX:
        png = os.path.join(TMP, "cta.png")
        _cta_png(png)
        overlays.append((png, 0.6))
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
    return out


def build_thumbnail():
    base = Image.open(os.path.join(IMG_DIR, "hepburn_kelly.jpg")).convert("RGB")
    w, h = base.size
    target = FRAME_WIDTH / FRAME_HEIGHT
    if w / h > target:
        nw = int(h * target)
        base = base.crop(((w - nw) // 2, 0, (w + nw) // 2, h))
    else:
        nh = int(w / target)
        base = base.crop((0, (h - nh) // 2, w, (h + nh) // 2))
    base = base.resize((FRAME_WIDTH, FRAME_HEIGHT), Image.LANCZOS)
    img = base.convert("RGBA")
    ov = Image.new("RGBA", (FRAME_WIDTH, FRAME_HEIGHT), (0, 0, 0, 0))
    ov.alpha_composite(_vignette_layer(0.55))
    d = ImageDraw.Draw(ov)
    draw_tracked_fit(d, (FRAME_WIDTH // 2, 200), "CAVALRY GEAR",
                     FONT_SERIF_BOLD, 84, CREAM, tracking=7)
    d.line([(FRAME_WIDTH * 0.34, 268), (FRAME_WIDTH * 0.66, 268)],
           fill=GOLD, width=2)
    cy = FRAME_HEIGHT - 400
    draw_plain_fit(d, (FRAME_WIDTH // 2, cy), "That $4,000 Dior bag?",
                   FONT_SERIF_BOLD, 58, CREAM)
    draw_plain_fit(d, (FRAME_WIDTH // 2, cy + 82),
                   "The real 5,000-year story.", FONT_SERIF_BOLD, 50, GOLD)
    img.alpha_composite(_with_shadow(ov))
    img.convert("RGB").save(THUMB_PATH, quality=90)


def assemble():
    os.makedirs(TMP, exist_ok=True)
    import short_videos.saddlebag_film as sf

    segs, starts, cursor = [], [], 0.0
    for i, (name, beats, cap, vo_id, zs, ze, pan) in enumerate(SHOTS):
        dur = beats * BEAT
        print(f"[archival] shot {i + 1}/{len(SHOTS)}")
        segs.append(_render_shot(i, name, dur, cap, zs, ze, pan))
        starts.append(cursor)
        cursor += dur
    total = cursor

    # reuse the saddlebag audio builder (VO + ducked score)
    sf.SHOTS = [(IMG_DIR, name, 0, beats, cap, vo_id, 1.0)
                for (name, beats, cap, vo_id, zs, ze, pan) in SHOTS]
    wav = os.path.join(TMP, "mix.wav")
    print(f"[archival] audio: total {total:.2f}s")
    sf.build_audio(starts, total, wav)

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
        f"[cat][wm]overlay=0:0:shortest=1,noise=alls=5:allf=t[outv]",
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
    print(f"\nArchival pilot saved: {OUT_PATH} ({size:.1f} MB, {total:.1f}s)")


if __name__ == "__main__":
    assemble()
