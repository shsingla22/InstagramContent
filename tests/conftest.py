"""Shared fixtures for video and showcase tests."""
import os
import http.server
import threading
import socket
import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIDEO_DIR = os.path.join(PROJECT_ROOT, "output", "videos")
SHOWCASE_HTML = os.path.join(PROJECT_ROOT, "showcase.html")

CHROMIUM_PATH = "/root/.cache/ms-playwright/chromium-1194/chrome-linux/chrome"

REEL_FILES = sorted([
    f for f in os.listdir(VIDEO_DIR)
    if f.startswith("reel_") and f.endswith(".mp4")
]) if os.path.isdir(VIDEO_DIR) else []


def _find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, directory=None, **kwargs):
        super().__init__(*args, directory=directory or PROJECT_ROOT, **kwargs)

    def log_message(self, *args):
        pass


@pytest.fixture(scope="session")
def local_server():
    """Start a local HTTP server serving the project root."""
    port = _find_free_port()
    handler = lambda *args, **kwargs: QuietHandler(*args, directory=PROJECT_ROOT, **kwargs)
    httpd = http.server.HTTPServer(("127.0.0.1", port), handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{port}"
    httpd.shutdown()


@pytest.fixture(scope="session")
def browser_page(local_server):
    """Launch a headless Chromium browser and provide a page."""
    from playwright.sync_api import sync_playwright

    pw = sync_playwright().start()
    browser = pw.chromium.launch(
        headless=True,
        executable_path=CHROMIUM_PATH,
        args=[
            "--no-sandbox",
            "--autoplay-policy=no-user-gesture-required",
            "--disable-gpu",
        ],
    )
    context = browser.new_context(
        viewport={"width": 430, "height": 932},
    )
    page = context.new_page()
    page.goto(f"{local_server}/showcase.html", wait_until="networkidle")
    page.wait_for_timeout(3000)
    yield page
    browser.close()
    pw.stop()
