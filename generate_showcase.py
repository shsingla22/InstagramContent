"""
Generate an HTML showcase page displaying all Instagram posts WITH embedded videos.

Reads post data and video paths, producing a polished responsive HTML file
that previews each Instagram post with its embedded short video Reel.
"""

import html as html_mod
import json
import os
from typing import List, Dict

from posts.post_generator import InstagramPost


def build_post_card(post: InstagramPost, index: int, video_path: str = "") -> str:
    """Build a single Instagram post card HTML with optional embedded video."""
    hashtag_html = " ".join(
        f'<span class="hashtag">{html_mod.escape(tag)}</span>' for tag in post.hashtags[:15]
    )
    remaining = len(post.hashtags) - 15
    if remaining > 0:
        hashtag_html += f' <span class="hashtag-more">+{remaining} more</span>'

    additional_imgs = ""
    for img_url in post.additional_images:
        additional_imgs += f'<img src="{html_mod.escape(img_url)}" alt="Additional image" loading="lazy">\n'

    # Video section — embedded if video exists
    if video_path and os.path.exists(video_path):
        video_section = f"""
        <div class="post-video">
          <div class="video-badge">
            <svg viewBox="0 0 24 24" width="14" height="14" fill="white"><polygon points="5 3 19 12 5 21 5 3"/></svg>
            REEL
          </div>
          <video class="reel-player" loop muted playsinline preload="auto" poster="{html_mod.escape(post.image_url)}">
            <source src="{html_mod.escape(video_path.replace('.mp4', '.webm'))}" type="video/webm">
            <source src="{html_mod.escape(video_path)}" type="video/mp4">
          </video>
          <div class="video-controls">
            <button class="play-btn" aria-label="Play video">
              <svg viewBox="0 0 24 24" width="40" height="40"><circle cx="12" cy="12" r="11" fill="rgba(0,0,0,0.5)" stroke="white" stroke-width="1.5"/><polygon points="10 8 17 12 10 16" fill="white"/></svg>
            </button>
            <button class="mute-btn" aria-label="Toggle sound">
              <svg class="muted-icon" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="white" stroke-width="2"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><line x1="23" y1="9" x2="17" y2="15"/><line x1="17" y1="9" x2="23" y2="15"/></svg>
              <svg class="unmuted-icon" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="white" stroke-width="2" style="display:none"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"/><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"/></svg>
            </button>
          </div>
        </div>
        """
    else:
        video_section = f"""
        <div class="post-video post-video-placeholder">
          <img src="{html_mod.escape(post.image_url)}" alt="{html_mod.escape(post.article_title)}" loading="lazy" class="placeholder-img">
          <div class="video-badge">
            <svg viewBox="0 0 24 24" width="14" height="14" fill="white"><polygon points="5 3 19 12 5 21 5 3"/></svg>
            REEL
          </div>
          <div class="video-pending-label">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
            Video generating...
          </div>
        </div>
        """

    return f"""
    <article class="post-card" id="post-{index}">
      <div class="post-header">
        <div class="post-avatar">TRG</div>
        <div class="post-meta">
          <span class="post-username">theridergang</span>
          <span class="post-category">{html_mod.escape(post.category)}</span>
        </div>
        <span class="post-number">#{index}</span>
      </div>

      {video_section}

      <div class="post-image-carousel">
        <img src="{html_mod.escape(post.image_url)}" alt="{html_mod.escape(post.article_title)}" loading="lazy" class="main-image">
        <div class="additional-images">
          {additional_imgs}
        </div>
      </div>

      <div class="post-content">
        <div class="post-actions">
          <div class="action-left">
            <svg class="icon" viewBox="0 0 24 24"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>
            <svg class="icon" viewBox="0 0 24 24"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
            <svg class="icon" viewBox="0 0 24 24"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
          </div>
          <svg class="icon" viewBox="0 0 24 24"><path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/></svg>
        </div>

        <h2 class="post-title">{html_mod.escape(post.post_title)}</h2>
        <p class="post-description"><strong>theridergang</strong> {html_mod.escape(post.description)}</p>
        <blockquote class="post-quote">"{html_mod.escape(post.quote)}"</blockquote>
        <p class="post-cta">{html_mod.escape(post.call_to_action)}</p>

        <div class="post-hashtags">{hashtag_html}</div>

        <div class="post-link">
          <a href="{html_mod.escape(post.article_url)}" target="_blank" rel="noopener">
            Read Full Article &rarr;
          </a>
          <span class="read-time">{html_mod.escape(post.read_time)} read</span>
        </div>
      </div>
    </article>
    """


