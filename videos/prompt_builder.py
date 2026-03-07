"""
Video Prompt Builder

Generates detailed text-to-video prompts from article data, tuned for
retro / old-money aesthetics that match The Rider's Gang brand.
"""

from common.content_data import ArticleData


# Style prefixes applied to every prompt for consistent branding
STYLE_PREFIX = (
    "Cinematic 4K short film, warm amber and sepia color grading, "
    "subtle film grain, shallow depth of field, golden hour lighting, "
    "old-money aesthetic, vintage elegance, smooth slow-motion camera movement"
)

STYLE_SUFFIX = (
    "No text overlays, no logos. Natural lighting, rich textures, "
    "muted earth tones with warm gold highlights. "
    "Shot on 35mm film, anamorphic lens flare, gentle vignette."
)


def build_video_prompt(article: ArticleData) -> str:
    """
    Build a detailed text-to-video prompt for a single article.

    Each prompt is hand-crafted per article to produce visually stunning,
    story-driven 8-second clips that feel premium and editorial.
    """
    prompts = {
        "the-cafe-racer-how-coffee-gave-birth-to-motorcycle-culture": (
            "A gleaming vintage café racer motorcycle parked outside a dimly lit 1950s London coffee shop at dusk. "
            "Rain-slicked cobblestone street reflecting warm neon light. Camera slowly dollies forward toward the "
            "chrome handlebars. A leather-gloved hand reaches into frame and grips the throttle. "
            "Steam rises from a coffee cup on the windowsill beside the bike. "
            "The headlight flickers on, casting a golden beam into the misty evening."
        ),
        "the-saddlebag-from-horse-leather-to-high-fashion": (
            "Close-up of an artisan's weathered hands stitching rich brown leather in a dimly lit Parisian workshop. "
            "Camera slowly pulls back to reveal a handcrafted leather saddlebag taking shape on a wooden workbench. "
            "Antique tools, brass buckles, and rolls of premium leather surround the craftsman. "
            "Golden afternoon light streams through a tall window, catching dust particles in the air. "
            "The camera glides to a finished luxury bag displayed on velvet."
        ),
        "the-polo-shirt-from-horseback-to-high-street": (
            "A polo player on a magnificent brown horse galloping across a manicured green field at golden hour. "
            "Camera follows in smooth tracking shot. The rider's white polo shirt catches the warm sunlight. "
            "Mallet swings in elegant slow motion, connecting with the ball. "
            "Cut to: the same style polo shirt draped over a mahogany chair in a wood-paneled gentlemen's club, "
            "a crystal glass of amber whiskey beside it. Afternoon light through venetian blinds."
        ),
        "denim-and-the-rider-how-jeans-were-born-in-the-saddle": (
            "Extreme close-up of copper rivets on vintage indigo denim, camera slowly pulling back. "
            "A cowboy on horseback silhouetted against a burning orange desert sunset, dust trailing behind. "
            "Camera sweeps low across sun-baked terrain. The rider's worn denim catches golden light. "
            "Horse and rider cross a shallow stream in slow motion, water droplets sparkling like diamonds. "
            "Wide shot of the vast American frontier at magic hour."
        ),
        "the-riding-crop-from-horse-command-to-fashion-icon": (
            "A braided leather riding crop resting on a polished mahogany table beside riding gloves. "
            "Camera slowly rotates around the object, revealing intricate leather detail. "
            "Cut to: a rider in formal dressage attire on a white horse in an English countryside arena. "
            "Soft morning mist. The rider's hand gently adjusts the crop. "
            "The horse responds with an elegant passage step, hooves in perfect slow-motion rhythm."
        ),
        "hermes-from-horse-harnesses-to-high-fashion": (
            "Inside a heritage leather workshop: warm lamplight on rows of leather hides and brass tools. "
            "Master craftsman's hands performing the famous Hermès saddle stitch — two needles, one thread, "
            "precise rhythm. Camera glides along a wall of antique wooden lasts and equestrian forms. "
            "Pull back to reveal the iconic orange Hermès box being carefully closed, "
            "tissue paper folded with ritual precision. A single perfect leather bag sits in golden light."
        ),
        "belstaff-the-jacket-that-built-a-riding-legend": (
            "A weathered waxed cotton Belstaff jacket hanging on a wooden peg in a rustic English garage. "
            "Vintage motorcycle visible in soft background. Camera slowly pushes in on the jacket's texture — "
            "every scratch and wax mark tells a story. A rider's hand lifts the jacket, shouldering it on. "
            "Cut to: motorcycle headlight igniting in a dark barn doorway. "
            "The rider rolls out into misty morning English countryside, gravel crunching beneath tyres."
        ),
        "the-gucci-horsebit-loafer-born-in-the-saddle": (
            "Extreme close-up of the iconic gold horsebit hardware on polished black calfskin leather. "
            "Camera slowly tilts up to reveal the classic Gucci loafer on a marble surface. "
            "Warm side lighting creates dramatic shadows. Cut to: a snaffle bit on a horse's bridle, "
            "the same double-ring shape gleaming in stable light. Horse breathes softly. "
            "Return to: the loafer placed on a velvet museum pedestal, bathed in gallery spotlighting."
        ),
        "riding-boots-from-cavalry-to-catwalk": (
            "Tall leather riding boots being polished by careful hands with a soft cloth. "
            "Camera captures the mirror-like shine developing on rich brown leather. "
            "Cut to: boots in stirrups, horse cantering through an autumn forest — golden leaves falling. "
            "Smooth tracking shot follows the rider's legs in elegant rhythm with the horse. "
            "Final shot: the same style boots on a fashion runway, model striding confidently, "
            "camera low angle, bokeh lights in background."
        ),
        "leh-ladakh-the-ride-that-changes-everything": (
            "Aerial drone shot: a lone Royal Enfield motorcycle winds along a narrow mountain road "
            "carved into the side of a Himalayan cliff at 18,000 feet. Vast barren landscape stretches "
            "to snow-capped peaks. Camera descends to rider level — wind-weathered face behind goggles, "
            "prayer flags fluttering on a mountain pass. "
            "The motorcycle crosses a shallow glacial stream, turquoise water sparkling in harsh altitude sunlight. "
            "Wide shot of the infinite road ahead, dissolving into clouds."
        ),
    }

    article_prompt = prompts.get(article.slug, f"Cinematic footage related to: {article.title}")
    return f"{STYLE_PREFIX}. {article_prompt} {STYLE_SUFFIX}"


