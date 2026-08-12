"""
Real-recording engine track — replaces synthesized exhaust.

Sources (Wikimedia Commons, free licenses):
    Jawa 250 exhaust      — period 1950s-60s motorcycle, used for the
                            launch scene's rev-up
    Yamaha RX-100 run     — a real recorded acceleration to top speed,
                            used for the corner, the doppler pass-by,
                            and the head-on approach

Each racing scene gets a purpose-cut slice of real audio with
scene-appropriate shaping (fades, amplitude swells, and a numpy
resampling doppler bend for the pass-by).
"""

import os
import subprocess
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SR = 44100
SFX_DIR = "output/short_videos/sfx"

JAWA = os.path.join(SFX_DIR, "Jawa250_motorbike_exhaust_sound.ogg")
YAMAHA = os.path.join(SFX_DIR, "Yamaha_RX-100_accelerates_to_top_speed.ogg")


def _load_mono(path: str) -> np.ndarray:
    """Decode any audio file to float mono 44.1 kHz via ffmpeg."""
    out = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", path, "-f", "f32le",
         "-ac", "1", "-ar", str(SR), "-"],
        capture_output=True, check=True,
    )
    return np.frombuffer(out.stdout, dtype=np.float32).astype(np.float64)


def _slice_sec(audio: np.ndarray, start: float, dur: float) -> np.ndarray:
    a = int(start * SR)
    return audio[a:a + int(dur * SR)].copy()


def _norm_rms(seg: np.ndarray, target: float = 0.18) -> np.ndarray:
    rms = np.sqrt((seg ** 2).mean())
    return seg * (target / rms) if rms > 0 else seg


def _fade(seg: np.ndarray, fin: float = 0.15, fout: float = 0.25) -> np.ndarray:
    n = len(seg)
    a = int(fin * SR)
    b = int(fout * SR)
    if a > 0:
        seg[:a] *= np.linspace(0, 1, a)
    if b > 0:
        seg[-b:] *= np.linspace(1, 0, b)
    return seg


def _doppler(seg: np.ndarray, bend: float = 0.13) -> np.ndarray:
    """Resample with a time-varying rate: pitch high → low mid-way."""
    n = len(seg)
    t = np.linspace(0, 1, n)
    rate = 1.0 + bend * np.tanh((0.5 - t) / 0.12)      # >1 early, <1 late
    positions = np.cumsum(rate)
    positions *= (n - 1) / positions[-1]
    return np.interp(positions, np.arange(n), seg)


def build_engine_track(duration_sec: float, race_span: tuple[float, float],
                       out_path: str) -> None:
    """Assemble the full-length engine layer from real recordings."""
    jawa = _load_mono(JAWA)
    yamaha = _load_mono(YAMAHA)

    n = int(duration_sec * SR)
    track = np.zeros(n)
    r0, r1 = race_span
    seg_len = (r1 - r0) / 4.0

    def place(seg: np.ndarray, at: float):
        a = int(at * SR)
        b = min(a + len(seg), n)
        track[a:b] += seg[: b - a]

    # 1) launch: Jawa rev-up (its liveliest stretch), building volume
    launch = _norm_rms(_slice_sec(jawa, 13.0, seg_len), 0.20)
    launch *= np.linspace(0.45, 1.0, len(launch))       # pulls away
    place(_fade(launch, 0.2, 0.3), r0)

    # 2) corner: Yamaha mid-run high-rpm wail
    corner = _norm_rms(_slice_sec(yamaha, 9.0, seg_len), 0.24)
    place(_fade(corner, 0.25, 0.25), r0 + seg_len)

    # 3) pass-by: Yamaha slice with doppler bend + swell-and-fade
    pas = _norm_rms(_slice_sec(yamaha, 6.5, seg_len), 0.27)
    pas = _doppler(pas)
    tt = np.linspace(0, 1, len(pas))
    pas *= np.clip(1.25 - 1.7 * np.abs(tt - 0.5), 0.30, 1.0) ** 1.4
    place(_fade(pas, 0.15, 0.3), r0 + 2 * seg_len)

    # 4) approach: Yamaha opening pull, growing from distant to close
    app = _norm_rms(_slice_sec(yamaha, 0.0, seg_len), 0.24)
    app *= np.linspace(0.25, 1.0, len(app)) ** 1.3
    place(_fade(app, 0.2, 0.35), r0 + 3 * seg_len)

    # keep peaks civil; the score's tape saturation does the final glue
    peak = np.abs(track).max()
    if peak > 0.9:
        track *= 0.9 / peak

    track.astype(np.float32).tofile(out_path)


def load_engine_track(path: str, n: int) -> np.ndarray:
    """Read the raw f32 track back and fit it to n samples."""
    track = np.fromfile(path, dtype=np.float32).astype(np.float64)
    if len(track) < n:
        track = np.concatenate([track, np.zeros(n - len(track))])
    return track[:n]
