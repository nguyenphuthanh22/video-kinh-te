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
