"""
Short Videos Module — The Rider's Gang

Module 2 of the Instagram content pipeline. Runs alongside the posts
module and produces one short cinematic video per article, derived
from the same post content (common/content_data.py).

The look is deliberately retro / old money: real photographs, warm
film grade, slow Ken Burns camera moves, serif typography, and a
vinyl-crackle music bed.
"""

# Output location for rendered short videos
SHORT_VIDEOS_DIR = "output/short_videos"

# Render settings
FRAME_WIDTH = 1080
FRAME_HEIGHT = 1920          # 9:16 portrait for Instagram
FPS = 24                     # filmic frame rate

# Source photos are fetched oversized so the Ken Burns crop window
# always has room to move without upscaling artifacts
SOURCE_WIDTH = 1440
SOURCE_HEIGHT = 2560

# Crossfade length between scenes (seconds)
CROSSFADE_SEC = 0.6

# Old-money palette (matches the posts module's RETRO_STYLE)
PALETTE = {
    "espresso": (44, 24, 16),      # #2C1810 — deep brown shadows
    "gold": (212, 168, 67),        # #D4A843 — brand accent
    "cream": (245, 230, 200),      # #F5E6C8 — highlights / cards
    "ink": (26, 26, 46),           # #1A1A2E — night blue-black
}

# Serif fonts available on the render host
FONT_SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
FONT_SERIF_ITALIC = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
FONT_SERIF_REGULAR = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
