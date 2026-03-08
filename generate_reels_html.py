"""
Module 2: Generate reels-only HTML showcase with embedded video.

Produces a self-contained HTML file displaying Instagram Reels with
the video embedded as base64 data URIs (WebM + MP4 for cross-browser
support). Uses native browser <video controls> for maximum compatibility.
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


def build_reel_card(reel: dict, webm_b64: str | None, mp4_b64: str | None) -> str:
    """Build HTML for a single reel card with embedded video."""
    title = html_mod.escape(reel["title"].replace("\n", " "))
    subtitle = html_mod.escape(reel["subtitle"].replace("\n", " "))
    hook = html_mod.escape(reel["hook"])
    accent = reel["color_accent"]
    narration = html_mod.escape(reel["narration"])
    scenes_html = ""
    for i, scene in enumerate(reel["scenes"]):
        scenes_html += f'<div class="scene"><span class="scene-num">{i+1}</span> {html_mod.escape(scene["text"].replace(chr(10), " "))}</div>\n'

    # Build <source> elements — WebM first (smaller), MP4 fallback (Safari)
    sources = ""
    if webm_b64:
        sources += f'          <source src="data:video/webm;base64,{webm_b64}" type="video/webm">\n'
    if mp4_b64:
        sources += f'          <source src="data:video/mp4;base64,{mp4_b64}" type="video/mp4">\n'

    return f"""
    <div class="reel-card">
      <div class="reel-info">
        <div class="reel-badge" style="background:{accent}">REEL</div>
        <h2 class="reel-title">{title}</h2>
        <p class="reel-subtitle">{subtitle}</p>
        <p class="reel-hook" style="color:{accent}">{hook}</p>
      </div>

      <div class="video-container">
        <video class="reel-player" controls playsinline preload="auto"
               poster="" style="width:100%; background:#000;">
{sources}          <p style="color:red; padding:20px;">Your browser does not support video playback.
             Try opening this file in Chrome, Firefox, or Safari.</p>
        </video>
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

    /* ── Video ── */
    .video-container {{
      width: 100%;
      background: #000;
    }}
    .reel-player {{
      display: block;
      width: 100%;
      max-height: 80vh;
      background: #000;
    }}
    /* Style the native controls on dark background */
    .reel-player::-webkit-media-controls-panel {{
      background: linear-gradient(transparent, rgba(0,0,0,0.7));
    }}

    .video-error {{
      display: none;
      padding: 20px;
      text-align: center;
      color: #ff6b6b;
      font-weight: 600;
      background: rgba(255,0,0,0.1);
      border: 1px solid rgba(255,0,0,0.3);
      border-radius: 8px;
      margin: 10px 20px;
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
    <p>{count} Reel{"s" if count != 1 else ""} &mdash; Stories about riding culture, equestrian fashion, and motorcycle heritage</p>
  </div>

  <div class="reels-container">
    {reel_cards_html}
  </div>

  <footer>
    <p>The Rider's Gang &mdash; Reels Module</p>
    <p style="margin-top: 6px">Source: <a href="https://shsingla22.github.io/TheRidersGangContent/index.html#articles" target="_blank">TheRidersGangContent</a></p>
  </footer>

  <script>
    // Show error messages if video fails to load
    document.querySelectorAll('.reel-player').forEach(video => {{
      video.addEventListener('error', function(e) {{
        const errDiv = this.closest('.reel-card').querySelector('.video-error');
        if (errDiv) {{
          const src = this.querySelector('source');
          const err = this.error;
          errDiv.textContent = 'Video failed to load. Error: ' +
            (err ? 'code=' + err.code + ' ' + (err.message || '') : 'unknown') +
            '. Try Chrome or Firefox.';
          errDiv.style.display = 'block';
        }}
      }});

      // Also listen on source elements
      this.querySelectorAll && video.querySelectorAll('source').forEach(src => {{
        src.addEventListener('error', function() {{
          console.log('Source failed:', this.type);
        }});
      }});
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

        # Find WebM
        webm_path = os.path.join(video_dir, f"{slug}.webm")
        webm_b64 = None
        if os.path.exists(webm_path):
            size = os.path.getsize(webm_path) / 1024 / 1024
            print(f"  Embedding WebM: {slug}.webm ({size:.1f} MB)")
            webm_b64 = _encode_b64(webm_path)
        else:
            print(f"  WARNING: {slug}.webm not found")

        # Find MP4
        mp4_path = os.path.join(video_dir, f"{slug}.mp4")
        mp4_b64 = None
        if os.path.exists(mp4_path):
            size = os.path.getsize(mp4_path) / 1024 / 1024
            print(f"  Embedding MP4:  {slug}.mp4 ({size:.1f} MB)")
            mp4_b64 = _encode_b64(mp4_path)
        else:
            print(f"  WARNING: {slug}.mp4 not found")

        if not webm_b64 and not mp4_b64:
            print(f"  SKIPPING: no video files found for {slug}")
            continue

        cards.append(build_reel_card(reel, webm_b64, mp4_b64))

    html = generate_reels_html("\n".join(cards), len(cards))
    outpath = "reels_showcase.html"
    with open(outpath, "w", encoding="utf-8") as f:
        f.write(html)

    size_mb = os.path.getsize(outpath) / 1024 / 1024
    print(f"\nReels HTML saved to: {outpath} ({size_mb:.1f} MB)")


if __name__ == "__main__":
    main()
