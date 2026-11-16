"""Kiểm thử bộ quản lý asset, chuẩn hóa 16:9 và tạo placeholder."""

from pathlib import Path
from PIL import Image

from playwright_pipeline.asset_manager import (
    create_placeholder_image,
    import_downloaded_files,
    ingest_assets,
    normalize_image_to_16_9,
    parse_scene_number,
    scan_scene_assets,
)


def test_parse_scene_number():
    assert parse_scene_number(Path("scene_001.png")) == 1
    assert parse_scene_number(Path("scene-15.mp4")) == 15
    assert parse_scene_number(Path("scene042.jpg")) == 42
    assert parse_scene_number(Path("random_image.png")) is None


def test_create_placeholder_image(tmp_path: Path):
    target = tmp_path / "placeholder_001.png"
    create_placeholder_image(target, scene_id=1, width=1920, height=1080)
    assert target.exists()
    with Image.open(target) as img:
        assert img.size == (1920, 1080)


def test_normalize_image_to_16_9(tmp_path: Path):
    # Tạo một ảnh tỷ lệ vuông 1000x1000
    src = tmp_path / "square.png"
    with Image.new("RGB", (1000, 1000), color=(255, 0, 0)) as img:
        img.save(src)

    dst = tmp_path / "normalized_16_9.png"
    normalize_image_to_16_9(src, dst, target_width=1920, target_height=1080)
    assert dst.exists()
    with Image.open(dst) as img:
        assert img.size == (1920, 1080)


def test_ingest_assets_with_placeholders(tmp_path: Path):
    scenes_dir = tmp_path / "scenes"
    norm_dir = scenes_dir / "_normalized"

    # Chỉ tạo file cho cảnh 1, cảnh 2 và 3 để trống
    scenes_dir.mkdir(parents=True, exist_ok=True)
    with Image.new("RGB", (1920, 1080), color=(0, 255, 0)) as img:
        img.save(scenes_dir / "scene_001.png")

    report = ingest_assets(
        scene_ids=[1, 2, 3],
        search_dirs=[scenes_dir],
        work_images_dir=norm_dir,
        allow_placeholder=True,
    )

    assert 1 in report.from_source
    assert 2 in report.placeholders
    assert 3 in report.placeholders
    assert len(report.assets) == 3
    assert (norm_dir / "scene_001.png").exists()
    assert (norm_dir / "placeholder_002.png").exists()
    assert (norm_dir / "placeholder_003.png").exists()


def test_import_downloaded_files(tmp_path: Path):
    dl_dir = tmp_path / "downloads"
    dest_dir = tmp_path / "dest_scenes"
    dl_dir.mkdir()

    # Tạo 2 file tải về: 1 file có số cảnh và 1 file không có số cảnh
    f1 = dl_dir / "flow_generation_scene_005.png"
    f2 = dl_dir / "unnamed_asset.png"
    f1.write_bytes(b"data1")
    f2.write_bytes(b"data2")

    copied = import_downloaded_files(dl_dir, dest_dir, scene_ids=[5, 6], by_order=True)
    assert len(copied) == 2
    assert (dest_dir / "scene_005.png").exists()
    assert (dest_dir / "scene_006.png").exists()
