"""
Module 2: Generate reels-only HTML showcase with embedded video.

Produces a self-contained HTML file displaying Instagram Reels with
the video embedded as a base64 WebM data URI — playable by just
opening the HTML file in any modern browser (no server needed).
"""

import base64
import html as html_mod
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "videos", "v2"))
from reel_content import REELS


def _encode_b64(path: str) -> str:
    """Return base64 encoded string of a file."""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


def build_reel_card(reel: dict, webm_b64: str) -> str:
    """Build HTML for a single reel card with embedded video."""
    title = html_mod.escape(reel["title"].replace("\n", " "))
    subtitle = html_mod.escape(reel["subtitle"].replace("\n", " "))
    hook = html_mod.escape(reel["hook"])
    accent = reel["color_accent"]
    narration = html_mod.escape(reel["narration"])
    scenes_html = ""
    for i, scene in enumerate(reel["scenes"]):
        scenes_html += f'<div class="scene"><span class="scene-num">{i+1}</span> {html_mod.escape(scene["text"].replace(chr(10), " "))}</div>\n'

    return f"""
    <div class="reel-card">
      <div class="reel-info">
        <div class="reel-badge" style="background:{accent}">REEL</div>
        <h2 class="reel-title">{title}</h2>
        <p class="reel-subtitle">{subtitle}</p>
        <p class="reel-hook" style="color:{accent}">{hook}</p>
      </div>

      <div class="video-container">
        <video class="reel-player" loop muted playsinline preload="auto">
          <source src="data:video/webm;base64,{webm_b64}" type="video/webm">
        </video>
        <div class="video-overlay" id="video-overlay">
          <button class="big-play-btn" id="big-play" aria-label="Play video">
            <svg viewBox="0 0 80 80" width="80" height="80">
              <circle cx="40" cy="40" r="38" fill="rgba(0,0,0,0.6)" stroke="white" stroke-width="2"/>
              <polygon points="32 24 60 40 32 56" fill="white"/>
            </svg>
          </button>
        </div>
        <div class="video-controls">
          <button class="play-btn" aria-label="Play/Pause">
            <svg class="icon-play" viewBox="0 0 24 24" width="28" height="28">
              <polygon points="6 3 20 12 6 21" fill="white"/>
            </svg>
            <svg class="icon-pause" viewBox="0 0 24 24" width="28" height="28" style="display:none">
              <rect x="5" y="3" width="5" height="18" rx="1" fill="white"/>
              <rect x="14" y="3" width="5" height="18" rx="1" fill="white"/>
            </svg>
          </button>
          <div class="progress-bar">
            <div class="progress-fill" id="progress-fill"></div>
          </div>
          <span class="time-display" id="time-display">0:00 / 0:00</span>
          <button class="mute-btn" aria-label="Toggle sound">
            <svg class="icon-muted" viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="white" stroke-width="2">
              <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/>
              <line x1="23" y1="9" x2="17" y2="15"/><line x1="17" y1="9" x2="23" y2="15"/>
            </svg>
            <svg class="icon-unmuted" viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="white" stroke-width="2" style="display:none">
              <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/>
              <path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"/>
            </svg>
          </button>
        </div>
      </div>

      <div class="reel-details">
        <h3>Narration</h3>
        <p class="narration-text">{narration}</p>
        <h3>Scenes</h3>
        <div class="scenes-list">
          {scenes_html}
        </div>
      </div>
    </div>
    """


