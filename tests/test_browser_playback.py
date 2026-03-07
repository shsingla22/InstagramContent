"""Browser-based tests for video playback using Playwright (headless Chromium)."""
import os
import pytest

CHROMIUM_PATH = "/root/.cache/ms-playwright/chromium-1194/chrome-linux/chrome"

# Skip all tests in this module if Chromium is not available
pytestmark = pytest.mark.skipif(
    not os.path.exists(CHROMIUM_PATH),
    reason="Headless Chromium not installed"
)


class TestVideoLoading:
    """Verify all videos load successfully in the browser."""

    def test_10_video_elements_found(self, browser_page):
        videos = browser_page.query_selector_all("video.reel-player")
        assert len(videos) == 10

    def test_all_videos_have_enough_data(self, browser_page):
        """readyState 4 (HAVE_ENOUGH_DATA) means the video is fully loadable."""
        states = browser_page.evaluate("""() => {
            return Array.from(document.querySelectorAll('video.reel-player')).map((v, i) => ({
                index: i + 1,
                readyState: v.readyState,
                networkState: v.networkState,
            }));
        }""")
        for s in states:
            assert s["readyState"] == 4, (
                f"Video #{s['index']}: readyState={s['readyState']} "
                f"(expected 4=ENOUGH_DATA), networkState={s['networkState']}"
            )

    def test_all_videos_have_no_errors(self, browser_page):
        errors = browser_page.evaluate("""() => {
            return Array.from(document.querySelectorAll('video.reel-player')).map((v, i) => ({
                index: i + 1,
                error: v.error ? {code: v.error.code, message: v.error.message} : null,
            }));
        }""")
        for e in errors:
            assert e["error"] is None, f"Video #{e['index']} has error: {e['error']}"

    def test_all_videos_have_duration(self, browser_page):
        durations = browser_page.evaluate("""() => {
            return Array.from(document.querySelectorAll('video.reel-player')).map((v, i) => ({
                index: i + 1,
                duration: v.duration,
            }));
        }""")
        for d in durations:
            assert d["duration"] > 10 and d["duration"] < 40, (
                f"Video #{d['index']}: duration={d['duration']} (expected 15-35s)"
            )

    def test_all_videos_have_dimensions(self, browser_page):
        dims = browser_page.evaluate("""() => {
            return Array.from(document.querySelectorAll('video.reel-player')).map((v, i) => ({
                index: i + 1,
                w: v.videoWidth,
                h: v.videoHeight,
            }));
        }""")
        for d in dims:
            assert d["w"] > 0 and d["h"] > 0, (
                f"Video #{d['index']}: {d['w']}x{d['h']} (expected non-zero)"
            )
            assert d["h"] > d["w"], (
                f"Video #{d['index']}: {d['w']}x{d['h']} should be portrait (height > width)"
            )


