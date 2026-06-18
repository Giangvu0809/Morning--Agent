from datetime import datetime
import pytz
import feedparser

def fetch_rss_news():
    # Cấu hình danh sách nguồn RSS
    rss_sources = {
        "VnExpress": "https://vnexpress.net/rss/tin-noi-bat.rss",
        "Dân Trí": "https://dantri.com.vn/rss/home.rss",
        "BBC Tiếng Việt": "https://feeds.bbci.co.uk/vietnamese/rss.xml"
    }
    
    news_data = {}
    
    for source_name, url in rss_sources.items():
        try:
            feed = feedparser.parse(url)
            # Lấy tối đa 3 bài viết mới nhất từ mỗi nguồn
            entries = feed.entries[:3]
            news_data[source_name] = [
                {"title": item.title, "link": item.link} for item in entries
            ]
        except Exception as e:
            news_data[source_name] = [{"title": f"Lỗi tải tin: {str(e)}", "link": "#"}]
            
    return news_data

def generate_html():
    timezone = pytz.timezone('Asia/Ho_Chi_Minh')
    current_time = datetime.now(timezone).strftime('%Y-%m-%d %H:%M:%S')
    
    # Lấy dữ liệu tin tức
    all_news = fetch_rss_news()
    
    # Tạo chuỗi HTML động cho phần tin tức
    news_html_sections = ""
    for source, articles in all_news.items():
        news_html_sections += f"<h3>{source}</h3><ul>"
        for art in articles:
            news_html_sections += f'<li><a href="{art["link"]}" target="_blank">{art["title"]}</a></li>'
        news_html_sections += "</ul>"

    html_content = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Morning Financial Agent Dashboard</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background-color: #f4f6f9; color: #333; }}
        .container {{ background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); max-width: 800px; margin: 0 auto; }}
        h1 {{ color: #0056b3; border-bottom: 2px solid #0056b3; padding-bottom: 10px; }}
        h3 {{ color: #e44d26; margin-top: 20px; }}
        .status {{ font-weight: bold; color: #28a745; }}
        .time {{ font-style: italic; color: #666; }}
        ul {{ padding-left: 20px; }}
        li {{ margin-bottom: 8px; }}
        a {{ color: #007bff; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Morning Financial Agent</h1>
        <p class="status">Trạng thái: Đang hoạt động bình thường</p>
        <p>Cập nhật lần cuối (Giờ Việt Nam): <span class="time">{current_time}</span></p>
        
        <h2>📰 Tin Nóng Trong Nước & Quốc Tế</h2>
        {news_html_sections}
    </div>
</body>
</html>
"""
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Đã cập nhật dữ liệu RSS thành công lúc {current_time}")

if __name__ == "__main__":
    generate_html()
