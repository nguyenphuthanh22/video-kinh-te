"""Chụp ảnh biểu đồ kinh tế trực tuyến và render các card đồ họa tài chính 16:9."""

from __future__ import annotations

import datetime as dt
import json
import logging
import math
import time
import urllib.request
from pathlib import Path
from typing import Optional

from .browser import BrowserContextManager
from .card_templates import (
    render_breaking_news_html,
    render_financial_chart_html,
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


def _generate_fallback_candles(bars: int = 80) -> list[dict]:
    """Sinh dữ liệu nến VN-Index mẫu khi chạy offline hoặc kiểm thử."""
    candles = []
    base_price = 1245.0
    base_date = dt.date(2026, 7, 1)
    for i in range(bars):
        d = base_date + dt.timedelta(days=i)
        wave = math.sin(i / 6.5) * 14.0 + (i * 0.65)
        o_p = round(base_price + wave, 2)
        delta = round(math.cos(i / 3.2) * 8.5 + (1.8 if i % 3 != 0 else -2.4), 2)
        c_p = round(o_p + delta, 2)
        h_p = round(max(o_p, c_p) + abs(math.sin(i * 1.3)) * 6.5 + 1.2, 2)
        l_p = round(min(o_p, c_p) - abs(math.cos(i * 1.1)) * 6.0 - 1.0, 2)
        vol = int((680_000_000 + abs(delta) * 28_000_000) * (0.85 + (i % 5) * 0.08))
        candles.append(
            {
                "date": d.strftime("%d/%m"),
                "o": o_p,
                "h": h_p,
                "l": l_p,
                "c": c_p,
                "v": vol,
            }
        )
    return candles


def fetch_market_candles(symbol: str = "VNINDEX", bars: int = 80) -> list[dict]:
    """Lấy dữ liệu OHLCV thực tế từ VNDirect DChart API, tự động fallback nếu offline."""
    now_ts = int(time.time())
    from_ts = now_ts - max(bars * 2, 180) * 86400
    url = (
        f"https://dchart-api.vndirect.com.vn/dchart/history"
        f"?resolution=D&symbol={symbol}&from={from_ts}&to={now_ts}"
    )
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        t_list = data.get("t", [])
        o_list = data.get("o", [])
        h_list = data.get("h", [])
        l_list = data.get("l", [])
        c_list = data.get("c", [])
        v_list = data.get("v", [])
        if t_list and len(t_list) == len(c_list):
            candles = []
            for idx in range(len(t_list)):
                dt_obj = dt.datetime.fromtimestamp(int(t_list[idx]), tz=dt.timezone.utc)
                candles.append(
                    {
                        "date": dt_obj.strftime("%d/%m"),
                        "o": float(o_list[idx]),
                        "h": float(h_list[idx]),
                        "l": float(l_list[idx]),
                        "c": float(c_list[idx]),
                        "v": float(v_list[idx]) if idx < len(v_list) else 0.0,
                    }
                )
            return candles[-bars:]
    except Exception as e:
        log.warning("Không lấy được dữ liệu trực tuyến cho %s (%s), dùng dữ liệu mẫu.", symbol, e)

    return _generate_fallback_candles(bars=bars)


def render_financial_chart(
    output_path: Path | str,
    symbol: str = "VNINDEX",
    title: str = "CHỈ SỐ VN-INDEX — SÀN HOSE",
    subtitle: str = "Biểu đồ nến Nhật (Daily) • MA20 & MA50 • Khối lượng giao dịch",
    bars: int = 80,
    candles: Optional[list[dict]] = None,
    headless: bool = True,
) -> Path:
    """Render và chụp biểu đồ tài chính nến Nhật chuẩn 16:9 (1920x1080) bằng Playwright."""
    chart_candles = candles if candles is not None else fetch_market_candles(symbol=symbol, bars=bars)
    html_content = render_financial_chart_html(
        symbol=symbol,
        candles=chart_candles,
        title=title,
        subtitle=subtitle,
    )
    with BrowserContextManager(headless=headless, viewport_width=1920, viewport_height=1080) as bm:
        return bm.capture_html(html_content, output_path)

