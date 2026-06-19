from datetime import datetime, timezone, timedelta
import feedparser
import html
import re
import requests

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
    # Giai đoạn này để dạng an toàn.
    # Bước tiếp theo ta sẽ chọn nguồn giá vàng ổn định rồi nối API thật.
    return {
        "buy": "Đang kết nối",
        "sell": "Đang kết nối",
        "change": "Đang cập nhật",
        "note": "Sẽ nối nguồn giá vàng SJC/PNJ/DOJI ở bước kế tiếp."
    }


def get_vnindex():
    # Giai đoạn này để dạng an toàn.
    # Bước tiếp theo ta sẽ chọn nguồn VNINDEX ổn định rồi nối API thật.
    return {
        "value": "Đang kết nối",
        "change": "Đang cập nhật",
        "note": "Sẽ nối nguồn dữ liệu VNINDEX ở bước kế tiếp."
    }


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
            <p class="market-note">{gold['note']}</p>
        </div>

        <div class="market-box">
            <h3>₿ Bitcoin</h3>
            <p class="market-value">${bitcoin['price_usd']}</p>
            <p>Quy đổi: <strong>{bitcoin['price_vnd']} VND</strong></p>
            <p>24h: <strong>{bitcoin['change_24h']}</strong></p>
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

    <h2>🎯 AI Summary</h2>

    <p class="placeholder">
        Sẽ kết nối OpenAI API sau khi dữ liệu Tin tức, Bitcoin, Vàng và VNINDEX ổn định.
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
print(f"Gold status: {gold['note']}")
print(f"VNINDEX status: {vnindex['note']}")
