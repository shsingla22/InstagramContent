"""
Instagram Post Generator

Reads shared article data from common/ and produces Instagram-ready posts
with titles, descriptions, hashtags, images, and calls-to-action.
"""

import json
import os
from dataclasses import dataclass, asdict
from typing import List

from common.content_data import ArticleData, get_all_articles, get_article_url


@dataclass
class InstagramPost:
    """Represents a single Instagram post generated from an article."""
    article_title: str
    post_title: str
    description: str
    call_to_action: str
    article_url: str
    image_url: str
    additional_images: List[str]
    hashtags: List[str]
    category: str
    read_time: str
    quote: str
    video_path: str = ""


# ── Post content per article (keyed by slug) ──────────────────────────

POST_CONTENT = {
    "the-cafe-racer-how-coffee-gave-birth-to-motorcycle-culture": {
        "post_title": "Coffee + Speed = A Whole Culture",
        "description": (
            "In 1950s London, young rebels raced between coffee shops at 100 mph on stripped-down motorcycles. "
            "They called it 'doing the ton' — racing to a roundabout and back before a jukebox song ended. "
            "These daredevils became the Ton-Up Boys, and their DIY ethos birthed the café racer movement "
            "that still defines motorcycle culture today. From the legendary Ace Café on the North Circular "
            "to modern Triumph and Ducati models — every café racer owes its soul to a cup of coffee and "
            "a 3-minute rock 'n' roll song."
        ),
        "call_to_action": "Link in bio to read the full story of how coffee fueled a revolution on two wheels!",
        "hashtags": [
            "#CafeRacer", "#MotorcycleCulture", "#TonUpBoys", "#AceCafe",
            "#VintageMotorcycle", "#BikerLife", "#CafeRacerStyle", "#RidersGang",
            "#MotorcycleHistory", "#ClassicBikes", "#CafeRacerDreams",
            "#TwoWheels", "#RideOrDie", "#MotorcycleLifestyle", "#BikerCulture",
            "#RetroMoto", "#CafeRacerOfInstagram", "#MotorcycleLove",
            "#RockAndRide", "#BornToRide", "#TheRidersGang",
            "#MotorcycleHeritage", "#RidingCulture", "#BikerGang",
            "#CustomMotorcycle", "#StreetRacer", "#VintageBikes",
            "#MotorcyclePassion", "#CoffeeAndBikes", "#LiveToRide",
        ],
    },
    "the-saddlebag-from-horse-leather-to-high-fashion": {
        "post_title": "5,000 Years of the Perfect Bag",
        "description": (
            "Every luxury handbag traces its ancestry to a leather pouch strapped to a horse. "
            "From Persian cavalry warriors to medieval couriers, from American cowboys with tooled leather "
            "to Hermès transforming saddle carriers into the Kelly and Birkin bags — the saddlebag's journey "
            "is fashion's greatest origin story. When Galliano designed the Dior Saddle Bag in 1999, he wasn't "
            "inventing anything new. He was paying tribute to 5,000 years of riders who needed their essentials "
            "close at hand."
        ),
        "call_to_action": "Swipe through the evolution of riding gear to runway icon. Full story link in bio!",
        "hashtags": [
            "#Saddlebag", "#LuxuryFashion", "#Hermes", "#DiorSaddleBag",
            "#EquestrianStyle", "#LeatherCraft", "#FashionHistory",
            "#HorseRiding", "#DesignerBags", "#BirkinBag", "#KellyBag",
            "#RidingFashion", "#FashionHeritage", "#LuxuryLeather",
            "#EquestrianHeritage", "#CowboyStyle", "#WesternFashion",
            "#TheRidersGang", "#HandbagHistory", "#FashionOrigins",
            "#TimelessDesign", "#LeatherGoods", "#SaddleStitched",
            "#HorseCulture", "#VintageBags", "#FashionEvolution",
            "#RidersGang", "#FromSaddleToRunway", "#DesignerHeritage",
            "#ClassicLeather",
        ],
    },
    "the-polo-shirt-from-horseback-to-high-street": {
        "post_title": "The Shirt That Conquered the World — On Horseback",
        "description": (
            "A sport played on horseback in 1850s India gave the world its most versatile garment. "
            "Victorian polo players hated their stiff collars flapping in the wind, so tennis legend "
            "René Lacoste engineered the fix — a soft-collared, breathable shirt that debuted at the "
            "1926 US Open. Ralph Lauren turned it into a billion-dollar lifestyle symbol. Fred Perry's "
            "version fueled British subcultures. Today, 2 BILLION polo shirts sell every year. "
            "From ancient Persian cavalry training to your wardrobe — all because a rider needed "
            "a better collar."
        ),
        "call_to_action": "The full story of fashion's most democratic garment is in the link in bio!",
        "hashtags": [
            "#PoloShirt", "#RalphLauren", "#Lacoste", "#FredPerry",
            "#PoloSport", "#EquestrianFashion", "#FashionHistory",
            "#PrepStyle", "#ClassicFashion", "#PoloStyle",
            "#Menswear", "#Womenswear", "#StreetStyle", "#SportsFashion",
            "#HorsebackRiding", "#TheRidersGang", "#RidersGang",
            "#PoloLife", "#FashionEvolution", "#IconicFashion",
            "#TimelessStyle", "#BrandHistory", "#FashionOrigins",
            "#StyleInspo", "#OOTD", "#FashionFacts",
            "#DesignerFashion", "#ClassicMenswear", "#PoloRalphLauren",
            "#FashionCulture",
        ],
    },
    "denim-and-the-rider-how-jeans-were-born-in-the-saddle": {
        "post_title": "Born in the Saddle: The Real Origin of Your Jeans",
        "description": (
            "In 1873, a tailor added copper rivets to stop cowboys' pockets from tearing on horseback — "
            "and accidentally invented the most iconic garment in history. Denim survived 14-hour saddle days, "
            "hid trail dirt with indigo dye, and resisted desert thorns. Wrangler engineered the 'Cowboy Cut' "
            "specifically for rodeo riders. Then James Dean and Marlon Brando made jeans cool forever. "
            "Your favourite pair still carries those original copper rivets — a 150-year-old rider's innovation."
        ),
        "call_to_action": "Read the incredible journey from saddle to streetwear — link in bio!",
        "hashtags": [
            "#Denim", "#JeansHistory", "#LeviStrauss", "#Wrangler",
            "#CowboyStyle", "#WesternWear", "#DenimLove", "#JeansCulture",
            "#VintageDenim", "#RawDenim", "#DenimOnDenim",
            "#CowboyCulture", "#RodeoStyle", "#AmericanWest",
            "#FashionHistory", "#TheRidersGang", "#RidersGang",
            "#DenimHead", "#SelvedgeDenim", "#JamesDean",
            "#RebelStyle", "#WorkwearStyle", "#HeritageClothing",
            "#DenimDaily", "#JeansLover", "#FashionHeritage",
            "#IconicFashion", "#RiderStyle", "#BornInTheSaddle",
            "#CopperRivets",
        ],
    },
    "the-riding-crop-from-horse-command-to-fashion-icon": {
        "post_title": "2,000 Years of Precision: The Riding Crop Story",
        "description": (
            "For 2,000 years, a short leather instrument has connected rider to horse. "
            "Roman cavalry soldiers used leather flagella for battlefield communication. "
            "Today's dressage riders use crops as precise extensions of their leg aids — "
            "not force, but conversation. London's Swaine Adeney has been handcrafting them "
            "since 1750, with layered gut shafts and braided leather passed through generations. "
            "From ancient warfare to modern runways, the riding crop has never lost its power."
        ),
        "call_to_action": "Discover the fascinating 2,000-year journey — full article link in bio!",
        "hashtags": [
            "#RidingCrop", "#Equestrian", "#HorseRiding", "#Dressage",
            "#EquestrianLife", "#HorseLove", "#EquestrianStyle",
            "#ShowJumping", "#HorsebackRiding", "#EquestrianFashion",
            "#HorseCulture", "#EquestrianHeritage", "#RidingLife",
            "#HorseWorld", "#TheRidersGang", "#RidersGang",
            "#EquestrianHistory", "#RidingTradition", "#ClassicRiding",
            "#HorsemanShip", "#SwaineAdeney", "#BritishCraftsmanship",
            "#LeatherCraft", "#FashionIcon", "#TimelessDesign",
            "#HorseAndRider", "#EquestrianCommunity", "#RidingPassion",
            "#HorsebackLife", "#EquestrianWorld",
        ],
    },
    "hermes-from-horse-harnesses-to-high-fashion": {
        "post_title": "From Horse Harnesses to $200 Billion: The Hermès Story",
        "description": (
            "In 1837, Thierry Hermès opened a Paris workshop making horse harnesses. "
            "When automobiles replaced horses, his family didn't panic — they turned their "
            "legendary leather skills toward handbags. The Kelly bag? Originally a saddle carrier. "
            "Each one takes 18-24 hours of hand-stitching using the same saddle stitch technique "
            "from the original harnesses. The Birkin? 48 hours per piece. Some sell for $400,000+. "
            "Today Hermès is worth over $200 billion, but the horse remains at its heart."
        ),
        "call_to_action": "The full Hermès origin story is unlike anything you've read — link in bio!",
        "hashtags": [
            "#Hermes", "#HermèsParis", "#KellyBag", "#BirkinBag",
            "#LuxuryFashion", "#HighFashion", "#FashionHistory",
            "#EquestrianHeritage", "#ParisianLuxury", "#HandCrafted",
            "#LeatherCraft", "#SaddleStitch", "#DesignerBags",
            "#FashionIcon", "#LuxuryBrand", "#TheRidersGang", "#RidersGang",
            "#HermesHeritage", "#FrenchLuxury", "#Craftsmanship",
            "#TimelessElegance", "#LuxuryLeather", "#FashionLegacy",
            "#IconicBrands", "#HauteCouture", "#LuxuryLifestyle",
            "#DesignerFashion", "#FashionOrigins", "#HorseToHanabag",
            "#LegendaryBrands",
        ],
    },
    "belstaff-the-jacket-that-built-a-riding-legend": {
        "post_title": "The Jacket Worn on Every Great Motorcycle Journey",
        "description": (
            "In 1924, Harry Grosberg coated Egyptian cotton with wax and created the ultimate "
            "motorcycle jacket. The Trialmaster — built for grueling off-road competition — became "
            "the jacket of legends. Che Guevara wore one across South America. Steve McQueen got "
            "muddy in one at the 1964 International Six Days Trial. London's Ton-Up Boys made it "
            "the uniform of café racer culture. 100 years later, Belstaff still makes them the same way. "
            "Some legends never need updating."
        ),
        "call_to_action": "Read the century-long story of the world's greatest riding jacket — link in bio!",
        "hashtags": [
            "#Belstaff", "#MotorcycleJacket", "#WaxedCotton", "#Trialmaster",
            "#SteveMcQueen", "#MotorcycleCulture", "#BikerJacket",
            "#VintageMotorcycle", "#CafeRacer", "#RidingGear",
            "#BritishHeritage", "#MotorcycleLife", "#BikerStyle",
            "#ClassicMotorcycle", "#TheRidersGang", "#RidersGang",
            "#MotorcycleHeritage", "#RidingLegend", "#IconicJacket",
            "#MotorcycleFashion", "#WaxedJacket", "#BikerCulture",
            "#AdventureRiding", "#TonUpBoys", "#RidingHistory",
            "#MotorcycleGear", "#HeritageClothing", "#RiderLife",
            "#CenturyOfRiding", "#LegendaryGear",
        ],
    },
    "the-gucci-horsebit-loafer-born-in-the-saddle": {
        "post_title": "A Horse Bit on a Shoe Changed Fashion Forever",
        "description": (
            "In 1953, Aldo Gucci took a snaffle bit — the metal device riders use to communicate "
            "with horses — miniaturized it in gold-toned metal, and placed it on a black calfskin "
            "loafer. It became the shoe of presidents, movie stars, and Wall Street traders who "
            "called them 'deal sleds.' In 1985, the Met Museum acquired one for its permanent "
            "collection — the ONLY shoe ever given that honor. When Gucci nearly died in the '90s, "
            "Tom Ford brought it back and saved the brand."
        ),
        "call_to_action": "From horse riding to the Met Museum — read the incredible story. Link in bio!",
        "hashtags": [
            "#Gucci", "#GucciLoafer", "#HorsebitLoafer", "#LuxuryShoes",
            "#ItalianFashion", "#DesignerShoes", "#TomFord", "#GucciFashion",
            "#EquestrianStyle", "#FashionHistory", "#IconicDesign",
            "#LuxuryFootwear", "#ClassicStyle", "#WallStreetStyle",
            "#TheRidersGang", "#RidersGang", "#FashionHeritage",
            "#ShoesOfInstagram", "#DesignerFashion", "#ItalianLuxury",
            "#TimelessFashion", "#FashionIcon", "#GucciGang",
            "#LoaferStyle", "#SaddleToStreet", "#FashionLegend",
            "#LuxuryLife", "#ClassicShoes", "#BornInTheSaddle",
            "#HorsebitStyle",
        ],
    },
    "riding-boots-from-cavalry-to-catwalk": {
        "post_title": "500 Years on the Runway — and Still Going Strong",
        "description": (
            "Every design detail of riding boots serves a purpose: the tall shaft protects from "
            "saddle rub, the smooth sole slides into stirrups, the angled heel prevents slipping through. "
            "The Duke of Wellington redesigned them in 1817. Indian royalty created the jodhpur boot in "
            "Rajasthan. Italian craftsmen at De Niro hide a lucky penny in each pair. Today, search interest "
            "is up 260% and brands like Hermès, Chanel, and Ralph Lauren put them on every runway. "
            "Five centuries of proof that great design never goes out of style."
        ),
        "call_to_action": "From cavalry charges to fashion week — the full boot story awaits. Link in bio!",
        "hashtags": [
            "#RidingBoots", "#EquestrianFashion", "#BootsOfInstagram",
            "#CavalryBoots", "#FashionBoots", "#EquestrianStyle",
            "#HorseRiding", "#BootLove", "#WellingtonBoots",
            "#JodhpurBoots", "#Ariat", "#DeNiroBoots",
            "#ItalianCraftsmanship", "#TheRidersGang", "#RidersGang",
            "#RunwayFashion", "#FashionWeek", "#BootSeason",
            "#EquestrianLife", "#ClassicBoots", "#FashionHistory",
            "#TimelessStyle", "#HorseLover", "#RidingStyle",
            "#CatwalkFashion", "#DesignerBoots", "#BootGoals",
            "#FashionHeritage", "#CavalryToCatwalk", "#BootCulture",
        ],
    },
    "leh-ladakh-the-ride-that-changes-everything": {
        "post_title": "18,000 Feet. Zero Oxygen. One Life-Changing Ride.",
        "description": (
            "Khardung La at 5,359 metres. Oxygen-thin air. Roads that disappear into rivers. "
            "The Leh-Ladakh motorcycle journey isn't a vacation — it's a pilgrimage. Riders on "
            "Royal Enfields cross multiple Himalayan passes through landscapes that look like another "
            "planet. India's motorcycle heritage runs deep — Royal Enfield has been made there since 1955, "
            "serving the military, postal service, and now millions of adventure seekers. The Bikerni women's "
            "riding group with 2,500 members proves this journey belongs to everyone."
        ),
        "call_to_action": "Ready to understand why riders say Ladakh changes your life? Full story — link in bio!",
        "hashtags": [
            "#LehLadakh", "#Ladakh", "#RoyalEnfield", "#HimalayanRide",
            "#MotorcycleTravel", "#AdventureRiding", "#KhardungLa",
            "#IndiaRide", "#BikerTravel", "#MotorcycleAdventure",
            "#Himalaya", "#MountainRide", "#RoadTrip", "#MotorcycleTrip",
            "#TheRidersGang", "#RidersGang", "#ManaliToLeh",
            "#BulletRide", "#RoyalEnfieldIndia", "#Bikerni",
            "#WomenRiders", "#AdventureMotorcycle", "#EpicRide",
            "#TravelIndia", "#IncredibleIndia", "#BikerLife",
            "#MotoTravel", "#LifeChangingRide", "#RideTheHimalayas",
            "#TwoWheelTravel",
        ],
    },
}


