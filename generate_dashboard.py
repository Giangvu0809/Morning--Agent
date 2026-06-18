from datetime import datetime
import random

now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
rand = random.randint(1000, 9999)

html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Morning Dashboard</title>
</head>
<body>

<h1>Morning Dashboard</h1>

<p>Cập nhật lúc: {now}</p>

<p>Run ID: {rand}</p>

</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Dashboard generated successfully")
