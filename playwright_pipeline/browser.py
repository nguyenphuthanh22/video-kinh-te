"""Quản lý vòng đời trình duyệt Playwright cho pipeline tạo asset video 16:9."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Optional

log = logging.getLogger("playwright_pipeline.browser")


class BrowserContextManager:
    """Wrapper quản lý Playwright Chromium persistent hoặc transient context."""

    def __init__(
        self,
        headless: bool = True,
        session_dir: Optional[Path | str] = None,
        viewport_width: int = 1920,
        viewport_height: int = 1080,
        user_agent: Optional[str] = None,
    ):
        self.headless = headless
        self.session_dir = Path(session_dir).resolve() if session_dir else None
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height
        self.user_agent = (
            user_agent
            or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        )
        self._pw: Any = None
        self._browser: Any = None
        self._ctx: Any = None
        self._page: Any = None

    def __enter__(self) -> "BrowserContextManager":
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def start(self) -> None:
        """Khởi động Playwright và khởi tạo page."""
        try:
            from playwright.sync_api import sync_playwright
        except ImportError as exc:
            raise RuntimeError(
                "Chưa cài đặt Playwright. Vui lòng chạy: pip install playwright && python -m playwright install chromium"
            ) from exc

        self._pw = sync_playwright().start()

        launch_args = [
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            f"--window-size={self.viewport_width},{self.viewport_height}",
        ]

        if self.session_dir:
            self.session_dir.mkdir(parents=True, exist_ok=True)
            log.info("Sử dụng session profile tại: %s", self.session_dir)
            self._ctx = self._pw.chromium.launch_persistent_context(
                user_data_dir=str(self.session_dir),
                headless=self.headless,
                accept_downloads=True,
                viewport={"width": self.viewport_width, "height": self.viewport_height},
                user_agent=self.user_agent,
                args=launch_args,
            )
            self._page = self._ctx.pages[0] if self._ctx.pages else self._ctx.new_page()
        else:
            self._browser = self._pw.chromium.launch(
                headless=self.headless,
                args=launch_args,
            )
            self._ctx = self._browser.new_context(
                viewport={"width": self.viewport_width, "height": self.viewport_height},
                user_agent=self.user_agent,
                accept_downloads=True,
            )
            self._page = self._ctx.new_page()

        # Áp dụng stealth script cơ bản
        self._apply_stealth(self._page)

    def _apply_stealth(self, page: Any) -> None:
        """Che giấu dấu hiệu tự động hóa để tránh bị các trang web chặn."""
        stealth_js = """
        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        window.navigator.chrome = { runtime: {} };
        Object.defineProperty(navigator, 'languages', { get: () => ['vi-VN', 'vi', 'en-US', 'en'] });
        Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
        """
        try:
            page.add_init_script(stealth_js)
        except Exception as e:
            log.debug("Không thể thêm stealth script: %s", e)

    @property
    def page(self) -> Any:
        if not self._page:
            raise RuntimeError("Trình duyệt chưa được khởi động.")
        return self._page

    @property
    def context(self) -> Any:
        return self._ctx

    def new_page(self) -> Any:
        """Tạo tab/page mới."""
        page = self._ctx.new_page()
        self._apply_stealth(page)
        return page

    def capture_html(self, html_content: str, output_path: Path | str) -> Path:
        """Render nội dung HTML trực tiếp và chụp ảnh tỷ lệ 16:9 (1920x1080)."""
        output_path = Path(output_path).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)

        page = self.page
        page.set_content(html_content, wait_until="load")
        page.wait_for_timeout(200)  # Chờ font và css layout render ổn định
        page.screenshot(
            path=str(output_path),
            clip={"x": 0, "y": 0, "width": self.viewport_width, "height": self.viewport_height},
        )
        log.info("Đã xuất ảnh card: %s", output_path)
        return output_path

    def close(self) -> None:
        """Đóng context và Playwright."""
        try:
            if self._ctx:
                self._ctx.close()
            if self._browser:
                self._browser.close()
        finally:
            if self._pw:
                self._pw.stop()
            self._page = None
            self._ctx = None
            self._browser = None
            self._pw = None
