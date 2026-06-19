from datetime import datetime, timezone, timedelta

from modules.news import get_all_news
from modules.market import get_bitcoin_price, get_gold_price, get_vnindex
from modules.charts import get_history_with_rsi, build_candlestick_svg
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
vnindex_chart_data, vnindex_rsi, vnindex_rsi_note = get_history_with_rsi("^VNINDEX.VN")

ai_summary = get_ai_summary(
    news_items=all_news,
    bitcoin=bitcoin,
    gold=gold,
    vnindex=vnindex
)


# =========================
# TIME
# =========================

vn_time = datetime.now(timezone(timedelta(hours=7)))
report_date = vn_time.strftime("%d/%m/%Y")
updated_at = vn_time.strftime("%H:%M:%S")


# =========================
# BUILD NEWS BY SOURCE
# =========================

def build_source_news(source_name):
    source_news = [
        item for item in all_news
        if item.get("source") == source_name
    ]

    if not source_news:
        return "<p class='empty-news'>Chưa có tin.</p>"

    html = ""

    for index, item in enumerate(source_news, start=1):
        html += f"""
        <div class="terminal-news-item">
            <div class="terminal-news-index">{index:02d}</div>

            <div>
                <a href="{item['link']}" target="_blank">
                    {item['title']}
                </a>

                <p>
                    {item['summary']}
                </p>
            </div>
        </div>
        """

    return html


vnexpress_news_html = build_source_news("VnExpress")
dantri_news_html = build_source_news("Dân Trí")
bbc_news_html = build_source_news("BBC")


# =========================
# BUILD CHARTS
# =========================

bitcoin_chart_html = build_candlestick_svg(
    bitcoin_chart_data,
    "Bitcoin / Nến ngày / 3 tháng",
    "Giá BTC/USD mới nhất",
    "RSI 14 ngày"
)

gold_chart_html = build_candlestick_svg(
    gold_chart_data,
    "Vàng quốc tế / Nến ngày / 3 tháng",
    "Giá Gold Futures mới nhất",
    "RSI 14 ngày"
)

vnindex_chart_html = build_candlestick_svg(
    vnindex_chart_data,
    "VNINDEX / Nến ngày / 3 tháng",
    "Điểm VNINDEX mới nhất",
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
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>Bảng tổng hợp tin tức ngày {report_date}</title>

<style>

* {{
    box-sizing: border-box;
}}

body {{
    margin: 0;
    font-family: Arial, sans-serif;
    background: #020617;
    color: #e5e7eb;
}}

.page {{
    max-width: 1280px;
    margin: 0 auto;
    padding: 26px 18px 50px;
}}

.terminal-header {{
    background:
        linear-gradient(135deg, rgba(15, 118, 110, 0.95), rgba(30, 64, 175, 0.95)),
        #0f172a;
    border: 1px solid #1e293b;
    border-radius: 18px;
    padding: 26px;
    margin-bottom: 18px;
    box-shadow: 0 18px 40px rgba(0, 0, 0, 0.35);
}}

.header-row {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 18px;
    flex-wrap: wrap;
}}

.header-title h1 {{
    margin: 0;
    font-size: 30px;
    line-height: 1.25;
    letter-spacing: -0.5px;
}}

.subtitle {{
    margin-top: 8px;
    color: #cbd5e1;
    font-size: 14px;
    letter-spacing: 1.8px;
    text-transform: uppercase;
}}

.updated {{
    background: rgba(15, 23, 42, 0.48);
    border: 1px solid rgba(255,255,255,0.18);
    color: #f8fafc;
    padding: 11px 15px;
    border-radius: 999px;
    font-size: 14px;
    white-space: nowrap;
}}

.kpi-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
    gap: 14px;
    margin-bottom: 18px;
}}

.kpi-card {{
    background: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 16px;
    padding: 18px;
    box-shadow: 0 10px 24px rgba(0,0,0,0.22);
}}

.kpi-label {{
    color: #94a3b8;
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    margin-bottom: 10px;
}}

.kpi-value {{
    font-size: 26px;
    font-weight: bold;
    color: #f8fafc;
    margin-bottom: 8px;
}}

.kpi-note {{
    color: #94a3b8;
    font-size: 14px;
    line-height: 1.5;
}}

.kpi-news {{
    border-top: 4px solid #38bdf8;
}}

.kpi-bitcoin {{
    border-top: 4px solid #f97316;
}}

.kpi-gold {{
    border-top: 4px solid #f59e0b;
}}

.kpi-vnindex {{
    border-top: 4px solid #22c55e;
}}

.terminal-grid {{
    display: grid;
    grid-template-columns: minmax(0, 1.35fr) minmax(320px, 0.65fr);
    gap: 18px;
    margin-bottom: 18px;
}}

.panel {{
    background: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 18px;
    padding: 20px;
    box-shadow: 0 10px 24px rgba(0,0,0,0.22);
}}

