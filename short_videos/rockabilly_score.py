"""
Rockabilly Score — story-synced soundtrack, synthesized with numpy.

The jukebox is the story's clock, so the music follows the plot:

    title card      → lone upright bass, quiet
    cafe            → bass + brushed hi-hat
    jukebox scene   → THE COIN DROPS: full band kicks in
    launch + race   → driving rockabilly groove + engine rumble
    return          → groove resolves, triumphant last chord
    outro           → ring-out and fade

Everything is synthesized (no samples): walking upright bass
(triangle-ish), kick, snare (noise burst), swung hi-hat, and a
low sawtooth engine layer under the racing scenes. 44.1 kHz stereo.
"""

import wave

import numpy as np

SR = 44100
BPM = 152
BEAT = 60.0 / BPM
SWING = 0.63           # swung eighths: first eighth gets this share

# A-blues walking pattern (frequencies, Hz) — A1/D2/E2 territory
A1, Cs2, D2, E2, G2 = 55.0, 69.3, 73.42, 82.41, 98.0
WALK_A = [A1, Cs2, E2, G2]
WALK_D = [D2, 91.0, 110.0, 91.0]
WALK_E = [E2, 103.83, 123.47, 103.83]

# 12-bar-ish loop of walking-bass bars
BARS = [WALK_A, WALK_A, WALK_D, WALK_A, WALK_E, WALK_D, WALK_A, WALK_E]


def _env(n, attack, decay):
    e = np.ones(n)
    a = min(attack, n)
    e[:a] = np.linspace(0, 1, a)
    d = min(decay, n)
    e[-d:] *= np.linspace(1, 0, d)
    return e


def _bass_note(freq, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    # triangle-ish pluck with a thump of second harmonic
    wave_ = (np.sin(2 * np.pi * freq * t)
             + 0.4 * np.sin(2 * np.pi * freq * 2 * t)
             + 0.15 * np.sin(2 * np.pi * freq * 3 * t))
    return wave_ * _env(n, int(0.004 * SR), int(0.6 * n)) * 0.5


def _kick(dur=0.12):
    n = int(dur * SR)
    t = np.arange(n) / SR
    freq = np.linspace(95, 45, n)          # pitch drop = thump
    return np.sin(2 * np.pi * freq * t) * _env(n, 20, n - 40) * 0.9


def _snare(rng, dur=0.11):
    n = int(dur * SR)
    noise = rng.normal(0, 1, n)
    kernel = np.ones(4) / 4.0              # tame the highs a little
    noise = np.convolve(noise, kernel, mode="same")
    body = np.sin(2 * np.pi * 190 * np.arange(n) / SR) * 0.4
    return (noise * 0.55 + body) * _env(n, 8, n - 20) * 0.55


def _hat(rng, dur=0.04):
    n = int(dur * SR)
    noise = rng.normal(0, 1, n)
    noise -= np.convolve(noise, np.ones(8) / 8.0, mode="same")  # highpass
    return noise * _env(n, 4, n - 8) * 0.16


def _engine(rng, dur, base=88.0):
    """Low sawtooth rumble with throttle wobble — mixed quietly."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    rpm = base * (1.0 + 0.25 * np.sin(2 * np.pi * 0.31 * t)
                  + 0.12 * np.sin(2 * np.pi * 1.7 * t))
    phase = 2 * np.pi * np.cumsum(rpm) / SR
    saw = 2 * ((phase / (2 * np.pi)) % 1.0) - 1.0
    saw = np.convolve(saw, np.ones(12) / 12.0, mode="same")   # soften
    growl = rng.normal(0, 0.08, n)
    growl = np.convolve(growl, np.ones(32) / 32.0, mode="same")
    return (saw * 0.6 + growl) * _env(n, int(0.4 * SR), int(0.6 * SR))


def _add(audio, snippet, at_sec):
    start = int(at_sec * SR)
    end = min(start + len(snippet), len(audio))
    if start < len(audio):
        audio[start:end] += snippet[: end - start]


def build_score(duration_sec: float, out_path: str,
                band_in_sec: float, race_span: tuple[float, float],
                seed: int = 1959) -> None:
    """
    Render the score.

    band_in_sec     - when the full band kicks in (the coin drop)
    race_span       - (start, end) seconds of the racing scenes,
                      where the engine layer runs
    """
    rng = np.random.default_rng(seed)
    n = int(duration_sec * SR)
    audio = np.zeros(n)

    # ── walking bass through the whole piece ─────────────────────
    t_cursor = 0.0
    bar_i = 0
    while t_cursor < duration_sec - BEAT:
        walk = BARS[bar_i % len(BARS)]
        for beat_i in range(4):
            if t_cursor >= duration_sec - BEAT:
                break
            note = _bass_note(walk[beat_i], BEAT * 0.95)
            _add(audio, note, t_cursor)
            t_cursor += BEAT
        bar_i += 1

    # ── drums ────────────────────────────────────────────────────
    t_cursor = 0.0
    beat_count = 0
    while t_cursor < duration_sec - BEAT:
        in_band = t_cursor >= band_in_sec
        # hats: swung eighths from the start (brushed feel pre-band)
        vol = 1.0 if in_band else 0.5
        h1 = _hat(rng) * vol
        h2 = _hat(rng) * vol * 0.7
        _add(audio, h1, t_cursor)
        _add(audio, h2, t_cursor + BEAT * SWING)
        if in_band:
            if beat_count % 2 == 0:
                _add(audio, _kick(), t_cursor)
            else:
                _add(audio, _snare(rng), t_cursor)   # backbeat
        t_cursor += BEAT
        beat_count += 1

    # ── engine layer under the races ─────────────────────────────
    r0, r1 = race_span
    if r1 > r0:
        _add(audio, _engine(rng, r1 - r0) * 0.16, r0)

    # ── closing chord ring-out at the return ─────────────────────
    ring_at = duration_sec - 5.5
    nring = int(3.5 * SR)
    t = np.arange(nring) / SR
    chord = sum(np.sin(2 * np.pi * f * t) for f in (110.0, 138.6, 164.8, 220.0))
    _add(audio, chord * _env(nring, int(0.02 * SR), int(2.8 * SR)) * 0.12, ring_at)

    # ── master fades + normalize ─────────────────────────────────
    fade_in = int(0.6 * SR)
    fade_out = int(2.2 * SR)
    audio[:fade_in] *= 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, fade_in))
    audio[-fade_out:] *= 0.5 + 0.5 * np.cos(np.linspace(0, np.pi, fade_out))

    peak = np.abs(audio).max()
    if peak > 0:
        audio = audio / peak * 0.55

    delay = int(0.012 * SR)
    right = np.concatenate([np.zeros(delay), audio[:-delay]])
    stereo = np.stack([audio, right], axis=1)
    pcm = (stereo * 32767).astype(np.int16)
    with wave.open(out_path, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(pcm.tobytes())
