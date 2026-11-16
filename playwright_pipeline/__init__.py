"""Playwright Pipeline for video-kinh-te (16:9 HD video asset generation)."""

from .asset_manager import (
    IngestReport,
    create_placeholder_image,
    import_downloaded_files,
    ingest_assets,
    normalize_image_to_16_9,
    parse_scene_number,
    scan_scene_assets,
)
from .browser import BrowserContextManager
from .chart_capture import (
    capture_url,
    fetch_market_candles,
    render_breaking_news,
    render_financial_chart,
    render_metric_card,
    render_quote_card,
)
from .flow_client import FlowBrowser, FlowError, load_flow_selectors

__all__ = [
    "BrowserContextManager",
    "FlowBrowser",
    "FlowError",
    "load_flow_selectors",
    "capture_url",
    "fetch_market_candles",
    "render_financial_chart",
    "render_metric_card",
    "render_breaking_news",
    "render_quote_card",
    "IngestReport",
    "create_placeholder_image",
    "import_downloaded_files",
    "ingest_assets",
    "normalize_image_to_16_9",
    "parse_scene_number",
    "scan_scene_assets",
]
