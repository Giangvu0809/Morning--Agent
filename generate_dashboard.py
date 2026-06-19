from datetime import datetime, timezone, timedelta
import feedparser
import html
import re
import requests
import yfinance as yf
import pandas as pd

# =========================
# RSS SOURCES
# =========================

RSS_FEEDS = {
    "VnExpress": "https://vnexpress.net/rss/kinh-doanh.rss",
    "Dân Trí": "https://dantri.com.vn/rss/kinh-doanh.rss",
    "BBC": "https://feeds.bbci.co.uk/vietnamese/rss.xml",
}


# =========================
# CLEAN TEXT
# =========================

def clean_summary(text):
    if not text:
        return "Chưa có mô tả ngắn cho bài viết này."

    text = re.sub("<.*?>", "", text)
    text = html.unescape(text)
    text = text.strip()

    if not text:
        return "Chưa có mô tả ngắn cho bài viết này."

    return html.escape(text)


# =========================
# LOAD RSS NEWS
# =========================

def get_news_from_feed(source_name, rss_url, limit=5):
    feed = feedparser.parse(rss_url)

    news = []

    for entry in feed.entries[:limit]:
        title = html.escape(entry.get("title", "Không có tiêu đề"))
        link = entry.get("link", "#")
        summary = clean_summary(entry.get("summary", ""))

        news.append({
            "source": source_name,
            "title": title,
            "summary": summary,
            "link": link
        })

    return news


# =========================
# MARKET DATA
# =========================

def safe_request_json(url, params=None, timeout=15):
    try:
        response = requests.get(
            url,
            params=params,
            timeout=timeout,
            headers={
                "User-Agent": "Morning-Financial-Agent/1.0"
            }
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"ERROR request failed: {url} - {e}")
        return None


def format_number(value, digits=2):
    try:
        return f"{float(value):,.{digits}f}"
    except Exception:
        return "N/A"


def get_bitcoin_price():
    url = "https://api.coingecko.com/api/v3/simple/price"

    params = {
        "ids": "bitcoin",
        "vs_currencies": "usd,vnd",
        "include_24hr_change": "true"
    }

    data = safe_request_json(url, params=params)

    if not data or "bitcoin" not in data:
        return {
            "price_usd": "N/A",
            "price_vnd": "N/A",
            "change_24h": "N/A",
            "note": "Chưa lấy được dữ liệu Bitcoin."
        }

    btc = data["bitcoin"]

    price_usd = format_number(btc.get("usd"), 2)
    price_vnd = format_number(btc.get("vnd"), 0)
    change_24h_raw = btc.get("usd_24h_change")

    if change_24h_raw is None:
        change_24h = "N/A"
        trend = "Chưa có dữ liệu biến động 24h."
    else:
        change_24h = f"{float(change_24h_raw):.2f}%"
        trend = "Tăng trong 24h" if float(change_24h_raw) > 0 else "Giảm trong 24h"

    return {
        "price_usd": price_usd,
        "price_vnd": price_vnd,
        "change_24h": change_24h,
        "note": trend
    }


def get_gold_price():
    return {
        "buy": "Đang kết nối",
        "sell": "Đang kết nối",
        "change": "Đang cập nhật",
        "note": "Chart bên dưới đang dùng dữ liệu vàng quốc tế Gold Futures."
    }


def get_vnindex():
    return {
        "value": "Đang kết nối",
        "change": "Đang cập nhật",
        "note": "Sẽ nối nguồn dữ liệu VNINDEX ở bước kế tiếp."
    }


# =========================
# CHART DATA + RSI
# =========================

def calculate_rsi(close_series, period=14):
    delta = close_series.diff()

    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi


def get_history_with_rsi(ticker, period="3mo", interval="1d"):
    try:
        data = yf.download(
            ticker,
            period=period,
            interval=interval,
            progress=False,
            auto_adjust=True
        )

        if data.empty:
            print(f"ERROR no historical data for {ticker}")
            return [], "N/A", "Không có dữ liệu chart."

        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        data = data.reset_index()

        close_column = "Close"

        data["RSI"] = calculate_rsi(data[close_column], period=14)

        chart_rows = []

        for _, row in data.tail(90).iterrows():
            date_value = row["Date"]

            if hasattr(date_value, "strftime"):
                date_label = date_value.strftime("%d/%m")
            else:
                date_label = str(date_value)

            close_value = row[close_column]
            rsi_value = row["RSI"]

            if pd.isna(close_value):
                continue

            chart_rows.append({
                "date": date_label,
                "close": round(float(close_value), 2),
                "rsi": None if pd.isna(rsi_value) else round(float(rsi_value), 2)
            })

        latest_close = chart_rows[-1]["close"] if chart_rows else "N/A"
        latest_rsi = chart_rows[-1]["rsi"] if chart_rows else "N/A"

        if latest_rsi == "N/A" or latest_rsi is None:
            rsi_note = "Chưa đủ dữ liệu RSI."
        elif latest_rsi >= 70:
            rsi_note = "RSI cao: vùng mua mạnh/quá mua."
        elif latest_rsi <= 30:
            rsi_note = "RSI thấp: vùng bán mạnh/quá bán."
        else:
            rsi_note = "RSI trung tính."

        return chart_rows, latest_rsi, rsi_note

    except Exception as e:
        print(f"ERROR loading history for {ticker}: {e}")
        return [], "N/A", "Không lấy được dữ liệu chart."


