```python
from datetime import datetime, timezone, timedelta
import feedparser
import html

# =========================
# RSS SOURCES
# =========================
RSS_FEEDS = {
    "VnExpress": "https://vnexpress.net/rss/kinh-doanh.rss",
    "Dân Trí": "https://dantri.com.vn/rss/kinh-doanh.rss",
    "BBC": "https://feeds.bbci.co.uk/vietnamese/rss.xml",
}


# =========================
# LOAD RSS NEWS
# =========================

def get_news_from_feed(source_name, rss_url, limit=5):
    feed = feedparser.parse(rss_url)

    news = []

    for entry in feed.entries[:limit]:
        title = html.escape(entry.get("title", "Không có tiêu đề"))
        link = entry.get("link", "#")

        news.append({
            "source": source_name,
            "title": title,
            "link": link
        })

    return news


all_news = []

for source_name, rss_url in RSS_FEEDS.items():
    try:
        items = get_news_from_feed(source_name, rss_url, limit=5)
        all_news.extend(items)
    except Exception as e:
        print(f"ERROR loading {source_name}: {e}")


# =========================
# TIME
# =========================

vn_time = datetime.now(
    timezone(
        timedelta(hours=7)
    )
)

updated_at = vn_time.strftime(
    "%H:%M:%S ngày %d/%m/%Y"
)


# =========================
# BUILD NEWS HTML
# =========================

news_html = ""

if all_news:

    for index, item in enumerate(all_news, start=1):

        news_html += f"""
        <li>
            <a href="{item['link']}" target="_blank">
                {index}. [{item['source']}] {item['title']}
            </a>
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

li {{
    margin: 12px 0;
    line-height: 1.6;
}}

a {{
    color: #111827;
    text-decoration: none;
}}

a:hover {{
    text-decoration: underline;
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

    <h2>📈 Giá vàng</h2>

    <p class="placeholder">
        Sẽ bổ sung ở bước tiếp theo.
    </p>

</div>


<div class="card">

    <h2>₿ Bitcoin</h2>

    <p class="placeholder">
        Sẽ bổ sung ở bước tiếp theo.
    </p>

</div>


<div class="card">

    <h2>📊 VNINDEX</h2>

    <p class="placeholder">
        Sẽ bổ sung ở bước tiếp theo.
    </p>

</div>


<div class="card">

    <h2>🎯 AI Summary</h2>

    <p class="placeholder">
        Sẽ kết nối OpenAI API ở giai đoạn sau.
    </p>

</div>

</body>
</html>
"""


# =========================
# WRITE FILE
# =========================

with open(
    "index.html",
    "w",
    encoding="utf-8"
) as f:

    f.write(html_content)


print(
    f"Generated dashboard at {updated_at}"
)

print(
    f"Loaded {len(all_news)} news items from RSS feeds"
)
```
