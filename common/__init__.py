"""
Common configuration for The Rider's Gang Instagram Content modules.
"""

# Base URL for all articles
BASE_URL = "https://shsingla22.github.io/TheRidersGangContent"

# Output directories
OUTPUT_DIR = "output"
CAPTIONS_DIR = f"{OUTPUT_DIR}/captions"
VIDEOS_DIR = f"{OUTPUT_DIR}/videos"
POSTS_JSON = f"{OUTPUT_DIR}/posts_data.json"
SHOWCASE_HTML = "showcase.html"

# Instagram post image dimensions
POST_IMAGE_WIDTH = 1080
POST_IMAGE_HEIGHT = 1080

# Video settings
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920  # 9:16 for Reels
VIDEO_FPS = 24
VIDEO_DURATION_SEC = 8  # Short reel duration

# Aesthetic settings
RETRO_STYLE = {
    "color_palette": ["#2C1810", "#8B6914", "#D4A843", "#F5E6C8", "#1A1A2E"],
    "font_style": "serif",
    "vignette_intensity": 0.4,
    "grain_intensity": 0.08,
    "warmth_shift": 15,
}
