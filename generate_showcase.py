"""
Generate an HTML showcase page displaying all Instagram posts.

Reads from the content module and produces a polished, responsive HTML file
that previews each Instagram post as it would appear on the platform.
"""

import html
from instagram_content import generate_all_posts, export_posts_to_json, export_captions, InstagramPost
from typing import List


def build_post_card(post: InstagramPost, index: int) -> str:
    """Build a single Instagram post card HTML."""
    hashtag_html = " ".join(
        f'<span class="hashtag">{html.escape(tag)}</span>' for tag in post.hashtags[:15]
    )
    remaining = len(post.hashtags) - 15
    if remaining > 0:
        hashtag_html += f' <span class="hashtag-more">+{remaining} more</span>'

    additional_imgs = ""
    for img_url in post.additional_images:
        additional_imgs += f'<img src="{html.escape(img_url)}" alt="Additional image" loading="lazy">\n'

    return f"""
    <article class="post-card" id="post-{index}">
      <div class="post-header">
        <div class="post-avatar">TRG</div>
        <div class="post-meta">
          <span class="post-username">theridergang</span>
          <span class="post-category">{html.escape(post.category)}</span>
        </div>
        <span class="post-number">#{index}</span>
      </div>

      <div class="post-image-carousel">
        <img src="{html.escape(post.image_url)}" alt="{html.escape(post.article_title)}" loading="lazy" class="main-image">
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

        <h2 class="post-title">{html.escape(post.post_title)}</h2>
        <p class="post-description"><strong>theridergang</strong> {html.escape(post.description)}</p>
        <blockquote class="post-quote">"{html.escape(post.quote)}"</blockquote>
        <p class="post-cta">{html.escape(post.call_to_action)}</p>

        <div class="post-hashtags">{hashtag_html}</div>

        <div class="post-link">
          <a href="{html.escape(post.article_url)}" target="_blank" rel="noopener">
            Read Full Article &rarr;
          </a>
          <span class="read-time">{html.escape(post.read_time)} read</span>
        </div>
      </div>
    </article>
    """


