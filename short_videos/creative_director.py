"""
Creative Direction — written by Claude Fable 5.

Each article gets a hand-crafted scene script derived from its post
content (title, summary, key quote from common/content_data.py).
The scripts control what the camera does, what the viewer reads,
and the emotional pacing — the renderer just executes them.

Scene fields:
    image     - which article photo to use: "hero", "alt1", "alt2",
                or "outro" (generated brand card)
    move      - Ken Burns camera move:
                zoom_in | zoom_out | pan_left | pan_right | drift_up
    duration  - seconds on screen (before crossfade overlap)
    kind      - "title" | "beat" | "quote" | "outro" (typography style)
    eyebrow   - small caps line above the main text (optional)
    text      - the main line(s) the viewer reads
    footnote  - small line under the main text (optional)

Mood picks the music bed: "midnight" (minor, moto grit) or
"heritage" (major, equestrian warmth).
"""

SHORT_VIDEO_SCRIPTS = {
    "the-cafe-racer-how-coffee-gave-birth-to-motorcycle-culture": {
        "mood": "midnight",
        "scenes": [
            {"image": "hero", "move": "zoom_in", "duration": 4.0, "kind": "title",
             "eyebrow": "THE RIDER'S GANG • EST. 1950s",
             "text": "THE CAFÉ RACER",
             "footnote": "How coffee gave birth to motorcycle culture"},
            {"image": "alt1", "move": "pan_right", "duration": 4.0, "kind": "beat",
             "eyebrow": "LONDON, 1950s",
             "text": "A jukebox drops a record.\nThe car park empties."},
            {"image": "alt2", "move": "zoom_out", "duration": 4.0, "kind": "beat",
             "eyebrow": "DOING THE TON",
             "text": "100 mph to the roundabout\nand back — before the song ends."},
            {"image": "hero", "move": "drift_up", "duration": 4.5, "kind": "quote",
             "text": "“You'd hear the jukebox start… and suddenly\nthe car park was empty. Everyone was on\nthe North Circular, flat out.”"},
            {"image": "outro", "move": "zoom_in", "duration": 3.0, "kind": "outro",
             "text": "THE RIDER'S GANG",
             "footnote": "Read the full story • link in bio"},
        ],
    },

    "the-saddlebag-from-horse-leather-to-high-fashion": {
        "mood": "heritage",
        "scenes": [
            {"image": "hero", "move": "zoom_in", "duration": 4.0, "kind": "title",
             "eyebrow": "THE RIDER'S GANG • ANCIENT TO MODERN",
             "text": "THE SADDLEBAG",
             "footnote": "From horse leather to high fashion"},
            {"image": "alt1", "move": "pan_left", "duration": 4.0, "kind": "beat",
             "eyebrow": "FASHION'S ORIGIN STORY",
             "text": "Every luxury handbag began as\na pouch strapped to a horse."},
            {"image": "alt2", "move": "zoom_out", "duration": 4.0, "kind": "beat",
             "eyebrow": "PERSIA → PARIS",
             "text": "From cavalry warriors to the\nKelly and the Birkin."},
            {"image": "hero", "move": "drift_up", "duration": 4.5, "kind": "quote",
             "text": "“Hermès didn't become a luxury brand\nby accident. They simply pointed their\nskills at a different customer.”"},
            {"image": "outro", "move": "zoom_in", "duration": 3.0, "kind": "outro",
             "text": "THE RIDER'S GANG",
             "footnote": "Read the full story • link in bio"},
        ],
    },

    "the-polo-shirt-from-horseback-to-high-street": {
        "mood": "heritage",
        "scenes": [
            {"image": "hero", "move": "zoom_in", "duration": 4.0, "kind": "title",
             "eyebrow": "THE RIDER'S GANG • 1850s–PRESENT",
             "text": "THE POLO SHIRT",
             "footnote": "From horseback to high street"},
            {"image": "alt1", "move": "pan_right", "duration": 4.0, "kind": "beat",
             "eyebrow": "INDIA, 1850s",
             "text": "A sport played on horseback gave\nthe world its most versatile garment."},
            {"image": "alt2", "move": "zoom_out", "duration": 4.0, "kind": "beat",
             "eyebrow": "2,000,000,000 SOLD A YEAR",
             "text": "Lacoste engineered it.\nRalph Lauren made it an empire."},
            {"image": "hero", "move": "drift_up", "duration": 4.5, "kind": "quote",
             "text": "“The polo shirt signals both old-money\nprivilege and working-class rebellion,\nconformity and independence.”"},
            {"image": "outro", "move": "zoom_in", "duration": 3.0, "kind": "outro",
             "text": "THE RIDER'S GANG",
             "footnote": "Read the full story • link in bio"},
        ],
    },

    "denim-and-the-rider-how-jeans-were-born-in-the-saddle": {
        "mood": "midnight",
        "scenes": [
            {"image": "hero", "move": "zoom_in", "duration": 4.0, "kind": "title",
             "eyebrow": "THE RIDER'S GANG • EST. 1873",
             "text": "DENIM & THE RIDER",
             "footnote": "How jeans were born in the saddle"},
            {"image": "alt1", "move": "pan_left", "duration": 4.0, "kind": "beat",
             "eyebrow": "1873",
             "text": "A tailor added copper rivets to stop\npockets tearing on horseback."},
            {"image": "alt2", "move": "zoom_out", "duration": 4.0, "kind": "beat",
             "eyebrow": "THE ACCIDENTAL ICON",
             "text": "14-hour saddle days. Desert thorns.\nNothing else survived."},
            {"image": "hero", "move": "drift_up", "duration": 4.5, "kind": "quote",
             "text": "“The cowboy didn't choose denim.\nDenim chose the cowboy — because nothing\nelse could survive the life he lived.”"},
            {"image": "outro", "move": "zoom_in", "duration": 3.0, "kind": "outro",
             "text": "THE RIDER'S GANG",
             "footnote": "Read the full story • link in bio"},
        ],
    },

    "the-riding-crop-from-horse-command-to-fashion-icon": {
        "mood": "heritage",
        "scenes": [
            {"image": "hero", "move": "zoom_in", "duration": 4.0, "kind": "title",
             "eyebrow": "THE RIDER'S GANG • TWO THOUSAND YEARS",
             "text": "THE RIDING CROP",
             "footnote": "From horse command to fashion icon"},
            {"image": "alt1", "move": "pan_right", "duration": 4.0, "kind": "beat",
             "eyebrow": "ROME TO ASCOT",
             "text": "Roman cavalry carried it into battle.\nDressage riders carry it still."},
            {"image": "alt2", "move": "zoom_out", "duration": 4.0, "kind": "beat",
             "eyebrow": "SWAINE ADENEY, LONDON",
             "text": "Handcrafted by the same house\nsince 1750."},
            {"image": "hero", "move": "drift_up", "duration": 4.5, "kind": "quote",
             "text": "“The crop is not about force. It's about\nconversation — a language between rider\nand horse refined over millennia.”"},
            {"image": "outro", "move": "zoom_in", "duration": 3.0, "kind": "outro",
             "text": "THE RIDER'S GANG",
             "footnote": "Read the full story • link in bio"},
        ],
    },

    "hermes-from-horse-harnesses-to-high-fashion": {
        "mood": "heritage",
        "scenes": [
            {"image": "hero", "move": "zoom_in", "duration": 4.0, "kind": "title",
             "eyebrow": "THE RIDER'S GANG • PARIS, 1837",
             "text": "HERMÈS",
             "footnote": "From horse harnesses to high fashion"},
            {"image": "alt1", "move": "pan_left", "duration": 4.0, "kind": "beat",
             "eyebrow": "A HARNESS WORKSHOP",
             "text": "It began with buckles and bridles\nfor the carriages of Paris."},
            {"image": "alt2", "move": "zoom_out", "duration": 4.0, "kind": "beat",
             "eyebrow": "THE SADDLE STITCH",
             "text": "The same hands, the same thread —\nturned to scarves, bags, and legend."},
            {"image": "hero", "move": "drift_up", "duration": 4.5, "kind": "quote",
             "text": "“The horse is the heart of Hermès.\nIt lives in every stitch, every buckle,\nevery piece of leather we touch.”"},
            {"image": "outro", "move": "zoom_in", "duration": 3.0, "kind": "outro",
             "text": "THE RIDER'S GANG",
             "footnote": "Read the full story • link in bio"},
        ],
    },

    "belstaff-the-jacket-that-built-a-riding-legend": {
        "mood": "midnight",
        "scenes": [
            {"image": "hero", "move": "zoom_in", "duration": 4.0, "kind": "title",
             "eyebrow": "THE RIDER'S GANG • EST. 1924",
             "text": "BELSTAFF",
             "footnote": "The jacket that built a riding legend"},
            {"image": "alt1", "move": "pan_right", "duration": 4.0, "kind": "beat",
             "eyebrow": "STOKE-ON-TRENT, 1924",
             "text": "Waxed cotton, built for riders\nwho refused to stop for weather."},
            {"image": "alt2", "move": "zoom_out", "duration": 4.0, "kind": "beat",
             "eyebrow": "THE TRIALMASTER",
             "text": "Worn by Che Guevara, McQueen,\nand every rider in between."},
            {"image": "hero", "move": "drift_up", "duration": 4.5, "kind": "quote",
             "text": "“A Belstaff isn't bought for a season.\nIt's bought for a lifetime — then\nhanded down.”"},
            {"image": "outro", "move": "zoom_in", "duration": 3.0, "kind": "outro",
             "text": "THE RIDER'S GANG",
             "footnote": "Read the full story • link in bio"},
        ],
    },

    "the-gucci-horsebit-loafer-born-in-the-saddle": {
        "mood": "heritage",
        "scenes": [
            {"image": "hero", "move": "zoom_in", "duration": 4.0, "kind": "title",
             "eyebrow": "THE RIDER'S GANG • FLORENCE, 1953",
             "text": "THE HORSEBIT LOAFER",
             "footnote": "Born in the saddle, worn in the boardroom"},
            {"image": "alt1", "move": "pan_left", "duration": 4.0, "kind": "beat",
             "eyebrow": "A PIECE OF TACK",
             "text": "Gucci took the metal bit from a\nhorse's bridle — and put it on a shoe."},
            {"image": "alt2", "move": "zoom_out", "duration": 4.0, "kind": "beat",
             "eyebrow": "MoMA PERMANENT COLLECTION",
             "text": "Seventy years on, it is still\nthe quietest way to say old money."},
            {"image": "hero", "move": "drift_up", "duration": 4.5, "kind": "quote",
             "text": "“Two rings and a bar. The simplest\npiece of stable hardware became\nfashion's most copied signature.”"},
            {"image": "outro", "move": "zoom_in", "duration": 3.0, "kind": "outro",
             "text": "THE RIDER'S GANG",
             "footnote": "Read the full story • link in bio"},
        ],
    },

    "riding-boots-from-cavalry-to-catwalk": {
        "mood": "heritage",
        "scenes": [
            {"image": "hero", "move": "zoom_in", "duration": 4.0, "kind": "title",
             "eyebrow": "THE RIDER'S GANG • CAVALRY TO CATWALK",
             "text": "RIDING BOOTS",
             "footnote": "A thousand years of tall leather"},
            {"image": "alt1", "move": "pan_right", "duration": 4.0, "kind": "beat",
             "eyebrow": "BUILT FOR BATTLE",
             "text": "Cavalry officers needed leather\nthat gripped the stirrup and survived."},
            {"image": "alt2", "move": "zoom_out", "duration": 4.0, "kind": "beat",
             "eyebrow": "FROM PARADE GROUND TO RUNWAY",
             "text": "The same silhouette now walks\nevery fashion week on earth."},
            {"image": "hero", "move": "drift_up", "duration": 4.5, "kind": "quote",
             "text": "“A proper riding boot is armour,\ninstrument, and heirloom —\nall in one piece of leather.”"},
            {"image": "outro", "move": "zoom_in", "duration": 3.0, "kind": "outro",
             "text": "THE RIDER'S GANG",
             "footnote": "Read the full story • link in bio"},
        ],
    },

    "leh-ladakh-the-ride-that-changes-everything": {
        "mood": "midnight",
        "scenes": [
            {"image": "hero", "move": "zoom_in", "duration": 4.0, "kind": "title",
             "eyebrow": "THE RIDER'S GANG • 18,000 FEET",
             "text": "LEH–LADAKH",
             "footnote": "The ride that changes everything"},
            {"image": "alt1", "move": "pan_left", "duration": 4.0, "kind": "beat",
             "eyebrow": "THE HIMALAYAS",
             "text": "Thin air. Broken roads.\nThe most beautiful ride on earth."},
            {"image": "alt2", "move": "zoom_out", "duration": 4.0, "kind": "beat",
             "eyebrow": "KHARDUNG LA",
             "text": "Every rider who climbs it\ncomes down someone else."},
            {"image": "hero", "move": "drift_up", "duration": 4.5, "kind": "quote",
             "text": "“You don't conquer Ladakh.\nYou survive it, and it rewards you\nwith who you become.”"},
            {"image": "outro", "move": "zoom_in", "duration": 3.0, "kind": "outro",
             "text": "THE RIDER'S GANG",
             "footnote": "Read the full story • link in bio"},
        ],
    },
}
