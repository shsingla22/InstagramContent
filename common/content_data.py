"""
Shared content data for all modules.

This is the single source of truth for article data used by both
the posts module and the videos module.
"""

from dataclasses import dataclass, field
from typing import List

from common import BASE_URL


@dataclass
class ArticleData:
    """Raw article data shared across modules."""
    slug: str
    title: str
    category: str
    read_time: str
    hero_image: str
    additional_images: List[str]
    key_quote: str
    summary: str
    visual_keywords: List[str] = field(default_factory=list)
    era: str = ""


def get_all_articles() -> List[ArticleData]:
    """Return all article data as the single source of truth."""
    return [
        ArticleData(
            slug="the-cafe-racer-how-coffee-gave-birth-to-motorcycle-culture",
            title="The Café Racer: How Coffee Gave Birth to Motorcycle Culture",
            category="Motorcycle Culture",
            read_time="5 min",
            hero_image="https://images.unsplash.com/photo-1558981359-219d6364c9c8?w=1080&h=1080&fit=crop",
            additional_images=[
                "https://images.unsplash.com/photo-1558981806-ec527fa84c39?w=1080&h=1080&fit=crop",
                "https://images.unsplash.com/photo-1568708167256-1f385e6485f5?w=1080&h=1080&fit=crop",
            ],
            key_quote="You'd hear the jukebox start...and suddenly the car park was empty. Everyone was on the North Circular, flat out.",
            summary=(
                "In 1950s London, young rebels raced between coffee shops at 100 mph on stripped-down motorcycles. "
                "They called it 'doing the ton' — racing to a roundabout and back before a jukebox song ended. "
                "These daredevils became the Ton-Up Boys, and their DIY ethos birthed the café racer movement "
                "that still defines motorcycle culture today."
            ),
            visual_keywords=["vintage motorcycle", "1950s London cafe", "leather jacket rider", "neon cafe sign at night", "chrome motorcycle engine"],
            era="1950s",
        ),
        ArticleData(
            slug="the-saddlebag-from-horse-leather-to-high-fashion",
            title="The Saddlebag: From Horse Leather to High Fashion",
            category="Riding Fashion",
            read_time="5 min",
            hero_image="https://images.unsplash.com/photo-1473188588951-666fce8e7c68?w=1080&h=1080&fit=crop",
            additional_images=[
                "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=1080&h=1080&fit=crop",
                "https://images.unsplash.com/photo-1590874103328-eac38a683ce7?w=1080&h=1080&fit=crop",
            ],
            key_quote="Hermès didn't become a luxury brand by accident. They simply pointed their skills at a different customer.",
            summary=(
                "Every luxury handbag traces its ancestry to a leather pouch strapped to a horse. "
                "From Persian cavalry warriors to medieval couriers, from American cowboys with tooled leather "
                "to Hermès transforming saddle carriers into the Kelly and Birkin bags — the saddlebag's journey "
                "is fashion's greatest origin story."
            ),
            visual_keywords=["leather saddlebag on horse", "luxury handbag close-up", "artisan leather workshop", "vintage equestrian equipment", "Paris fashion boutique"],
            era="Ancient to Modern",
        ),
        ArticleData(
            slug="the-polo-shirt-from-horseback-to-high-street",
            title="The Polo Shirt: From Horseback to High Street",
            category="Riding Fashion",
            read_time="5 min",
            hero_image="https://images.unsplash.com/photo-1550126417-c0c9e38eba50?w=1080&h=1080&fit=crop",
            additional_images=[
                "https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=1080&h=1080&fit=crop",
                "https://images.unsplash.com/photo-1564859228273-274232fdb516?w=1080&h=1080&fit=crop",
            ],
            key_quote="The polo shirt signals both old-money privilege and working-class rebellion, conformity and independence.",
            summary=(
                "A sport played on horseback in 1850s India gave the world its most versatile garment. "
                "Victorian polo players hated their stiff collars, so tennis legend René Lacoste engineered the fix. "
                "Ralph Lauren turned it into a billion-dollar lifestyle symbol. Today, 2 BILLION polo shirts sell every year."
            ),
            visual_keywords=["polo match horseback", "vintage polo shirt display", "Ralph Lauren store", "1920s tennis court", "polo player galloping"],
            era="1850s-Present",
        ),
        ArticleData(
            slug="denim-and-the-rider-how-jeans-were-born-in-the-saddle",
            title="Denim and the Rider: How Jeans Were Born in the Saddle",
            category="Riding Fashion",
            read_time="5 min",
            hero_image="https://images.unsplash.com/photo-1542272604-787c3835535d?w=1080&h=1080&fit=crop",
            additional_images=[
                "https://images.unsplash.com/photo-1582552938357-32b906df40cb?w=1080&h=1080&fit=crop",
                "https://images.unsplash.com/photo-1565084888279-aca607ecce0c?w=1080&h=1080&fit=crop",
            ],
            key_quote="The cowboy didn't choose denim. Denim chose the cowboy — because nothing else could survive the life he lived.",
            summary=(
                "In 1873, a tailor added copper rivets to stop cowboys' pockets from tearing on horseback — "
                "and accidentally invented the most iconic garment in history. Denim survived 14-hour saddle days, "
                "hid trail dirt with indigo dye, and resisted desert thorns."
            ),
            visual_keywords=["vintage denim jeans detail", "cowboy on horseback desert", "copper rivets close-up", "1950s James Dean style", "western rodeo rider"],
            era="1873-Present",
        ),
        ArticleData(
            slug="the-riding-crop-from-horse-command-to-fashion-icon",
            title="The Riding Crop: From Horse Command to Fashion Icon",
            category="Equestrian Heritage",
            read_time="5 min",
            hero_image="https://images.unsplash.com/photo-1598974357801-cbca100e65d3?w=1080&h=1080&fit=crop",
            additional_images=[
                "https://images.unsplash.com/photo-1553284965-83fd3e82fa5a?w=1080&h=1080&fit=crop",
                "https://images.unsplash.com/photo-1566251037378-5e04e3bec343?w=1080&h=1080&fit=crop",
            ],
            key_quote="The crop is not about force. It's about conversation — a language between rider and horse refined over millennia.",
            summary=(
                "For 2,000 years, a short leather instrument has connected rider to horse. "
                "Roman cavalry soldiers used leather flagella for battlefield communication. "
                "Today's dressage riders use crops as precise extensions of their leg aids. "
                "London's Swaine Adeney has been handcrafting them since 1750."
            ),
            visual_keywords=["leather riding crop detail", "dressage horse and rider", "Roman cavalry illustration", "English countryside riding", "artisan leather braiding"],
            era="Ancient Rome-Present",
        ),
        ArticleData(
            slug="hermes-from-horse-harnesses-to-high-fashion",
            title="Hermès: From Horse Harnesses to High Fashion",
            category="Equestrian Heritage",
            read_time="5 min",
            hero_image="https://images.unsplash.com/photo-1553284965-83fd3e82fa5a?w=1080&h=1080&fit=crop",
            additional_images=[
                "https://images.unsplash.com/photo-1598974357801-cbca100e65d3?w=1080&h=1080&fit=crop",
                "https://images.unsplash.com/photo-1566251037378-5e04e3bec343?w=1080&h=1080&fit=crop",
            ],
            key_quote="The horse is the heart of Hermès. It lives in every stitch, every buckle, every piece of leather we touch.",
            summary=(
                "In 1837, Thierry Hermès opened a Paris workshop making horse harnesses. "
                "When automobiles replaced horses, his family turned their legendary leather skills toward handbags. "
                "The Kelly bag takes 18-24 hours of hand-stitching. The Birkin, 48 hours. "
                "Today Hermès is worth over $200 billion."
            ),
            visual_keywords=["Hermès leather workshop", "vintage horse harness", "Paris luxury boutique", "hand-stitching leather close-up", "elegant equestrian equipment"],
            era="1837-Present",
        ),
        ArticleData(
            slug="belstaff-the-jacket-that-built-a-riding-legend",
            title="Belstaff: The Jacket That Built a Riding Legend",
            category="Motorcycle Culture",
            read_time="5 min",
            hero_image="https://images.unsplash.com/photo-1558981806-ec527fa84c39?w=1080&h=1080&fit=crop",
            additional_images=[
                "https://images.unsplash.com/photo-1568708167256-1f385e6485f5?w=1080&h=1080&fit=crop",
                "https://images.unsplash.com/photo-1585640120759-e47f0048cbf3?w=1080&h=1080&fit=crop",
            ],
            key_quote="Belstaff jackets have been worn on every great motorcycle journey of the twentieth century.",
            summary=(
                "In 1924, Harry Grosberg coated Egyptian cotton with wax and created the ultimate motorcycle jacket. "
                "Che Guevara wore one across South America. Steve McQueen got muddy in one at the 1964 International "
                "Six Days Trial. 100 years later, Belstaff still makes them the same way."
            ),
            visual_keywords=["waxed cotton jacket detail", "vintage motorcycle adventure", "Steve McQueen riding", "English countryside motorcycle", "rugged adventure gear"],
            era="1924-Present",
        ),
        ArticleData(
            slug="the-gucci-horsebit-loafer-born-in-the-saddle",
            title="The Gucci Horsebit Loafer: Born in the Saddle",
            category="Riding Fashion",
            read_time="5 min",
            hero_image="https://images.unsplash.com/photo-1615979474401-8a6a344de5bd?w=1080&h=1080&fit=crop",
            additional_images=[
                "https://images.unsplash.com/photo-1576792741377-eb0f4f6d1a47?w=1080&h=1080&fit=crop",
                "https://images.unsplash.com/photo-1655664994589-c18d906f7ed4?w=1080&h=1080&fit=crop",
            ],
            key_quote="The snaffle bit was made to help a rider talk to a horse. That it became a fashion icon is one of the great surprises of the twentieth century.",
            summary=(
                "In 1953, Aldo Gucci took a snaffle bit — the metal device riders use to communicate with horses — "
                "miniaturized it in gold-toned metal, and placed it on a black calfskin loafer. "
                "In 1985, the Met Museum acquired one for its permanent collection — the ONLY shoe ever given that honor."
            ),
            visual_keywords=["gold horsebit loafer detail", "Italian leather craftsman", "1950s Manhattan street", "horse snaffle bit close-up", "luxury shoe display"],
            era="1953-Present",
        ),
        ArticleData(
            slug="riding-boots-from-cavalry-to-catwalk",
            title="Riding Boots: From Cavalry to Catwalk",
            category="Boots & Shoes",
            read_time="5 min",
            hero_image="https://images.unsplash.com/photo-1722109283665-05e8a7db546e?w=1080&h=1080&fit=crop",
            additional_images=[
                "https://images.unsplash.com/photo-1551107696-a4b0c5a0d9a2?w=1080&h=1080&fit=crop",
                "https://images.unsplash.com/photo-1598974357801-cbca100e65d3?w=1080&h=1080&fit=crop",
            ],
            key_quote="The riding boot didn't become fashionable because designers chose it. It became fashionable because its design was already perfect.",
            summary=(
                "Every detail of riding boots serves a purpose: tall shaft protects from saddle rub, smooth sole slides "
                "into stirrups, angled heel prevents slipping. The Duke of Wellington redesigned them in 1817. "
                "Indian royalty created the jodhpur boot. Today, search interest is up 260%."
            ),
            visual_keywords=["tall leather riding boots", "cavalry charge painting", "fashion runway boots", "boot craftsmanship detail", "equestrian field boots"],
            era="1500s-Present",
        ),
        ArticleData(
            slug="leh-ladakh-the-ride-that-changes-everything",
            title="Leh-Ladakh: The Ride That Changes Everything",
            category="Motorcycle Lifestyle",
            read_time="6 min",
            hero_image="https://images.unsplash.com/photo-1670644654521-6fbfffeaba87?w=1080&h=1080&fit=crop",
            additional_images=[
                "https://images.unsplash.com/photo-1609766856923-7e0a7a3084e4?w=1080&h=1080&fit=crop",
                "https://images.unsplash.com/photo-1591378603223-e15b45a81640?w=1080&h=1080&fit=crop",
            ],
            key_quote="You don't ride because it's easy. You ride because it's the hardest thing you've done — and because the mountains don't care who you are.",
            summary=(
                "Khardung La at 5,359 metres. Oxygen-thin air. Roads that disappear into rivers. "
                "The Leh-Ladakh motorcycle journey isn't a vacation — it's a pilgrimage. Riders on Royal Enfields "
                "cross multiple Himalayan passes through landscapes that look like another planet."
            ),
            visual_keywords=["Himalayan mountain pass motorcycle", "Khardung La sign", "Royal Enfield on mountain road", "Ladakh monastery landscape", "high altitude desert road"],
            era="Modern",
        ),
    ]


def get_article_url(article: ArticleData) -> str:
    """Get the full URL for an article."""
    return f"{BASE_URL}/articles/{article.slug}.html"
