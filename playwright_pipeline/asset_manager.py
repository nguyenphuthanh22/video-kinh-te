"""Quản lý, chuẩn hóa kích thước 16:9 (1920x1080), kiểm tra và tạo placeholder cho các cảnh video."""

from __future__ import annotations

import logging
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from PIL import Image, ImageDraw, ImageFont

log = logging.getLogger("playwright_pipeline.asset_manager")

IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp"}
VIDEO_EXT = {".mp4", ".mov", ".mkv", ".webm"}
SCENE_REGEX = re.compile(r"scene[_\- ]?0*(\d+)", re.IGNORECASE)


@dataclass
class IngestReport:
    """Báo cáo kết quả chuẩn bị asset cho các cảnh."""
    assets: dict[int, Path] = field(default_factory=dict)       # scene_id -> đường dẫn file chuẩn 16:9
    from_source: list[int] = field(default_factory=list)
    placeholders: list[int] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def parse_scene_number(path: Path) -> Optional[int]:
    """Trích xuất số thứ tự cảnh từ tên file (ví dụ: scene_001.png -> 1)."""
    match = SCENE_REGEX.search(path.stem)
    return int(match.group(1)) if match else None


def scan_scene_assets(*search_dirs: Path | str) -> dict[int, Path]:
    """
    Quét các thư mục để tìm file asset cho từng cảnh (scene_001.png, scene_002.mp4,...).
    Nếu cả ảnh và video cùng tồn tại cho 1 cảnh, video sẽ được ưu tiên.
    """
    found: dict[int, Path] = {}
    for d_path in search_dirs:
        d = Path(d_path)
        if not d.exists() or not d.is_dir():
            continue
        for p in sorted(d.iterdir()):
            if not p.is_file() or p.suffix.lower() not in (IMAGE_EXT | VIDEO_EXT):
                continue
            idx = parse_scene_number(p)
            if idx is None:
                continue
            cur = found.get(idx)
            # Ưu tiên video hơn ảnh tĩnh
            if cur is None or (p.suffix.lower() in VIDEO_EXT and cur.suffix.lower() in IMAGE_EXT):
                found[idx] = p
    return found


def normalize_image_to_16_9(
    src_path: Path,
    dst_path: Path,
    target_width: int = 1920,
    target_height: int = 1080,
) -> Path:
    """Crop ảnh ở giữa theo tỷ lệ 16:9 và resize về 1920x1080 bằng Pillow chất lượng cao."""
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(src_path) as img:
        img = img.convert("RGB")
        w, h = img.size
        target_ratio = target_width / target_height
        current_ratio = w / h

        if current_ratio > target_ratio:
            # Ảnh quá rộng -> crop bớt 2 bên
            new_w = int(h * target_ratio)
            offset = (w - new_w) // 2
            img = img.crop((offset, 0, offset + new_w, h))
        elif current_ratio < target_ratio:
            # Ảnh quá cao -> crop bớt trên dưới
            new_h = int(w / target_ratio)
            offset = (h - new_h) // 2
            img = img.crop((0, offset, w, offset + new_h))

        img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
        img.save(dst_path, format="PNG", quality=95)
    return dst_path


def create_placeholder_image(
    output_path: Path,
    scene_id: int,
    width: int = 1920,
    height: int = 1080,
    text: str = "",
) -> Path:
    """Tạo ảnh placeholder 16:9 đẹp mắt khi chưa có ảnh chính thức từ Flow/Web."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", (width, height), color=(15, 23, 42))  # Slate dark background
    draw = ImageDraw.Draw(img)

    # Vẽ đường viền
    draw.rectangle([(20, 20), (width - 20, height - 20)], outline=(51, 65, 85), width=4)

    # Hiển thị số cảnh
    scene_text = f"CẢNH {scene_id:03d}"
    sub_text = text or "Đang chờ ảnh từ Google Flow / Web Capture"

    # Dùng font mặc định nếu không load được font hệ thống
    draw.text((width // 2, height // 2 - 40), scene_text, fill=(255, 230, 0), anchor="mm")
    draw.text((width // 2, height // 2 + 40), sub_text, fill=(148, 163, 184), anchor="mm")

    img.save(output_path, format="PNG")
    return output_path


def ingest_assets(
    scene_ids: list[int],
    search_dirs: list[Path | str],
    work_images_dir: Path | str,
    allow_placeholder: bool = True,
    width: int = 1920,
    height: int = 1080,
) -> IngestReport:
    """Khớp asset cho từng phân cảnh, tự động chuẩn hóa 16:9 hoặc sinh placeholder."""
    report = IngestReport()
    found = scan_scene_assets(*search_dirs)
    work_dir = Path(work_images_dir)
    work_dir.mkdir(parents=True, exist_ok=True)

    for sid in scene_ids:
        src = found.get(sid)
        if src is not None:
            if src.suffix.lower() in IMAGE_EXT:
                dst = work_dir / f"scene_{sid:03d}.png"
                # Chuẩn hóa nếu chưa có hoặc file nguồn mới hơn
                if not dst.exists() or dst.stat().st_mtime < src.stat().st_mtime:
                    normalize_image_to_16_9(src, dst, width, height)
                report.assets[sid] = dst
            else:
                report.assets[sid] = src
            report.from_source.append(sid)
        elif allow_placeholder:
            dst = work_dir / f"placeholder_{sid:03d}.png"
            if not dst.exists():
                create_placeholder_image(dst, sid, width, height)
            report.assets[sid] = dst
            report.placeholders.append(sid)
        else:
            raise FileNotFoundError(f"Thiếu file asset hình ảnh/video cho cảnh {sid}")

    if report.placeholders:
        report.warnings.append(
            f"{len(report.placeholders)} cảnh đang sử dụng ảnh placeholder: {report.placeholders}"
        )
    return report


def import_downloaded_files(
    download_dir: Path | str,
    dest_dir: Path | str,
    scene_ids: list[int],
    by_order: bool = False,
) -> list[Path]:
    """
    Sao chép các file ảnh/video vừa tải về từ Flow/trình duyệt vào thư mục scenes.
    Nếu by_order=True: các file chưa có số cảnh trong tên sẽ được gán lần lượt cho các cảnh còn thiếu.
    """
    dest_dir = Path(dest_dir).resolve()
    dest_dir.mkdir(parents=True, exist_ok=True)
    copied: list[Path] = []

    src_files = [
        p for p in sorted(Path(download_dir).iterdir(), key=lambda f: f.stat().st_mtime)
        if p.is_file() and p.suffix.lower() in (IMAGE_EXT | VIDEO_EXT)
    ]

    taken_ids = set(scan_scene_assets(dest_dir).keys())
    unnamed_files: list[Path] = []

    for p in src_files:
        sid = parse_scene_number(p)
        if sid is None:
            unnamed_files.append(p)
        elif sid in scene_ids:
            dst = dest_dir / f"scene_{sid:03d}{p.suffix.lower()}"
            shutil.copy2(p, dst)
            copied.append(dst)
            taken_ids.add(sid)

    if by_order:
        missing_ids = [s for s in scene_ids if s not in taken_ids]
        for sid, p in zip(missing_ids, unnamed_files):
            dst = dest_dir / f"scene_{sid:03d}{p.suffix.lower()}"
            shutil.copy2(p, dst)
            copied.append(dst)

    return copied
