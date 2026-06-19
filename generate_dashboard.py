from datetime import datetime, timezone, timedelta
import feedparser
import html

VNEXPRESS_RSS = "https://vnexpress.net/rss/kinh-doanh.rss"


def get_news():
    feed = feedparser.parse(VNEXPRESS_RSS)
    news = []

    for entry in feed.entries[:5]:
        title = html.escape(entry.get("title", "Không có tiêu đề"))
        link = entry.get("link", "#")
        news.append({
            "title": title,
            "link": link
        })

    return news


vn_time = datetime.now(timezone(timedelta(hours=7)))
updated_at = vn_time.strftime("%H:%M:%S ngày %d/%m/%Y")

news_items = get_news()

news_html = ""

if news_items:
    for index, item in enumerate(news_items, start=1):
        news_html += f"""
        <li>
          <a href="{item['link']}" target="_blank">
            {index}. {item['title']}
          </a>
        </li>
        """
else:
    news_html = "<li>Chưa lấy được tin RSS.</li>"


html_content = f"""
<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <title>Morning Financial Agent</title>
  <style>
    body {{
      font-family: Arial, sans-serif;
      max-width: 1000px;
      margin: 40px auto;
      padding: 20px;
      background: #f6f8fa;
      color: #222;
    }}

    .card {{
      background: white;
      padding: 24px;
      border-radius: 12px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.08);
      margin-bottom: 20px;
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
      padding-left: 0;
      list-style: none;
    }}

    li {{
      margin: 12px 0;
      font-size: 18px;
      line-height: 1.5;
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
    <p>Dashboard tài chính tự động bằng Python + GitHub Actions + GitHub Pages.</p>
    <p>Cập nhật lần cuối:</p>
    <p class="time">{updated_at}</p>
  </div>

  <div class="card">
    <h2>🔥 Tin nóng hôm nay</h2>
    <p>Nguồn: VnExpress Kinh doanh RSS</p>
    <ul>
      {news_html}
    </ul>
  </div>

  <div class="card">
    <h2>📈 Vàng</h2>
    <p class="placeholder">Sẽ bổ sung ở giai đoạn tiếp theo.</p>
  </div>

  <div class="card">
    <h2>₿ Bitcoin</h2>
    <p class="placeholder">Sẽ bổ sung ở giai đoạn tiếp theo.</p>
  </div>

  <div class="card">
    <h2>📊 VNINDEX</h2>
    <p class="placeholder">Sẽ bổ sung ở giai đoạn tiếp theo.</p>
  </div>

  <div class="card">
    <h2>🎯 AI Summary</h2>
    <p class="placeholder">Sẽ kết nối OpenAI API sau khi dữ liệu RSS và giá thị trường ổn định.</p>
  </div>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"Generated dashboard at {updated_at}")
print(f"Loaded {len(news_items)} news items from VnExpress")
