from datetime import datetime

now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

html = f"""

<!DOCTYPE html>

<html lang="vi">

<head>
    <meta charset="UTF-8">
    <title>Morning Dashboard</title>
</head>

<body>

```
<h1>📊 Morning Intelligence Dashboard</h1>

<h2>Hệ thống hoạt động bình thường</h2>

<p>
    Cập nhật lúc:
    <strong>{now}</strong>
</p>
```

</body>

</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
f.write(html)

print("Dashboard generated successfully")
