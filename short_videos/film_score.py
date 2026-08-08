"""
Film Score Engine — mood-matched soundtracks for every film.

Moods:
    rockabilly     - the Ace Cafe groove (walking bass, backbeat)
    western        - slow shuffle, plucked twang (Karplus-Strong)
    elegant_waltz  - 3/4 plucked harp-like waltz with warm pads
    epic           - slow pulse, drone fifths, wind, rising energy

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


MOODS = {
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
    for scene_idx, effect in film.get("sfx", {}).items():
        at = title_sec + scene_idx * scene_sec
        fx = SFX[effect](rng, scene_sec)
        _add(audio, fx, at)

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
