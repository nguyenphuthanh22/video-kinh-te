"""Tự động hóa Google Flow bằng Playwright để sinh ảnh/video nhân vật nhất quán và các cảnh kịch bản 16:9."""

from __future__ import annotations

import base64
import json
import logging
import time
from pathlib import Path
from typing import Any, Optional

import yaml

from .browser import BrowserContextManager

log = logging.getLogger("playwright_pipeline.flow")

IMG_JS = """() => [...document.images]
  .filter(i => (i.naturalWidth >= 512 && i.naturalHeight >= 288) || (i.width >= 512 && i.height >= 288))
  .map(i => i.currentSrc || i.src)"""


class FlowError(RuntimeError):
    """Lỗi trong quá trình thao tác trên giao diện Google Flow."""
    pass


def load_flow_selectors(path: Optional[Path | str] = None) -> dict[str, list[str]]:
    """Đọc cấu hình selector từ file YAML."""
    p = Path(path) if path else Path(__file__).resolve().parent.parent / "config" / "flow_selectors.yaml"
    if not p.exists():
        log.warning("Không tìm thấy file selector tại %s, dùng danh sách mặc định", p)
        return {}
    with open(p, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return {k: list(v) for k, v in data.get("selectors", {}).items()}


class FlowBrowser:
    """Điều khiển trình duyệt tương tác với Google Flow (Labs FX)."""

    def __init__(
        self,
        url: str = "https://labs.google/fx/tools/flow",
        session_dir: Optional[Path | str] = ".flow_session",
        headless: bool = False,
        generation_timeout: int = 240,
        selectors: Optional[dict[str, list[str]]] = None,
    ):
        self.url = url
        self.session_dir = Path(session_dir).resolve() if session_dir else Path(".flow_session").resolve()
        self.headless = headless
        self.generation_timeout = generation_timeout
        self.sel = selectors if selectors is not None else load_flow_selectors()
        self._bm: Optional[BrowserContextManager] = None

    def __enter__(self) -> "FlowBrowser":
        self._bm = BrowserContextManager(
            headless=self.headless,
            session_dir=self.session_dir,
            viewport_width=1600,
            viewport_height=900,
        )
        self._bm.start()
        return self

    def __exit__(self, *exc) -> None:
        if self._bm:
            self._bm.close()
            self._bm = None

    @property
    def page(self) -> Any:
        if not self._bm:
            raise FlowError("Chưa mở trình duyệt. Hãy dùng context manager `with FlowBrowser(...) as fb:`")
        return self._bm.page

    # ---- Tiện ích tìm selector -----------------------------------------------
    def find_element(self, key: str, timeout_ms: int = 4000, **fmt) -> Optional[Any]:
        """Trả về locator đầu tiên hiển thị từ danh sách ứng viên của key, hoặc None."""
        deadline = time.time() + timeout_ms / 1000.0
        while True:
            for cand in self.sel.get(key, []):
                try:
                    selector = cand.format(**fmt) if fmt else cand
                    loc = self.page.locator(selector).first
                    if loc.count() > 0 and loc.is_visible():
                        return loc
                except Exception:
                    continue
            if time.time() >= deadline:
                return None
            self.page.wait_for_timeout(200)

    def require_element(self, key: str, timeout_ms: int = 8000, **fmt) -> Any:
        """Bắt buộc phải tìm thấy element, nếu không ném ra ngoại lệ FlowError."""
        loc = self.find_element(key, timeout_ms, **fmt)
        if loc is None:
            raise FlowError(
                f"Không tìm thấy phần tử '{key}' trên giao diện Flow. "
                "Hãy chạy lệnh `doctor` để kiểm tra các selector hiện tại."
            )
        return loc

    # ---- Điều hướng & Quản lý phiên ------------------------------------------
    def open(self, login_wait_seconds: int = 300) -> None:
        """Mở trang Google Flow và kiểm tra trạng thái đăng nhập."""
        log.info("Mở Google Flow: %s", self.url)
        self.page.goto(self.url, wait_until="domcontentloaded", timeout=60000)

        end_time = time.time() + login_wait_seconds
        notified = False

        while time.time() < end_time:
            # Kiểm tra xem đã đăng nhập chưa
            if "accounts.google.com" not in self.page.url and self.find_element("logged_in_marker", 1500):
                log.info("Đã đăng nhập Google Flow thành công: %s", self.page.url)
                return

            if not notified:
                log.warning(
                    "Google Flow yêu cầu đăng nhập: hãy hoàn tất đăng nhập trong cửa sổ trình duyệt (chờ tối đa %d giây)...",
                    login_wait_seconds,
                )
                notified = True
            self.page.wait_for_timeout(2000)

        raise FlowError("Hết thời gian chờ đăng nhập tài khoản Google.")

    def new_project(self) -> None:
        """Tạo một project mới trong Flow nếu có nút 'New project'."""
        btn = self.find_element("new_project", 4000)
        if btn:
            log.info("Bấm tạo project mới...")
            btn.click()
            self.page.wait_for_timeout(2000)

    def set_aspect_16_9(self) -> bool:
        """Chọn tỷ lệ 16:9 trong giao diện Flow."""
        opt = self.find_element("aspect_16_9", 1500)
        if opt is None:
            settings_btn = self.find_element("settings_button", 1500)
            if settings_btn:
                settings_btn.click()
                self.page.wait_for_timeout(500)
            opt = self.find_element("aspect_16_9", 2500)

        if opt:
            opt.click()
            self.page.wait_for_timeout(400)
            self.page.keyboard.press("Escape")
            log.info("Đã chọn tỷ lệ 16:9")
            return True

        log.warning("Không tìm thấy tùy chọn 16:9 trong giao diện; sẽ duy trì từ khóa '16:9' trong prompt.")
        return False

    # ---- Xử lý Prompt & Sinh ảnh ---------------------------------------------
    def _get_image_srcs(self) -> list[str]:
        """Lấy danh sách các src ảnh hợp lệ hiện tại trên trang."""
        return list(self.page.evaluate(IMG_JS))

    def _type_prompt(self, prompt: str, mention: Optional[str] = None) -> None:
        """Nhập prompt vào ô nhập liệu."""
        box = self.require_element("prompt_box")
        box.click()
        box.press("Control+A")
        box.press("Delete")

        if mention and prompt.startswith(mention):
            # Gõ @Tag để kích hoạt menu chọn nhân vật đã lưu
            box.type(mention, delay=40)
            char_name = mention.lstrip("@")
            opt = self.find_element("mention_option", 1500, name=char_name)
            if opt:
                opt.click()
            else:
                box.press("Space")
            rest = prompt[len(mention):].lstrip()
            box.type(rest, delay=5)
        else:
            box.fill(prompt)

    def _save_image_src(self, src: str, out_path: Path) -> Path:
        """Tải và lưu ảnh từ URL hoặc data/blob URL vào file đích."""
        out_path = Path(out_path).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)

        if src.startswith("blob:") or src.startswith("data:"):
            fetch_js = """async (url) => {
                const response = await fetch(url);
                const blob = await response.blob();
                return await new Promise((resolve) => {
                    const reader = new FileReader();
                    reader.onload = () => resolve(reader.result.split(',')[1]);
                    reader.readAsDataURL(blob);
                });
            }"""
            b64_data = self.page.evaluate(fetch_js, src)
            out_path.write_bytes(base64.b64decode(b64_data))
        else:
            resp = self._bm.context.request.get(src)
            if not resp.ok:
                raise FlowError(f"Không thể tải ảnh từ URL: HTTP {resp.status}")
            out_path.write_bytes(resp.body())

        log.info("Đã lưu ảnh cảnh vào: %s", out_path)
        return out_path

    def generate_image(self, prompt: str, out_path: Path | str, mention: Optional[str] = None) -> Path:
        """Nhập prompt, nhấn Generate, chờ ảnh hoàn thành và tải về."""
        out_path = Path(out_path)
        before_srcs = set(self._get_image_srcs())

        log.info("Gửi prompt tạo ảnh: %s...", prompt[:80])
        self._type_prompt(prompt, mention)
        self.require_element("generate_button").click()

        deadline = time.time() + self.generation_timeout
        while time.time() < deadline:
            self.page.wait_for_timeout(3000)
            current_srcs = self._get_image_srcs()
            new_srcs = [s for s in current_srcs if s not in before_srcs]
            if new_srcs:
                # Chờ thêm một chút để ảnh render đủ độ phân giải cao nhất
                self.page.wait_for_timeout(1500)
                return self._save_image_src(new_srcs[0], out_path)

        raise FlowError(f"Hết thời gian {self.generation_timeout}s chưa thấy ảnh sinh ra cho prompt: {prompt[:60]}")

    def create_character(self, profile_name: str, prompts: list[str], out_dir: Path | str) -> list[Path]:
        """Tạo các ảnh tham chiếu (reference shots) cho nhân vật mẫu và lưu vào Ingredients."""
        out_dir = Path(out_dir).resolve()
        out_dir.mkdir(parents=True, exist_ok=True)
        saved_paths: list[Path] = []

        for idx, prompt in enumerate(prompts, 1):
            target = out_dir / f"{profile_name}_ref_{idx:02d}.png"
            log.info("[%d/%d] Sinh ảnh nhân vật tham chiếu: %s", idx, len(prompts), target.name)
            self.generate_image(prompt, target)
            saved_paths.append(target)

            # Thử lưu ảnh làm Ingredient nếu có nút
            add_btn = self.find_element("add_ingredient", 2000)
            if add_btn:
                add_btn.click()
                self.page.wait_for_timeout(1000)

        log.info("Hoàn tất tạo %d ảnh nhân vật cho '%s'", len(saved_paths), profile_name)
        return saved_paths

    def generate_scenes(
        self,
        prompts: list[dict],
        out_dir: Path | str,
        mention: Optional[str] = None,
        skip_existing: bool = True,
        retries: int = 1,
    ) -> dict[int, Path]:
        """
        Sinh ảnh cho danh sách các phân cảnh:
        prompts: [{'scene_id': 1, 'prompt': '...'}, ...]
        """
        out_dir = Path(out_dir).resolve()
        out_dir.mkdir(parents=True, exist_ok=True)
        results: dict[int, Path] = {}

        for item in prompts:
            sid = item["scene_id"]
            p = item["prompt"]
            target_file = out_dir / f"scene_{sid:03d}.png"

            if skip_existing and target_file.exists():
                log.info("Cảnh %03d đã tồn tại, bỏ qua: %s", sid, target_file.name)
                results[sid] = target_file
                continue

            success = False
            for attempt in range(retries + 1):
                try:
                    saved = self.generate_image(p, target_file, mention=mention)
                    results[sid] = saved
                    log.info("Hoàn thành cảnh %03d", sid)
                    success = True
                    break
                except FlowError as err:
                    log.warning("Cảnh %03d lần %d thất bại: %s", sid, attempt + 1, err)
                    if attempt < retries:
                        self.page.wait_for_timeout(3000)

            if not success:
                log.error("Không thể tạo ảnh cho cảnh %03d sau %d lần thử.", sid, retries + 1)

        return results

    def doctor(self, out_dir: Path | str) -> Path:
        """Chụp ảnh màn hình hiện tại và xuất JSON các selector/nút/ô nhập để chẩn đoán."""
        out_dir = Path(out_dir).resolve()
        out_dir.mkdir(parents=True, exist_ok=True)

        screenshot_path = out_dir / "flow_doctor.png"
        self.page.screenshot(path=str(screenshot_path), full_page=True)

        inspect_js = """() => ({
            url: location.href,
            title: document.title,
            buttons: [...document.querySelectorAll('button, [role=button]')].slice(0, 100).map(b => ({
                text: (b.innerText || '').trim().slice(0, 60),
                aria: b.getAttribute('aria-label') || ''
            })),
            inputs: [...document.querySelectorAll('textarea, input, [contenteditable=true], [role=textbox]')].map(e => ({
                tag: e.tagName,
                placeholder: e.getAttribute('placeholder') || '',
                aria: e.getAttribute('aria-label') || ''
            }))
        })"""
        dom_info = self.page.evaluate(inspect_js)

        # Kiểm tra trạng thái các selector đã cấu hình
        selector_check = {}
        for k in self.sel:
            if k != "mention_option":
                selector_check[k] = bool(self.find_element(k, 500))
        dom_info["selector_status"] = selector_check

        json_path = out_dir / "flow_doctor.json"
        json_path.write_text(json.dumps(dom_info, ensure_ascii=False, indent=2), encoding="utf-8")
        log.info("Đã lưu báo cáo chẩn đoán tại: %s và ảnh chụp tại %s", json_path, screenshot_path)
        return json_path
