"""Chụp ảnh biểu đồ kinh tế trực tuyến và render các card đồ họa tài chính 16:9."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from .browser import BrowserContextManager
from .card_templates import (
    render_breaking_news_html,
    render_metric_card_html,
    render_quote_card_html,
)

log = logging.getLogger("playwright_pipeline.chart_capture")


def capture_url(
    url: str,
    output_path: Path | str,
    wait_selector: Optional[str] = None,
    delay_ms: int = 2000,
    headless: bool = True,
    width: int = 1920,
    height: int = 1080,
    session_dir: Optional[Path | str] = None,
) -> Path:
    """Mở một URL web tài chính (TradingView, CafeF, Vietstock,...) và chụp ảnh màn hình 16:9."""
    output_path = Path(output_path).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with BrowserContextManager(
        headless=headless,
        session_dir=session_dir,
        viewport_width=width,
        viewport_height=height,
    ) as bm:
        page = bm.page
        log.info("Đang điều hướng đến: %s", url)
        page.goto(url, wait_until="domcontentloaded", timeout=60000)

        if wait_selector:
            try:
                log.info("Chờ selector '%s' hiển thị...", wait_selector)
                page.wait_for_selector(wait_selector, timeout=15000)
            except Exception as e:
                log.warning("Không thấy selector '%s' trong 15s: %s", wait_selector, e)

        if delay_ms > 0:
            page.wait_for_timeout(delay_ms)

        # Ẩn các banner quảng cáo / cookie nếu có
        hide_clutter_js = """
        const selectors = [
            '#cookie-banner', '.cookie-banner', '.gdpr-consent',
            '#onesignal-slidedown-dialog', '.advertisement', '.ads',
            '[id*="google_ads"]', '[id*="ad_"]'
        ];
        selectors.forEach(sel => {
            document.querySelectorAll(sel).forEach(el => el.style.display = 'none');
        });
        """
        try:
            page.evaluate(hide_clutter_js)
        except Exception:
            pass

        page.screenshot(
            path=str(output_path),
            clip={"x": 0, "y": 0, "width": width, "height": height},
        )
        log.info("Đã chụp màn hình thành công: %s", output_path)
        return output_path


def render_metric_card(
    title: str,
    value: str,
    output_path: Path | str,
    subtitle: str = "",
    tag: str = "KINH TẾ & THỊ TRƯỜNG",
    delta: str = "",
    is_positive: bool = True,
    headless: bool = True,
) -> Path:
    """Tạo ảnh card chỉ số kinh tế 16:9 (1920x1080)."""
    html_content = render_metric_card_html(
        title=title,
        value=value,
        subtitle=subtitle,
        tag=tag,
        delta=delta,
        is_positive=is_positive,
    )
    with BrowserContextManager(headless=headless) as bm:
        return bm.capture_html(html_content, output_path)


def render_breaking_news(
    headline: str,
    output_path: Path | str,
    source: str = "TIN NÓNG KINH TẾ",
    summary: str = "",
    headless: bool = True,
) -> Path:
    """Tạo ảnh card tin nóng kinh tế 16:9 (1920x1080)."""
    html_content = render_breaking_news_html(
        headline=headline,
        source=source,
        summary=summary,
    )
    with BrowserContextManager(headless=headless) as bm:
        return bm.capture_html(html_content, output_path)


def render_quote_card(
    quote: str,
    author: str,
    output_path: Path | str,
    role: str = "",
    headless: bool = True,
) -> Path:
    """Tạo ảnh card trích dẫn danh ngôn / nhận định kinh tế 16:9 (1920x1080)."""
    html_content = render_quote_card_html(
        quote=quote,
        author=author,
        role=role,
    )
    with BrowserContextManager(headless=headless) as bm:
        return bm.capture_html(html_content, output_path)
