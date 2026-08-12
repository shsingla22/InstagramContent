# InstagramContent

Instagram content creation system for **The Rider's Gang** — generating posts and short video Reels from articles.

## Architecture

```
InstagramContent/
├── common/                     # Shared data layer (both modules use this)
│   ├── __init__.py             # Config: URLs, dimensions, video settings, aesthetic palette
│   └── content_data.py         # Single source of truth for all 10 articles
├── posts/                      # Instagram Posts module
│   ├── __init__.py
│   └── post_generator.py       # Generates post titles, descriptions, hashtags, CTAs
├── videos/                     # Instagram Reels module
│   ├── __init__.py
│   ├── prompt_builder.py       # Cinematic text-to-video prompts per article
│   └── video_generator.py      # Video generation (CogVideoX-5b or moviepy fallback)
├── output/                     # Generated content
│   ├── captions/               # Ready-to-paste Instagram caption files
│   ├── videos/                 # Generated .mp4 Reel videos
│   └── posts_data.json         # Structured JSON data for all posts
├── generate_all.py             # Master orchestrator script
├── generate_showcase.py        # HTML showcase builder (posts + embedded videos)
├── showcase.html               # Visual preview of all posts with Reels
└── requirements.txt            # Python dependencies
```

## Modules

### Posts Module (`posts/`)
Generates Instagram-ready posts from articles with:
- Catchy post title and engaging description
- 30 optimized hashtags per post for maximum reach
- Memorable quote from each article
- Call-to-action directing followers to the full article

### Videos Module (`videos/`)
Generates short Instagram Reel videos with:
- **Primary**: CogVideoX-5b (open-source text-to-video diffusion model via HuggingFace diffusers) — requires CUDA GPU
- **Fallback**: moviepy-based Ken Burns effect + vintage film grading — runs on any machine
- Retro/old-money aesthetic: warm sepia tones, film grain, serif typography, golden vignettes
- 8-second clips at 1080x1920 (9:16 vertical) with text overlays

### Common Module (`common/`)
Shared by both posts and videos:
- Article database (titles, images, quotes, visual keywords)
- Configuration (output paths, video dimensions, aesthetic palette)

## Articles Covered (10 Posts + 10 Reels)

| # | Article | Category |
|---|---------|----------|
| 1 | The Cafe Racer: How Coffee Gave Birth to Motorcycle Culture | Motorcycle Culture |
| 2 | The Saddlebag: From Horse Leather to High Fashion | Riding Fashion |
| 3 | The Polo Shirt: From Horseback to High Street | Riding Fashion |
| 4 | Denim and the Rider: How Jeans Were Born in the Saddle | Riding Fashion |
| 5 | The Riding Crop: From Horse Command to Fashion Icon | Equestrian Heritage |
| 6 | Hermes: From Horse Harnesses to High Fashion | Equestrian Heritage |
| 7 | Belstaff: The Jacket That Built a Riding Legend | Motorcycle Culture |
| 8 | The Gucci Horsebit Loafer: Born in the Saddle | Riding Fashion |
| 9 | Riding Boots: From Cavalry to Catwalk | Boots & Shoes |
| 10 | Leh-Ladakh: The Ride That Changes Everything | Motorcycle Lifestyle |

## Usage

```bash
# Install dependencies
pip install -r requirements.txt

# Generate everything (posts + videos + HTML showcase)
python generate_all.py

# Posts only (skip video generation)
python generate_all.py --posts-only

# Videos only
python generate_all.py --videos-only

# Force moviepy fallback (skip CogVideoX even if GPU available)
python generate_all.py --force-fallback
```

## Video Generation

The video module supports two backends:

| Backend | Requirements | Quality | Speed |
|---------|-------------|---------|-------|
| **CogVideoX-5b** | CUDA GPU, 24GB+ VRAM, `diffusers` | AI-generated cinematic scenes | ~2 min/video |
| **moviepy fallback** | CPU only, `moviepy` + `Pillow` | Ken Burns animation + vintage filters | ~1 min/video |

To enable CogVideoX-5b, uncomment the GPU dependencies in `requirements.txt` and install them.
