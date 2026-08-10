"""
Film Score Engine — mood-matched soundtracks for every film.

Moods:
    rockabilly     - the Ace Cafe groove (walking bass, backbeat)
    western        - slow shuffle, plucked twang (Karplus-Strong)
    elegant_waltz  - 3/4 plucked harp-like waltz with warm pads
    epic           - slow pulse, drone fifths, wind, rising energy
    classic_rock   - open-road driving rock: power chords, backbeat,
                     pentatonic lead (the riding soundtrack)

Scene-cued SFX (all synthesized except the engine recordings):
    hoofbeats - four-beat canter pattern of damped thumps
    ticks     - workshop tapping (hammer / stitching rhythm)
    rain      - filtered noise shower
    wind      - slow low-passed noise swells
    engine    - real motorcycle recordings (sfx_engine sources)

The builder takes the film config + scene timings and renders one
mastered stereo WAV.
"""

import os
import sys
import wave

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from short_videos.rockabilly_score import (
    SR, _add, _bass_note, _env, _hat, _kick, _snare,
)

# ── extra instruments ────────────────────────────────────────────────

def _pluck(freq, dur, bright=0.5):
    """Karplus-Strong plucked string — guitar/harp depending on bright."""
    n = int(dur * SR)
    period = max(2, int(SR / freq))
    buf = np.random.uniform(-1, 1, period)
    out = np.empty(n)
    damp = 0.994 + 0.005 * (1 - bright)
    for i in range(n):
        out[i] = buf[i % period]
        buf[i % period] = damp * 0.5 * (buf[i % period] + buf[(i + 1) % period])
    return out * _env(n, int(0.002 * SR), int(0.5 * n)) * 0.5


def _pad_chord(freqs, dur, level=0.05):
    n = int(dur * SR)
    t = np.arange(n) / SR
    seg = sum(np.sin(2 * np.pi * f * t) + 0.2 * np.sin(2 * np.pi * f * 2.003 * t)
              for f in freqs)
    fade = int(0.4 * SR)
    e = np.ones(n)
    e[:min(fade, n)] = np.linspace(0, 1, min(fade, n))
    e[-min(fade, n):] *= np.linspace(1, 0.3, min(fade, n))
    return seg * e * level


def _tom(freq=110, dur=0.25):
    n = int(dur * SR)
    t = np.arange(n) / SR
    sweep = np.linspace(freq, freq * 0.6, n)
    return np.sin(2 * np.pi * sweep * t) * _env(n, 30, n - 60) * 0.8


def _crash(rng, dur=1.8):
    """Crash cymbal: high-passed noise with a long exponential wash."""
    n = int(dur * SR)
    noise = rng.normal(0, 1, n)
    noise -= np.convolve(noise, np.ones(12) / 12.0, mode="same") * 0.9
    t = np.arange(n) / SR
    return noise * np.exp(-t * 2.6) * _env(n, 8, int(0.3 * SR)) * 0.5


_CHORD_CACHE = {}


def _power_chord(freq, dur, mute=False, drive=5.0):
    """Distorted electric power chord (root + fifth + octave), double
    tracked with a slight detune, tanh drive, then tone-shaped. Palm
    muted version is darker and chokes fast — the classic chug."""
    key = (round(freq, 2), round(dur, 3), mute)
    if key in _CHORD_CACHE:
        return _CHORD_CACHE[key]
    n = int(dur * SR)
    t = np.arange(n) / SR
    sig = np.zeros(n)
    for root in (freq, freq * 1.5, freq * 2.0):
        for det in (0.9975, 1.0025):
            f = root * det
            for k in range(1, min(30, int(4500 / f)) + 1):
                sig += np.sin(2 * np.pi * f * k * t + 0.7 * k) / k
    sig = np.tanh(sig * drive / 10.0)
    kern = 16 if mute else 7                     # palm mute = darker tone
    sig = np.convolve(sig, np.ones(kern) / kern, mode="same")
    if mute:
        env = _env(n, int(0.002 * SR), max(2, int(0.3 * n))) * np.exp(-t * 11.0)
    else:
        env = _env(n, int(0.003 * SR), max(2, int(0.3 * n))) * np.exp(-t * 0.9)
    out = sig * env
    _CHORD_CACHE[key] = out
    return out