def load_video_manifest(manifest_path: str = "output/videos/video_manifest.json") -> Dict[str, str]:
    """Load the video manifest mapping slugs to file paths."""
    if os.path.exists(manifest_path):
        with open(manifest_path) as f:
            return json.load(f)
    return {}


def generate_html(posts: List[InstagramPost], video_map: Dict[str, str] = None) -> str:
    """Generate the complete HTML showcase page with embedded videos."""
    if video_map is None:
        video_map = load_video_manifest()

    # Match posts to videos by extracting slug from article_url
    def get_slug(post):
        url = post.article_url
        name = url.split("/")[-1]
        if name.endswith(".html"):
            name = name[:-5]
        return name

    post_cards = "\n".join(
        build_post_card(post, i + 1, video_map.get(get_slug(post), ""))
        for i, post in enumerate(posts)
    )

    video_count = sum(1 for post in posts if video_map.get(get_slug(post), ""))

    nav_items = "\n".join(
        f'<a href="#post-{i+1}" class="nav-item">'
        f'<span class="nav-num">{i+1}</span>'
        f'<span class="nav-title">{html_mod.escape(post.post_title[:30])}{"..." if len(post.post_title) > 30 else ""}</span>'
        f'</a>'
        for i, post in enumerate(posts)
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>The Rider's Gang — Instagram Content Showcase</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=Inter:wght@400;500;600;700&display=swap');

    :root {{
      --bg: #f5f0eb;
      --card-bg: #ffffff;
      --text: #1a1a1a;
      --text-secondary: #6b6259;
      --border: #d4c9bc;
      --accent: #8B6914;
      --accent-dark: #2C1810;
      --accent-light: #D4A843;
      --gold: #C9A84C;
      --cream: #F5E6C8;
      --accent-gradient: linear-gradient(135deg, #2C1810, #8B6914, #D4A843);
      --blue: #5C4A2E;
      --shadow: 0 2px 8px rgba(44,24,16,0.08), 0 1px 3px rgba(44,24,16,0.06);
      --shadow-hover: 0 8px 24px rgba(44,24,16,0.12), 0 2px 8px rgba(44,24,16,0.08);
      --radius: 8px;
    }}

    * {{ margin: 0; padding: 0; box-sizing: border-box; }}

    body {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.6;
    }}

    /* ── Hero Section ──────────────────────────────── */
    .hero {{
      background: var(--accent-gradient);
      color: var(--cream);
      text-align: center;
      padding: 70px 20px 60px;
      position: relative;
      overflow: hidden;
    }}
    .hero::before {{
      content: '';
      position: absolute;
      top: 0; left: 0; right: 0; bottom: 0;
      background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.03'%3E%3Cpath d='m36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
      opacity: 0.5;
    }}
    .hero-content {{
      position: relative;
      z-index: 1;
      max-width: 750px;
      margin: 0 auto;
    }}
    .hero h1 {{
      font-family: 'Playfair Display', Georgia, serif;
      font-size: 3rem;
      font-weight: 900;
      margin-bottom: 10px;
      letter-spacing: 2px;
      text-transform: uppercase;
    }}
    .hero .subtitle {{
      font-size: 1rem;
      letter-spacing: 4px;
      text-transform: uppercase;
      opacity: 0.7;
      margin-bottom: 8px;
    }}
    .hero p {{
      font-size: 1.05rem;
      opacity: 0.85;
      max-width: 600px;
      margin: 0 auto;
    }}
    .hero .stats {{
      display: flex;
      justify-content: center;
      gap: 50px;
      margin-top: 35px;
    }}
    .hero .stat {{ text-align: center; }}
    .hero .stat-num {{
      font-family: 'Playfair Display', serif;
      font-size: 2.2rem;
      font-weight: 900;
      display: block;
      color: var(--gold);
    }}
    .hero .stat-label {{
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 2px;
      opacity: 0.7;
    }}
    .hero .divider {{
      width: 60px;
      height: 2px;
      background: var(--gold);
      margin: 20px auto;
    }}

    /* ── Navigation ────────────────────────────────── */
    .post-nav {{
      background: var(--card-bg);
      border-bottom: 1px solid var(--border);
      padding: 14px 20px;
      position: sticky;
      top: 0;
      z-index: 100;
      overflow-x: auto;
      white-space: nowrap;
      display: flex;
      gap: 8px;
      scrollbar-width: thin;
    }}
    .nav-item {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 7px 14px;
      border-radius: 4px;
      background: var(--bg);
      border: 1px solid var(--border);
      text-decoration: none;
      color: var(--text);
      font-size: 0.8rem;
      font-weight: 500;
      transition: all 0.2s;
      flex-shrink: 0;
    }}
    .nav-item:hover {{
      background: var(--accent-dark);
      color: var(--cream);
      border-color: var(--accent-dark);
    }}
    .nav-num {{
      background: var(--accent);
      color: white;
      width: 20px;
      height: 20px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 0.65rem;
      font-weight: 700;
    }}
    .nav-item:hover .nav-num {{
      background: var(--gold);
      color: var(--accent-dark);
    }}

    /* ── Posts Grid ─────────────────────────────────── */
    .posts-container {{
      max-width: 1300px;
      margin: 35px auto;
      padding: 0 20px;
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
      gap: 30px;
    }}

    /* ── Post Card ─────────────────────────────────── */
    .post-card {{
      background: var(--card-bg);
      border-radius: var(--radius);
      border: 1px solid var(--border);
      overflow: hidden;
      box-shadow: var(--shadow);
      transition: box-shadow 0.3s, transform 0.3s;
      scroll-margin-top: 80px;
    }}
    .post-card:hover {{
      box-shadow: var(--shadow-hover);
      transform: translateY(-3px);
    }}

    .post-header {{
      display: flex;
      align-items: center;
      padding: 12px 16px;
      border-bottom: 1px solid var(--border);
      background: linear-gradient(to right, rgba(44,24,16,0.03), transparent);
    }}
    .post-avatar {{
      width: 36px;
      height: 36px;
      border-radius: 50%;
      background: var(--accent-gradient);
      color: var(--cream);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 0.65rem;
      font-weight: 800;
      margin-right: 10px;
      letter-spacing: 0.5px;
    }}
    .post-meta {{ flex: 1; }}
    .post-username {{
      font-weight: 600;
      font-size: 0.88rem;
      display: block;
      color: var(--accent-dark);
    }}
    .post-category {{
      font-size: 0.72rem;
      color: var(--text-secondary);
      text-transform: uppercase;
      letter-spacing: 1px;
    }}
    .post-number {{
      font-family: 'Playfair Display', serif;
      font-size: 1rem;
      color: var(--accent-light);
      font-weight: 700;
    }}

    /* ── Video Section ─────────────────────────────── */
    .post-video {{
      position: relative;
      width: 100%;
      aspect-ratio: 9/16;
      max-height: 500px;
      background: #0a0806;
      overflow: hidden;
    }}
    .reel-player {{
      width: 100%;
      height: 100%;
      object-fit: cover;
      cursor: pointer;
    }}
    .placeholder-img {{
      width: 100%;
      height: 100%;
      object-fit: cover;
      filter: brightness(0.4) sepia(0.3);
    }}
    .video-badge {{
      position: absolute;
      top: 12px;
      right: 12px;
      background: rgba(44,24,16,0.8);
      backdrop-filter: blur(4px);
      color: var(--gold);
      padding: 4px 10px;
      border-radius: 4px;
      font-size: 0.7rem;
      font-weight: 700;
      letter-spacing: 2px;
      display: flex;
      align-items: center;
      gap: 5px;
      z-index: 2;
    }}
    .video-controls {{
      position: absolute;
      bottom: 0;
      left: 0;
      right: 0;
      padding: 16px;
      display: flex;
      justify-content: center;
      align-items: center;
      gap: 16px;
      background: linear-gradient(transparent, rgba(0,0,0,0.6));
      z-index: 2;
    }}
    .play-btn, .mute-btn {{
      background: none;
      border: none;
      cursor: pointer;
      padding: 4px;
      opacity: 0.9;
      transition: opacity 0.2s, transform 0.2s;
    }}
    .play-btn:hover, .mute-btn:hover {{
      opacity: 1;
      transform: scale(1.1);
    }}
    .mute-btn {{
      position: absolute;
      bottom: 16px;
      right: 16px;
    }}
    .video-pending-label {{
      position: absolute;
      bottom: 50%;
      left: 50%;
      transform: translate(-50%, 50%);
      color: var(--gold);
      font-size: 0.85rem;
      font-weight: 500;
      display: flex;
      align-items: center;
      gap: 8px;
      background: rgba(44,24,16,0.7);
      padding: 10px 20px;
      border-radius: 6px;
      backdrop-filter: blur(4px);
      z-index: 2;
    }}

    /* ── Image Carousel ────────────────────────────── */
    .post-image-carousel {{
      position: relative;
      border-top: 1px solid var(--border);
    }}
    .post-image-carousel .main-image {{
      width: 100%;
      aspect-ratio: 1;
      object-fit: cover;
      display: block;
    }}
    .additional-images {{
      display: flex;
      gap: 2px;
      background: var(--border);
    }}
    .additional-images img {{
      flex: 1;
      height: 90px;
      object-fit: cover;
    }}

    /* ── Post Content ──────────────────────────────── */
    .post-content {{ padding: 16px; }}

    .post-actions {{
      display: flex;
      justify-content: space-between;
      margin-bottom: 12px;
    }}
    .action-left {{ display: flex; gap: 16px; }}
    .icon {{
      width: 22px;
      height: 22px;
      fill: none;
      stroke: var(--text);
      stroke-width: 2;
      stroke-linecap: round;
      stroke-linejoin: round;
      cursor: pointer;
      transition: transform 0.2s;
    }}
    .icon:hover {{ transform: scale(1.15); }}

    .post-title {{
      font-family: 'Playfair Display', serif;
      font-size: 1.2rem;
      font-weight: 700;
      margin-bottom: 8px;
      line-height: 1.3;
      color: var(--accent-dark);
    }}
    .post-description {{
      font-size: 0.88rem;
      margin-bottom: 12px;
      line-height: 1.6;
    }}
    .post-quote {{
      font-family: 'Playfair Display', serif;
      font-style: italic;
      color: var(--accent-dark);
      border-left: 3px solid var(--gold);
      padding: 10px 16px;
      margin: 14px 0;
      font-size: 0.88rem;
      background: linear-gradient(to right, rgba(212,168,67,0.08), transparent);
      border-radius: 0 6px 6px 0;
    }}
    .post-cta {{
      font-size: 0.84rem;
      color: var(--accent);
      font-weight: 600;
      margin-bottom: 14px;
    }}
    .post-hashtags {{
      display: flex;
      flex-wrap: wrap;
      gap: 4px;
      margin-bottom: 14px;
    }}
    .hashtag {{
      font-size: 0.75rem;
      color: var(--accent);
      background: rgba(139,105,20,0.08);
      padding: 3px 8px;
      border-radius: 3px;
      font-weight: 500;
    }}
    .hashtag-more {{
      font-size: 0.75rem;
      color: var(--text-secondary);
      padding: 3px 8px;
    }}
    .post-link {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-top: 12px;
      border-top: 1px solid var(--border);
    }}
    .post-link a {{
      color: var(--accent);
      text-decoration: none;
      font-weight: 600;
      font-size: 0.85rem;
      transition: opacity 0.2s;
    }}
    .post-link a:hover {{ opacity: 0.7; }}
    .read-time {{
      font-size: 0.78rem;
      color: var(--text-secondary);
    }}

    /* ── Footer ────────────────────────────────────── */
    footer {{
      text-align: center;
      padding: 50px 20px;
      color: var(--text-secondary);
      font-size: 0.82rem;
      border-top: 1px solid var(--border);
      margin-top: 40px;
      background: linear-gradient(to bottom, transparent, rgba(44,24,16,0.03));
    }}
    footer a {{
      color: var(--accent);
      text-decoration: none;
    }}
    footer .footer-brand {{
      font-family: 'Playfair Display', serif;
      font-size: 1.1rem;
      font-weight: 700;
      color: var(--accent-dark);
      margin-bottom: 8px;
    }}

    @media (max-width: 600px) {{
      .posts-container {{
        grid-template-columns: 1fr;
        padding: 0 10px;
      }}
      .hero h1 {{ font-size: 2rem; }}
      .hero .stats {{ gap: 20px; }}
      .post-video {{ max-height: 400px; }}
    }}
  </style>
