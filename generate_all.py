#!/usr/bin/env python3
"""
Master Generation Script — The Rider's Gang Instagram Content

Orchestrates both the Posts module and the Videos module, then
generates the unified HTML showcase with embedded Reels.

Usage:
    python generate_all.py              # Generate everything
    python generate_all.py --posts-only # Skip video generation
    python generate_all.py --videos-only # Only generate videos
"""

import argparse
import os
import sys
import json

from common.content_data import get_all_articles
from posts.post_generator import generate_all_posts, export_posts_to_json, export_captions
from videos.video_generator import generate_all_videos
from generate_showcase import generate_html, load_video_manifest


def main():
    parser = argparse.ArgumentParser(description="Generate Instagram content for The Rider's Gang")
    parser.add_argument("--posts-only", action="store_true", help="Only generate posts, skip videos")
    parser.add_argument("--videos-only", action="store_true", help="Only generate videos, skip posts")
    parser.add_argument("--force-fallback", action="store_true", help="Force moviepy fallback for videos")
    args = parser.parse_args()

    print("=" * 60)
    print("  THE RIDER'S GANG — Instagram Content Generator")
    print("=" * 60)

    articles = get_all_articles()
    print(f"\nLoaded {len(articles)} articles from content database.\n")

    # ── Step 1: Generate Posts ─────────────────────────────────
    if not args.videos_only:
        print("─── STEP 1: Generating Instagram Posts ───")
        posts = generate_all_posts()
        print(f"  Created {len(posts)} posts.")
        export_posts_to_json(posts)
        print("  Exporting captions:")
        export_captions(posts)
        print()

    # ── Step 2: Generate Videos ────────────────────────────────
    video_map = {}
    if not args.posts_only:
        print("─── STEP 2: Generating Short Videos (Reels) ───")
        video_map = generate_all_videos(
            articles=articles,
            force_fallback=args.force_fallback,
        )
        generated = sum(1 for v in video_map.values() if v)
        print(f"\n  Videos generated: {generated}/{len(video_map)}")
        print()

    # ── Step 3: Build Showcase ─────────────────────────────────
    print("─── STEP 3: Building HTML Showcase ───")
    if args.videos_only:
        posts = generate_all_posts()
    if not video_map:
        video_map = load_video_manifest()

    html_content = generate_html(posts, video_map)
    with open("showcase.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("  Showcase saved: showcase.html")

    # ── Summary ────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("  GENERATION COMPLETE")
    print("=" * 60)
    print(f"  Posts:    {len(posts)}")
    print(f"  Videos:   {sum(1 for v in video_map.values() if v)}/{len(video_map)}")
    print(f"  Showcase: showcase.html")
    print(f"\n  Output files in: output/")
    print(f"  Open showcase.html in a browser to preview everything.")
    print("=" * 60)


if __name__ == "__main__":
    main()