def _lead_note(f0, dur, f1=None, level=1.0):
    """Overdriven lead-guitar note with glide (bend) and late vibrato."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    freq = np.linspace(f0, f1 or f0, n)
    vib = 1 + 0.006 * np.sin(2 * np.pi * 5.5 * t) * np.minimum(1, t / 0.25)
    phase = 2 * np.pi * np.cumsum(freq * vib) / SR
    sig = sum(np.sin(phase * k) / k for k in range(1, 9))
    sig = np.tanh(sig * 3.5)
    sig = np.convolve(sig, np.ones(5) / 5.0, mode="same")
    return (sig * _env(n, int(0.004 * SR), max(2, int(0.3 * n)))
            * np.exp(-t * 1.1) * level)


# ── moods ────────────────────────────────────────────────────────────

def _mood_western(rng, dur, band_in):
    """Slow two-beat shuffle with plucked twang — trail music."""
    audio = np.zeros(int(dur * SR))
    bpm, beat = 96, 60.0 / 96
    E, A, B = 82.41, 110.0, 123.47
    bars = [[E, B], [A, E], [E, B], [B, A]]
    t, bar = 0.0, 0
    while t < dur - beat:
        root, alt = bars[bar % len(bars)]
        for b in range(4):
            if t >= dur - beat:
                break
            quiet = 0.5 if t < band_in else 1.0
            _add(audio, _bass_note(root if b % 2 == 0 else alt, beat * 0.9) * quiet, t)
            if t >= band_in:
                if b in (1, 3):
                    _add(audio, _snare(rng) * 0.4, t)          # brushy backbeat
                # twangy pluck answering on the off-beats
                _add(audio, _pluck(root * 2, beat * 0.8, 0.8) * 0.5, t + beat * 0.5)
            t += beat
        bar += 1
    return audio


def _mood_waltz(rng, dur, band_in):
    """3/4 plucked waltz — bass on 1, harp chords on 2 and 3."""
    audio = np.zeros(int(dur * SR))
    bpm, beat = 100, 60.0 / 100
    # Cmaj-Am-F-G in a gentle loop (roots + chord tones)
    prog = [(130.8, [261.6, 329.6, 392.0]), (110.0, [220.0, 261.6, 329.6]),
            (87.3, [174.6, 220.0, 261.6]), (98.0, [196.0, 246.9, 293.7])]
    t, bar = 0.0, 0
    while t < dur - 3 * beat:
        root, chord = prog[bar % len(prog)]
        quiet = 0.55 if t < band_in else 1.0
        _add(audio, _bass_note(root, beat * 0.95) * 0.8 * quiet, t)
        for b in (1, 2):
            for i, f in enumerate(chord):
                _add(audio, _pluck(f, beat * 0.9, 0.3) * 0.30 * quiet,
                     t + b * beat + i * 0.012)
        if t >= band_in:
            _add(audio, _pad_chord([root, chord[0] / 2], 3 * beat, 0.03), t)
        t += 3 * beat
        bar += 1
    return audio


def _mood_epic(rng, dur, band_in):
    """Slow pulse, drone fifths, toms building through the journey."""
    audio = np.zeros(int(dur * SR))
    beat = 60.0 / 60
    D, A = 73.42, 110.0
    # continuous drone
    _add(audio, _pad_chord([D, A, D * 2], dur, 0.045), 0)
    t, i = 0.0, 0
    while t < dur - beat:
        intensity = min(1.0, max(0.25, (t - band_in) / (dur * 0.5)))
        if t >= band_in:
            _add(audio, _kick() * 0.9 * intensity, t)
            if i % 2 == 1:
                _add(audio, _tom(90) * 0.5 * intensity, t + beat * 0.5)
            if i % 4 == 3:                       # rolling fill
                for k in range(3):
                    _add(audio, _tom(120 - 15 * k) * 0.35 * intensity,
                         t + beat * (0.625 + 0.125 * k))
        else:
            _add(audio, _kick() * 0.35, t)       # distant heartbeat
        t += beat
        i += 1
    return audio


def _mood_rockabilly(rng, dur, band_in):
    """The Ace Cafe groove, reused from the original score."""
    from short_videos.rockabilly_score import BARS, BEAT, SWING
    audio = np.zeros(int(dur * SR))
    t, bar = 0.0, 0
    while t < dur - BEAT:
        walk = BARS[bar % len(BARS)]
        for b in range(4):
            if t >= dur - BEAT:
                break
            note = _bass_note(walk[b], BEAT * 0.95)
            _add(audio, note * (0.55 if t < band_in else 1.0), t)
            t += BEAT
        bar += 1
    t, cnt = 0.0, 0
    while t < dur - BEAT:
        vol = 1.0 if t >= band_in else 0.5
        _add(audio, _hat(rng) * vol, t)
        _add(audio, _hat(rng) * vol * 0.7, t + BEAT * SWING)
        if t >= band_in:
            _add(audio, _kick() if cnt % 2 == 0 else _snare(rng), t)
        t += BEAT
        cnt += 1
    return audio


def _mood_storm(rng, dur, band_in):
    """Brooding British heritage: low drone, slow heartbeat pulse,
    dark plucked figures that warm as the story resolves."""
    audio = np.zeros(int(dur * SR))
    beat = 60.0 / 70                           # slow, deliberate
    D, F, A_ = 73.42, 87.31, 110.0             # D minor world
    # evolving drone: minor early, warms toward the end
    half = dur * 0.62
    _add(audio, _pad_chord([D, F, A_], half, 0.05), 0)
    _add(audio, _pad_chord([D, 92.5, A_, 146.8], dur - half + 1, 0.055), half - 1)
    t, i = 0.0, 0
    while t < dur - beat:
        grown = min(1.0, max(0.3, (t - band_in) / (dur * 0.45)))
        _add(audio, _kick() * (0.5 if t < band_in else 0.85) * grown, t)
        if t >= band_in and i % 2 == 1:
            _add(audio, _kick() * 0.35 * grown, t + beat * 0.18)   # heartbeat double
        # sparse dark plucks answering the pulse
        if i % 4 == 2:
            freq = [D * 2, F * 2, A_ * 2, D * 3][(i // 4) % 4]
            _add(audio, _pluck(freq, beat * 1.6, 0.25) * 0.4 * grown, t + beat * 0.5)
        t += beat
        i += 1
    return audio


def _mood_classic_rock(rng, dur, band_in):
    """Open-road classic rock in E, full band from the very first
    beat: crash on the downbeat, driving kick/snare, warm E–D–A
    power chords with light chug fills, locked eighth-note bass,
    and an anthemic E-major-pentatonic lead melody that carries
    the whole piece.  (band_in is unused — the band never waits.)"""
    audio = np.zeros(int(dur * SR))
    beat = 60.0 / 112                            # confident highway tempo
    bar = 4 * beat
    E, D, A_ = 82.41, 73.42, 110.0
    PROG = [E, D, A_, E]
    groove_end = dur - 1.5

    # rhythm guitar + bass
    t, bar_i = 0.0, 0
    while t < groove_end:
        root = PROG[bar_i % len(PROG)]
        _add(audio, _power_chord(root, beat * 2.2, drive=3.6) * 0.5, t)
        _add(audio, _pluck(root * 4, beat * 2.0, bright=0.35) * 0.22, t)
        for e8 in (5, 6, 7):                     # light chug into the next bar
            at = t + e8 * beat / 2
            if at >= groove_end:
                break
            _add(audio, _power_chord(root, beat * 0.5, mute=True,
                                     drive=3.6) * 0.34, at)
        for e8 in range(8):
            at = t + e8 * beat / 2
            if at >= groove_end:
                break
            _add(audio, _bass_note(root / 2, beat * 0.45) * 0.8, at)
        t += bar
        bar_i += 1

    # drums: full groove from the downbeat
    t, beat_i = 0.0, 0
    while t < groove_end:
        _add(audio, _hat(rng) * 0.85, t)
        _add(audio, _hat(rng) * 0.55, t + beat / 2)
        if beat_i % 2 == 0:
            _add(audio, _kick() * 1.1, t)
            if beat_i % 4 == 2:                  # push into the backbeat
                _add(audio, _kick() * 0.7, t + beat / 2)
        else:
            _add(audio, _snare(rng) * 1.1, t)
        t += beat
        beat_i += 1

    # crashes: on the very first beat, then the top of every 4 bars
    t = 0.0
    while t < groove_end:
        _add(audio, _crash(rng) * (1.0 if t == 0.0 else 0.55), t)
        t += 4 * bar

    # lead melody: 4-bar anthemic hook (E major pentatonic), repeating
    E4, Fs4, Gs4, A4, B4, Cs5, E5 = (329.63, 369.99, 415.30, 440.0,
                                     493.88, 554.37, 659.26)
    HOOK = [
        (0.0, E4, 0.75, None), (0.75, Gs4, 0.75, None), (1.5, B4, 2.3, None),
        (4.0, A4, 0.75, None), (4.75, B4, 0.75, None),
        (5.5, A4, 0.75, None), (6.25, Fs4, 1.6, None),
        (8.0, Cs5, 1.5, None), (9.5, B4, 0.75, None), (10.25, A4, 1.6, None),
        (12.0, B4, 1.0, None), (13.0, B4, 2.8, E5),    # long bend up to E
    ]
    t = 0.0
    while t < groove_end - bar:
        for off, f0, ndur, f1 in HOOK:
            at = t + off * beat
            if at >= groove_end:
                break
            _add(audio, _lead_note(f0, ndur * beat, f1, 0.42), at)
        t += 4 * bar
    return audio


def _slapback(sig, delay_s=0.09, level=0.35):
    d = int(delay_s * SR)
    out = sig.copy()
    out[d:] += sig[:-d] * level
    return out


def _mood_retro_ride(rng, dur, band_in):
    """1950s retro riding groove, full band from the first beat:
    swung shuffle, walking upright bass over a 12-bar loop in A,
    brushed backbeat, twangy off-beat guitar stabs with slapback
    echo, and a catchy A-pentatonic twang lead that repeats like a
    chorus. band_in only places an extra crash accent (title card)."""
    audio = np.zeros(int(dur * SR))
    beat = 60.0 / 138                            # bright shuffle
    swing = 0.66
    bar = 4 * beat
    A_, D, E = 110.0, 146.83, 164.81             # A2 D3 E3 roots
    PROG = [A_, A_, D, A_, E, D, A_, E]
    WALKS = {A_: [110.0, 138.59, 164.81, 196.0],
             D: [146.83, 185.0, 220.0, 185.0],
             E: [164.81, 207.65, 246.94, 207.65]}
    groove_end = dur - 1.4

    # walking bass + twang stabs on the off-beats
    t, bar_i = 0.0, 0
    while t < groove_end:
        root = PROG[bar_i % len(PROG)]
        for b in range(4):
            at = t + b * beat
            if at >= groove_end:
                break
            _add(audio, _bass_note(WALKS[root][b] / 2, beat * 0.95) * 0.85, at)
            stab = sum(_pluck(f, beat * 0.55, 0.75) for f in
                       (root * 2, root * 2 * 1.25, root * 2 * 1.5))
            _add(audio, _slapback(stab) * 0.20, at + beat * swing)
        t += bar
        bar_i += 1

    # drums: brushed shuffle with backbeat, from the downbeat
    t, beat_i = 0.0, 0
    while t < groove_end:
        _add(audio, _hat(rng) * 0.8, t)
        _add(audio, _hat(rng) * 0.5, t + beat * swing)
        if beat_i % 2 == 0:
            _add(audio, _kick() * 0.95, t)
        else:
            _add(audio, _snare(rng) * 0.95, t)
        t += beat
        beat_i += 1

    # crashes: downbeat, the title card, then every 4 bars
    _add(audio, _crash(rng) * 0.9, 0.0)
    if band_in > 0.5:
        _add(audio, _crash(rng) * 0.8, band_in)
    t = 4 * bar
    while t < groove_end:
        _add(audio, _crash(rng) * 0.45, t)
        t += 4 * bar

    # twang lead chorus: A major pentatonic, swung, with slapback
    A4, B4, Cs5, E5, Fs5, A5 = 440.0, 493.88, 554.37, 659.26, 739.99, 880.0
    HOOK = [
        (0.0, E5, 0.6), (0.66, Cs5, 0.4), (1.0, A4, 1.6),
        (2.66, B4, 0.4), (3.0, Cs5, 1.6),
        (4.0, E5, 0.6), (4.66, Fs5, 0.4), (5.0, A5, 1.6),
        (6.66, Fs5, 0.4), (7.0, E5, 1.8),
        (8.0, Cs5, 0.6), (8.66, B4, 0.4), (9.0, A4, 1.6),
        (10.66, B4, 0.4), (11.0, Cs5, 0.9), (12.0, E5, 0.9),
        (13.0, A4, 2.6),
    ]
    t = bar                                      # lead enters bar 2
    while t < groove_end - bar:
        for off, f0, ndur in HOOK:
            at = t + off * beat
            if at >= groove_end:
                break
            note = _slapback(_pluck(f0, ndur * beat, 0.9))
            _add(audio, note * 0.62, at)
        t += 4 * bar
    return audio


MOODS = {
    "storm_heritage": _mood_storm,
    "classic_rock": _mood_classic_rock,
    "retro_ride": _mood_retro_ride,
    "western": _mood_western,
    "elegant_waltz": _mood_waltz,
    "epic": _mood_epic,
    "rockabilly": _mood_rockabilly,
}


# ── sound effects ────────────────────────────────────────────────────

def _hoof(rng):
    n = int(0.05 * SR)
    noise = rng.normal(0, 1, n)
    noise = np.convolve(noise, np.ones(20) / 20.0, mode="same")
    thump = np.sin(2 * np.pi * 70 * np.arange(n) / SR) * 0.6
    return (noise * 0.5 + thump) * _env(n, 8, n - 16)


def sfx_hoofbeats(rng, dur):
    """Canter rhythm: da-da-DUM ... da-da-DUM."""
    out = np.zeros(int(dur * SR))
    t = 0.15
    while t < dur - 0.5:
        for off, amp in ((0.0, 0.5), (0.14, 0.55), (0.30, 0.9)):
            _add(out, _hoof(rng) * amp, t + off)
        t += 0.62
    return out * 0.5


def sfx_ticks(rng, dur):
    """Workshop rhythm: hammer taps / stitching clicks."""
    out = np.zeros(int(dur * SR))
    t = 0.2
    while t < dur - 0.3:
        n = int(0.03 * SR)
        tick = rng.normal(0, 1, n)
        tick -= np.convolve(tick, np.ones(6) / 6.0, mode="same")
        tick += np.sin(2 * np.pi * 900 * np.arange(n) / SR) * 0.4
        _add(out, tick * _env(n, 3, n - 6) * 0.5, t)
        t += 0.42 + 0.1 * rng.random()
    return out * 0.45


def sfx_rain(rng, dur):
    n = int(dur * SR)
    rain = rng.normal(0, 1, n)
    rain = np.convolve(rain, np.ones(3) / 3.0, mode="same")
    swell = 0.8 + 0.2 * np.sin(2 * np.pi * 0.23 * np.arange(n) / SR)
    return rain * swell * _env(n, int(0.4 * SR), int(0.5 * SR)) * 0.16


def sfx_wind(rng, dur):
    n = int(dur * SR)
    wind = rng.normal(0, 1, n)
    wind = np.convolve(wind, np.ones(220) / 220.0, mode="same")
    swell = 0.6 + 0.4 * np.sin(2 * np.pi * 0.11 * np.arange(n) / SR + 1.2)
    return wind * swell * _env(n, int(0.5 * SR), int(0.5 * SR)) * 3.2


def sfx_engine(rng, dur):
    """Slice of the real Yamaha recording, faded."""
    from short_videos.sfx_engine import _fade, _load_mono, _norm_rms, YAMAHA
    yam = _load_mono(YAMAHA)
    start = 6.0 + 8.0 * rng.random()
    seg = yam[int(start * SR):int((start + dur) * SR)].copy()
    seg = _norm_rms(seg, 0.20)
    return _fade(seg, 0.25, 0.4)


SFX = {
    "hoofbeats": sfx_hoofbeats,
    "ticks": sfx_ticks,
    "rain": sfx_rain,
    "wind": sfx_wind,
    "engine": sfx_engine,
}


# ── master builder ───────────────────────────────────────────────────

def build_film_audio(film: dict, duration: float, title_sec: float,
                     scene_sec: float, out_path: str, seed: int = 7) -> None:
    rng = np.random.default_rng(seed)
    n = int(duration * SR)

    band_in = title_sec + film["band_in"] * scene_sec
    audio = MOODS[film["mood"]](rng, duration, band_in)[:n]
    if len(audio) < n:
        audio = np.concatenate([audio, np.zeros(n - len(audio))])

    # scene-cued SFX
    for scene_idx, effects in film.get("sfx", {}).items():
        if isinstance(effects, str):
            effects = [effects]
        at = title_sec + scene_idx * scene_sec
        for effect in effects:
            _add(audio, SFX[effect](rng, scene_sec), at)

    # closing chord + master (same finishing chain as the Ace Cafe film)
    ring_at = duration - 5.5
    nring = int(3.5 * SR)
    t = np.arange(nring) / SR
    chord = sum(np.sin(2 * np.pi * f * t) for f in (110.0, 138.6, 164.8, 220.0))
    _add(audio, chord * _env(nring, int(0.02 * SR), int(2.8 * SR)) * 0.10, ring_at)

    fade_in = int(0.6 * SR)
    fade_out = int(2.2 * SR)
    audio[:fade_in] *= 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, fade_in))
    audio[-fade_out:] *= 0.5 + 0.5 * np.cos(np.linspace(0, np.pi, fade_out))

    audio = np.tanh(audio * 1.6) / np.tanh(1.6)      # tape warmth
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
