import html
import os
import re
from datetime import datetime, timezone, timedelta

try:
    from zoneinfo import ZoneInfo
except Exception:
    ZoneInfo = None


FAST_MODE = os.getenv("FAST_MODE", "true").lower() == "false"


STABLECOINS = {
    "USDT", "USDC", "DAI", "FDUSD", "TUSD", "PYUSD", "USDE", "USDD",
    "FRAX", "LUSD", "BUSD", "GUSD", "EURC"
}


NEWS_KEYWORDS = [
    "kinh tế", "thị trường", "chứng khoán", "cổ phiếu", "vn-index",
    "vnindex", "vàng", "usd", "lãi suất", "ngân hàng", "tỷ giá",
    "bitcoin", "crypto", "tiền số", "đầu tư", "bất động sản",
    "doanh nghiệp", "xuất khẩu", "nhập khẩu", "fed", "oil", "gold",
    "stock", "market", "finance", "economy", "inflation", "rate"
]


def vn_now():
    if ZoneInfo:
        return datetime.now(ZoneInfo("Asia/Ho_Chi_Minh"))
    return datetime.now(timezone.utc) + timedelta(hours=7)


def safe_text(value, default="N/A"):
    if value is None:
        return default
    return html.escape(str(value))


def is_na(value):
    if value is None:
        return True
    return str(value).strip().upper() in {"", "N/A", "NONE", "NULL"}


def parse_percent(value):
    if value is None:
        return None

    match = re.search(r"[-+]?\d+(\.\d+)?", str(value))

    if not match:
        return None

    try:
        return float(match.group(0))
    except Exception:
        return None


def clean_price_prefix(value, prefix="$"):
    if is_na(value):
        return "N/A"

    text = str(value)

    if text.startswith(prefix):
        return text

    return f"{prefix}{text}"


def render_list(items):
    return "".join([f"<li>{safe_text(item)}</li>" for item in items])


def filter_crypto_items(items, limit=8):
    filtered = []

    for item in items or []:
        symbol = str(item.get("symbol", "")).upper()

        if not symbol or symbol in STABLECOINS:
            continue

        filtered.append(item)

        if len(filtered) >= limit:
            break

    return filtered


def is_financial_news(item):
    text = f"{item.get('title', '')} {item.get('summary', '')}".lower()
    return any(keyword.lower() in text for keyword in NEWS_KEYWORDS)


def filter_curated_news(news_items, max_items=15):
    curated = [item for item in news_items if is_financial_news(item)]

    if len(curated) < 6:
        curated = news_items

    return curated[:max_items]


def group_news_by_source(news_items):
    grouped = {
        "VnExpress": [],
        "Dân Trí": [],
        "BBC": [],
    }

    for item in news_items:
        source = item.get("source", "Khác")
        grouped.setdefault(source, [])
        grouped[source].append(item)

    return grouped
