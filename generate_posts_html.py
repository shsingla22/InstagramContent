"""
Module 1: Generate posts-only HTML showcase (no videos).

Produces a lightweight HTML file displaying all 10 Instagram posts
with images, captions, hashtags, and article links — no video embedding.
"""

import html as html_mod
import json
import os
from typing import List

from posts.post_generator import InstagramPost, generate_all_posts, export_posts_to_json, export_captions


def build_post_card(post: InstagramPost, index: int) -> str:
    """Build a single Instagram post card HTML (no video)."""
    hashtag_html = " ".join(
        f'<span class="hashtag">{html_mod.escape(tag)}</span>' for tag in post.hashtags[:15]
    )
    remaining = len(post.hashtags) - 15
    if remaining > 0:
        hashtag_html += f' <span class="hashtag-more">+{remaining} more</span>'

    additional_imgs = ""
    for img_url in post.additional_images:
        additional_imgs += f'<img src="{html_mod.escape(img_url)}" alt="Additional image" loading="lazy">\n'

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


def generate_posts_html(posts: List[InstagramPost]) -> str:
    """Generate the complete posts-only HTML page."""
    post_cards = "\n".join(build_post_card(post, i + 1) for i, post in enumerate(posts))

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
  <title>The Rider's Gang — Instagram Posts</title>
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

    .hero {{
      background: var(--accent-gradient);
      color: var(--cream);
      text-align: center;
      padding: 70px 20px 60px;
      position: relative;
      overflow: hidden;
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

    .post-nav {{
      display: flex;
      overflow-x: auto;
      gap: 0;
      padding: 0 20px;
      background: var(--card-bg);
      border-bottom: 1px solid var(--border);
      position: sticky;
      top: 0;
      z-index: 100;
    }}
    .nav-item {{
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 14px 18px;
      text-decoration: none;
      white-space: nowrap;
      border-bottom: 2px solid transparent;
      transition: all 0.2s;
      flex-shrink: 0;
    }}
    .nav-item:hover {{
      border-bottom-color: var(--accent-light);
      background: rgba(139,105,20,0.03);
    }}
    .nav-num {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 22px;
      height: 22px;
      border-radius: 50%;
      background: var(--accent-gradient);
      color: #fff;
      font-size: 0.7rem;
      font-weight: 700;
    }}
    .nav-title {{
      font-size: 0.78rem;
      color: var(--text-secondary);
      font-weight: 500;
    }}

    .posts-container {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
      gap: 30px;
      max-width: 1200px;
      margin: 40px auto;
      padding: 0 20px;
    }}
    .post-card {{
      background: var(--card-bg);
      border-radius: var(--radius);
      overflow: hidden;
      box-shadow: var(--shadow);
      transition: box-shadow 0.3s, transform 0.3s;
    }}
    .post-card:hover {{
      box-shadow: var(--shadow-hover);
      transform: translateY(-2px);
    }}
    .post-header {{
      display: flex;
      align-items: center;
      padding: 14px 16px;
      gap: 10px;
      border-bottom: 1px solid var(--border);
    }}
    .post-avatar {{
      width: 36px;
      height: 36px;
      border-radius: 50%;
      background: var(--accent-gradient);
      display: flex;
      align-items: center;
      justify-content: center;
      color: #fff;
      font-size: 0.65rem;
      font-weight: 800;
      letter-spacing: 1px;
    }}
    .post-username {{
      font-weight: 700;
      font-size: 0.88rem;
      display: block;
    }}
    .post-category {{
      font-size: 0.72rem;
      color: var(--text-secondary);
      text-transform: uppercase;
      letter-spacing: 1px;
    }}
    .post-number {{
      margin-left: auto;
      color: var(--accent-light);
      font-weight: 700;
    }}

    .post-image-carousel .main-image {{
      width: 100%;
      aspect-ratio: 1;
      object-fit: cover;
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
    }}
    .post-link a:hover {{ opacity: 0.7; }}
    .read-time {{
      font-size: 0.78rem;
      color: var(--text-secondary);
    }}

    footer {{
      text-align: center;
      padding: 50px 20px;
      color: var(--text-secondary);
      font-size: 0.82rem;
      border-top: 1px solid var(--border);
      margin-top: 40px;
    }}
    footer a {{ color: var(--accent); text-decoration: none; }}
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
    }}
  </style>
</head>
<body>

  <div class="hero">
    <div class="hero-content">
      <div class="subtitle">Est. 2026</div>
      <h1>The Rider's Gang</h1>
      <p>Instagram posts crafted from stories about riding culture, equestrian fashion, and motorcycle heritage</p>
      <div class="stats">
        <div class="stat">
          <span class="stat-num">{len(posts)}</span>
          <span class="stat-label">Posts</span>
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
    <p>Instagram Posts Module</p>
    <p style="margin-top: 6px">Source: <a href="https://shsingla22.github.io/TheRidersGangContent/index.html#articles" target="_blank">TheRidersGangContent</a></p>
  </footer>

  <script>
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
    print("=== Generating Instagram Posts Showcase ===\n")

    posts = generate_all_posts()
    print(f"Loaded {len(posts)} posts.")

    export_posts_to_json(posts)
    print("Exporting captions:")
    export_captions(posts)

    html_content = generate_posts_html(posts)
    with open("posts_showcase.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    size_kb = os.path.getsize("posts_showcase.html") / 1024
    print(f"\nPosts HTML saved to: posts_showcase.html ({size_kb:.0f} KB)")


if __name__ == "__main__":
    main()