def generate_html(posts: List[InstagramPost]) -> str:
    """Generate the complete HTML showcase page."""
    post_cards = "\n".join(build_post_card(post, i + 1) for i, post in enumerate(posts))

    nav_items = "\n".join(
        f'<a href="#post-{i+1}" class="nav-item">'
        f'<span class="nav-num">{i+1}</span>'
        f'<span class="nav-title">{html.escape(post.post_title[:30])}{"..." if len(post.post_title) > 30 else ""}</span>'
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
    :root {{
      --bg: #fafafa;
      --card-bg: #ffffff;
      --text: #262626;
      --text-secondary: #8e8e8e;
      --border: #dbdbdb;
      --accent: #e1306c;
      --accent-gradient: linear-gradient(45deg, #f09433, #e6683c, #dc2743, #cc2366, #bc1888);
      --blue: #0095f6;
      --shadow: 0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.12);
      --shadow-hover: 0 4px 12px rgba(0,0,0,0.12), 0 2px 4px rgba(0,0,0,0.08);
      --radius: 12px;
    }}

    * {{ margin: 0; padding: 0; box-sizing: border-box; }}

    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.6;
    }}

    /* Hero Section */
    .hero {{
      background: var(--accent-gradient);
      color: white;
      text-align: center;
      padding: 60px 20px;
      position: relative;
      overflow: hidden;
    }}
    .hero::before {{
      content: '';
      position: absolute;
      top: 0; left: 0; right: 0; bottom: 0;
      background: rgba(0,0,0,0.2);
    }}
    .hero-content {{
      position: relative;
      z-index: 1;
      max-width: 700px;
      margin: 0 auto;
    }}
    .hero h1 {{
      font-size: 2.5rem;
      font-weight: 800;
      margin-bottom: 12px;
      letter-spacing: -0.5px;
    }}
    .hero p {{
      font-size: 1.15rem;
      opacity: 0.9;
    }}
    .hero .stats {{
      display: flex;
      justify-content: center;
      gap: 40px;
      margin-top: 30px;
    }}
    .hero .stat {{
      text-align: center;
    }}
    .hero .stat-num {{
      font-size: 2rem;
      font-weight: 800;
      display: block;
    }}
    .hero .stat-label {{
      font-size: 0.85rem;
      text-transform: uppercase;
      letter-spacing: 1px;
      opacity: 0.8;
    }}

    /* Navigation */
    .post-nav {{
      background: var(--card-bg);
      border-bottom: 1px solid var(--border);
      padding: 16px 20px;
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
      padding: 8px 14px;
      border-radius: 20px;
      background: var(--bg);
      border: 1px solid var(--border);
      text-decoration: none;
      color: var(--text);
      font-size: 0.82rem;
      font-weight: 500;
      transition: all 0.2s;
      flex-shrink: 0;
    }}
    .nav-item:hover {{
      background: var(--accent);
      color: white;
      border-color: var(--accent);
    }}
    .nav-num {{
      background: var(--accent);
      color: white;
      width: 22px;
      height: 22px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 0.7rem;
      font-weight: 700;
    }}
    .nav-item:hover .nav-num {{
      background: white;
      color: var(--accent);
    }}

    /* Posts Grid */
    .posts-container {{
      max-width: 1200px;
      margin: 30px auto;
      padding: 0 20px;
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
      gap: 30px;
    }}

    /* Post Card */
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
      transform: translateY(-2px);
    }}

    .post-header {{
      display: flex;
      align-items: center;
      padding: 14px 16px;
      border-bottom: 1px solid var(--border);
    }}
    .post-avatar {{
      width: 36px;
      height: 36px;
      border-radius: 50%;
      background: var(--accent-gradient);
      color: white;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 0.7rem;
      font-weight: 800;
      margin-right: 10px;
    }}
    .post-meta {{
      flex: 1;
    }}
    .post-username {{
      font-weight: 600;
      font-size: 0.9rem;
      display: block;
    }}
    .post-category {{
      font-size: 0.75rem;
      color: var(--text-secondary);
    }}
    .post-number {{
      font-size: 0.8rem;
      color: var(--text-secondary);
      font-weight: 600;
    }}

    .post-image-carousel {{
      position: relative;
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
      height: 100px;
      object-fit: cover;
    }}

    .post-content {{
      padding: 16px;
    }}

    .post-actions {{
      display: flex;
      justify-content: space-between;
      margin-bottom: 12px;
    }}
    .action-left {{
      display: flex;
      gap: 16px;
    }}
    .icon {{
      width: 24px;
      height: 24px;
      fill: none;
      stroke: var(--text);
      stroke-width: 2;
      stroke-linecap: round;
      stroke-linejoin: round;
      cursor: pointer;
      transition: transform 0.2s;
    }}
    .icon:hover {{
      transform: scale(1.15);
    }}

    .post-title {{
      font-size: 1.15rem;
      font-weight: 700;
      margin-bottom: 8px;
      line-height: 1.3;
    }}
    .post-description {{
      font-size: 0.9rem;
      color: var(--text);
      margin-bottom: 12px;
      line-height: 1.55;
    }}
    .post-quote {{
      font-style: italic;
      color: var(--text-secondary);
      border-left: 3px solid var(--accent);
      padding: 8px 14px;
      margin: 12px 0;
      font-size: 0.88rem;
      background: #fef7f9;
      border-radius: 0 6px 6px 0;
    }}
    .post-cta {{
      font-size: 0.85rem;
      color: var(--blue);
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
      font-size: 0.78rem;
      color: var(--blue);
      background: #e8f4fd;
      padding: 3px 8px;
      border-radius: 4px;
      font-weight: 500;
    }}
    .hashtag-more {{
      font-size: 0.78rem;
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
      font-size: 0.88rem;
      transition: opacity 0.2s;
    }}
    .post-link a:hover {{
      opacity: 0.8;
    }}
    .read-time {{
      font-size: 0.8rem;
      color: var(--text-secondary);
    }}

    /* Footer */
    footer {{
      text-align: center;
      padding: 40px 20px;
      color: var(--text-secondary);
      font-size: 0.85rem;
      border-top: 1px solid var(--border);
      margin-top: 40px;
    }}
    footer a {{
      color: var(--accent);
      text-decoration: none;
    }}

    /* Copy button */
    .copy-btn {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: var(--bg);
      border: 1px solid var(--border);
      padding: 6px 12px;
      border-radius: 6px;
      cursor: pointer;
      font-size: 0.8rem;
      color: var(--text);
      transition: all 0.2s;
      margin-top: 10px;
    }}
    .copy-btn:hover {{
      background: var(--accent);
      color: white;
      border-color: var(--accent);
    }}
    .copy-btn.copied {{
      background: #22c55e;
      color: white;
      border-color: #22c55e;
    }}

    @media (max-width: 600px) {{
      .posts-container {{
        grid-template-columns: 1fr;
        padding: 0 10px;
      }}
      .hero h1 {{ font-size: 1.8rem; }}
      .hero .stats {{ gap: 20px; }}
    }}
  </style>
</head>
<body>

  <div class="hero">
    <div class="hero-content">
      <h1>The Rider's Gang</h1>
      <p>Instagram Content Showcase — 10 posts crafted from articles about riding culture, fashion heritage, and motorcycle adventures</p>
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
    <p>Generated by <strong>The Rider's Gang Instagram Content Module</strong></p>
    <p>Source: <a href="https://shsingla22.github.io/TheRidersGangContent/index.html#articles" target="_blank">TheRidersGangContent</a></p>
  </footer>

  <script>
    // Copy caption to clipboard
    document.querySelectorAll('.copy-btn').forEach(btn => {{
      btn.addEventListener('click', () => {{
        const caption = btn.getAttribute('data-caption');
        navigator.clipboard.writeText(caption).then(() => {{
          btn.classList.add('copied');
          btn.textContent = 'Copied!';
          setTimeout(() => {{
            btn.classList.remove('copied');
            btn.textContent = 'Copy Caption';
          }}, 2000);
        }});
      }});
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
    print("=== Generating Instagram Content Showcase ===\n")

    posts = generate_all_posts()
    print(f"Loaded {len(posts)} posts.\n")

    # Export JSON
    export_posts_to_json(posts)

    # Export captions
    print("Exporting caption files:")
    export_captions(posts)

    # Generate HTML
    html_content = generate_html(posts)
    output_file = "showcase.html"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"\nHTML showcase saved to: {output_file}")
    print("Open it in a browser to preview all Instagram posts!")


if __name__ == "__main__":
    main()