def generate_reels_html(reel_cards_html: str, count: int) -> str:
    """Generate the complete reels HTML page."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>The Rider's Gang — Instagram Reels</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=Inter:wght@400;500;600;700&display=swap');

    :root {{
      --bg: #0a0806;
      --card-bg: #151210;
      --text: #e8e0d4;
      --text-secondary: #8a7e70;
      --border: #2a2420;
      --accent: #D4A843;
      --accent-dark: #2C1810;
      --gold: #C9A84C;
      --cream: #F5E6C8;
    }}

    * {{ margin: 0; padding: 0; box-sizing: border-box; }}

    body {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.6;
    }}

    .hero {{
      text-align: center;
      padding: 60px 20px 40px;
      border-bottom: 1px solid var(--border);
    }}
    .hero .subtitle {{
      font-size: 0.8rem;
      letter-spacing: 4px;
      text-transform: uppercase;
      color: var(--text-secondary);
      margin-bottom: 8px;
    }}
    .hero h1 {{
      font-family: 'Playfair Display', Georgia, serif;
      font-size: 2.5rem;
      font-weight: 900;
      color: var(--accent);
      letter-spacing: 3px;
      text-transform: uppercase;
    }}
    .hero p {{
      color: var(--text-secondary);
      margin-top: 10px;
      font-size: 0.9rem;
    }}

    .reels-container {{
      max-width: 500px;
      margin: 40px auto;
      padding: 0 20px;
    }}

    .reel-card {{
      background: var(--card-bg);
      border-radius: 16px;
      overflow: hidden;
      border: 1px solid var(--border);
    }}

    .reel-info {{
      padding: 20px 20px 16px;
    }}
    .reel-badge {{
      display: inline-block;
      padding: 3px 12px;
      border-radius: 4px;
      font-size: 0.7rem;
      font-weight: 700;
      letter-spacing: 2px;
      color: #fff;
      margin-bottom: 12px;
    }}
    .reel-title {{
      font-family: 'Playfair Display', serif;
      font-size: 1.6rem;
      font-weight: 900;
      color: var(--cream);
      letter-spacing: 1px;
      margin-bottom: 4px;
    }}
    .reel-subtitle {{
      font-size: 0.9rem;
      color: var(--text-secondary);
      margin-bottom: 8px;
    }}
    .reel-hook {{
      font-size: 0.8rem;
      font-weight: 700;
      letter-spacing: 2px;
      text-transform: uppercase;
    }}

    /* ── Video Player ── */
    .video-container {{
      position: relative;
      width: 100%;
      aspect-ratio: 9/16;
      background: #000;
      cursor: pointer;
    }}
    .reel-player {{
      width: 100%;
      height: 100%;
      object-fit: cover;
    }}
    .video-overlay {{
      position: absolute;
      inset: 0;
      display: flex;
      align-items: center;
      justify-content: center;
      background: rgba(0,0,0,0.3);
      transition: opacity 0.3s;
    }}
    .video-overlay.hidden {{
      opacity: 0;
      pointer-events: none;
    }}
    .big-play-btn {{
      background: none;
      border: none;
      cursor: pointer;
      transition: transform 0.2s;
    }}
    .big-play-btn:hover {{
      transform: scale(1.1);
    }}
    .video-controls {{
      position: absolute;
      bottom: 0;
      left: 0;
      right: 0;
      padding: 12px 16px;
      display: flex;
      align-items: center;
      gap: 12px;
      background: linear-gradient(transparent, rgba(0,0,0,0.8));
    }}
    .play-btn, .mute-btn {{
      background: none;
      border: none;
      cursor: pointer;
      padding: 4px;
      opacity: 0.9;
      display: flex;
      align-items: center;
    }}
    .play-btn:hover, .mute-btn:hover {{ opacity: 1; }}

    .progress-bar {{
      flex: 1;
      height: 4px;
      background: rgba(255,255,255,0.2);
      border-radius: 2px;
      cursor: pointer;
      position: relative;
    }}
    .progress-fill {{
      height: 100%;
      background: var(--accent);
      border-radius: 2px;
      width: 0%;
      transition: width 0.1s linear;
    }}
    .time-display {{
      font-size: 0.7rem;
      color: rgba(255,255,255,0.7);
      font-variant-numeric: tabular-nums;
      white-space: nowrap;
    }}

    /* ── Reel Details ── */
    .reel-details {{
      padding: 20px;
      border-top: 1px solid var(--border);
    }}
    .reel-details h3 {{
      font-family: 'Playfair Display', serif;
      font-size: 0.9rem;
      font-weight: 700;
      color: var(--accent);
      text-transform: uppercase;
      letter-spacing: 2px;
      margin-bottom: 8px;
      margin-top: 16px;
    }}
    .reel-details h3:first-child {{ margin-top: 0; }}
    .narration-text {{
      font-size: 0.85rem;
      color: var(--text-secondary);
      line-height: 1.7;
    }}
    .scenes-list {{
      display: flex;
      flex-direction: column;
      gap: 6px;
    }}
    .scene {{
      font-size: 0.8rem;
      color: var(--text-secondary);
      padding: 6px 10px;
      background: rgba(255,255,255,0.03);
      border-radius: 6px;
      border-left: 2px solid var(--accent);
    }}
    .scene-num {{
      color: var(--accent);
      font-weight: 700;
      margin-right: 6px;
    }}

    footer {{
      text-align: center;
      padding: 40px 20px;
      color: var(--text-secondary);
      font-size: 0.8rem;
      border-top: 1px solid var(--border);
      margin-top: 40px;
    }}
    footer a {{ color: var(--accent); text-decoration: none; }}

    @media (max-width: 540px) {{
      .reels-container {{ padding: 0 10px; }}
      .hero h1 {{ font-size: 1.8rem; }}
    }}
  </style>
</head>
<body>

  <div class="hero">
    <div class="subtitle">Instagram Reels</div>
    <h1>The Rider's Gang</h1>
    <p>{count} Reel{"s" if count != 1 else ""} — Stories about riding culture, equestrian fashion, and motorcycle heritage</p>
  </div>

  <div class="reels-container">
    {reel_cards_html}
  </div>

  <footer>
    <p>The Rider's Gang &mdash; Reels Module</p>
    <p style="margin-top: 6px">Source: <a href="https://shsingla22.github.io/TheRidersGangContent/index.html#articles" target="_blank">TheRidersGangContent</a></p>
  </footer>

  <script>
    document.querySelectorAll('.reel-card').forEach(card => {{
      const video = card.querySelector('.reel-player');
      const playBtn = card.querySelector('.play-btn');
      const muteBtn = card.querySelector('.mute-btn');
      const overlay = card.querySelector('.video-overlay');
      const bigPlay = card.querySelector('.big-play-btn');
      const progressFill = card.querySelector('.progress-fill');
      const timeDisplay = card.querySelector('.time-display');
      const progressBar = card.querySelector('.progress-bar');

      if (!video || !playBtn) return;

      function fmt(s) {{
        const m = Math.floor(s / 60);
        const sec = Math.floor(s % 60);
        return m + ':' + (sec < 10 ? '0' : '') + sec;
      }}

      function togglePlay() {{
        if (video.paused) {{
          // Pause all other videos
          document.querySelectorAll('.reel-player').forEach(v => {{
            if (v !== video) v.pause();
          }});
          video.play().then(() => {{
            playBtn.querySelector('.icon-play').style.display = 'none';
            playBtn.querySelector('.icon-pause').style.display = 'block';
            overlay.classList.add('hidden');
          }}).catch(() => {{}});
        }} else {{
          video.pause();
          playBtn.querySelector('.icon-play').style.display = 'block';
          playBtn.querySelector('.icon-pause').style.display = 'none';
        }}
      }}

      bigPlay.addEventListener('click', (e) => {{ e.stopPropagation(); togglePlay(); }});
      playBtn.addEventListener('click', togglePlay);
      video.addEventListener('click', togglePlay);

      video.addEventListener('timeupdate', () => {{
        if (video.duration) {{
          const pct = (video.currentTime / video.duration) * 100;
          progressFill.style.width = pct + '%';
          timeDisplay.textContent = fmt(video.currentTime) + ' / ' + fmt(video.duration);
        }}
      }});

      video.addEventListener('pause', () => {{
        playBtn.querySelector('.icon-play').style.display = 'block';
        playBtn.querySelector('.icon-pause').style.display = 'none';
      }});

      video.addEventListener('play', () => {{
        playBtn.querySelector('.icon-play').style.display = 'none';
        playBtn.querySelector('.icon-pause').style.display = 'block';
        overlay.classList.add('hidden');
      }});

      progressBar.addEventListener('click', (e) => {{
        const rect = progressBar.getBoundingClientRect();
        const pct = (e.clientX - rect.left) / rect.width;
        video.currentTime = pct * video.duration;
      }});

      if (muteBtn) {{
        muteBtn.addEventListener('click', () => {{
          video.muted = !video.muted;
          muteBtn.querySelector('.icon-muted').style.display = video.muted ? 'block' : 'none';
          muteBtn.querySelector('.icon-unmuted').style.display = video.muted ? 'none' : 'block';
        }});
      }}
    }});
  </script>
</body>
</html>"""


def main():
    video_dir = os.path.join(os.path.dirname(__file__), "output", "videos")
    count = 1  # Generate for first reel only

    print(f"=== Generating Reels HTML ({count} reel) ===\n")

    cards = []
    for reel in REELS[:count]:
        slug = reel["slug"]
        webm_path = os.path.join(video_dir, f"{slug}.webm")
        if not os.path.exists(webm_path):
            print(f"  WARNING: {webm_path} not found, skipping")
            continue

        print(f"  Embedding: {slug}.webm ({os.path.getsize(webm_path)/1024/1024:.1f} MB)")
        webm_b64 = _encode_b64(webm_path)
        cards.append(build_reel_card(reel, webm_b64))

    html = generate_reels_html("\n".join(cards), len(cards))
    outpath = "reels_showcase.html"
    with open(outpath, "w", encoding="utf-8") as f:
        f.write(html)

    size_mb = os.path.getsize(outpath) / 1024 / 1024
    print(f"\nReels HTML saved to: {outpath} ({size_mb:.1f} MB)")


if __name__ == "__main__":
    main()