def build_chart_svg(chart_data, title, price_label, rsi_label):
    if not chart_data:
        return f"""
        <div class="chart-empty">
            Không có dữ liệu chart cho {title}.
        </div>
        """

    width = 900
    height = 360
    padding_left = 55
    padding_right = 25
    padding_top = 35
    price_height = 210
    rsi_top = 265
    rsi_height = 70

    prices = [item["close"] for item in chart_data]
    rsis = [item["rsi"] for item in chart_data if item["rsi"] is not None]

    min_price = min(prices)
    max_price = max(prices)

    if min_price == max_price:
        min_price = min_price * 0.98
        max_price = max_price * 1.02

    chart_width = width - padding_left - padding_right

    points_price = []
    points_rsi = []

    for index, item in enumerate(chart_data):
        x = padding_left + (index / max(len(chart_data) - 1, 1)) * chart_width

        y_price = padding_top + (
            (max_price - item["close"]) / (max_price - min_price)
        ) * price_height

        points_price.append(f"{x:.2f},{y_price:.2f}")

        if item["rsi"] is not None:
            y_rsi = rsi_top + ((100 - item["rsi"]) / 100) * rsi_height
            points_rsi.append(f"{x:.2f},{y_rsi:.2f}")

    first_date = chart_data[0]["date"]
    last_date = chart_data[-1]["date"]

    latest_close = prices[-1]
    latest_rsi = chart_data[-1]["rsi"]

    latest_rsi_text = "N/A" if latest_rsi is None else f"{latest_rsi:.2f}"

    min_price_text = f"{min_price:,.2f}"
    max_price_text = f"{max_price:,.2f}"
    latest_price_text = f"{latest_close:,.2f}"

    return f"""
    <div class="chart-wrapper">
        <div class="chart-title">
            {title}
        </div>

        <svg viewBox="0 0 {width} {height}" class="chart-svg" role="img">

            <line x1="{padding_left}" y1="{padding_top}" x2="{width - padding_right}" y2="{padding_top}" class="grid-line" />
            <line x1="{padding_left}" y1="{padding_top + price_height}" x2="{width - padding_right}" y2="{padding_top + price_height}" class="grid-line" />

            <text x="10" y="{padding_top + 5}" class="axis-text">{max_price_text}</text>
            <text x="10" y="{padding_top + price_height}" class="axis-text">{min_price_text}</text>

            <polyline
                fill="none"
                class="price-line"
                points="{" ".join(points_price)}"
            />

            <line x1="{padding_left}" y1="{rsi_top}" x2="{width - padding_right}" y2="{rsi_top}" class="grid-line" />
            <line x1="{padding_left}" y1="{rsi_top + rsi_height * 0.3}" x2="{width - padding_right}" y2="{rsi_top + rsi_height * 0.3}" class="rsi-high-line" />
            <line x1="{padding_left}" y1="{rsi_top + rsi_height * 0.7}" x2="{width - padding_right}" y2="{rsi_top + rsi_height * 0.7}" class="rsi-low-line" />
            <line x1="{padding_left}" y1="{rsi_top + rsi_height}" x2="{width - padding_right}" y2="{rsi_top + rsi_height}" class="grid-line" />

            <text x="10" y="{rsi_top + 5}" class="axis-text">RSI 100</text>
            <text x="10" y="{rsi_top + rsi_height * 0.3 + 5}" class="axis-text">70</text>
            <text x="10" y="{rsi_top + rsi_height * 0.7 + 5}" class="axis-text">30</text>
            <text x="10" y="{rsi_top + rsi_height}" class="axis-text">0</text>

            <polyline
                fill="none"
                class="rsi-line"
                points="{" ".join(points_rsi)}"
            />

            <text x="{padding_left}" y="{height - 8}" class="axis-text">{first_date}</text>
            <text x="{width - padding_right - 45}" y="{height - 8}" class="axis-text">{last_date}</text>

        </svg>

        <div class="chart-meta">
            <span>{price_label}: <strong>{latest_price_text}</strong></span>
            <span>{rsi_label}: <strong>{latest_rsi_text}</strong></span>
        </div>
    </div>
    """


# =========================
# LOAD DATA
# =========================

all_news = []

for source_name, rss_url in RSS_FEEDS.items():
    try:
        items = get_news_from_feed(source_name, rss_url, limit=5)
        all_news.extend(items)
    except Exception as e:
        print(f"ERROR loading {source_name}: {e}")

bitcoin = get_bitcoin_price()
gold = get_gold_price()
vnindex = get_vnindex()

bitcoin_chart_data, bitcoin_rsi, bitcoin_rsi_note = get_history_with_rsi("BTC-USD")
gold_chart_data, gold_rsi, gold_rsi_note = get_history_with_rsi("GC=F")


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
    news_html = """
    <li>Không lấy được dữ liệu RSS.</li>
    """


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
        Sẽ kết nối OpenAI API sau khi dữ liệu Tin tức, Bitcoin, Vàng, Chart và RSI ổn định.
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
