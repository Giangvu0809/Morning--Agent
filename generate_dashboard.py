from datetime import datetime

html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Morning Dashboard</title>
</head>
<body>

<h1>Morning Dashboard</h1>

<p>Cập nhật lúc:
{datetime.now().strftime("%d/%m/%Y %H:%M:%S")}
</p>

<h2>Hệ thống hoạt động bình thường</h2>

</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Dashboard generated")
