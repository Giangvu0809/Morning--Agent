from datetime import datetime
import pytz

def generate_html():
    # Lấy múi giờ Việt Nam (ICT)
    timezone = pytz.timezone('Asia/Ho_Chi_Minh')
    current_time = datetime.now(timezone).strftime('%Y-%m-%d %H:%M:%S')

    html_content = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Morning Financial Agent Dashboard</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background-color: #f4f6f9; color: #333; }}
        .container {{ background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        h1 {{ color: #0056b3; }}
        .status {{ font-weight: bold; color: #28a745; }}
        .time {{ font-style: italic; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Morning Financial Agent</h1>
        <p class="status">Trạng thái: Đang hoạt động bình thường</p>
        <p>Cập nhật lần cuối (Giờ Việt Nam): <span class="time">{current_time}</span></p>
    </div>
</body>
</html>
"""
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Đã cập nhật index.html thành công lúc {current_time}")

if __name__ == "__main__":
    generate_html()
