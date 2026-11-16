"""Kiểm thử render card đồ họa kinh tế 16:9 bằng Playwright."""

from pathlib import Path
from PIL import Image

from playwright_pipeline.card_templates import (
    render_breaking_news_html,
    render_financial_chart_html,
    render_metric_card_html,
    render_quote_card_html,
)
from playwright_pipeline.chart_capture import (
    _generate_fallback_candles,
    render_breaking_news,
    render_financial_chart,
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


def test_render_financial_chart_file(tmp_path: Path):
    candles = _generate_fallback_candles(bars=40)
    html_chart = render_financial_chart_html("VNINDEX", candles)
    assert "VNINDEX" in html_chart
    assert "<svg" in html_chart

    target = tmp_path / "vnindex_chart_test.png"
    render_financial_chart(
        output_path=target,
        symbol="VNINDEX",
        candles=candles,
        headless=True,
    )
    assert target.exists()
    with Image.open(target) as img:
        assert img.size == (1920, 1080)

