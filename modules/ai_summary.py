import os
import html
from openai import OpenAI


def build_news_text(news_items, max_items=8):
    lines = []

    for item in news_items[:max_items]:
        source = item.get("source", "")
        title = item.get("title", "")
        summary = item.get("summary", "")

        lines.append(
            f"- [{source}] {title}\n  Mô tả: {summary}"
        )

    return "\n".join(lines)


def fallback_summary(bitcoin, gold, vnindex):
    return f"""
    <p><strong>Bản tin tự động chưa dùng AI.</strong></p>
    <ul>
        <li>Bitcoin hiện ở mức <strong>${bitcoin.get("price_usd", "N/A")}</strong>, biến động 24h: <strong>{bitcoin.get("change_24h", "N/A")}</strong>.</li>
        <li>Vàng SJC bán ra: <strong>{gold.get("domestic", {}).get("sell", "N/A")}</strong>, 24h: <strong>{gold.get("domestic", {}).get("change_24h", "N/A")}</strong>.</li>
        <li>Vàng thế giới: <strong>{gold.get("world", {}).get("price", "N/A")}</strong>, 24h: <strong>{gold.get("world", {}).get("change_24h", "N/A")}</strong>.</li>
        <li>VNINDEX: <strong>{vnindex.get("value", "N/A")}</strong>, biến động: <strong>{vnindex.get("change", "N/A")}</strong>.</li>
    </ul>
    <p>Đây không phải lời khuyên đầu tư.</p>
    """


def clean_ai_html(text):
    if not text:
        return ""

    allowed_tags = [
        "p", "/p",
        "ul", "/ul",
        "li", "/li",
        "strong", "/strong",
        "br"
    ]

    escaped = html.escape(text)

    for tag in allowed_tags:
        escaped = escaped.replace(f"&lt;{tag}&gt;", f"<{tag}>")

    return escaped


def get_ai_summary(news_items=None, bitcoin=None, gold=None, vnindex=None):
    api_key = os.getenv("OPENAI_API_KEY")

    news_items = news_items or []
    bitcoin = bitcoin or {}
    gold = gold or {}
    vnindex = vnindex or {}

    if not api_key:
        print("OPENAI_API_KEY exists: False")
        return """
        <p><strong>Chưa cấu hình OPENAI_API_KEY.</strong></p>
        <p>Dashboard vẫn chạy bình thường. Hãy kiểm tra GitHub Secret và bước env trong workflow.</p>
        """

    print("OPENAI_API_KEY exists: True")

    news_text = build_news_text(news_items)

    market_text = f"""
Bitcoin:
- Giá USD: {bitcoin.get("price_usd", "N/A")}
- Giá VND: {bitcoin.get("price_vnd", "N/A")}
- Biến động 24h: {bitcoin.get("change_24h", "N/A")}

Vàng trong nước:
- Mua vào: {gold.get("domestic", {}).get("buy", "N/A")}
- Bán ra: {gold.get("domestic", {}).get("sell", "N/A")}
- Biến động 24h: {gold.get("domestic", {}).get("change_24h", "N/A")}

Vàng thế giới:
- Giá hiện tại: {gold.get("world", {}).get("price", "N/A")}
- Biến động 24h: {gold.get("world", {}).get("change_24h", "N/A")}

VNINDEX:
- Điểm số: {vnindex.get("value", "N/A")}
- Biến động: {vnindex.get("change", "N/A")}
"""

    prompt = f"""
Bạn là trợ lý tài chính cá nhân cho dashboard Morning Market Terminal.

Dữ liệu tin tức:
{news_text}

Dữ liệu thị trường:
{market_text}

Hãy viết bản tóm tắt tiếng Việt ngắn gọn, rõ ràng, không khuyến nghị mua bán.

Chỉ dùng HTML đơn giản:
<p>, <ul>, <li>, <strong>, <br>

Yêu cầu:
1. Một đoạn tổng quan thị trường.
2. 3-5 ý chính từ tin tức.
3. Nhận định ngắn cho Bitcoin.
4. Nhận định ngắn cho vàng trong nước.
5. Nhận định ngắn cho vàng thế giới.
6. Nhận định ngắn cho VNINDEX.
7. Một câu cảnh báo: đây không phải lời khuyên đầu tư.
"""

    try:
        client = OpenAI(api_key=api_key)

        response = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            input=prompt,
            temperature=0.4,
            max_output_tokens=700
        )

        text = response.output_text

        if not text:
            return fallback_summary(bitcoin, gold, vnindex)

        return clean_ai_html(text)

    except Exception as e:
        print(f"ERROR OpenAI summary failed: {e}")
        return fallback_summary(bitcoin, gold, vnindex)