class TestVideoPlayback:
    """Verify videos actually play when the play button is clicked."""

    def test_click_play_starts_video(self, browser_page):
        """Click the first play button and verify the video plays."""
        # Reset: pause all videos
        browser_page.evaluate("""() => {
            document.querySelectorAll('video.reel-player').forEach(v => {
                v.pause();
                v.currentTime = 0;
            });
        }""")
        browser_page.wait_for_timeout(500)

        play_btn = browser_page.query_selector(".play-btn")
        assert play_btn is not None, "No play button found"
        play_btn.click()
        browser_page.wait_for_timeout(2000)

        state = browser_page.evaluate("""() => {
            const v = document.querySelector('video.reel-player');
            return { paused: v.paused, currentTime: v.currentTime };
        }""")
        assert not state["paused"], "Video should not be paused after clicking play"
        assert state["currentTime"] > 0.5, (
            f"Video currentTime={state['currentTime']} — should have advanced"
        )

    def test_click_play_again_pauses(self, browser_page):
        """Clicking play again should pause the video."""
        play_btn = browser_page.query_selector(".play-btn")
        # First ensure it's playing
        state = browser_page.evaluate("""() => {
            const v = document.querySelector('video.reel-player');
            return { paused: v.paused };
        }""")
        if state["paused"]:
            play_btn.click()
            browser_page.wait_for_timeout(500)

        # Now click to pause
        play_btn.click()
        browser_page.wait_for_timeout(500)

        state = browser_page.evaluate("""() => {
            const v = document.querySelector('video.reel-player');
            return { paused: v.paused };
        }""")
        assert state["paused"], "Video should be paused after second click"

    def test_programmatic_play(self, browser_page):
        """Verify programmatic play() works for all videos."""
        results = browser_page.evaluate("""async () => {
            const videos = document.querySelectorAll('video.reel-player');
            const results = [];
            for (let i = 0; i < videos.length; i++) {
                const v = videos[i];
                v.currentTime = 0;
                try {
                    await v.play();
                    await new Promise(r => setTimeout(r, 500));
                    const ok = v.currentTime > 0 && !v.paused;
                    v.pause();
                    results.push({index: i + 1, ok, time: v.currentTime});
                } catch(e) {
                    v.pause();
                    results.push({index: i + 1, ok: false, error: e.message});
                }
            }
            return results;
        }""")
        for r in results:
            if not r["ok"]:
                err = r.get("error", f"time={r.get('time', 0)}")
                assert False, f"Video #{r['index']} failed to play: {err}"

    def test_only_one_video_plays_at_a_time(self, browser_page):
        """When clicking play on one video, others should pause."""
        # Scroll to second video and click its play button
        browser_page.evaluate("""() => {
            document.querySelectorAll('video.reel-player').forEach(v => {
                v.pause();
                v.currentTime = 0;
            });
        }""")
        browser_page.wait_for_timeout(300)

        play_btns = browser_page.query_selector_all(".play-btn")
        assert len(play_btns) >= 2

        # Play first video
        play_btns[0].click()
        browser_page.wait_for_timeout(500)

        # Now play second video (should pause first)
        play_btns[1].scroll_into_view_if_needed()
        browser_page.wait_for_timeout(300)
        play_btns[1].click()
        browser_page.wait_for_timeout(1000)

        states = browser_page.evaluate("""() => {
            return Array.from(document.querySelectorAll('video.reel-player')).map((v, i) => ({
                index: i + 1,
                paused: v.paused,
            }));
        }""")

        playing_count = sum(1 for s in states if not s["paused"])
        assert playing_count <= 1, (
            f"{playing_count} videos playing simultaneously — expected at most 1"
        )


class TestMuteToggle:
    """Verify the mute/unmute button works."""

    def test_mute_toggle(self, browser_page):
        mute_btn = browser_page.query_selector(".mute-btn")
        assert mute_btn is not None

        # Initially muted
        is_muted = browser_page.evaluate("""() => {
            return document.querySelector('video.reel-player').muted;
        }""")
        assert is_muted, "Video should start muted"

        # Click to unmute
        mute_btn.click()
        browser_page.wait_for_timeout(300)
        is_muted = browser_page.evaluate("""() => {
            return document.querySelector('video.reel-player').muted;
        }""")
        assert not is_muted, "Video should be unmuted after clicking mute button"

        # Click again to re-mute
        mute_btn.click()
        browser_page.wait_for_timeout(300)
        is_muted = browser_page.evaluate("""() => {
            return document.querySelector('video.reel-player').muted;
        }""")
        assert is_muted, "Video should be muted again after second click"


class TestVideoClickToPlay:
    """Verify clicking directly on the video toggles play/pause."""

    def test_click_video_element_toggles_play(self, browser_page):
        # Reset
        browser_page.evaluate("""() => {
            document.querySelectorAll('video.reel-player').forEach(v => {
                v.pause();
                v.currentTime = 0;
            });
        }""")
        browser_page.wait_for_timeout(300)

        video_el = browser_page.query_selector("video.reel-player")
        video_el.scroll_into_view_if_needed()
        browser_page.wait_for_timeout(300)

        # Click video to play
        video_el.click()
        browser_page.wait_for_timeout(1000)

        state = browser_page.evaluate("""() => {
            const v = document.querySelector('video.reel-player');
            return { paused: v.paused, time: v.currentTime };
        }""")
        assert not state["paused"], "Video should play when clicked"
        assert state["time"] > 0, "Video should have advanced"
