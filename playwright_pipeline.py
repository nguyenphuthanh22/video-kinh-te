"""CLI điều phối toàn bộ các tác vụ Playwright cho pipeline Video Kinh Tế 16:9.

Các lệnh chính:
  python playwright_pipeline.py check
  python playwright_pipeline.py card --type metric --title "LÃI SUẤT FED" --value "4.5%" -o output/scene_001.png
  python playwright_pipeline.py card --type breaking --headline "GIÁ VÀNG LẬP ĐỈNH MỚI" -o output/scene_002.png
  python playwright_pipeline.py capture --url "https://vnexpress.net/kinh-doanh" -o output/scene_003.png
  python playwright_pipeline.py flow doctor -o output/doctor
  python playwright_pipeline.py flow scenes --prompts flow_prompts.json -o output/scenes
  python playwright_pipeline.py ingest --from ./downloads --to ./output/normalized --scenes 1 2 3
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from playwright_pipeline import (
    FlowBrowser,
    FlowError,
    capture_url,
    create_placeholder_image,
    import_downloaded_files,
    ingest_assets,
    render_breaking_news,
    render_metric_card,
    render_quote_card,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
log = logging.getLogger("playwright_cli")


def cmd_check(args) -> int:
    """Kiểm tra môi trường Playwright và Chromium."""
    print("=== KIỂM TRA MÔI TRƯỜNG PLAYWRIGHT ===")
    ok = True

    try:
        import importlib.metadata
        pw_ver = importlib.metadata.version("playwright")
        print(f"[OK] Thư viện Playwright: phiên bản {pw_ver}")
    except Exception:
        try:
            import playwright
            print("[OK] Thư viện Playwright: đã cài đặt")
        except ImportError:
            print("[!!] Chưa cài thư viện Playwright (chạy: pip install playwright)")
            return 1

    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_viewport_size({"width": 1920, "height": 1080})
            ua = page.evaluate("navigator.userAgent")
            browser.close()
            print(f"[OK] Trình duyệt Chromium: sẵn sàng (1920x1080 16:9, {ua[:50]}...)")
    except Exception as e:
        print(f"[!!] Lỗi khởi động Chromium: {e}")
        print("     Hãy chạy: python -m playwright install chromium")
        ok = False

    session_path = Path(args.session_dir or ".flow_session").resolve()
    if session_path.exists():
        print(f"[OK] Thư mục lưu phiên Google Flow: {session_path}")
    else:
        print(f"[INFO] Thư mục phiên Google Flow: {session_path} (chưa tạo, sẽ tự tạo khi chạy)")

    return 0 if ok else 1


def cmd_card(args) -> int:
    """Render card kinh tế đồ họa 16:9 bằng Playwright."""
    out = Path(args.output).resolve()
    card_type = args.type.lower()

    if card_type == "metric":
        render_metric_card(
            title=args.title or "CHỈ SỐ THỊ TRƯỜNG",
            value=args.value or "1,250.00",
            subtitle=args.subtitle or "",
            tag=args.tag or "KINH TẾ & THỊ TRƯỜNG",
            delta=args.delta or "",
            is_positive=not args.negative,
            output_path=out,
            headless=not args.headed,
        )
    elif card_type == "breaking":
        render_breaking_news(
            headline=args.headline or args.title or "TIN NÓNG THỊ TRƯỜNG KINH TẾ",
            source=args.tag or "TIN NÓNG KINH TẾ",
            summary=args.subtitle or "",
            output_path=out,
            headless=not args.headed,
        )
    elif card_type == "quote":
        render_quote_card(
            quote=args.quote or args.title or "Đầu tư vào tri thức mang lại lợi nhuận cao nhất.",
            author=args.author or "Benjamin Franklin",
            role=args.subtitle or "",
            output_path=out,
            headless=not args.headed,
        )
    else:
        print(f"Lỗi: loại card '{card_type}' không hỗ trợ (chọn: metric, breaking, quote)", file=sys.stderr)
        return 1

    print(f"OK: Đã xuất ảnh card 16:9 tại: {out}")
    return 0


def cmd_capture(args) -> int:
    """Chụp trang web hoặc biểu đồ kinh tế theo tỷ lệ 16:9."""
    out = Path(args.output).resolve()
    capture_url(
        url=args.url,
        output_path=out,
        wait_selector=args.wait_selector,
        delay_ms=args.delay,
        headless=not args.headed,
        width=args.width,
        height=args.height,
    )
    print(f"OK: Đã chụp màn hình 16:9 tại: {out}")
    return 0


def cmd_flow(args) -> int:
    """Thao tác với Google Flow bằng Playwright."""
    action = args.flow_action
    session_dir = Path(args.session_dir or ".flow_session")

    try:
        with FlowBrowser(session_dir=session_dir, headless=args.headless) as fb:
            fb.open()

            if action == "doctor":
                out_dir = Path(args.output or "output/flow_doctor")
                p = fb.doctor(out_dir)
                print(f"OK: Đã xuất báo cáo chẩn đoán tại: {p}")

            elif action == "character":
                out_dir = Path(args.output or "assets/characters")
                prompts = [
                    "Vietnamese male economist 32yo, front view, looking at camera, navy blazer, 16:9 aspect ratio",
                    "Vietnamese male economist 32yo, 3/4 view, smiling confident, modern financial studio background, 16:9",
                ]
                fb.new_project()
                fb.set_aspect_16_9()
                saved = fb.create_character(args.name or "MinhKinhTe", prompts, out_dir)
                print(f"OK: Đã tạo {len(saved)} ảnh nhân vật mẫu tại: {out_dir}")

            elif action == "scenes":
                if not args.prompts:
                    print("Lỗi: cần truyền đường dẫn file JSON kịch bản qua --prompts", file=sys.stderr)
                    return 1
                prompts_data = json.loads(Path(args.prompts).read_text(encoding="utf-8"))
                out_dir = Path(args.output or "output/scenes")
                fb.new_project()
                fb.set_aspect_16_9()
                done = fb.generate_scenes(prompts_data, out_dir, mention=args.mention)
                print(f"OK: Đã sinh {len(done)} ảnh cảnh kịch bản tại: {out_dir}")

    except FlowError as e:
        print(f"Lỗi Flow: {e}", file=sys.stderr)
        return 2

    return 0


def cmd_ingest(args) -> int:
    """Nạp, kiểm tra và chuẩn hóa các ảnh asset về đúng tỷ lệ 16:9 (1920x1080)."""
    scene_ids = args.scenes or list(range(1, 21))
    src_dir = Path(args.src_dir) if args.src_dir else None
    dest_dir = Path(args.to_dir or "assets/scenes")

    if src_dir and src_dir.exists():
        copied = import_downloaded_files(src_dir, dest_dir, scene_ids, by_order=args.by_order)
        print(f"Đã sao chép {len(copied)} file từ thư mục tải về.")

    rep = ingest_assets(
        scene_ids=scene_ids,
        search_dirs=[dest_dir],
        work_images_dir=dest_dir / "_normalized",
        allow_placeholder=True,
    )
    print(f"Tổng cảnh: {len(scene_ids)} | Có ảnh: {len(rep.from_source)} | Placeholder: {len(rep.placeholders)}")
    for w in rep.warnings:
        print(f"  [Cảnh báo] {w}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Playwright Pipeline cho Video Kinh Tế 16:9")
    sub = parser.add_subparsers(dest="command", required=True)

    # 1. check
    p_check = sub.add_parser("check", help="Kiểm tra môi trường Playwright & Chromium")
    p_check.add_argument("--session-dir", default=".flow_session")
    p_check.set_defaults(func=cmd_check)

    # 2. card
    p_card = sub.add_parser("card", help="Render infographic card kinh tế 16:9 (1920x1080)")
    p_card.add_argument("--type", choices=["metric", "breaking", "quote"], default="metric")
    p_card.add_argument("-o", "--output", required=True, help="File PNG đầu ra")
    p_card.add_argument("--title", help="Tiêu đề card hoặc chỉ số")
    p_card.add_argument("--value", help="Giá trị số liệu (ví dụ: 82.500.000 VNĐ, 4.5%%,...)")
    p_card.add_argument("--subtitle", help="Phụ đề / dòng giải thích")
    p_card.add_argument("--tag", help="Thẻ phân loại (ví dụ: TIN NÓNG, THỊ TRƯỜNG)")
    p_card.add_argument("--delta", help="Độ biến động (ví dụ: +1.2%%, -0.5%%)")
    p_card.add_argument("--negative", action="store_true", help="Đặt màu biến động thành đỏ giảm")
    p_card.add_argument("--quote", help="Nội dung trích dẫn")
    p_card.add_argument("--author", help="Tác giả câu trích dẫn")
    p_card.add_argument("--headline", help="Dòng tin nóng tiêu đề lớn")
    p_card.add_argument("--headed", action="store_true", help="Chạy có hiển thị cửa sổ")
    p_card.set_defaults(func=cmd_card)

    # 3. capture
    p_cap = sub.add_parser("capture", help="Chụp biểu đồ hoặc trang web kinh tế theo tỷ lệ 16:9")
    p_cap.add_argument("--url", required=True, help="URL trang web cần chụp")
    p_cap.add_argument("-o", "--output", required=True, help="File PNG đầu ra")
    p_cap.add_argument("--wait-selector", help="Selector CSS chờ xuất hiện trước khi chụp")
    p_cap.add_argument("--delay", type=int, default=2000, help="Thời gian chờ thêm (ms)")
    p_cap.add_argument("--width", type=int, default=1920)
    p_cap.add_argument("--height", type=int, default=1080)
    p_cap.add_argument("--headed", action="store_true")
    p_cap.set_defaults(func=cmd_capture)

    # 4. flow
    p_flow = sub.add_parser("flow", help="Tự động hóa tạo ảnh bằng Google Flow")
    p_flow.add_argument("flow_action", choices=["doctor", "character", "scenes"])
    p_flow.add_argument("-o", "--output")
    p_flow.add_argument("--prompts", help="Đường dẫn file JSON danh sách prompt cảnh")
    p_flow.add_argument("--name", default="MinhKinhTe")
    p_flow.add_argument("--mention", default="@MinhKinhTe")
    p_flow.add_argument("--session-dir", default=".flow_session")
    p_flow.add_argument("--headless", action="store_true")
    p_flow.set_defaults(func=cmd_flow)

    # 5. ingest
    p_ing = sub.add_parser("ingest", help="Chuẩn hóa ảnh cảnh về 16:9 hoặc sinh placeholder")
    p_ing.add_argument("--from", dest="src_dir", help="Thư mục file mới tải về")
    p_ing.add_argument("--to", dest="to_dir", default="assets/scenes", help="Thư mục lưu trữ scenes")
    p_ing.add_argument("--scenes", nargs="+", type=int, help="Danh sách số ID cảnh (ví dụ: --scenes 1 2 3)")
    p_ing.add_argument("--by-order", action="store_true")
    p_ing.set_defaults(func=cmd_ingest)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except KeyboardInterrupt:
        print("\nĐã hủy tác vụ.", file=sys.stderr)
        return 130
    except Exception as e:
        log.exception("Lỗi thực thi: %s", e)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