def build_image_to_video_prompt(article: ArticleData) -> str:
    """
    Build a prompt for image-to-video generation (animating the hero image).
    Used as a complementary approach alongside text-to-video.
    """
    motion_prompts = {
        "the-cafe-racer-how-coffee-gave-birth-to-motorcycle-culture":
            "Slow zoom into the motorcycle, subtle engine vibration, steam rising from nearby, ambient cafe lighting flickers gently",
        "the-saddlebag-from-horse-leather-to-high-fashion":
            "Gentle camera orbit around the leather bag, light shifts slowly across the surface revealing texture and grain",
        "the-polo-shirt-from-horseback-to-high-street":
            "Horse and rider in gentle motion, mane flowing in breeze, grass swaying, warm golden light intensifies",
        "denim-and-the-rider-how-jeans-were-born-in-the-saddle":
            "Slow dolly forward on denim texture, dust particles float in sunlight, fabric creases shift subtly",
        "the-riding-crop-from-horse-command-to-fashion-icon":
            "Horse breathes gently, slow head turn, riding crop held steady, morning mist drifts across the arena",
        "hermes-from-horse-harnesses-to-high-fashion":
            "Camera slowly orbits the horse, leather tack catches shifting light, horse shifts weight gracefully",
        "belstaff-the-jacket-that-built-a-riding-legend":
            "Wind subtly moves the jacket fabric, motorcycle exhaust shimmer in background, moody atmospheric shift",
        "the-gucci-horsebit-loafer-born-in-the-saddle":
            "Slow rotation revealing gold horsebit detail, light reflections dance across polished leather surface",
        "riding-boots-from-cavalry-to-catwalk":
            "Camera glides upward along the boot shaft, leather catches warm light, subtle stable atmosphere in background",
        "leh-ladakh-the-ride-that-changes-everything":
            "Slow aerial drift over mountain landscape, prayer flags flutter in wind, clouds move across peaks",
    }

    motion = motion_prompts.get(article.slug, "Gentle camera movement, cinematic atmosphere")
    return f"{STYLE_PREFIX}. {motion}. {STYLE_SUFFIX}"
