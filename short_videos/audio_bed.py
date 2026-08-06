"""
Audio bed — synthesized with numpy, no external assets.

Two moods:
    midnight  - minor-seventh pad, slow and moody (motorcycle stories)
    heritage  - major-seventh pad, warm and stately (equestrian stories)

The pad is built from overlapping chord segments with cosine
fade-in/fade-out envelopes so chord changes never click, plus a very
soft low-passed air layer. No crackle pops — earlier versions had a
vinyl-pop layer that listeners heard as audio "breaking", so it was
removed. Written as 44.1 kHz stereo WAV.
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
            [1.0, 1.189, 1.498, 1.782],     # Am7  (A C E G)
            [0.8909, 1.122, 1.335, 1.682],  # Fmaj7-ish
            [1.0, 1.189, 1.498, 1.782],
            [0.6674, 0.8409, 1.0, 1.259],   # low D-ish resolution
        ],
    },
    "heritage": {
        "root": 130.81,  # C3
        "chords": [
            [1.0, 1.26, 1.498, 1.888],      # Cmaj7 (C E G B)
            [0.8409, 1.0587, 1.26, 1.498],  # Am-ish
            [0.6674, 0.8409, 1.0, 1.26],    # F-ish
            [0.749, 0.9439, 1.122, 1.335],  # G-ish
        ],
    },
}

# Seconds of overlap between neighbouring chords (crossfade zone)
CHORD_OVERLAP = 0.8


def _pad_voice(freq: float, t: np.ndarray) -> np.ndarray:
    """One soft pad voice: gentle detuned partials."""
    return (
        np.sin(2 * np.pi * freq * t)
        + 0.25 * np.sin(2 * np.pi * freq * 2.002 * t)   # slightly detuned octave
        + 0.15 * np.sin(2 * np.pi * freq * 0.5 * t)     # sub
    )


def _cosine_window(n: int, fade: int) -> np.ndarray:
    """Envelope that rises and falls with cosine ramps — click-free."""
    env = np.ones(n)
    fade = min(fade, n // 2)
    if fade > 0:
        ramp = 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, fade))
        env[:fade] = ramp
        env[-fade:] = ramp[::-1]
    return env


def build_audio_bed(duration_sec: float, mood: str, out_path: str, seed: int = 7) -> None:
    """Render the audio bed for one video and write it as WAV."""
    rng = np.random.default_rng(seed)
    cfg = MOODS.get(mood, MOODS["heritage"])

    n = int(duration_sec * SAMPLE_RATE)
    t = np.arange(n) / SAMPLE_RATE
    audio = np.zeros(n, dtype=np.float64)

    # ── Chord pad with crossfaded segments ───────────────────────
    n_chords = len(cfg["chords"])
    chord_len = duration_sec / n_chords
    overlap = int(CHORD_OVERLAP * SAMPLE_RATE)

    for i, ratios in enumerate(cfg["chords"]):
        start = max(0, int(i * chord_len * SAMPLE_RATE) - overlap // 2)
        end = min(int((i + 1) * chord_len * SAMPLE_RATE) + overlap // 2, n)
        seg_t = t[start:end]                 # global time → continuous phase
        seg = np.zeros(end - start)
        for r in ratios:
            seg += _pad_voice(cfg["root"] * r, seg_t)
        env = _cosine_window(end - start, overlap)
        audio[start:end] += seg * env * 0.055

    # ── Soft air layer (very quiet, heavily low-passed) ──────────
    air = rng.normal(0, 0.0015, n)
    kernel = np.ones(24) / 24.0              # stronger low-pass than before
    air = np.convolve(air, kernel, mode="same")
    audio += air

    # ── Master fades ─────────────────────────────────────────────
    fade_in = int(0.8 * SAMPLE_RATE)
    fade_out = int(2.0 * SAMPLE_RATE)
    audio[:fade_in] *= 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, fade_in))
    audio[-fade_out:] *= 0.5 + 0.5 * np.cos(np.linspace(0, np.pi, fade_out))

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
