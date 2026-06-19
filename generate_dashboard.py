from datetime import datetime, timezone, timedelta

from modules.news import get_all_news
from modules.market import get_bitcoin_price, get_gold_price, get_vnindex
from modules.charts import get_history_with_rsi, build_chart_svg
from modules.ai_summary import get_ai_summary


# =========================
# LOAD DATA
# =========================

all_news = get_all_news(limit_per_source=5)

bitcoin = get_bitcoin_price()
gold = get_gold_price()
vnindex = get_vnindex()

bitcoin_chart_data, bitcoin_rsi, bitcoin_rsi_note = get_history_with_rsi("BTC-USD")
gold_chart_data, gold_rsi, gold_rsi_note = get_history_with_rsi("GC=F")

ai_summary = get_ai_summary()


# =========================
# TIME
# =========================

vn_time = datetime.now(timezone(timedelta(hours=7)))
updated_at = vn_time.strftime("%H:%M:%S ngày %d/%m/%Y")


# =========================
# BUILD NEWS HTML
# =========================

news_html = ""

if all_news:
    for index, item in enumerate(all_news, start=1):
        news_html += f"""
        <li class="news-item">
            <a href="{item['link']}" target="_blank">
                <strong>
                    {index}. [{item['source']}] {item['title']}
                </strong>
            </a>

            <div class="news-summary">
                {item['summary']}
            </div>
        </li>
        """
else:
    news_html = "<li>Không lấy được dữ liệu RSS.</li>"


bitcoin_chart_html = build_chart_svg(
    bitcoin_chart_data,
    "Bitcoin 3 tháng gần nhất",
    "Giá BTC/USD mới nhất",
    "RSI 14 ngày"
)

gold_chart_html = build_chart_svg(
    gold_chart_data,
    "Vàng quốc tế 3 tháng gần nhất",
    "Giá Gold Futures mới nhất",
    "RSI 14 ngày"
)


# =========================
# HTML PAGE
# =========================

html_content = f"""
<!DOCTYPE html>
<html lang="vi">

<head>
<meta charset="UTF-8">

<title>Morning Financial Agent</title>

<style>

body {{
    font-family: Arial, sans-serif;
    max-width: 1100px;
    margin: 40px auto;
    padding: 20px;
    background: #f5f7fb;
    color: #222;
}}

.card {{
    background: white;
    padding: 24px;
    margin-bottom: 20px;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}}

h1 {{
    color: #0f766e;
}}

h2 {{
    color: #dc2626;
}}

.time {{
    font-size: 18px;
    font-weight: bold;
    color: #2563eb;
}}

ul {{
    list-style: none;
    padding-left: 0;
}}

.news-item {{
    margin-bottom: 28px;
    line-height: 1.6;
}}

.news-item a {{
    color: #111827;
    text-decoration: none;
    font-size: 17px;
}}

.news-item a:hover {{
    text-decoration: underline;
}}

.news-summary {{
    margin-top: 8px;
    color: #555;
    line-height: 1.7;
    font-size: 15px;
}}

.market-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    gap: 16px;
}}

.market-box {{
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    padding: 18px;
    border-radius: 10px;
}}

.market-value {{
    font-size: 24px;
    font-weight: bold;
    color: #111827;
    margin: 8px 0;
}}

.market-note {{
    color: #6b7280;
    line-height: 1.5;
}}

.chart-wrapper {{
    margin-top: 18px;
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 16px;
    overflow-x: auto;
}}

.chart-title {{
    font-weight: bold;
    margin-bottom: 10px;
    color: #111827;
}}

.chart-svg {{
    width: 100%;
    min-width: 760px;
    height: auto;
}}

.grid-line {{
    stroke: #e5e7eb;
    stroke-width: 1;
}}

.price-line {{
    stroke: #2563eb;
    stroke-width: 2.5;
}}

.rsi-line {{
    stroke: #dc2626;
    stroke-width: 2;
}}

.rsi-high-line {{
    stroke: #f59e0b;
    stroke-width: 1;
    stroke-dasharray: 5 5;
}}

.rsi-low-line {{
    stroke: #10b981;
    stroke-width: 1;
    stroke-dasharray: 5 5;
}}

.axis-text {{
    fill: #6b7280;
    font-size: 12px;
}}

.chart-meta {{
    display: flex;
    flex-wrap: wrap;
    gap: 18px;
    margin-top: 10px;
    color: #374151;
}}

.chart-empty {{
    color: #6b7280;
    padding: 16px;
    background: #f9fafb;
    border-radius: 10px;
}}

.placeholder {{
    color: #6b7280;
}}

</style>

</head>

<body>

<div class="card">

    <h1>Morning Financial Agent</h1>

    <p>
        Dashboard tài chính tự động bằng
        Python + GitHub Actions + GitHub Pages
    </p>

    <p>Cập nhật lần cuối:</p>

    <p class="time">
        {updated_at}
    </p>

</div>


<div class="card">

    <h2>🔥 Tin nóng hôm nay</h2>

    <p>
        Nguồn:
        VnExpress • Dân Trí • BBC
    </p>

    <ul>
        {news_html}
    </ul>

</div>


<div class="card">

    <h2>📈 Thị trường</h2>

    <div class="market-grid">

        <div class="market-box">
            <h3>📈 Giá vàng</h3>
            <p>Mua vào: <strong>{gold['buy']}</strong></p>
            <p>Bán ra: <strong>{gold['sell']}</strong></p>
            <p>Biến động: <strong>{gold['change']}</strong></p>
            <p>RSI: <strong>{gold_rsi}</strong></p>
            <p class="market-note">{gold_rsi_note}</p>
            <p class="market-note">{gold['note']}</p>
        </div>

        <div class="market-box">
            <h3>₿ Bitcoin</h3>
            <p class="market-value">${bitcoin['price_usd']}</p>
            <p>Quy đổi: <strong>{bitcoin['price_vnd']} VND</strong></p>
            <p>24h: <strong>{bitcoin['change_24h']}</strong></p>
            <p>RSI: <strong>{bitcoin_rsi}</strong></p>
            <p class="market-note">{bitcoin_rsi_note}</p>
            <p class="market-note">{bitcoin['note']}</p>
        </div>

        <div class="market-box">
            <h3>📊 VNINDEX</h3>
            <p class="market-value">{vnindex['value']}</p>
            <p>Biến động: <strong>{vnindex['change']}</strong></p>
            <p class="market-note">{vnindex['note']}</p>
        </div>

    </div>

</div>


<div class="card">

    <h2>📊 Chart Bitcoin</h2>

    {bitcoin_chart_html}

</div>


<div class="card">

    <h2>📊 Chart vàng</h2>

    {gold_chart_html}

</div>


<div class="card">

    <h2>🎯 AI Summary</h2>

    <p class="placeholder">
        {ai_summary}
    </p>

</div>

</body>
</html>
"""


# =========================
# WRITE FILE
# =========================

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)


print(f"Generated dashboard at {updated_at}")
print(f"Loaded {len(all_news)} news items from RSS feeds")
print(f"Bitcoin USD: {bitcoin['price_usd']}")
print(f"Bitcoin RSI: {bitcoin_rsi}")
print(f"Gold RSI: {gold_rsi}")
print(f"Gold status: {gold['note']}")
print(f"VNINDEX status: {vnindex['note']}")
