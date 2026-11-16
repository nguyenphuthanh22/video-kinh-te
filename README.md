# video-kinh-te — Playwright Pipeline

Pipeline tự động hóa trình duyệt bằng Playwright phục vụ sản xuất hình ảnh/footage tỷ lệ 16:9 (1920×1080) cho video kinh tế & tài chính:

1. **Render Infographic Card Kinh Tế 16:9 (`card`)**: Sinh các card đồ họa tài chính độ phân giải 1920×1080 chuẩn 16:9 trực tiếp bằng Playwright:
   - **Metric Card**: Chỉ số tài chính, lãi suất, giá vàng, GDP (ví dụ: `LÃI SUẤT FED: 4.5%`, `GIÁ VÀNG SJC: 82.500.000 VNĐ`).
   - **Breaking News Card**: Tin tức nóng, tiêu đề sự kiện thị trường khẩn cấp.
   - **Quote Card**: Danh ngôn, nhận định chuyên gia kinh tế (Warren Buffett, Jerome Powell,...).
2. **Chụp Biểu Đồ & Web Tài Chính 16:9 (`capture`)**: Tự động mở các trang tài chính (TradingView, CafeF, Vietstock, VnExpress Kinh doanh), xóa quảng cáo / banner cookie và chụp màn hình chuẩn 16:9.
3. **Tự Động Hóa Google Flow (`flow`)**: Tương tác với Google Flow (Labs FX) qua Playwright context để tạo nhân vật đồng nhất (`@MinhKinhTe`), sinh ảnh kịch bản và chẩn đoán giao diện (`doctor`).
4. **Bộ Chuẩn Hóa & Placeholder (`ingest`)**: Tự động crop/scale ảnh về chuẩn 1920×1080 (Lanczos) hoặc tạo placeholder khi chưa có asset thật để pipeline dựng video không bao giờ bị nghẽn.

---

## 1. Cài Đặt

Yêu cầu:
- Python 3.10 trở lên
- Thư viện Playwright & trình duyệt Chromium

```powershell
pip install -r requirements.txt
python -m playwright install chromium
```

---

## 2. Hướng Dẫn Sử Dụng

### Kiểm tra môi trường
```powershell
python playwright_pipeline.py check
```

### Tạo Card Đồ Họa Kinh Tế 16:9 (1920×1080)
```powershell
# 1. Card chỉ số tài chính (Metric Card)
python playwright_pipeline.py card --type metric --title "LÃI SUẤT FED" --value "4.5%" --delta "-0.25%" --subtitle "Dự báo quý 4/2026" -o output/scene_001.png

# 2. Card tin nóng thị trường (Breaking News)
python playwright_pipeline.py card --type breaking --headline "GIÁ VÀNG SJC VƯỢT 82.500.000 ĐỒNG/LƯỢNG" --subtitle "Thị trường vàng trong nước ghi nhận mức kỷ lục mới" -o output/scene_002.png

# 3. Card danh ngôn / nhận định chuyên gia (Quote)
python playwright_pipeline.py card --type quote --title "Hãy tham lam khi người khác sợ hãi." --author "Warren Buffett" --subtitle "Chủ tịch Berkshire Hathaway" -o output/scene_003.png
```

### Chụp biểu đồ / trang web tài chính 16:9
```powershell
python playwright_pipeline.py capture --url "https://vnexpress.net/kinh-doanh" -o output/scene_004.png
```

### Tự động hóa Google Flow
```powershell
# Chẩn đoán giao diện & selector Google Flow
python playwright_pipeline.py flow doctor -o output/flow_doctor

# Sinh ảnh nhân vật tham chiếu (@MinhKinhTe)
python playwright_pipeline.py flow character --name MinhKinhTe -o assets/characters

# Sinh ảnh theo các cảnh kịch bản
python playwright_pipeline.py flow scenes --prompts flow_prompts.json -o output/scenes
```

### Chuẩn hóa ảnh về 16:9 hoặc sinh ảnh placeholder
```powershell
python playwright_pipeline.py ingest --from ./downloads --to ./assets/scenes --scenes 1 2 3
```

---

## 3. Kiểm Thử Tự Động

Bộ unit test kiểm thử toàn diện module trình duyệt, template card, quản lý asset và selector Flow mà không phụ thuộc vào mạng hay đăng nhập Google:

```powershell
python -m pytest tests -v
```