def generate_all_posts() -> List[InstagramPost]:
    """Generate Instagram posts for all articles using shared data."""
    articles = get_all_articles()
    posts = []
    for article in articles:
        content = POST_CONTENT[article.slug]
        post = InstagramPost(
            article_title=article.title,
            post_title=content["post_title"],
            description=content["description"],
            call_to_action=content["call_to_action"],
            article_url=get_article_url(article),
            image_url=article.hero_image,
            additional_images=article.additional_images,
            hashtags=content["hashtags"],
            category=article.category,
            read_time=article.read_time,
            quote=article.key_quote,
        )
        posts.append(post)
    return posts


def export_posts_to_json(posts: List[InstagramPost], output_path: str = "output/posts_data.json"):
    """Export all posts to a JSON file."""
    data = [asdict(post) for post in posts]
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"  Exported {len(data)} posts to {output_path}")
    return data


def export_captions(posts: List[InstagramPost], output_dir: str = "output/captions"):
    """Export individual caption text files for each post."""
    os.makedirs(output_dir, exist_ok=True)
    for i, post in enumerate(posts, 1):
        filename = f"post_{i:02d}.txt"
        filepath = os.path.join(output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(format_post_caption(post))
        print(f"  Caption saved: {filepath}")


def format_post_caption(post: InstagramPost) -> str:
    """Format a single post as Instagram-ready caption text."""
    lines = [
        post.post_title,
        "",
        post.description,
        "",
        f'"{post.quote}"',
        "",
        post.call_to_action,
        "",
        " ".join(post.hashtags),
    ]
    return "\n".join(lines)