.panel-title {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid #1e293b;
}}

.panel-title h2 {{
    margin: 0;
    font-size: 21px;
    color: #f8fafc;
}}

.panel-badge {{
    font-size: 12px;
    color: #93c5fd;
    background: rgba(37, 99, 235, 0.18);
    border: 1px solid rgba(59, 130, 246, 0.35);
    padding: 6px 9px;
    border-radius: 999px;
}}

.ai-summary {{
    line-height: 1.75;
    color: #dbeafe;
    font-size: 15px;
}}

.ai-summary p {{
    margin-top: 0;
}}

.ai-summary ul {{
    padding-left: 22px;
}}

.ai-summary li {{
    margin-bottom: 8px;
}}

.snapshot-list {{
    display: grid;
    gap: 12px;
}}

.snapshot-item {{
    background: #111827;
    border: 1px solid #243244;
    border-radius: 14px;
    padding: 14px;
}}

.snapshot-name {{
    color: #94a3b8;
    font-size: 13px;
    margin-bottom: 6px;
}}

.snapshot-value {{
    color: #f8fafc;
    font-size: 22px;
    font-weight: bold;
    margin-bottom: 7px;
}}

.snapshot-detail {{
    color: #cbd5e1;
    line-height: 1.5;
    font-size: 14px;
}}

.news-columns {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 14px;
}}

.news-column {{
    background: #111827;
    border: 1px solid #243244;
    border-radius: 16px;
    padding: 16px;
}}

.news-source {{
    color: #f8fafc;
    font-weight: bold;
    font-size: 18px;
    margin-bottom: 14px;
}}

.terminal-news-item {{
    display: grid;
    grid-template-columns: 38px minmax(0, 1fr);
    gap: 10px;
    padding: 12px 0;
    border-bottom: 1px solid #1f2937;
}}

.terminal-news-item:last-child {{
    border-bottom: none;
}}

.terminal-news-index {{
    width: 32px;
    height: 32px;
    border-radius: 10px;
    background: rgba(56, 189, 248, 0.12);
    border: 1px solid rgba(56, 189, 248, 0.3);
    color: #7dd3fc;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 13px;
    font-weight: bold;
}}

.terminal-news-item a {{
    color: #e5e7eb;
    text-decoration: none;
    font-weight: bold;
    line-height: 1.45;
}}

.terminal-news-item a:hover {{
    color: #38bdf8;
    text-decoration: underline;
}}

.terminal-news-item p {{
    color: #94a3b8;
    line-height: 1.6;
    font-size: 14px;
    margin: 7px 0 0;
}}

.empty-news {{
    color: #94a3b8;
}}

.chart-section {{
    margin-top: 18px;
}}

.chart-wrapper {{
    margin-top: 12px;
    background: #020617;
    border: 1px solid #1e293b;
    border-radius: 14px;
    padding: 16px;
    overflow-x: auto;
}}

.chart-title {{
    font-weight: bold;
    margin-bottom: 10px;
    color: #e5e7eb;
}}

.chart-svg {{
    width: 100%;
    min-width: 760px;
    height: auto;
}}

.grid-line {{
    stroke: #1e293b;
    stroke-width: 1;
}}

.candle-up {{
    stroke: #22c55e;
    fill: #22c55e;
}}

.candle-down {{
    stroke: #ef4444;
    fill: #ef4444;
}}

.rsi-line {{
    stroke: #38bdf8;
    stroke-width: 2;
}}

.rsi-high-line {{
    stroke: #f59e0b;
    stroke-width: 1;
    stroke-dasharray: 5 5;
}}

.rsi-low-line {{
    stroke: #22c55e;
    stroke-width: 1;
    stroke-dasharray: 5 5;
}}

.axis-text {{
    fill: #94a3b8;
    font-size: 12px;
}}

.chart-meta {{
    display: flex;
    flex-wrap: wrap;
    gap: 18px;
    margin-top: 10px;
    color: #cbd5e1;
}}

.chart-empty {{
    color: #94a3b8;
    padding: 16px;
    background: #111827;
    border-radius: 10px;
}}

.footer {{
    color: #64748b;
    text-align: center;
    font-size: 13px;
    margin-top: 24px;
}}

@media (max-width: 920px) {{
    .terminal-grid {{
        grid-template-columns: 1fr;
    }}

    .news-columns {{
        grid-template-columns: 1fr;
    }}
}}

@media (max-width: 620px) {{
    .header-title h1 {{
        font-size: 24px;
    }}

    .terminal-header,
    .panel {{
        padding: 18px;
    }}

    .kpi-value {{
        font-size: 22px;
    }}
}}

</style>

</head>

<body>

