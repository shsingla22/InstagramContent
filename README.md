# InstagramContent

Instagram content creation module for **The Rider's Gang** articles.

## What It Does

Generates Instagram-ready posts from articles published on [TheRidersGangContent](https://shsingla22.github.io/TheRidersGangContent/index.html#articles). Each article produces one Instagram post with:

- Catchy post title and engaging description
- High-quality images (main + additional carousel images)
- 30 optimized hashtags per post for maximum reach
- Memorable quote from the article
- Call-to-action directing followers to the full article
- Link to the original article

## Articles Covered (10 Posts)

| # | Article | Category |
|---|---------|----------|
| 1 | The Café Racer: How Coffee Gave Birth to Motorcycle Culture | Motorcycle Culture |
| 2 | The Saddlebag: From Horse Leather to High Fashion | Riding Fashion |
| 3 | The Polo Shirt: From Horseback to High Street | Riding Fashion |
| 4 | Denim and the Rider: How Jeans Were Born in the Saddle | Riding Fashion |
| 5 | The Riding Crop: From Horse Command to Fashion Icon | Equestrian Heritage |
| 6 | Hermès: From Horse Harnesses to High Fashion | Equestrian Heritage |
| 7 | Belstaff: The Jacket That Built a Riding Legend | Motorcycle Culture |
| 8 | The Gucci Horsebit Loafer: Born in the Saddle | Riding Fashion |
| 9 | Riding Boots: From Cavalry to Catwalk | Boots & Shoes |
| 10 | Leh-Ladakh: The Ride That Changes Everything | Motorcycle Lifestyle |

## Usage

```bash
# Generate all content (JSON, captions, and HTML showcase)
python generate_showcase.py

# Or just use the content module directly
python instagram_content.py
```

## Output Files

- `showcase.html` — Visual HTML showcase of all 10 posts (open in browser)
- `posts_data.json` — Structured JSON data for all posts
- `captions/post_XX.txt` — Ready-to-paste Instagram caption for each post

## Project Structure

```
InstagramContent/
├── instagram_content.py    # Core content generation module
├── generate_showcase.py    # HTML showcase generator
├── showcase.html           # Generated visual showcase
├── posts_data.json         # Generated JSON data
├── captions/               # Generated caption text files
│   ├── post_01.txt
│   ├── ...
│   └── post_10.txt
└── README.md
```
