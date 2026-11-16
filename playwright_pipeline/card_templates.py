"""HTML & CSS templates cho các infographic và card kinh tế 16:9 (1920x1080)."""

from __future__ import annotations

import html


BASE_STYLE = """
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}
body {
    width: 1920px;
    height: 1080px;
    overflow: hidden;
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    background: radial-gradient(circle at 80% 20%, #1a2a44 0%, #0d131f 60%, #06090e 100%);
    color: #ffffff;
    display: flex;
    align-items: center;
    justify-content: center;
}
.grid-overlay {
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background-image: 
        linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
    background-size: 60px 60px;
    pointer-events: none;
}
.accent-glow {
    position: absolute;
    width: 600px;
    height: 600px;
    border-radius: 50%;
    filter: blur(140px);
    opacity: 0.25;
    pointer-events: none;
}
"""


def render_metric_card_html(
    title: str,
    value: str,
    subtitle: str = "",
    tag: str = "KINH TẾ & THỊ TRƯỜNG",
    delta: str = "",
    is_positive: bool = True,
) -> str:
    """Card hiển thị số liệu / chỉ số kinh tế lớn (1920x1080)."""
    t_safe = html.escape(title)
    v_safe = html.escape(value)
    sub_safe = html.escape(subtitle)
    tag_safe = html.escape(tag)
    delta_safe = html.escape(delta)

    delta_color = "#10b981" if is_positive else "#ef4444"
    glow_color = "#3b82f6"

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
{BASE_STYLE}
.card {{
    position: relative;
    z-index: 10;
    width: 1400px;
    padding: 80px 100px;
    background: rgba(18, 25, 38, 0.75);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 28px;
    backdrop-filter: blur(20px);
    box-shadow: 0 30px 60px rgba(0, 0, 0, 0.6);
}}
.tag {{
    display: inline-block;
    padding: 8px 24px;
    background: rgba(59, 130, 246, 0.2);
    border: 1px solid rgba(59, 130, 246, 0.4);
    border-radius: 999px;
    color: #60a5fa;
    font-size: 24px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 30px;
}}
.title {{
    font-size: 56px;
    font-weight: 800;
    color: #f1f5f9;
    line-height: 1.2;
    margin-bottom: 24px;
    letter-spacing: -0.5px;
}}
.metric-row {{
    display: flex;
    align-items: baseline;
    gap: 30px;
    margin-top: 10px;
    margin-bottom: 24px;
}}
.value {{
    font-size: 110px;
    font-weight: 900;
    color: #FFE600;
    text-shadow: 0 4px 30px rgba(255, 230, 0, 0.35);
    letter-spacing: -2px;
}}
.delta {{
    font-size: 42px;
    font-weight: 800;
    color: {delta_color};
    padding: 6px 18px;
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.05);
}}
.subtitle {{
    font-size: 32px;
    color: #94a3b8;
    line-height: 1.5;
    font-weight: 400;
}}
</style>
</head>
<body>
<div class="grid-overlay"></div>
<div class="accent-glow" style="background: {glow_color}; top: 10%; right: 15%;"></div>
<div class="card">
    <div class="tag">{tag_safe}</div>
    <div class="title">{t_safe}</div>
    <div class="metric-row">
        <div class="value">{v_safe}</div>
        {f'<div class="delta">{delta_safe}</div>' if delta_safe else ''}
    </div>
    {f'<div class="subtitle">{sub_safe}</div>' if sub_safe else ''}
</div>
</body>
</html>"""


def render_breaking_news_html(
    headline: str,
    source: str = "TIN NÓNG KINH TẾ",
    summary: str = "",
) -> str:
    """Card đồ họa tin nóng kinh tế (1920x1080)."""
    h_safe = html.escape(headline)
    src_safe = html.escape(source)
    sum_safe = html.escape(summary)

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
{BASE_STYLE}
.container {{
    position: relative;
    z-index: 10;
    width: 1500px;
    padding: 70px 90px;
    background: rgba(15, 23, 42, 0.85);
    border-left: 12px solid #ef4444;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
    border-right: 1px solid rgba(255, 255, 255, 0.1);
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 20px;
    box-shadow: 0 40px 80px rgba(0, 0, 0, 0.7);
}}
.badge {{
    display: inline-flex;
    align-items: center;
    gap: 12px;
    background: #ef4444;
    color: #ffffff;
    font-size: 26px;
    font-weight: 800;
    padding: 10px 28px;
    border-radius: 8px;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 35px;
}}
.pulse-dot {{
    width: 14px;
    height: 14px;
    background: white;
    border-radius: 50%;
}}
.headline {{
    font-size: 64px;
    font-weight: 900;
    color: #ffffff;
    line-height: 1.25;
    margin-bottom: 30px;
    letter-spacing: -1px;
}}
.summary {{
    font-size: 34px;
    color: #cbd5e1;
    line-height: 1.6;
}}
</style>
</head>
<body>
<div class="grid-overlay"></div>
<div class="accent-glow" style="background: #ef4444; bottom: 10%; left: 10%;"></div>
<div class="container">
    <div class="badge">
        <span class="pulse-dot"></span>
        {src_safe}
    </div>
    <div class="headline">{h_safe}</div>
    {f'<div class="summary">{sum_safe}</div>' if sum_safe else ''}
</div>
</body>
</html>"""


