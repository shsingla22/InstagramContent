"""
Cinematic Scene Generator — two-stage photoreal pipeline on free
Hugging Face ZeroGPU quota:

    Stage 1: FLUX.1 Krea renders a photorealistic 35mm-film still
             per scene (wide/medium framing, real environments —
             kills the "toy" look of direct text-to-video)
    Stage 2: Wan 2.2 image-to-video animates each still, preserving
             its realism while adding racing motion

Storyboard: a proper racing arc for "The Night They Raced the
Jukebox" — cafe, coin drop, launch, corner, flat-out, final
straight, and the return.

Requires HF_TOKEN in the environment.

Run:  HF_TOKEN=... python3 -m short_videos.cinematic_generator
      HF_TOKEN=... python3 -m short_videos.cinematic_generator --only 05_flatout
"""

import argparse
import os
import shutil
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

FLUX_SPACE = "black-forest-labs/FLUX.1-Krea-dev"
WAN_SPACE = "zerogpu-aoti/wan2-2-fp8da-aoti-faster"

STORY_DIR = "output/short_videos/story"
STILLS_DIR = os.path.join(STORY_DIR, "stills")

STILL_WIDTH = 576
STILL_HEIGHT = 1024
CLIP_SECONDS = 3.5

# Photographic language shared by every still — this is what keeps
# the footage looking like archival film instead of CGI
FILM = (
    "shot on 35mm Kodachrome film, 1959 London, documentary photography, "
    "gritty, weathered, realistic proportions, natural muted colors, "
    "film grain, dusk light"
)

WAN_NEGATIVE = "static, still, frozen, warped, distorted, morphing, low quality"

STORYBOARD = [
    {
        "id": "01_cafe",
        "seed": 111,
        "flux_prompt": (
            'Wide shot of a 1950s British transport cafe at dusk, a large sign '
            'reading "ACE CAFE" above the roof, a dozen classic cafe racer '
            'motorcycles parked in rows out front, riders in black leather '
            'jackets talking in groups, warm light spilling from the windows, '
            + FILM
        ),
        "motion_prompt": (
            "riders walk between the parked motorcycles, warm light flickers "
            "in the cafe windows, slow cinematic push-in"
        ),
        "caption": "London, 1959.\nThe Ace Cafe never slept.",
        "eyebrow": "A TRUE STORY",
    },
    {
        "id": "02_jukebox",
        "seed": 212,
        "flux_prompt": (
            "Interior of a smoky 1950s British cafe, a rider's leather-gloved "
            "hand dropping a sixpence coin into a chrome Wurlitzer jukebox, "
            "warm glowing amber lights reflecting on the chrome, vinyl record "
            "visible behind glass, shallow depth of field, " + FILM
        ),
        "motion_prompt": (
            "the gloved hand drops the coin into the slot, the jukebox lights "
            "glow brighter, the vinyl record begins to spin"
        ),
        "caption": "A coin drops. The record spins.\nThe clock starts.",
        "eyebrow": "THE BET",
    },
    {
        "id": "03_launch",
        "seed": 333,
        "flux_prompt": (
            "Riders in black leather sprinting to their parked cafe racer "
            "motorcycles outside a British cafe at dusk, one rider already "
            "kick-starting his engine, others swinging a leg over their bikes, "
            "urgency, wide dynamic composition showing the whole street, "
            + FILM
        ),
        "motion_prompt": (
            "the riders mount their motorcycles, the first bikes launch "
            "forward with spinning rear wheels, others kick engines to life"
        ),
        "caption": "Back before the song ends —\nor don't come back.",
        "eyebrow": "THREE MINUTES. ONE SONG.",
    },
    {
        "id": "04_race",
        "seed": 525,
        "flux_prompt": (
            "1959 London street race, wide cinematic shot: a rider on a vintage "
            "Triton cafe racer motorcycle leaning hard into a corner, knee "
            "close to the road, three more racers visible behind him down the "
            "long street, victorian brick buildings and gas lamps lining the "
            "road, " + FILM
        ),
        "motion_prompt": (
            "The motorcycles race toward the camera at high speed, the lead "
            "rider leans through the bend, the pack behind accelerates, wheels "
            "spinning fast, camera slowly tracking, cinematic motion, film grain"
        ),
        "caption": "They called it\n“doing the ton.”",
        "eyebrow": "100 MPH",
    },
    {
        "id": "05_flatout",
        "seed": 555,
        "flux_prompt": (
            "Low roadside panning shot of three vintage cafe racer motorcycles "
            "at full racing speed on a London street, riders tucked flat over "
            "their fuel tanks, the background motion-blurred, victorian gas "
            "lamps streaking past, sense of extreme speed, " + FILM
        ),
        "motion_prompt": (
            "the motorcycles blast past the camera at very high speed, the "
            "background streaks with motion blur, riders hold their tuck"
        ),
        "caption": "Flat out\npast the gas lamps.",
        "eyebrow": "FLAT OUT",
    },
    {
        "id": "06_finish",
        "seed": 616,
        "flux_prompt": (
            "Head-on shot down a long London street at dusk, the lead rider on "
            "a vintage cafe racer racing directly toward the camera, headlamp "
            "glowing, two rival racers close behind him, victorian terraced "
            "buildings on both sides, long empty road, " + FILM
        ),
        "motion_prompt": (
            "the motorcycles speed toward the camera growing larger, the lead "
            "headlamp flares, the rivals close in behind"
        ),
        "caption": "One song. One shot.\nNo brakes.",
        "eyebrow": "THE LAST STRAIGHT",
    },
    {
        "id": "07_return",
        "seed": 727,
        "flux_prompt": (
            "A rider braking to a stop on his vintage cafe racer outside a "
            "neon-lit British cafe at dusk, a waiting crowd of riders in "
            "leather jackets erupting in cheers with raised arms around him, "
            "jubilant celebration, medium-wide shot, " + FILM
        ),
        "motion_prompt": (
            "the motorcycle comes to a stop, the crowd cheers and raises "
            "their arms, the rider raises a fist in triumph"
        ),
        "caption": "The ones who made it back\nbecame legends.",
        "eyebrow": "THE TON-UP BOYS",
    },
]


