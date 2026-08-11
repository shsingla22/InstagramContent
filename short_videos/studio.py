"""
Studio — the production layer for the score engine.

Upgrades the mathematically-synthesized sound toward record quality:
layered drum voices (sub+click kick, banded snare, metallic hats)
with humanized timing and velocity, a synthetic-impulse room reverb
applied by FFT convolution, parallel "glue" compression, and a
mastering stage that targets streaming loudness (~-14 LUFS) with a
true peak ceiling.

Also home of STEED's THEME — the frozen 3.5 s sonic logo (drum
pickup, walking bass, signature twang lick ending in a rising
whinny-like bend over an engine rumble) that opens every episode
identically, so the sound itself becomes recognizable.
"""

import numpy as np

from short_videos.film_score import SFX, _crash, _pluck, _slapback
from short_videos.rockabilly_score import (
    BARS, BEAT, SR, SWING, _add, _bass_note, _env,
)


def _fft_convolve(sig, ir):
    n = len(sig) + len(ir) - 1
    size = 1 << (n - 1).bit_length()
    out = np.fft.irfft(np.fft.rfft(sig, size) * np.fft.rfft(ir, size), size)
    return out[:n]


def room(sig, wet=0.16, decay=22.0, dur=0.22, seed=99):
    """Small live room: exponentially decaying noise IR, low-cut."""
    rng = np.random.default_rng(seed)
    m = int(dur * SR)
    t = np.arange(m) / SR
    ir = rng.normal(0, 1, m) * np.exp(-t * decay)
    ir -= np.convolve(ir, np.ones(64) / 64.0, mode="same")   # low cut
    ir /= np.abs(ir).sum() ** 0.5
    return sig + _fft_convolve(sig, ir)[: len(sig)] * wet


def glue(sig, amount=0.4, drive=2.2):
    """Parallel (New York) compression: crushed copy blended under."""
    crushed = np.tanh(sig * drive) / drive
    return sig * (1 - amount) + crushed * amount * drive


def master(audio, target_rms_db=-16.0, ceiling=0.92):
    """Gated-RMS loudness normalization (~-14 LUFS) + soft limiter."""
    frame = int(0.4 * SR)
    n_frames = len(audio) // frame
    if n_frames:
        frames = audio[: n_frames * frame].reshape(n_frames, frame)
        rms = np.sqrt((frames ** 2).mean(axis=1))
        loud = rms[rms > rms.max() * 0.1]
        level = loud.mean() if len(loud) else rms.max()
    else:
        level = np.sqrt((audio ** 2).mean())
    if level > 0:
        audio = audio * (10 ** (target_rms_db / 20) / level)
    audio = np.tanh(audio * 1.15) / np.tanh(1.15)
    peak = np.abs(audio).max()
    if peak > ceiling:
        audio = audio / peak * ceiling
    return audio


# ── upgraded drum voices ─────────────────────────────────────────────

