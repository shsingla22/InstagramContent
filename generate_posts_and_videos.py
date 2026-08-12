#!/usr/bin/env python3
"""
Combined Pipeline — Posts + Short Videos

Runs both content modules together over the shared article data in
common/content_data.py:

    Module 1 (posts/)        → Instagram post images, captions,
                               posts_showcase.html
    Module 2 (short_videos/) → one short cinematic MP4 per article
                               in output/short_videos/

Usage:
    python3 generate_posts_and_videos.py                # both modules
    python3 generate_posts_and_videos.py --posts-only
    python3 generate_posts_and_videos.py --videos-only
    python3 generate_posts_and_videos.py --limit 3      # first 3 videos
"""

import argparse
import sys


def main():
    parser = argparse.ArgumentParser(
        description="Run the posts module and the short video module together"
    )
    parser.add_argument("--posts-only", action="store_true",
                        help="Only run the posts module")
    parser.add_argument("--videos-only", action="store_true",
                        help="Only run the short video module")
    parser.add_argument("--limit", type=int, default=None,
                        help="Only render the first N short videos")
    args = parser.parse_args()

    print("=" * 60)
    print("  THE RIDER'S GANG — Posts + Short Videos Pipeline")
    print("=" * 60)

    # ── Module 1: Instagram posts ──────────────────────────────
    if not args.videos_only:
        print("\n[Module 1] Instagram Posts\n" + "-" * 40)
        import generate_posts_html
        generate_posts_html.main()

    # ── Module 2: Short videos ─────────────────────────────────
    if not args.posts_only:
        print("\n[Module 2] Short Videos\n" + "-" * 40)
        from short_videos.generator import generate_all_short_videos
        manifest = generate_all_short_videos(limit=args.limit)
        if not manifest:
            print("ERROR: no short videos were rendered")
            sys.exit(1)

    print("\nPipeline complete.")


if __name__ == "__main__":
    main()
