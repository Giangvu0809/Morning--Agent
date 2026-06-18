from datetime import datetime
import random

html = f"""
<html>
<body>
<h1>TEST</h1>
<p>{datetime.now()}</p>
<p>Random: {random.randint(100000,999999)}</p>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Done")
