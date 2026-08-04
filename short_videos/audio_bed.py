"""
Vintage audio bed — synthesized with numpy, no external assets.

Two moods:
    midnight  - minor-seventh pad, slow and moody (motorcycle stories)
    heritage  - major-seventh pad, warm and stately (equestrian stories)

On top of the pad: vinyl crackle (sparse filtered impulses) and a low
tape-hiss floor, with a gentle fade in and a longer fade out. Written
as 44.1 kHz stereo WAV.
"""

import wave

import numpy as np

SAMPLE_RATE = 44100

# Chord progressions as frequency ratios from the root (Hz values below).
# Voicings stay low and close — felt more than heard.
MOODS = {
    "midnight": {
        "root": 110.0,  # A2
        "chords": [
            [1.0, 1.189, 1.498, 1.782],   # Am7  (A C E G)
            [0.8909, 1.122, 1.335, 1.682],  # Fmaj7-ish
            [1.0, 1.189, 1.498, 1.782],
            [0.6674, 0.8409, 1.0, 1.259],   # low D-ish resolution
        ],
    },
    "heritage": {
        "root": 130.81,  # C3
        "chords": [
            [1.0, 1.26, 1.498, 1.888],    # Cmaj7 (C E G B)
            [0.8409, 1.0587, 1.26, 1.498],  # Am-ish
            [0.6674, 0.8409, 1.0, 1.26],    # F-ish
            [0.749, 0.9439, 1.122, 1.335],  # G-ish
        ],
    },
}


def _pad_voice(freq: float, t: np.ndarray) -> np.ndarray:
    """One soft pad voice: detuned triangle-ish partials with slow attack."""
    v = (
        np.sin(2 * np.pi * freq * t)
        + 0.35 * np.sin(2 * np.pi * freq * 2.003 * t)   # slightly detuned octave
        + 0.15 * np.sin(2 * np.pi * freq * 0.5 * t)     # sub
    )
    return v


def build_audio_bed(duration_sec: float, mood: str, out_path: str, seed: int = 7) -> None:
    """Render the audio bed for one video and write it as WAV."""
    rng = np.random.default_rng(seed)
    cfg = MOODS.get(mood, MOODS["heritage"])

    n = int(duration_sec * SAMPLE_RATE)
    t = np.arange(n) / SAMPLE_RATE
    audio = np.zeros(n, dtype=np.float64)

    # ── Chord pad ────────────────────────────────────────────────
    chord_len = duration_sec / len(cfg["chords"])
    for i, ratios in enumerate(cfg["chords"]):
        start = int(i * chord_len * SAMPLE_RATE)
        end = min(int((i + 1) * chord_len * SAMPLE_RATE), n)
        seg_t = t[start:end]
        seg = np.zeros(end - start)
        for r in ratios:
            seg += _pad_voice(cfg["root"] * r, seg_t)
        # slow attack/release envelope per chord so changes breathe
        env_len = end - start
        attack = int(0.35 * SAMPLE_RATE)
        release = int(0.45 * SAMPLE_RATE)
        env = np.ones(env_len)
        env[: min(attack, env_len)] = np.linspace(0, 1, min(attack, env_len))
        env[-min(release, env_len):] *= np.linspace(1, 0.25, min(release, env_len))
        audio[start:end] += seg * env * 0.055

    # ── Vinyl crackle ────────────────────────────────────────────
    crackle = np.zeros(n)
    n_pops = int(duration_sec * 9)  # ~9 pops per second, mostly tiny
    pop_positions = rng.integers(0, n - 100, size=n_pops)
    for pos in pop_positions:
        amp = rng.uniform(0.004, 0.045) * rng.choice([1, -1])
        width = rng.integers(8, 40)
        pop = amp * np.exp(-np.linspace(0, 6, width))
        crackle[pos:pos + width] += pop
    audio += crackle

    # ── Tape hiss floor ──────────────────────────────────────────
    hiss = rng.normal(0, 0.0035, n)
    # crude low-pass: moving average so the hiss is soft, not harsh
    kernel = np.ones(8) / 8.0
    hiss = np.convolve(hiss, kernel, mode="same")
    audio += hiss

    # ── Master fades ─────────────────────────────────────────────
    fade_in = int(0.8 * SAMPLE_RATE)
    fade_out = int(2.0 * SAMPLE_RATE)
    audio[:fade_in] *= np.linspace(0, 1, fade_in)
    audio[-fade_out:] *= np.linspace(1, 0, fade_out)

    # Normalize to a quiet, comfortable bed
    peak = np.abs(audio).max()
    if peak > 0:
        audio = audio / peak * 0.5

    # Stereo: tiny delay on the right channel for width
    delay = int(0.011 * SAMPLE_RATE)
    right = np.concatenate([np.zeros(delay), audio[:-delay]])
    stereo = np.stack([audio, right], axis=1)

    pcm = (stereo * 32767).astype(np.int16)
    with wave.open(out_path, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(pcm.tobytes())