def kick2(vel=1.0):
    n = int(0.17 * SR)
    t = np.arange(n) / SR
    sweep = 115 * np.exp(-t * 26) + 41
    sub = np.sin(2 * np.pi * np.cumsum(sweep) / SR)
    click = np.random.default_rng(3).normal(0, 1, int(0.002 * SR))
    click -= np.convolve(click, np.ones(8) / 8.0, mode="same") * 0.5
    body = np.sin(2 * np.pi * 68 * t) * np.exp(-t * 34)
    out = sub * np.exp(-t * 17) + body * 0.5
    out[: len(click)] += click * 0.35
    return out * _env(n, 4, n // 3) * 0.95 * vel


def snare2(rng, vel=1.0):
    n = int(0.16 * SR)
    t = np.arange(n) / SR
    noise = rng.normal(0, 1, n)
    bright = noise - np.convolve(noise, np.ones(10) / 10.0, mode="same")
    body = np.sin(2 * np.pi * (192 - 40 * t / t[-1]) * t) * np.exp(-t * 38)
    wires = bright * np.exp(-t * 24)
    wires += np.roll(wires, int(0.0021 * SR)) * 0.5     # wire flutter
    return (body * 0.55 + wires * 0.5) * _env(n, 6, n // 2) * 0.6 * vel


def hat2(rng, vel=1.0, open_=False):
    n = int((0.16 if open_ else 0.05) * SR)
    t = np.arange(n) / SR
    noise = rng.normal(0, 1, n)
    noise -= np.convolve(noise, np.ones(6) / 6.0, mode="same")
    metal = sum(np.sin(2 * np.pi * f * t)
                for f in (6317.0, 7433.0, 9101.0, 11267.0)) * 0.08
    decay = 9 if open_ else 55
    return (noise * 0.75 + metal) * np.exp(-t * decay) * 0.17 * vel


# ── the upgraded rockabilly bed (STEED's series sound) ───────────────

def steed_bed(rng, dur):
    """Swung rockabilly groove rendered with the studio drum voices,
    humanized timing/velocity, room and glue on the buses."""
    n = int(dur * SR)
    bass = np.zeros(n)
    drums = np.zeros(n)
    gtr = np.zeros(n)

    def j():                                        # human timing
        return rng.normal(0, 0.006)

    def jat(at):
        return max(0.0, at + j())

    def v():                                        # human velocity
        return rng.uniform(0.85, 1.12)

    t_cursor, bar_i = 0.0, 0
    while t_cursor < dur - BEAT:
        walk = BARS[bar_i % len(BARS)]
        for beat_i in range(4):
            if t_cursor >= dur - BEAT:
                break
            at = t_cursor
            _add(bass, _bass_note(walk[beat_i], BEAT * 0.95) * 0.9, jat(at))
            _add(drums, hat2(rng, v()), jat(at))
            _add(drums, hat2(rng, v() * 0.7), jat(at + BEAT * SWING))
            if beat_i % 2 == 0:
                _add(drums, kick2(v()), jat(at))
            else:
                _add(drums, snare2(rng, v()), jat(at))
            if beat_i % 2 == 1:                     # off-beat twang stab
                root = walk[beat_i]
                _add(gtr, _slapback(_pluck(root * 2, BEAT * 0.8, 0.8),
                                    0.09, 0.32) * 0.5,
                     jat(at + BEAT * SWING))
            t_cursor += BEAT
        bar_i += 1

    drums = room(glue(drums, 0.5, 2.6), wet=0.14)
    bass = glue(bass, 0.35, 2.0)
    gtr = room(gtr, wet=0.2)
    return (drums + bass + gtr)[:n]


# ── STEED's theme: the 3.5 s sonic logo ─────────────────────────────

THEME_SECONDS = 3.5


def steed_theme():
    """Frozen signature: crash + drum pickup, four walking bass notes,
    the twang lick, and the rising whinny bend over an engine rumble.
    Fully deterministic — identical in every episode."""
    rng = np.random.default_rng(5)
    n = int(THEME_SECONDS * SR)
    audio = np.zeros(n)

    _add(audio, _crash(rng) * 0.7, 0.0)
    for i, f in enumerate([55.0, 69.3, 82.41, 98.0]):    # A walk up
        _add(audio, _bass_note(f, BEAT * 0.95) * 0.95, i * BEAT)
        _add(audio, kick2(1.0 if i % 2 == 0 else 0.8), i * BEAT)
        _add(audio, hat2(rng, 1.0), i * BEAT)
        _add(audio, hat2(rng, 0.7), i * BEAT + BEAT * SWING)
        if i % 2 == 1:
            _add(audio, snare2(rng, 1.0), i * BEAT)
    # snare pickup into the lick
    for k in range(3):
        _add(audio, snare2(rng, 0.55 + 0.2 * k),
             4 * BEAT - 0.18 + k * 0.06)

    LICK = [(0.0, 659.26, 0.4), (0.3, 587.33, 0.35), (0.6, 493.88, 0.35),
            (0.9, 440.0, 0.55)]
    base = 4 * BEAT
    for off, f, d in LICK:
        _add(audio, _slapback(_pluck(f, d, 0.85), 0.09, 0.35) * 0.62,
             base + off)
    # the whinny: bend B4 → E5 with wide vibrato
    from short_videos.film_score import _lead_note
    _add(audio, _lead_note(493.88, 0.65, 659.26, 0.5), base + 1.25)
    _add(audio, SFX["engine"](rng, 2.2) * 0.35, 0.9)

    audio = room(glue(audio, 0.45, 2.4), wet=0.15)
    fade = int(0.25 * SR)
    audio[-fade:] *= np.linspace(1, 0.4, fade)
    return audio[:n]
