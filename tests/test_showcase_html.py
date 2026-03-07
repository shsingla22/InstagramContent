"""Tests for showcase.html structure, video embedding, and content correctness."""
import os
import re
import pytest

import os
SHOWCASE_HTML = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "showcase.html")


@pytest.fixture(scope="module")
def html_content():
    with open(SHOWCASE_HTML, "r") as f:
        return f.read()


class TestHTMLStructure:
    """Verify the showcase HTML has correct structure."""

    def test_html_file_exists(self):
        assert os.path.exists(SHOWCASE_HTML), "showcase.html not found"

    def test_is_valid_html5(self, html_content):
        assert html_content.strip().startswith("<!DOCTYPE html>")

    def test_has_viewport_meta(self, html_content):
        assert 'name="viewport"' in html_content

    def test_has_title(self, html_content):
        assert "<title>" in html_content


class TestVideoEmbedding:
    """Verify videos are properly embedded as base64 data URIs."""

    def test_10_video_elements(self, html_content):
        video_count = html_content.count('class="reel-player"')
        assert video_count == 10, f"Found {video_count} video elements, expected 10"

    def test_no_relative_video_paths(self, html_content):
        """Ensure no relative file paths remain (would break when shared)."""
        assert 'src="output/videos/' not in html_content, (
            "Found relative video paths - videos should be embedded as base64"
        )

    def test_webm_sources_present(self, html_content):
        """WebM format should be primary source for broad compatibility."""
        webm_count = len(re.findall(r'type="video/webm"', html_content))
        assert webm_count == 10, f"Found {webm_count} WebM sources, expected 10"

    def test_mp4_sources_present(self, html_content):
        """MP4 format should be fallback for Safari."""
        mp4_count = len(re.findall(r'type="video/mp4"', html_content))
        assert mp4_count == 10, f"Found {mp4_count} MP4 sources, expected 10"

    def test_base64_data_uris(self, html_content):
        """All video sources should use base64 data URIs."""
        webm_b64 = len(re.findall(r'data:video/webm;base64,', html_content))
        mp4_b64 = len(re.findall(r'data:video/mp4;base64,', html_content))
        assert webm_b64 == 10, f"Found {webm_b64} WebM base64 URIs, expected 10"
        assert mp4_b64 == 10, f"Found {mp4_b64} MP4 base64 URIs, expected 10"

    def test_videos_have_playsinline(self, html_content):
        """playsinline is required for iOS Safari."""
        count = html_content.count("playsinline")
        assert count >= 10, f"Only {count} videos have playsinline attribute"

    def test_videos_are_muted(self, html_content):
        """Muted videos can autoplay in most browsers."""
        count = len(re.findall(r'\bmuted\b', html_content))
        assert count >= 10, f"Only {count} videos have muted attribute"

    def test_videos_have_loop(self, html_content):
        count = len(re.findall(r'\bloop\b', html_content))
        assert count >= 10, f"Only {count} videos have loop attribute"

    def test_preload_set_to_auto(self, html_content):
        count = html_content.count('preload="auto"')
        assert count >= 10, f"Only {count} videos have preload=auto"

    def test_no_video_generating_placeholder(self, html_content):
        """All videos should be embedded, no 'generating...' placeholders."""
        assert "Video generating" not in html_content, (
            "Found 'Video generating' placeholder - all videos should be embedded"
        )


class TestPlayControls:
    """Verify play/pause and mute controls exist."""

    def test_play_buttons_exist(self, html_content):
        count = html_content.count('class="play-btn"')
        assert count == 10, f"Found {count} play buttons, expected 10"

    def test_mute_buttons_exist(self, html_content):
        count = html_content.count('class="mute-btn"')
        assert count == 10, f"Found {count} mute buttons, expected 10"

    def test_play_script_exists(self, html_content):
        assert "playBtn.addEventListener" in html_content or "play-btn" in html_content


class TestContentCompleteness:
    """Verify all 10 posts have proper content."""

    def test_all_10_post_numbers(self, html_content):
        for i in range(1, 11):
            assert f"#{i}" in html_content, f"Post #{i} number not found"

    def test_reel_badges(self, html_content):
        count = html_content.count("REEL")
        assert count >= 10, f"Found {count} REEL badges, expected >= 10"
