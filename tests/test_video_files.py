"""Tests for video file integrity, format, and encoding correctness."""
import os
import struct
import subprocess
import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIDEO_DIR = os.path.join(PROJECT_ROOT, "output", "videos")
REEL_FILES = sorted([
    f for f in os.listdir(VIDEO_DIR)
    if f.startswith("reel_") and f.endswith(".mp4")
]) if os.path.isdir(VIDEO_DIR) else []


class TestVideoFileIntegrity:
    """Verify all 10 reel video files exist and are valid MP4s."""

    def test_all_10_reels_exist(self):
        assert len(REEL_FILES) == 10, f"Expected 10 reel files, found {len(REEL_FILES)}"

    @pytest.mark.parametrize("filename", REEL_FILES)
    def test_file_not_empty(self, filename):
        path = os.path.join(VIDEO_DIR, filename)
        size = os.path.getsize(path)
        assert size > 100_000, f"{filename} is only {size} bytes (expected > 100KB)"

    @pytest.mark.parametrize("filename", REEL_FILES)
    def test_valid_mp4_header(self, filename):
        """Check for ftyp box at start of file (MP4 signature)."""
        path = os.path.join(VIDEO_DIR, filename)
        with open(path, "rb") as f:
            header = f.read(32)
        assert b"ftyp" in header, f"{filename} missing ftyp box - not a valid MP4"

    @pytest.mark.parametrize("filename", REEL_FILES)
    def test_moov_before_mdat(self, filename):
        """Verify moov atom comes before mdat (faststart) for web streaming."""
        path = os.path.join(VIDEO_DIR, filename)
        with open(path, "rb") as f:
            data = f.read()

        moov_pos = data.find(b"moov")
        mdat_pos = data.find(b"mdat")
        assert moov_pos != -1, f"{filename} has no moov atom"
        assert mdat_pos != -1, f"{filename} has no mdat atom"
        assert moov_pos < mdat_pos, (
            f"{filename}: moov at {moov_pos} is AFTER mdat at {mdat_pos} - "
            "needs faststart for web playback"
        )


class TestVideoCodecAndFormat:
    """Verify video codec, resolution, and duration using ffprobe."""

    @pytest.fixture(autouse=True)
    def _check_ffprobe(self):
        result = subprocess.run(["ffprobe", "-version"], capture_output=True)
        if result.returncode != 0:
            pytest.skip("ffprobe not available")

    def _probe(self, filename):
        path = os.path.join(VIDEO_DIR, filename)
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-show_streams", "-show_format",
             "-print_format", "json", path],
            capture_output=True, text=True,
        )
        import json
        return json.loads(result.stdout)

    @pytest.mark.parametrize("filename", REEL_FILES)
    def test_h264_codec(self, filename):
        info = self._probe(filename)
        video_stream = info["streams"][0]
        assert video_stream["codec_name"] == "h264", (
            f"{filename} uses {video_stream['codec_name']}, expected h264"
        )

    @pytest.mark.parametrize("filename", REEL_FILES)
    def test_1080x1920_resolution(self, filename):
        info = self._probe(filename)
        video_stream = info["streams"][0]
        w, h = int(video_stream["width"]), int(video_stream["height"])
        assert (w, h) == (1080, 1920), f"{filename} is {w}x{h}, expected 1080x1920"

    @pytest.mark.parametrize("filename", REEL_FILES)
    def test_duration_reel_length(self, filename):
        info = self._probe(filename)
        duration = float(info["format"]["duration"])
        assert 15.0 <= duration <= 35.0, f"{filename} duration is {duration}s, expected 15-35s"

    @pytest.mark.parametrize("filename", REEL_FILES)
    def test_yuv420p_pixel_format(self, filename):
        """yuv420p is required for maximum browser compatibility."""
        info = self._probe(filename)
        pix_fmt = info["streams"][0]["pix_fmt"]
        assert pix_fmt == "yuv420p", f"{filename} uses {pix_fmt}, expected yuv420p"

    @pytest.mark.parametrize("filename", REEL_FILES)
    def test_has_audio_track(self, filename):
        info = self._probe(filename)
        audio_streams = [s for s in info["streams"] if s["codec_type"] == "audio"]
        assert len(audio_streams) >= 1, f"{filename} has no audio track"
        assert audio_streams[0]["codec_name"] == "aac", (
            f"{filename} audio is {audio_streams[0]['codec_name']}, expected aac"
        )

    @pytest.mark.parametrize("filename", REEL_FILES)
    def test_mp4_container_format(self, filename):
        info = self._probe(filename)
        fmt = info["format"]["format_name"]
        assert "mp4" in fmt or "mov" in fmt, f"{filename} format is {fmt}, expected mp4/mov"
