"""
Reel content: the most interesting excerpt from each article,
plus narration script and visual scene descriptions.
"""

REELS = [
    {
        "slug": "reel_01_the-cafe-racer",
        "title": "THE CAFÉ RACER",
        "subtitle": "How Coffee Gave Birth to\nMotorcycle Culture",
        "hook": "DOING THE TON",
        "narration": (
            "Nineteen fifties London. A jukebox starts playing. "
            "Young men sprint to their motorcycles and race into the night. "
            "The goal? Hit a hundred miles per hour and return before the song ends. "
            "They called it doing the ton. "
            "They stripped their bikes bare. Removed mudguards, lowered the handlebars, "
            "cut the exhausts short. "
            "These were the Ton-Up Boys of the Ace Cafe. "
            "And they built a culture that changed motorcycling forever."
        ),
        "scenes": [
            {"text": "1950s LONDON", "visual": "dark moody street, neon cafe sign glow"},
            {"text": "THE JUKEBOX\nSTARTS PLAYING", "visual": "warm interior, jukebox light"},
            {"text": "HIT 100 MPH\nBEFORE THE\nSONG ENDS", "visual": "motorcycle speeding, motion blur"},
            {"text": "THEY STRIPPED\nEVERYTHING", "visual": "close-up cafe racer details"},
            {"text": "THE TON-UP\nBOYS", "visual": "riders in leather, cafe exterior"},
            {"text": "A CULTURE WAS\nBORN", "visual": "group of cafe racers riding"},
        ],
        "color_accent": "#D4A843",
        "images": [
            "https://images.unsplash.com/photo-1558981359-219d6364c9c8?w=1080&h=1920&fit=crop",
            "https://images.unsplash.com/photo-1558981806-ec527fa84c39?w=1080&h=1920&fit=crop",
            "https://images.unsplash.com/photo-1609630875171-b1321377ee65?w=1080&h=1920&fit=crop",
        ],
    },
    {
        "slug": "reel_02_the-saddlebag",
        "title": "THE SADDLEBAG",
        "subtitle": "Five Thousand Years\nof Perfect Design",
        "hook": "UNCHANGED SINCE 500 BC",
        "narration": (
            "Five thousand years ago, Persian cavalry strapped leather pouches to their saddles. "
            "Wide openings for quick access. Rain-blocking flaps. Buckles that could survive years of war. "
            "The same design. The exact same shape. "
            "In eighteen thirty seven, Hermès used it to build their first handbags. "
            "In nineteen eighty four, it became the Birkin bag. "
            "The saddlebag was never redesigned. It was only rediscovered. "
            "From Persian warhorses to the most coveted handbag on earth."
        ),
        "scenes": [
            {"text": "500 BC\nPERSIA", "visual": "ancient leather, aged texture"},
            {"text": "STRAPPED TO\nTHE SADDLE", "visual": "horse saddle, leather details"},
            {"text": "THE SAME\nDESIGN", "visual": "close-up of buckle and leather"},
            {"text": "1837\nHERMÈS", "visual": "luxury leather workshop"},
            {"text": "NEVER\nREDESIGNED", "visual": "modern bag, golden tones"},
            {"text": "ONLY\nREDISCOVERED", "visual": "fashion runway, warm lighting"},
        ],
        "color_accent": "#C9A84C",
        "images": [
            "https://images.unsplash.com/photo-1473188588951-666fce8e7c68?w=1080&h=1920&fit=crop",
            "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=1080&h=1920&fit=crop",
            "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=1080&h=1920&fit=crop",
        ],
    },
    {
        "slug": "reel_03_the-polo-shirt",
        "title": "THE POLO SHIRT",
        "subtitle": "Two Billion Shirts a Year\nStarted on Horseback",
        "hook": "BORN ON HORSEBACK",
        "narration": (
            "Two billion polo shirts are sold every year. "
            "But here's what most people don't know. "
            "In Victorian England, polo players wore stiff starched collars on horseback. "
            "At full gallop, swinging a mallet, it was miserable. "
            "So they buttoned their collars down. "
            "Then Lacoste added the crocodile. Ralph Lauren added the horse. "
            "And a sport of kings gave the world its most democratic garment. "
            "Two billion shirts. And every one carries the ghost of a horse."
        ),
        "scenes": [
            {"text": "2 BILLION\nSHIRTS A YEAR", "visual": "stacked polo shirts, colorful"},
            {"text": "VICTORIAN\nPOLO FIELDS", "visual": "horses, green fields, golden hour"},
            {"text": "STIFF COLLARS\nAT FULL GALLOP", "visual": "horse polo action"},
            {"text": "LACOSTE\nADDED THE\nCROCODILE", "visual": "polo shirt detail"},
            {"text": "RALPH LAUREN\nADDED THE HORSE", "visual": "luxury fashion, warm tone"},
            {"text": "THE GHOST\nOF A HORSE", "visual": "silhouette of rider, sunset"},
        ],
        "color_accent": "#2C6B3F",
        "images": [
            "https://images.unsplash.com/photo-1550126417-c0c9e38eba50?w=1080&h=1920&fit=crop",
            "https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=1080&h=1920&fit=crop",
            "https://images.unsplash.com/photo-1564859228273-274232fdb516?w=1080&h=1920&fit=crop",
        ],
    },
    {
        "slug": "reel_04_denim-and-the-rider",
        "title": "DENIM & THE RIDER",
        "subtitle": "How Jeans Were Born\nin the Saddle",
        "hook": "BORN IN THE SADDLE",
        "narration": (
            "Eighteen seventy three. A tailor named Jacob Davis had a problem. "
            "Cowboys kept destroying their trousers on horseback. "
            "So he grabbed copper rivets from horse harnesses and hammered them into the pockets. "
            "The pants stopped tearing. "
            "Those rivets are still on your jeans today. "
            "The whisker fades on your thighs? Those come from the saddle. "
            "Every pair of jeans on earth is riding trousers. "
            "Denim was born in the saddle. And it never left."
        ),
        "scenes": [
            {"text": "1873", "visual": "vintage sepia tone, workshop"},
            {"text": "COWBOYS KEPT\nDESTROYING\nTHEIR TROUSERS", "visual": "cowboy on horse"},
            {"text": "COPPER RIVETS\nFROM HORSE\nHARNESSES", "visual": "close-up jeans rivets"},
            {"text": "STILL ON YOUR\nJEANS TODAY", "visual": "modern jeans detail"},
            {"text": "BORN IN\nTHE SADDLE", "visual": "western landscape, rider"},
            {"text": "AND NEVER LEFT", "visual": "denim close-up, vintage feel"},
        ],
        "color_accent": "#4A6A8A",
        "images": [
            "https://images.unsplash.com/photo-1542272604-787c3835535d?w=1080&h=1920&fit=crop",
            "https://images.unsplash.com/photo-1565084888279-aca607ecce0c?w=1080&h=1920&fit=crop",
            "https://images.unsplash.com/photo-1582552938357-32b906df40cb?w=1080&h=1920&fit=crop",
        ],
    },
    {
        "slug": "reel_05_the-riding-crop",
        "title": "THE RIDING CROP",
        "subtitle": "Not a Weapon.\nA Language.",
        "hook": "A PHYSICAL WORD",
        "narration": (
            "The riding crop is not a weapon. It is a word. "
            "A single tap means forward. Two taps mean urgency. "
            "For two thousand years, riders have spoken to horses through this tool. "
            "Roman cavalry used leather strips called flagella. "
            "Swaine Adeney in London has handcrafted crops since seventeen fifty. "
            "One craftsman. Braided leather. Designed to last generations. "
            "From ancient battlefields to fashion runways. "
            "The crop is the oldest conversation between human and horse."
        ),
        "scenes": [
            {"text": "NOT A WEAPON", "visual": "elegant riding crop, dark background"},
            {"text": "A LANGUAGE", "visual": "rider's hand with crop, horse"},
            {"text": "ONE TAP:\nFORWARD", "visual": "dressage, precision movement"},
            {"text": "SINCE 1750\nSWAINE ADENEY", "visual": "craftsman workshop, leather"},
            {"text": "BRAIDED\nLEATHER", "visual": "close-up detail, warm light"},
            {"text": "THE OLDEST\nCONVERSATION", "visual": "rider and horse silhouette"},
        ],
        "color_accent": "#8B4513",
        "images": [
            "https://images.unsplash.com/photo-1598974357801-cbca100e65d3?w=1080&h=1920&fit=crop",
            "https://images.unsplash.com/photo-1553284965-83fd3e82fa5a?w=1080&h=1920&fit=crop",
            "https://images.unsplash.com/photo-1516466723877-e4ec1d736c8a?w=1080&h=1920&fit=crop",
        ],
    },
    {
        "slug": "reel_06_hermes",
        "title": "HERMÈS",
        "subtitle": "From Horse Harnesses\nto High Fashion",
        "hook": "THE HORSE NEVER LEFT",
        "narration": (
            "In eighteen thirty seven, Thierry Hermès made horse harnesses in Paris. "
            "When cars replaced horses, most saddlers went bankrupt. "
            "But Hermès took their leather skills and made handbags instead. "
            "The Kelly bag? It was built to carry riding equipment. "
            "The Birkin? Same saddle stitch from eighteen thirty seven. "
            "Two needles. One hole. If one thread breaks, the other holds. "
            "Today Hermès is worth two hundred billion dollars. "
            "The horse never left. It lives in every stitch."
        ),
        "scenes": [
            {"text": "1837\nPARIS", "visual": "vintage paris street, warm light"},
            {"text": "HORSE\nHARNESSES", "visual": "leather harness, craftsmanship"},
            {"text": "CARS REPLACED\nHORSES", "visual": "transition era, moody"},
            {"text": "THE KELLY BAG\nWAS FOR RIDING\nEQUIPMENT", "visual": "elegant bag"},
            {"text": "SAME SADDLE\nSTITCH SINCE\n1837", "visual": "hand stitching close-up"},
            {"text": "THE HORSE\nNEVER LEFT", "visual": "Hermès logo, golden warm"},
        ],
        "color_accent": "#E8731A",
        "images": [
            "https://images.unsplash.com/photo-1553284965-83fd3e82fa5a?w=1080&h=1920&fit=crop",
            "https://images.unsplash.com/photo-1473188588951-666fce8e7c68?w=1080&h=1920&fit=crop",
            "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=1080&h=1920&fit=crop",
        ],
    },
    {
        "slug": "reel_07_belstaff",
        "title": "BELSTAFF",
        "subtitle": "The Jacket That Built\na Riding Legend",
        "hook": "EVERY SCRATCH IS A ROAD",
        "narration": (
            "Che Guevara wore one across South America. "
            "Steve McQueen wore one racing through Scotland, covered in mud, grinning. "
            "The Belstaff Trialmaster. Waxed cotton. Waterproof. Indestructible. "
            "Harry Grosberg built it in nineteen twenty four for British riders "
            "who needed gear that could survive the weather and the road. "
            "A new Belstaff is handsome. A worn one is magnificent. "
            "Every scratch is a road you've taken. "
            "Every stain is a journey you've completed."
        ),
        "scenes": [
            {"text": "CHE GUEVARA\nSOUTH AMERICA\n1952", "visual": "vintage motorcycle journey"},
            {"text": "STEVE McQUEEN\nSCOTLAND 1964", "visual": "muddy motorcycle racing"},
            {"text": "WAXED COTTON\nINDESTRUCTIBLE", "visual": "jacket texture close-up"},
            {"text": "BUILT FOR\nBRITISH RIDERS", "visual": "rainy road, motorcycle"},
            {"text": "A WORN ONE IS\nMAGNIFICENT", "visual": "aged leather, character"},
            {"text": "EVERY SCRATCH\nIS A ROAD", "visual": "open road, rider silhouette"},
        ],
        "color_accent": "#5C4033",
        "images": [
            "https://images.unsplash.com/photo-1558981806-ec527fa84c39?w=1080&h=1920&fit=crop",
            "https://images.unsplash.com/photo-1558981359-219d6364c9c8?w=1080&h=1920&fit=crop",
            "https://images.unsplash.com/photo-1609630875171-b1321377ee65?w=1080&h=1920&fit=crop",
        ],
    },
    {
        "slug": "reel_08_gucci-horsebit",
        "title": "THE GUCCI\nHORSEBIT LOAFER",
        "subtitle": "Born in the Saddle",
        "hook": "FROM A HORSE'S MOUTH",
        "narration": (
            "Inside a horse's mouth sits a snaffle bit. "
            "Two metal rings connected by a bar. It lets the rider talk to the horse. "
            "In nineteen fifty three, Gucci miniaturized that bit, "
            "cast it in gold, and placed it on a loafer. "
            "By the sixties, Audrey Hepburn and JFK were wearing them. "
            "By the eighties, Wall Street called them deal sleds. "
            "In nineteen eighty five, the Met put one in its permanent collection. "
            "A piece of horse equipment. In a museum. On your feet."
        ),
        "scenes": [
            {"text": "INSIDE A\nHORSE'S MOUTH", "visual": "horse close-up, noble"},
            {"text": "TWO RINGS\nONE BAR", "visual": "snaffle bit detail, golden"},
            {"text": "1953\nGUCCI", "visual": "elegant shoe, warm lighting"},
            {"text": "AUDREY HEPBURN\nJFK", "visual": "vintage glamour, gold tones"},
            {"text": "WALL STREET\nCALLED THEM\nDEAL SLEDS", "visual": "power style"},
            {"text": "HORSE EQUIPMENT\nIN A MUSEUM", "visual": "Met museum, artistic"},
        ],
        "color_accent": "#B8860B",
        "images": [
            "https://images.unsplash.com/photo-1615979474401-8a6a344de5bd?w=1080&h=1920&fit=crop",
            "https://images.unsplash.com/photo-1449505278894-297fdb3edbc1?w=1080&h=1920&fit=crop",
            "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=1080&h=1920&fit=crop",
        ],
    },
    {
        "slug": "reel_09_riding-boots",
        "title": "RIDING BOOTS",
        "subtitle": "From Cavalry\nto Catwalk",
        "hook": "FIVE CENTURIES. SAME BOOT.",
        "narration": (
            "Every part of a riding boot has a purpose. "
            "The shaft protects your calves. The smooth sole slides into stirrups. "
            "The angled heel stops your foot from slipping through. "
            "In eighteen seventeen, the Duke of Wellington redesigned the boot "
            "because trousers replaced breeches. "
            "His design became the template for every riding boot since. "
            "Five hundred years. From cavalry charges to Chanel runways. "
            "The boot never changed because the horse never changed."
        ),
        "scenes": [
            {"text": "EVERY PART\nHAS A PURPOSE", "visual": "riding boot detail, leather"},
            {"text": "THE SHAFT\nTHE SOLE\nTHE HEEL", "visual": "boot anatomy, warm light"},
            {"text": "1817\nTHE DUKE OF\nWELLINGTON", "visual": "historic, noble aesthetic"},
            {"text": "THE TEMPLATE\nFOR EVERY\nBOOT SINCE", "visual": "multiple boots, lineup"},
            {"text": "CAVALRY TO\nCATWALK", "visual": "fashion runway, boots"},
            {"text": "THE HORSE\nNEVER CHANGED", "visual": "horse and rider, golden hour"},
        ],
        "color_accent": "#704214",
        "images": [
            "https://images.unsplash.com/photo-1722109283665-05e8a7db546e?w=1080&h=1920&fit=crop",
            "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=1080&h=1920&fit=crop",
            "https://images.unsplash.com/photo-1449505278894-297fdb3edbc1?w=1080&h=1920&fit=crop",
        ],
    },
    {
        "slug": "reel_10_leh-ladakh",
        "title": "LEH-LADAKH",
        "subtitle": "The Ride That Changes\nEverything",
        "hook": "5,359 METRES ABOVE SEA LEVEL",
        "narration": (
            "Five thousand three hundred and fifty nine metres above sea level. "
            "Oxygen drops to half. Engines lose power. The road turns to gravel and river crossings. "
            "This is Khardung La. The top of the world. "
            "Every year, tens of thousands of riders on Royal Enfields make this journey. "
            "Not because it's easy. Because it's the hardest thing they've ever done. "
            "At the summit, riders say the same thing. "
            "Silence. Gratitude. And a feeling they can never quite explain."
        ),
        "scenes": [
            {"text": "5,359 METRES", "visual": "mountain pass, dramatic sky"},
            {"text": "OXYGEN DROPS\nTO HALF", "visual": "thin atmosphere, vast landscape"},
            {"text": "KHARDUNG LA\nTOP OF THE\nWORLD", "visual": "summit marker, snow peaks"},
            {"text": "ROYAL ENFIELD\nTENS OF\nTHOUSANDS", "visual": "riders on mountain road"},
            {"text": "NOT BECAUSE\nIT'S EASY", "visual": "challenging terrain, river crossing"},
            {"text": "SILENCE.\nGRATITUDE.", "visual": "rider at summit, vast mountains"},
        ],
        "color_accent": "#2E5090",
        "images": [
            "https://images.unsplash.com/photo-1670644654521-6fbfffeaba87?w=1080&h=1920&fit=crop",
            "https://images.unsplash.com/photo-1609630875171-b1321377ee65?w=1080&h=1920&fit=crop",
            "https://images.unsplash.com/photo-1558981806-ec527fa84c39?w=1080&h=1920&fit=crop",
        ],
    },
]