</head>
<body>

  <div class="hero">
    <div class="hero-content">
      <div class="subtitle">Est. 2026</div>
      <h1>The Rider's Gang</h1>
      <div class="divider"></div>
      <p>Instagram content showcase — posts and Reels crafted from stories about riding culture, equestrian fashion, and motorcycle heritage</p>
      <div class="stats">
        <div class="stat">
          <span class="stat-num">{len(posts)}</span>
          <span class="stat-label">Posts</span>
        </div>
        <div class="stat">
          <span class="stat-num">{video_count}</span>
          <span class="stat-label">Reels</span>
        </div>
        <div class="stat">
          <span class="stat-num">{sum(len(p.hashtags) for p in posts)}</span>
          <span class="stat-label">Hashtags</span>
        </div>
        <div class="stat">
          <span class="stat-num">{len(set(p.category for p in posts))}</span>
          <span class="stat-label">Categories</span>
        </div>
      </div>
    </div>
  </div>

  <nav class="post-nav">
    {nav_items}
  </nav>

  <main class="posts-container">
    {post_cards}
  </main>

  <footer>
    <p class="footer-brand">The Rider's Gang</p>
    <p>Instagram Content Module — Posts + Reels</p>
    <p style="margin-top: 6px">Source: <a href="https://shsingla22.github.io/TheRidersGangContent/index.html#articles" target="_blank">TheRidersGangContent</a></p>
  </footer>

  <script>
    // Video play/pause toggle
    document.querySelectorAll('.post-video').forEach(container => {{
      const video = container.querySelector('.reel-player');
      const playBtn = container.querySelector('.play-btn');
      const muteBtn = container.querySelector('.mute-btn');
      if (!video || !playBtn) return;

      const pauseIcon = '<svg viewBox="0 0 24 24" width="40" height="40"><circle cx="12" cy="12" r="11" fill="rgba(0,0,0,0.5)" stroke="white" stroke-width="1.5"/><rect x="8" y="7" width="3" height="10" rx="1" fill="white"/><rect x="13" y="7" width="3" height="10" rx="1" fill="white"/></svg>';
      const playIcon = '<svg viewBox="0 0 24 24" width="40" height="40"><circle cx="12" cy="12" r="11" fill="rgba(0,0,0,0.5)" stroke="white" stroke-width="1.5"/><polygon points="10 8 17 12 10 16" fill="white"/></svg>';

      playBtn.addEventListener('click', () => {{
        if (video.paused) {{
          // Pause all other videos first
          document.querySelectorAll('.reel-player').forEach(v => {{
            if (v !== video) v.pause();
          }});
          document.querySelectorAll('.play-btn').forEach(b => {{ b.innerHTML = playIcon; }});
          video.play().then(() => {{
            playBtn.innerHTML = pauseIcon;
          }}).catch(() => {{}});
        }} else {{
          video.pause();
          playBtn.innerHTML = playIcon;
        }}
      }});

      if (muteBtn) {{
        muteBtn.addEventListener('click', () => {{
          video.muted = !video.muted;
          muteBtn.querySelector('.muted-icon').style.display = video.muted ? 'block' : 'none';
          muteBtn.querySelector('.unmuted-icon').style.display = video.muted ? 'none' : 'block';
        }});
      }}

      video.addEventListener('click', () => playBtn.click());
    }});

    // Smooth scroll for nav
    document.querySelectorAll('.nav-item').forEach(item => {{
      item.addEventListener('click', (e) => {{
        e.preventDefault();
        const target = document.querySelector(item.getAttribute('href'));
        if (target) target.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
      }});
    }});
  </script>
</body>
</html>"""


def main():
    from posts.post_generator import generate_all_posts, export_posts_to_json, export_captions

    print("=== Generating Instagram Content Showcase ===\n")

    posts = generate_all_posts()
    print(f"Loaded {len(posts)} posts.")

    # Load video manifest
    video_map = load_video_manifest()
    if video_map:
        print(f"Loaded {sum(1 for v in video_map.values() if v)} video paths from manifest.")
    else:
        print("No video manifest found — showcase will show placeholders for Reels.")

    # Export data
    export_posts_to_json(posts)
    print("Exporting captions:")
    export_captions(posts)

    # Generate HTML
    html_content = generate_html(posts, video_map)
    with open("showcase.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"\nHTML showcase saved to: showcase.html")


if __name__ == "__main__":
    main()
