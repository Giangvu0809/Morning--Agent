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
    <p><strong>AI Market Brief đang dùng chế độ fallback.</strong></p>
    <p>
        Thị trường đang được cập nhật tự động. Bitcoin hiện biến động 
        <strong>{bitcoin.get("change_24h", "N/A")}</strong>, vàng SJC biến động 
        <strong>{gold.get("domestic", {}).get("change_24h", "N/A")}</strong>, 
        vàng thế giới biến động <strong>{gold.get("world", {}).get("change_24h", "N/A")}</strong>, 
        còn VNINDEX ghi nhận <strong>{vnindex.get("change", "N/A")}</strong>.
    </p>
    <ul>
        <li>Ưu tiên theo dõi xu hướng tài sản rủi ro như Bitcoin.</li>
        <li>Vàng trong nước cần được so sánh với vàng thế giới để đánh giá độ lệch giá.</li>
        <li>VNINDEX nên được quan sát thêm cùng thanh khoản và nhóm cổ phiếu dẫn dắt.</li>
    </ul>
    <p><strong>Lưu ý:</strong> Đây không phải lời khuyên đầu tư.</p>
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
- Biến động 24h: {bitcoin.get("change_24h", "N/A")}

Vàng trong nước:
- Biến động 24h: {gold.get("domestic", {}).get("change_24h", "N/A")}

Vàng thế giới:
- Biến động 24h: {gold.get("world", {}).get("change_24h", "N/A")}

VNINDEX:
- Biến động: {vnindex.get("change", "N/A")}
"""

    prompt = f"""
Bạn là trợ lý tài chính cá nhân cho dashboard Morning Agent Finance.

Dữ liệu tin tức:
{news_text}

Dữ liệu xu hướng thị trường:
{market_text}

Hãy viết bản tóm tắt tiếng Việt ngắn gọn, rõ ràng, chuyên nghiệp.

QUAN TRỌNG:
- Không lặp lại bảng số liệu chi tiết.
- Không đưa khuyến nghị mua bán.
- Không phóng đại.
- Tập trung vào bối cảnh, rủi ro và tín hiệu cần theo dõi.

Chỉ dùng HTML đơn giản:
<p>, <ul>, <li>, <strong>, <br>

Yêu cầu nội dung:
1. Một đoạn tổng quan ngắn về tâm lý thị trường.
2. 3-5 ý chính từ tin tức.
3. Một đoạn nhận định về tài sản rủi ro, vàng và chứng khoán Việt Nam.
4. Một câu cảnh báo: đây không phải lời khuyên đầu tư.
"""

    try:
        client = OpenAI(api_key=api_key)

        response = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            input=prompt,
            max_output_tokens=700
        )

        text = response.output_text

        if not text:
            return fallback_summary(bitcoin, gold, vnindex)

        return clean_ai_html(text)

    except Exception as e:
        print(f"ERROR OpenAI summary failed: {e}")
        return fallback_summary(bitcoin, gold, vnindex)
