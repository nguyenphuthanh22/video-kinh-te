"""Kiểm thử render card đồ họa kinh tế 16:9 bằng Playwright."""

from pathlib import Path
from PIL import Image

from playwright_pipeline.card_templates import (
    render_breaking_news_html,
    render_metric_card_html,
    render_quote_card_html,
)
from playwright_pipeline.chart_capture import (
    render_breaking_news,
    render_metric_card,
    render_quote_card,
)


def test_html_templates_generate_valid_content():
    html_metric = render_metric_card_html("LÃI SUẤT", "4.5%", "Quý 4")
    assert "LÃI SUẤT" in html_metric
    assert "4.5%" in html_metric
    assert "1920px" in html_metric

    html_breaking = render_breaking_news_html("VÀNG LẬP ĐỈNH", summary="Chi tiết")
    assert "VÀNG LẬP ĐỈNH" in html_breaking

    html_quote = render_quote_card_html("Đầu tư cho tri thức", "Benjamin Franklin")
    assert "Benjamin Franklin" in html_quote


def test_render_metric_card_file(tmp_path: Path):
    target = tmp_path / "metric_test.png"
    render_metric_card(
        title="VN-INDEX",
        value="1,280.50",
        delta="+15.20",
        is_positive=True,
        output_path=target,
        headless=True,
    )
    assert target.exists()
    with Image.open(target) as img:
        assert img.size == (1920, 1080)


def test_render_breaking_news_file(tmp_path: Path):
    target = tmp_path / "breaking_test.png"
    render_breaking_news(
        headline="THỊ TRƯỜNG BÙNG NỔ THANH KHOẢN",
        output_path=target,
        headless=True,
    )
    assert target.exists()
    with Image.open(target) as img:
        assert img.size == (1920, 1080)


def test_render_quote_card_file(tmp_path: Path):
    target = tmp_path / "quote_test.png"
    render_quote_card(
        quote="Hãy tham lam khi người khác sợ hãi.",
        author="Warren Buffett",
        output_path=target,
        headless=True,
    )
    assert target.exists()
    with Image.open(target) as img:
        assert img.size == (1920, 1080)
