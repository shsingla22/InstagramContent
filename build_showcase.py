#!/usr/bin/env python3
"""Build showcase.html with V2 reels embedded as base64 data URIs."""
import base64
import os
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "videos", "v2"))
from reel_content import REELS

VIDEO_DIR = os.path.join(os.path.dirname(__file__), "output", "videos")
OUTPUT_HTML = os.path.join(os.path.dirname(__file__), "showcase.html")


def encode_video_b64(mp4_path):
    """Return base64 encoded string of the video file."""
    with open(mp4_path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


def convert_to_webm(mp4_path):
    """Convert MP4 to WebM (VP8) and return base64."""
    webm_path = mp4_path.replace(".mp4", ".webm")
    if not os.path.exists(webm_path):
        subprocess.run([
            "ffmpeg", "-y", "-i", mp4_path,
            "-c:v", "libvpx", "-b:v", "1M", "-crf", "30",
            "-c:a", "libvorbis", "-b:a", "128k",
            "-vf", "scale=1080:1920",
            "-threads", "4",
            webm_path,
        ], capture_output=True, check=True)
    with open(webm_path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


def build_reel_card(index, reel, mp4_b64, webm_b64):
    """Build HTML for a single reel card."""
    num = index + 1
    title = reel["title"].replace("\n", " ")
    subtitle = reel["subtitle"].replace("\n", " ")
    accent = reel["color_accent"]
    hook = reel["hook"]

    return f'''
    <div class="reel-card">
      <div class="reel-header">
        <span class="reel-number">#{num}</span>
        <span class="reel-badge" style="background:{accent}">REEL</span>
      </div>
      <div class="reel-title">{title}</div>
      <div class="reel-subtitle">{subtitle}</div>
      <div class="reel-hook">{hook}</div>
      <div class="video-container">
        <video class="reel-player" playsinline muted loop preload="auto">
          <source src="data:video/webm;base64,{webm_b64}" type="video/webm">
          <source src="data:video/mp4;base64,{mp4_b64}" type="video/mp4">
        </video>
        <button class="play-btn">&#9654;</button>
        <button class="mute-btn">&#128263;</button>
      </div>
    </div>'''


def build_html(cards_html):
    """Build the complete HTML page."""
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>The Rider's Gang - Instagram Reels Showcase</title>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
      background: #0a0a0a;
      color: #fff;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      padding: 20px;
    }}
    .header {{
      text-align: center;
      padding: 40px 20px;
      border-bottom: 1px solid #222;
      margin-bottom: 40px;
    }}
    .header h1 {{
      font-size: 2rem;
      letter-spacing: 3px;
      color: #D4A843;
    }}
    .header p {{
      color: #888;
      margin-top: 10px;
      font-size: 0.9rem;
    }}
    .reels-grid {{
      display: flex;
      flex-wrap: wrap;
      justify-content: center;
      gap: 30px;
      max-width: 1400px;
      margin: 0 auto;
    }}
    .reel-card {{
      background: #111;
      border-radius: 16px;
      overflow: hidden;
      width: 320px;
      box-shadow: 0 4px 20px rgba(0,0,0,0.5);
    }}
    .reel-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px 16px;
    }}
    .reel-number {{
      font-size: 1.2rem;
      font-weight: 700;
      color: #888;
    }}
    .reel-badge {{
      padding: 3px 10px;
      border-radius: 4px;
      font-size: 0.7rem;
      font-weight: 700;
      letter-spacing: 2px;
      color: #fff;
    }}
    .reel-title {{
      padding: 0 16px;
      font-size: 1.1rem;
      font-weight: 700;
      letter-spacing: 1px;
    }}
    .reel-subtitle {{
      padding: 4px 16px 8px;
      font-size: 0.8rem;
      color: #aaa;
    }}
    .reel-hook {{
      padding: 0 16px 12px;
      font-size: 0.75rem;
      color: #D4A843;
      font-weight: 600;
      letter-spacing: 1px;
    }}
    .video-container {{
      position: relative;
      width: 100%;
      aspect-ratio: 9/16;
      background: #000;
    }}
    .reel-player {{
      width: 100%;
      height: 100%;
      object-fit: cover;
    }}
    .play-btn, .mute-btn {{
      position: absolute;
      background: rgba(0,0,0,0.5);
      border: none;
      color: #fff;
      cursor: pointer;
      border-radius: 50%;
      width: 44px;
      height: 44px;
      font-size: 18px;
      display: flex;
      align-items: center;
      justify-content: center;
    }}
    .play-btn {{
      bottom: 16px;
      left: 16px;
    }}
    .mute-btn {{
      bottom: 16px;
      right: 16px;
    }}
    .play-btn:hover, .mute-btn:hover {{
      background: rgba(255,255,255,0.2);
    }}
  </style>
</head>
<body>
  <div class="header">
    <h1>THE RIDER'S GANG</h1>
    <p>Instagram Reels Showcase &mdash; 10 Stories</p>
  </div>
  <div class="reels-grid">
    {cards_html}
  </div>
  <script>
    // Play/pause toggle + only one video plays at a time
    document.querySelectorAll('.reel-card').forEach(card => {{
      const video = card.querySelector('.reel-player');
      const playBtn = card.querySelector('.play-btn');
      const muteBtn = card.querySelector('.mute-btn');

      function togglePlay() {{
        if (video.paused) {{
          // Pause all other videos
          document.querySelectorAll('.reel-player').forEach(v => {{
            if (v !== video) {{ v.pause(); }}
          }});
          // Update all play buttons
          document.querySelectorAll('.play-btn').forEach(b => {{ b.textContent = '\\u25B6'; }});
          video.play().catch(() => {{}});
          playBtn.textContent = '\\u23F8';
        }} else {{
          video.pause();
          playBtn.textContent = '\\u25B6';
        }}
      }}

      playBtn.addEventListener('click', togglePlay);
      video.addEventListener('click', togglePlay);

      muteBtn.addEventListener('click', () => {{
        video.muted = !video.muted;
        muteBtn.textContent = video.muted ? '\\ud83d\\udd09' : '\\ud83d\\udd0a';
      }});
    }});
  </script>
</body>
</html>'''


def main():
    cards = []
    for i, reel in enumerate(REELS):
        mp4_file = os.path.join(VIDEO_DIR, f"{reel['slug']}.mp4")
        if not os.path.exists(mp4_file):
            print(f"WARNING: {mp4_file} not found, skipping")
            continue

        print(f"Processing reel {i+1}/10: {reel['slug']}...")
        mp4_b64 = encode_video_b64(mp4_file)
        webm_b64 = convert_to_webm(mp4_file)
        cards.append(build_reel_card(i, reel, mp4_b64, webm_b64))

    html = build_html("\n".join(cards))
    with open(OUTPUT_HTML, "w") as f:
        f.write(html)
    print(f"Wrote {OUTPUT_HTML} ({os.path.getsize(OUTPUT_HTML) / 1024 / 1024:.1f} MB)")


if __name__ == "__main__":
    main()
