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


def _exhaust_ir():
    """Impulse response of an exhaust pipe: decaying low resonance."""
    n = int(0.035 * SR)
    t = np.arange(n) / SR
    ir = (np.sin(2 * np.pi * 105 * t) * 0.9
          + np.sin(2 * np.pi * 210 * t) * 0.45
          + np.sin(2 * np.pi * 330 * t) * 0.2)
    return ir * np.exp(-t * 120)


def _engine_from_rpm(rng, rpm, amp):
    """
    Parallel-twin 4-stroke cafe racer from an RPM curve:
    a combustion pulse train convolved with an exhaust resonance,
    plus rpm-tracking intake drone and modulated exhaust hiss.
    rpm and amp are per-sample arrays.
    """
    n = len(rpm)
    fires_per_sec = rpm / 60.0            # twin 4-stroke: one bang per rev
    phase = np.cumsum(fires_per_sec) / SR
    # pulse at every integer phase crossing, strength slightly random
    crossings = np.diff(np.floor(phase), prepend=phase[0]) > 0
    pulses = np.zeros(n)
    idx = np.nonzero(crossings)[0]
    pulses[idx] = 0.8 + 0.4 * rng.random(len(idx))
    engine = np.convolve(pulses, _exhaust_ir(), mode="same")
    # intake drone follows rpm
    t = np.arange(n) / SR
    drone_phase = 2 * np.pi * np.cumsum(rpm / 60.0 * 2.0) / SR
    engine += 0.25 * np.sin(drone_phase)
    # exhaust hiss, louder with rpm
    hiss = rng.normal(0, 1.0, n)
    hiss = np.convolve(hiss, np.ones(6) / 6.0, mode="same")
    engine += hiss * 0.08 * (rpm / rpm.max())
    return engine * amp


def _seg_times(n):
    return np.arange(n) / SR


def _engine_launch(rng, dur):
    """Idle → rev blip → hard acceleration through two gear shifts."""
    n = int(dur * SR)
    t = _seg_times(n)
    rpm = np.full(n, 1300.0)
    rpm += 2500 * np.exp(-((t - 0.5) / 0.18) ** 2)          # warning blip
    accel = np.clip((t - 1.0) / (dur - 1.0), 0, 1)
    rpm += accel * 6000
    for shift_t in (dur * 0.55, dur * 0.8):                  # gear shifts
        rpm -= 1800 * np.clip((t - shift_t) / 0.12, 0, 1) * np.exp(
            -np.clip(t - shift_t, 0, None) / 0.5)
    amp = np.clip(0.4 + accel * 0.6, 0, 1)
    return _engine_from_rpm(rng, np.clip(rpm, 900, 8200), amp)


def _engine_corner(rng, dur):
    """High rpm, rolls off into the bend, drives hard out of it."""
    n = int(dur * SR)
    t = _seg_times(n)
    rpm = 6600 - 1400 * np.exp(-((t - dur * 0.4) / 0.5) ** 2)
    rpm += np.clip((t - dur * 0.6) / (dur * 0.4), 0, 1) * 1400
    amp = np.full(n, 0.85)
    return _engine_from_rpm(rng, rpm, amp)


def _engine_pass(rng, dur):
    """The classic full-throttle doppler pass-by."""
    n = int(dur * SR)
    t = _seg_times(n)
    mid = dur * 0.5
    doppler = 1.0 + 0.14 * np.tanh((mid - t) / 0.35)         # high→low pitch
    rpm = 7400 * doppler
    dist = np.abs(t - mid) / (dur * 0.5)
    amp = np.clip(1.15 - dist, 0.25, 1.0) ** 1.6             # swell and fade
    return _engine_from_rpm(rng, rpm, amp)


def _engine_approach(rng, dur):
    """Head-on: distant wail growing to full roar."""
    n = int(dur * SR)
    t = _seg_times(n)
    rpm = 7000 + 600 * np.sin(2 * np.pi * 0.8 * t)
    amp = np.clip((t / dur) ** 1.4, 0.1, 1.0)
    return _engine_from_rpm(rng, rpm, amp)


def _add(audio, snippet, at_sec):
    start = int(at_sec * SR)
    end = min(start + len(snippet), len(audio))
    if start < len(audio):
        audio[start:end] += snippet[: end - start]


def build_score(duration_sec: float, out_path: str,
                band_in_sec: float, race_span: tuple[float, float],
                seed: int = 1959, engine_track=None) -> None:
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
            if t_cursor < band_in_sec:
                note = note * 0.55           # intro stays intimate
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

    # ── engine layer: real recordings when provided, else synth ──
    r0, r1 = race_span
    if r1 > r0:
        if engine_track is not None:
            engines = engine_track[:n].copy()
            if len(engines) < n:
                engines = np.concatenate([engines, np.zeros(n - len(engines))])
        else:
            seg = (r1 - r0) / 4.0            # launch, corner, pass, approach
            engines = np.zeros(n)
            _add(engines, _engine_launch(rng, seg), r0)
            _add(engines, _engine_corner(rng, seg), r0 + seg)
            _add(engines, _engine_pass(rng, seg), r0 + 2 * seg)
            _add(engines, _engine_approach(rng, seg), r0 + 3 * seg)
            eng_rms = (np.sqrt((engines[engines != 0] ** 2).mean())
                       if engines.any() else 0)
            if eng_rms > 0:
                engines = engines / eng_rms * 0.22
        # duck the music under the engines so the roar reads clearly
        duck = np.ones(n)
        i0, i1 = int(r0 * SR), min(int(r1 * SR), n)
        duck[i0:i1] = 0.55
        ramp = int(0.4 * SR)
        if i0 > ramp:
            duck[i0 - ramp:i0] = np.linspace(1.0, 0.55, ramp)
        if i1 + ramp < n:
            duck[i1:i1 + ramp] = np.linspace(0.55, 1.0, ramp)
        audio *= duck
        audio += engines

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

    # gentle tape-style saturation: glues the mix, vintage warmth
    audio = np.tanh(audio * 1.6) / np.tanh(1.6)

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
