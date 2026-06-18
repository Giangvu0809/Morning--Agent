from datetime import datetime

now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

html = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Morning Dashboard</title>
</head>
<body>
<h1>Morning Dashboard</h1>
<p>Cập nhật lúc: TIME_HERE</p>
</body>
</html>
"""

html = html.replace("TIME_HERE", now)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Dashboard generated successfully")