def generate_still(flux, scene, still_path: str) -> bool:
    print(f"  [FLUX] still for {scene['id']}...")
    try:
        result = flux.predict(
            prompt=scene["flux_prompt"],
            seed=scene["seed"], randomize_seed=False,
            width=STILL_WIDTH, height=STILL_HEIGHT,
            guidance_scale=4.5, num_inference_steps=28,
            api_name="/infer",
        )
    except Exception as e:
        print(f"  FLUX ERROR: {e}")
        return False
    img = result[0] if isinstance(result, (list, tuple)) else result
    shutil.copy(img, still_path)
    return True


def animate_still(wan, scene, still_path: str, out_path: str) -> bool:
    print(f"  [Wan]  animating {scene['id']}...")
    from gradio_client import handle_file
    try:
        result = wan.predict(
            input_image=handle_file(still_path),
            prompt=scene["motion_prompt"],
            steps=6,
            negative_prompt=WAN_NEGATIVE,
            duration_seconds=CLIP_SECONDS,
            guidance_scale=1, guidance_scale_2=1,
            seed=scene["seed"], randomize_seed=False,
            api_name="/generate_video",
        )
    except Exception as e:
        print(f"  Wan ERROR: {e}")
        return False
    video = result[0]["video"] if isinstance(result[0], dict) else result[0]
    shutil.copy(video, out_path)
    return True


def main():
    parser = argparse.ArgumentParser(description="Two-stage photoreal scenes")
    parser.add_argument("--only", type=str, default=None)
    args = parser.parse_args()

    from gradio_client import Client
    token = os.environ.get("HF_TOKEN")
    if not token:
        print("ERROR: set HF_TOKEN")
        sys.exit(1)

    scenes = STORYBOARD
    if args.only:
        wanted = set(args.only.split(","))
        scenes = [s for s in STORYBOARD if s["id"] in wanted]

    os.makedirs(STILLS_DIR, exist_ok=True)
    flux = Client(FLUX_SPACE, token=token, verbose=False)
    wan = Client(WAN_SPACE, token=token, verbose=False)

    failed = []
    for scene in scenes:
        print(f"[{scene['id']}]")
        still = os.path.join(STILLS_DIR, f"{scene['id']}.png")
        clip = os.path.join(STORY_DIR, f"scene_{scene['id']}.mp4")
        if not os.path.exists(still):
            if not generate_still(flux, scene, still):
                failed.append(scene["id"])
                continue
            time.sleep(3)
        else:
            print("  still cached")
        if not os.path.exists(clip):
            if not animate_still(wan, scene, still, clip):
                failed.append(scene["id"])
                continue
            time.sleep(3)
        else:
            print("  clip cached")

    if failed:
        print(f"\nFailed (likely quota): {failed}")
        print("Resume later with:  --only " + ",".join(failed))
        sys.exit(1)
    print("\nAll scenes generated.")


if __name__ == "__main__":
    main()
