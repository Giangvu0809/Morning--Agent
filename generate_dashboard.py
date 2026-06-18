from datetime import datetime

with open("index.html", "w", encoding="utf-8") as f:
    f.write(f"""
    <html>
    <body>
    <h1>{datetime.now()}</h1>
    </body>
    </html>
    """)
