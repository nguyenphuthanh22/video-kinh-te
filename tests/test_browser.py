"""Kiểm thử vòng đời BrowserContextManager và xử lý HTML."""

from pathlib import Path
from PIL import Image

from playwright_pipeline.browser import BrowserContextManager


def test_browser_lifecycle():
    with BrowserContextManager(headless=True) as bm:
        assert bm.page is not None
        title = bm.page.evaluate("() => document.title")
        assert isinstance(title, str)


def test_browser_capture_html(tmp_path: Path):
    out = tmp_path / "custom_html.png"
    html = """
    <html>
    <body style="width:1920px;height:1080px;background:#0f172a;color:#ffffff;display:flex;align-items:center;justify-content:center;">
        <h1 style="font-size:72px;">TEST 16:9</h1>
    </body>
    </html>
    """
    with BrowserContextManager(headless=True) as bm:
        bm.capture_html(html, out)

    assert out.exists()
    with Image.open(out) as img:
        assert img.size == (1920, 1080)
