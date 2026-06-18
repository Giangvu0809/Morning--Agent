from datetime import datetime
import pytz
import feedparser
import requests
import xml.etree.ElementTree as ET

def fetch_rss_news():
    rss_sources = {
        "VnExpress": "https://vnexpress.net/rss/tin-noi-bat.rss",
        "Dân Trí": "https://dantri.com.vn/rss/home.rss",
        "BBC Tiếng Việt": "https://feeds.bbci.co.uk/vietnamese/rss.xml"
    }
    news_list = []
    for source_name, url in rss_sources.items():
        try:
            feed = feedparser.parse(url)
            for item in feed.entries[:2]: # Lấy 2 tin đầu từ mỗi nguồn
                news_list.append(f"[{source_name}] {item.title}")
        except:
            pass
    return news_list if news_list else ["Không thể tải tin tức hôm nay."]

def fetch_financial_data():
    # 1. Lấy giá Bitcoin từ Binance API
    btc_price, btc_change, btc_up = "$63,500", "-1.2%", False
    try:
        res = requests.get("https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT", timeout=5).json()
        price = float(res['lastPrice'])
        change = float(res['priceChangePercent'])
        btc_price = f"${price:,.0f}"
        btc_change = f"+{change:.1f}%" if change >= 0 else f"{change:.1f}%"
        btc_up = change >= 0
    except Exception as e:
        print(f"Lỗi lấy giá BTC: {e}")

    # 2. Lấy giá Vàng SJC thật qua API XML của DOJI/SJC đổi sang JSON
    gold_price, gold_change, gold_up = "85.0 triệu", "+0.0%", True
    try:
        # Cào dữ liệu tỷ giá vàng hôm nay từ nguồn công khai bọc try-except
        response = requests.get("https://sjc.com.vn/xml/tygiagold.xml", timeout=5)
        root = ET.fromstring(response.content)
        # Lấy loại vàng SJC TP.HCM đầu tiên
        item = root.find(".//item")
        buy = float(item.get('buy'))
        # Đổi đơn vị thành triệu đồng (ví dụ 85.00 -> 85 triệu)
        gold_price = f"{buy/1000:.1f} triệu"
    except Exception as e:
        print(f"Lỗi lấy giá Vàng: {e}")
    
    # 3. Chỉ số VNINDEX (Tạm thời neo dữ liệu mock ổn định chờ kết nối API Chứng khoán chuyên sâu ở bước sau)
    vnindex, vnindex_change, vnindex_up = "1,280", "+0.4%", True

    return {
        "gold": {"price": gold_price, "change": gold_change, "is_up": gold_up},
        "btc": {"price": btc_price, "change": btc_change, "is_up": btc_up},
        "vnindex": {"price": vnindex, "change": vnindex_change, "is_up": vnindex_up}
    }

def generate_html():
    timezone = pytz.timezone('Asia/Ho_Chi_Minh')
    current_time = datetime.now(timezone).strftime('%d/%m/%Y %H:%M')
    
    news = fetch_rss_news()
    finance = fetch_financial_data()
    
    news_li_html = "".join([f"<li>{title}</li>" for title in news])

    html_content = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Morning Intelligence Dashboard</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; padding: 40px; background-color: #f8f9fa; color: #333; }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .header h1 {{ font-size: 2.2rem; margin-bottom: 5px; }}
        .header .time {{ color: #6c757d; font-size: 0.95rem; }}
        
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; max-width: 1200px; margin: 0 auto 30px auto; }}
        .card {{ background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); border: 1px solid #eef2f5; }}
        .card-title {{ font-size: 1.1rem; font-weight: 600; margin-bottom: 15px; }}
        .card-price {{ font-size: 2rem; font-weight: bold; margin-bottom: 5px; }}
        
        .change {{ font-weight: 600; font-size: 0.95rem; display: flex; align-items: center; gap: 4px; }}
        .up {{ color: #28a745; }}
        .down {{ color: #dc3545; }}
        
        .news-section {{ background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); max-width: 1200px; margin: 0 auto; border: 1px solid #eef2f5; }}
        .news-section h2 {{ font-size: 1.5rem; margin-top: 0; margin-bottom: 20px; }}
        .news-section ul {{ padding-left: 20px; margin: 0; }}
        .news-section li {{ margin-bottom: 12px; font-size: 1.05rem; line-height: 1.6; color: #212529; }}
    </style>
</head>
<body>

    <div class="header">
        <h1>📊 Morning Intelligence Dashboard</h1>
        <div class="time">Cập nhật lần cuối: {current_time}</div>
    </div>

    <div class="grid">
        <div class="card">
            <div class="card-title">🥇 Vàng SJC (Mua vào)</div>
            <div class="card-price">{finance['gold']['price']}</div>
            <div class="change {'up' if finance['gold']['is_up'] else 'down'}">
                {'▲' if finance['gold']['is_up'] else '▼'} {finance['gold']['change']}
            </div>
        </div>

        <div class="card">
            <div class="card-title">₿ Bitcoin (USDT)</div>
            <div class="card-price">{finance['btc']['price']}</div>
            <div class="change {'up' if finance['btc']['is_up'] else 'down'}">
                {'▲' if finance['btc']['is_up'] else '▼'} {finance['btc']['change']}
            </div>
        </div>

        <div class="card">
            <div class="card-title">📈 VNINDEX</div>
            <div class="card-price">{finance['vnindex']['price']}</div>
            <div class="change {'up' if finance['vnindex']['is_up'] else 'down'}">
                {'▲' if finance['vnindex']['is_up'] else '▼'} {finance['vnindex']['change']}
            </div>
        </div>
    </div>

    <div class="news-section">
        <h2>🔥 Tin nóng hôm nay</h2>
        <ul>
            {news_li_html}
        </ul>
    </div>

</body>
</html>
"""
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("Đã cập nhật giao diện Dashboard thành công.")

if __name__ == "__main__":
    generate_html()