<div class="page">

    <header class="terminal-header">
        <div class="header-row">
            <div class="header-title">
                <h1>Bảng tổng hợp tin tức ngày {report_date}</h1>
                <div class="subtitle">Morning Market Terminal</div>
            </div>

            <div class="updated">
                Cập nhật lần cuối: {updated_at}
            </div>
        </div>
    </header>


    <section class="kpi-grid">

        <div class="kpi-card kpi-news">
            <div class="kpi-label">Tin nóng</div>
            <div class="kpi-value">{len(all_news)} tin</div>
            <div class="kpi-note">VnExpress • Dân Trí • BBC</div>
        </div>

        <div class="kpi-card kpi-bitcoin">
            <div class="kpi-label">Bitcoin</div>
            <div class="kpi-value">${bitcoin['price_usd']}</div>
            <div class="kpi-note">24h: {bitcoin['change_24h']} • RSI: {bitcoin_rsi}</div>
        </div>

        <div class="kpi-card kpi-gold">
            <div class="kpi-label">Vàng quốc tế</div>
            <div class="kpi-value">GC=F</div>
            <div class="kpi-note">RSI: {gold_rsi} • {gold_rsi_note}</div>
        </div>

        <div class="kpi-card kpi-vnindex">
            <div class="kpi-label">VNINDEX</div>
            <div class="kpi-value">{vnindex['value']}</div>
            <div class="kpi-note">{vnindex['change']} • RSI: {vnindex_rsi}</div>
        </div>

    </section>


    <section class="terminal-grid">

        <div class="panel">
            <div class="panel-title">
                <h2>🎯 AI Market Brief</h2>
                <div class="panel-badge">AUTO SUMMARY</div>
            </div>

            <div class="ai-summary">
                {ai_summary}
            </div>
        </div>

        <div class="panel">
            <div class="panel-title">
                <h2>📈 Market Snapshot</h2>
                <div class="panel-badge">LIVE DATA</div>
            </div>

            <div class="snapshot-list">

                <div class="snapshot-item">
                    <div class="snapshot-name">₿ Bitcoin</div>
                    <div class="snapshot-value">${bitcoin['price_usd']}</div>
                    <div class="snapshot-detail">
                        Quy đổi: {bitcoin['price_vnd']} VND<br>
                        24h: {bitcoin['change_24h']}<br>
                        RSI: {bitcoin_rsi} — {bitcoin_rsi_note}
                    </div>
                </div>

                <div class="snapshot-item">
                    <div class="snapshot-name">🟡 Gold Futures</div>
                    <div class="snapshot-value">RSI {gold_rsi}</div>
                    <div class="snapshot-detail">
                        {gold_rsi_note}<br>
                        {gold['note']}
                    </div>
                </div>

                <div class="snapshot-item">
                    <div class="snapshot-name">📊 VNINDEX</div>
                    <div class="snapshot-value">{vnindex['value']}</div>
                    <div class="snapshot-detail">
                        {vnindex['change']}<br>
                        RSI: {vnindex_rsi} — {vnindex_rsi_note}
                    </div>
                </div>

            </div>
        </div>

    </section>


    <section class="panel">
        <div class="panel-title">
            <h2>🔥 Tin nóng hôm nay</h2>
            <div class="panel-badge">RSS FEEDS</div>
        </div>

        <div class="news-columns">

            <div class="news-column">
                <div class="news-source">VnExpress</div>
                {vnexpress_news_html}
            </div>

            <div class="news-column">
                <div class="news-source">Dân Trí</div>
                {dantri_news_html}
            </div>

            <div class="news-column">
                <div class="news-source">BBC</div>
                {bbc_news_html}
            </div>

        </div>
    </section>


    <section class="panel chart-section">
        <div class="panel-title">
            <h2>📊 Bitcoin / Nến ngày / 3 tháng</h2>
            <div class="panel-badge">BTC-USD</div>
        </div>

        {bitcoin_chart_html}
    </section>


    <section class="panel chart-section">
        <div class="panel-title">
            <h2>🟡 Vàng / Nến ngày / 3 tháng</h2>
            <div class="panel-badge">GC=F</div>
        </div>

        {gold_chart_html}
    </section>


    <section class="panel chart-section">
        <div class="panel-title">
            <h2>📊 VNINDEX / Nến ngày / 3 tháng</h2>
            <div class="panel-badge">^VNINDEX.VN</div>
        </div>

        {vnindex_chart_html}
    </section>


    <div class="footer">
        Dữ liệu được tổng hợp tự động từ RSS, Yahoo Finance, CoinGecko và OpenAI API.
    </div>

</div>

</body>
</html>
"""


# =========================
# WRITE FILE
# =========================

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)


print(f"Generated dashboard at {updated_at} - {report_date}")
print(f"Loaded {len(all_news)} news items from RSS feeds")
print(f"Bitcoin USD: {bitcoin['price_usd']}")
print(f"Bitcoin RSI: {bitcoin_rsi}")
print(f"Gold RSI: {gold_rsi}")
print(f"VNINDEX: {vnindex['value']}")
print(f"VNINDEX RSI: {vnindex_rsi}")
print("AI Summary: generated")
