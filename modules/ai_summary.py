import os
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


def get_ai_summary(news_items=None, bitcoin=None, gold=None, vnindex=None):
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return """
        Chưa cấu hình OPENAI_API_KEY. Dashboard vẫn chạy bình thường.
        Sau khi thêm GitHub Secret OPENAI_API_KEY, phần AI Summary sẽ tự động hoạt động.
        """

    news_items = news_items or []
    bitcoin = bitcoin or {}
    gold = gold or {}
    vnindex = vnindex or {}

    news_text = build_news_text(news_items)

    market_text = f"""
Bitcoin:
- Giá USD: {bitcoin.get("price_usd", "N/A")}
- Giá VND: {bitcoin.get("price_vnd", "N/A")}
- Biến động 24h: {bitcoin.get("change_24h", "N/A")}
- Ghi chú: {bitcoin.get("note", "N/A")}

Vàng:
- Mua vào: {gold.get("buy", "N/A")}
- Bán ra: {gold.get("sell", "N/A")}
- Biến động: {gold.get("change", "N/A")}
- Ghi chú: {gold.get("note", "N/A")}

VNINDEX:
- Điểm số: {vnindex.get("value", "N/A")}
- Biến động: {vnindex.get("change", "N/A")}
- Ghi chú: {vnindex.get("note", "N/A")}
"""

    prompt = f"""
Bạn là trợ lý tài chính cá nhân cho dashboard Morning Financial Agent.

Dữ liệu tin tức:
{news_text}

Dữ liệu thị trường:
{market_text}

Hãy viết bản tóm tắt tiếng Việt ngắn gọn, dễ đọc, không khuyến nghị mua bán.
Định dạng HTML đơn giản, chỉ dùng:
- <p>
- <ul>
- <li>
- <strong>

Yêu cầu nội dung:
1. Một đoạn tổng quan thị trường.
2. 3-5 ý chính từ tin tức.
3. Nhận định ngắn cho Bitcoin.
4. Nhận định ngắn cho vàng.
5. Nhận định ngắn cho VNINDEX.
6. Một câu cảnh báo: đây không phải lời khuyên đầu tư.
"""

    try:
        client = OpenAI(api_key=api_key)

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt,
            temperature=0.4,
            max_output_tokens=700
        )

        return response.output_text

    except Exception as e:
        print(f"ERROR OpenAI summary failed: {e}")

        return """
        Không tạo được AI Summary trong lần chạy này.
        Vui lòng kiểm tra OPENAI_API_KEY, billing hoặc model trong OpenAI API.
        """