def render_quote_card_html(
    quote: str,
    author: str,
    role: str = "",
) -> str:
    """Card trích dẫn nhận định chuyên gia kinh tế (1920x1080)."""
    q_safe = html.escape(quote)
    a_safe = html.escape(author)
    r_safe = html.escape(role)

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
{BASE_STYLE}
.card {{
    position: relative;
    z-index: 10;
    width: 1400px;
    padding: 90px 100px;
    background: rgba(17, 24, 39, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 28px;
    box-shadow: 0 30px 60px rgba(0, 0, 0, 0.6);
}}
.quote-icon {{
    font-size: 100px;
    color: #FFE600;
    line-height: 1;
    font-family: Georgia, serif;
    margin-bottom: 20px;
}}
.quote-text {{
    font-size: 48px;
    font-weight: 600;
    color: #f8fafc;
    line-height: 1.4;
    font-style: italic;
    margin-bottom: 45px;
}}
.author {{
    font-size: 38px;
    font-weight: 800;
    color: #FFE600;
}}
.role {{
    font-size: 26px;
    color: #94a3b8;
    margin-top: 8px;
}}
</style>
</head>
<body>
<div class="grid-overlay"></div>
<div class="accent-glow" style="background: #eab308; top: 15%; right: 20%;"></div>
<div class="card">
    <div class="quote-icon">“</div>
    <div class="quote-text">{q_safe}</div>
    <div class="author">{a_safe}</div>
    {f'<div class="role">{r_safe}</div>' if r_safe else ''}
</div>
</body>
</html>"""


def render_financial_chart_html(
    symbol: str,
    candles: list[dict],
    title: str = "CHỈ SỐ VN-INDEX — SÀN HOSE",
    subtitle: str = "Biểu đồ nến Nhật (Daily) • MA20 & MA50 • Khối lượng giao dịch",
) -> str:
    """Render biểu đồ kỹ thuật nến Nhật + Volume + MA20/MA50 chuẩn 16:9 (1920x1080)."""
    if not candles:
        raise ValueError("Danh sách dữ liệu nến (candles) không được rỗng.")

    sym_safe = html.escape(symbol)
    title_safe = html.escape(title)
    sub_safe = html.escape(subtitle)

    last = candles[-1]
    prev = candles[-2] if len(candles) > 1 else last
    close_val = float(last["c"])
    open_val = float(last["o"])
    high_val = float(last["h"])
    low_val = float(last["l"])
    vol_val = float(last.get("v", 0))
    change = close_val - float(prev["c"])
    pct = (change / float(prev["c"]) * 100.0) if float(prev["c"]) else 0.0
    is_up = change >= 0

    sign = "+" if is_up else ""
    badge_color = "#10b981" if is_up else "#ef4444"
    badge_bg = "rgba(16, 185, 129, 0.16)" if is_up else "rgba(239, 68, 68, 0.16)"

    # Tính toán vùng vẽ SVG (1640 x 660)
    svg_w = 1640
    svg_h = 660
    pad_left = 20
    pad_right = 115
    pad_top = 24
    price_h = 460
    vol_top = 515
    vol_h = 110
    plot_w = svg_w - pad_left - pad_right

    highs = [float(c["h"]) for c in candles]
    lows = [float(c["l"]) for c in candles]
    vols = [float(c.get("v", 0)) for c in candles]

    min_p = min(lows)
    max_p = max(highs)
    p_range = max(max_p - min_p, 1.0)
    min_p -= p_range * 0.06
    max_p += p_range * 0.06
    p_span = max_p - min_p
    max_v = max(max(vols), 1.0)

    def y_price(p: float) -> float:
        return pad_top + price_h * (1.0 - (p - min_p) / p_span)

    def y_vol(v: float) -> float:
        return vol_top + vol_h * (1.0 - min(v / max_v, 1.0))

    n = len(candles)
    step_x = plot_w / max(n, 1)
    body_w = max(min(step_x * 0.64, 18.0), 4.0)

    # Đường lưới ngang và nhãn giá bên phải
    grid_lines = []
    for i in range(6):
        p_val = min_p + (p_span * (5 - i) / 5.0)
        gy = y_price(p_val)
        grid_lines.append(
            f'<line x1="{pad_left}" y1="{gy:.1f}" x2="{pad_left + plot_w}" y2="{gy:.1f}" '
            f'stroke="rgba(148, 163, 184, 0.14)" stroke-dasharray="4 6" stroke-width="1" />'
            f'<text x="{pad_left + plot_w + 14}" y="{gy + 6:.1f}" fill="#94a3b8" '
            f'font-size="18" font-weight="600" font-family="Segoe UI, sans-serif">{p_val:,.1f}</text>'
        )

    # Đường phân cách vùng giá và khối lượng
    grid_lines.append(
        f'<line x1="{pad_left}" y1="{vol_top - 14}" x2="{pad_left + plot_w}" y2="{vol_top - 14}" '
        f'stroke="rgba(148, 163, 184, 0.22)" stroke-width="1" />'
    )

    # Vẽ nến, khối lượng và trục thời gian
    candle_elems = []
    vol_elems = []
    date_labels = []
    closes = [float(c["c"]) for c in candles]

    label_step = max(n // 7, 1)
    for idx, c in enumerate(candles):
        cx = pad_left + (idx + 0.5) * step_x
        o_p, h_p, l_p, c_p = float(c["o"]), float(c["h"]), float(c["l"]), float(c["c"])
        v_p = float(c.get("v", 0))
        up = c_p >= o_p
        color = "#10b981" if up else "#ef4444"
        vol_color = "rgba(16, 185, 129, 0.45)" if up else "rgba(239, 68, 68, 0.45)"

        yh = y_price(h_p)
        yl = y_price(l_p)
        yo = y_price(o_p)
        yc = y_price(c_p)
        top_b = min(yo, yc)
        bh = max(abs(yc - yo), 2.5)

        candle_elems.append(
            f'<line x1="{cx:.1f}" y1="{yh:.1f}" x2="{cx:.1f}" y2="{yl:.1f}" '
            f'stroke="{color}" stroke-width="2" />'
            f'<rect x="{cx - body_w / 2:.1f}" y="{top_b:.1f}" width="{body_w:.1f}" height="{bh:.1f}" '
            f'rx="1.5" fill="{color}" />'
        )

        vy = y_vol(v_p)
        vh = max((vol_top + vol_h) - vy, 2.0)
        vol_elems.append(
            f'<rect x="{cx - body_w / 2:.1f}" y="{vy:.1f}" width="{body_w:.1f}" height="{vh:.1f}" '
            f'rx="1" fill="{vol_color}" />'
        )

        if (idx % label_step == 0 and (n - 1 - idx) >= label_step // 2) or idx == n - 1:
            d_str = html.escape(str(c.get("date", "")))
            if d_str:
                date_labels.append(
                    f'<text x="{cx:.1f}" y="{svg_h - 6}" fill="#94a3b8" font-size="16" '
                    f'font-weight="600" text-anchor="middle" font-family="Segoe UI, sans-serif">{d_str}</text>'
                )

    # Tính đường MA20 và MA50
    def build_ma_polyline(period: int, stroke_color: str) -> str:
        pts = []
        for i in range(n):
            window = closes[max(0, i - period + 1) : i + 1]
            avg = sum(window) / len(window)
            px = pad_left + (i + 0.5) * step_x
            py = y_price(avg)
            pts.append(f"{px:.1f},{py:.1f}")
        return (
            f'<polyline fill="none" stroke="{stroke_color}" stroke-width="3" '
            f'stroke-linecap="round" stroke-linejoin="round" points="{" ".join(pts)}" />'
        )

    ma20_svg = build_ma_polyline(20, "#38bdf8")
    ma50_svg = build_ma_polyline(50, "#f59e0b")

    # Đường giá đóng cửa hiện tại
    last_y = y_price(close_val)
    last_line_svg = (
        f'<line x1="{pad_left}" y1="{last_y:.1f}" x2="{pad_left + plot_w}" y2="{last_y:.1f}" '
        f'stroke="{badge_color}" stroke-dasharray="6 4" stroke-width="1.8" />'
        f'<rect x="{pad_left + plot_w + 6}" y="{last_y - 15:.1f}" width="104" height="30" rx="6" fill="{badge_color}" />'
        f'<text x="{pad_left + plot_w + 58}" y="{last_y + 6:.1f}" fill="#ffffff" font-size="17" '
        f'font-weight="800" text-anchor="middle" font-family="Segoe UI, sans-serif">{close_val:,.2f}</text>'
    )

    vol_million = vol_val / 1_000_000.0 if vol_val >= 1_000_000 else vol_val
    vol_unit = "triệu CP" if vol_val >= 1_000_000 else "CP"

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
{BASE_STYLE}
.chart-wrapper {{
    position: relative;
    z-index: 10;
    width: 1760px;
    height: 960px;
    padding: 44px 56px;
    background: rgba(13, 19, 32, 0.88);
    border: 1px solid rgba(148, 163, 184, 0.18);
    border-radius: 28px;
    box-shadow: 0 35px 80px rgba(0, 0, 0, 0.75);
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}}
.header {{
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    border-bottom: 1px solid rgba(148, 163, 184, 0.16);
    padding-bottom: 24px;
}}
.title-group .symbol-badge {{
    display: inline-flex;
    align-items: center;
    gap: 10px;
    padding: 6px 18px;
    border-radius: 999px;
    background: rgba(56, 189, 248, 0.15);
    border: 1px solid rgba(56, 189, 248, 0.4);
    color: #38bdf8;
    font-size: 20px;
    font-weight: 800;
    letter-spacing: 1.5px;
    margin-bottom: 12px;
}}
.title-group h1 {{
    font-size: 42px;
    font-weight: 900;
    color: #f8fafc;
    letter-spacing: -0.5px;
}}
.title-group p {{
    font-size: 22px;
    color: #94a3b8;
    margin-top: 6px;
}}
.price-group {{
    text-align: right;
}}
.price-main {{
    display: flex;
    align-items: baseline;
    justify-content: flex-end;
    gap: 18px;
}}
.price-value {{
    font-size: 64px;
    font-weight: 900;
    color: #FFE600;
    letter-spacing: -1.5px;
}}
.price-change {{
    font-size: 28px;
    font-weight: 800;
    color: {badge_color};
    background: {badge_bg};
    border: 1px solid {badge_color};
    padding: 6px 16px;
    border-radius: 12px;
}}
.stats-row {{
    display: flex;
    gap: 28px;
    margin-top: 12px;
    justify-content: flex-end;
    font-size: 20px;
    color: #cbd5e1;
}}
.stats-row span b {{
    color: #f8fafc;
}}
.legend-bar {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 4px 4px 4px;
    font-size: 19px;
    color: #94a3b8;
}}
.legend-items {{
    display: flex;
    gap: 28px;
    align-items: center;
}}
.legend-item {{
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 600;
}}
.dot {{
    width: 16px;
    height: 4px;
    border-radius: 2px;
}}
</style>
</head>
<body>
<div class="grid-overlay"></div>
<div class="accent-glow" style="background: #2563eb; top: 8%; left: 12%;"></div>
<div class="accent-glow" style="background: {badge_color}; bottom: 8%; right: 12%;"></div>
<div class="chart-wrapper">
    <div class="header">
        <div class="title-group">
            <div class="symbol-badge">● MARKET DATA • {sym_safe}</div>
            <h1>{title_safe}</h1>
            <p>{sub_safe}</p>
        </div>
        <div class="price-group">
            <div class="price-main">
                <span class="price-value">{close_val:,.2f}</span>
                <span class="price-change">{sign}{change:,.2f} ({sign}{pct:.2f}%)</span>
            </div>
            <div class="stats-row">
                <span>Mở cửa: <b>{open_val:,.2f}</b></span>
                <span>Cao nhất: <b>{high_val:,.2f}</b></span>
                <span>Thấp nhất: <b>{low_val:,.2f}</b></span>
                <span>Khối lượng: <b>{vol_million:,.1f} {vol_unit}</b></span>
            </div>
        </div>
    </div>
    <div class="legend-bar">
        <div class="legend-items">
            <div class="legend-item"><span class="dot" style="background:#10b981;height:12px;width:12px;"></span> Nến tăng</div>
            <div class="legend-item"><span class="dot" style="background:#ef4444;height:12px;width:12px;"></span> Nến giảm</div>
            <div class="legend-item"><span class="dot" style="background:#38bdf8;"></span> MA20</div>
            <div class="legend-item"><span class="dot" style="background:#f59e0b;"></span> MA50</div>
        </div>
        <div>Nguồn dữ liệu: HOSE / VNDirect DChart • Độ phân giải chuẩn 16:9 (1920×1080)</div>
    </div>
    <svg width="{svg_w}" height="{svg_h}" viewBox="0 0 {svg_w} {svg_h}" xmlns="http://www.w3.org/2000/svg">
        {"".join(grid_lines)}
        {"".join(vol_elems)}
        {"".join(candle_elems)}
        {ma50_svg}
        {ma20_svg}
        {last_line_svg}
        {"".join(date_labels)}
    </svg>
</div>
</body>
</html>"""

