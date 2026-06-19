import requests
import yfinance as yf
import pandas as pd


def safe_request_json(url, params=None, timeout=15):
    try:
        response = requests.get(
            url,
            params=params,
            timeout=timeout,
            headers={"User-Agent": "Morning-Financial-Agent/1.0"}
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"ERROR request failed: {url} - {e}")
        return None


def format_number(value, digits=2):
    try:
        return f"{float(value):,.{digits}f}"
    except Exception:
        return "N/A"


def format_vnd(value):
    try:
        return f"{float(value):,.0f} VND/lượng"
    except Exception:
        return "N/A"


def format_usd_oz(value):
    try:
        return f"${float(value):,.2f}/oz"
    except Exception:
        return "N/A"


def format_percent(value):
    try:
        value = float(value)
        sign = "+" if value >= 0 else ""
        return f"{sign}{value:.2f}%"
    except Exception:
        return "N/A"


def calc_percent_from_change(current_value, change_value):
    try:
        current_value = float(current_value)
        change_value = float(change_value)
        previous_value = current_value - change_value

        if previous_value == 0:
            return "N/A"

        percent = (change_value / previous_value) * 100
        return format_percent(percent)
    except Exception:
        return "N/A"


def get_change_class(change_text):
    try:
        if not change_text or change_text == "N/A":
            return "neutral"

        text = str(change_text).strip()

        if text.startswith("+"):
            return "positive"

        if text.startswith("-"):
            return "negative"

        return "neutral"
    except Exception:
        return "neutral"


def get_bitcoin_price():
    url = "https://api.coingecko.com/api/v3/simple/price"

    params = {
        "ids": "bitcoin",
        "vs_currencies": "usd,vnd",
        "include_24hr_change": "true"
    }

    data = safe_request_json(url, params=params)

    if not data or "bitcoin" not in data:
        return {
            "price_usd": "N/A",
            "price_vnd": "N/A",
            "change_24h": "N/A",
            "change_class": "neutral",
            "note": "Chưa lấy được dữ liệu Bitcoin."
        }

    btc = data["bitcoin"]

    price_usd = format_number(btc.get("usd"), 2)
    price_vnd = format_number(btc.get("vnd"), 0)
    change_24h_raw = btc.get("usd_24h_change")

    if change_24h_raw is None:
        change_24h = "N/A"
        note = "Chưa có dữ liệu biến động 24h."
    else:
        change_24h = format_percent(change_24h_raw)
        note = "Tăng trong 24h" if float(change_24h_raw) > 0 else "Giảm trong 24h"

    return {
        "price_usd": price_usd,
        "price_vnd": price_vnd,
        "change_24h": change_24h,
        "change_class": get_change_class(change_24h),
        "note": note
    }


def get_vang_today_price(type_code):
    url = "https://www.vang.today/api/prices"
    data = safe_request_json(url, params={"type": type_code})

    if not data:
        return None

    items = data.get("data")

    if not items or not isinstance(items, list):
        return None

    return items[0] if items else None


def get_domestic_gold_price():
    item = get_vang_today_price("SJL1L10")

    if not item:
        return {
            "buy": "N/A",
            "sell": "N/A",
            "change_24h": "N/A",
            "change_class": "neutral",
            "note": "Chưa lấy được giá vàng trong nước từ vang.today."
        }

    buy = item.get("buy")
    sell = item.get("sell")
    change_sell = item.get("change_sell")

    change_24h = calc_percent_from_change(sell, change_sell)

    return {
        "buy": format_vnd(buy),
        "sell": format_vnd(sell),
        "change_24h": change_24h,
        "change_class": get_change_class(change_24h),
        "note": "Giá vàng trong nước SJC, nguồn vang.today, đơn vị VND/lượng."
    }


def get_world_gold_price():
    item = get_vang_today_price("XAUUSD")

    if item:
        price = item.get("sell") or item.get("buy")
        change = item.get("change_sell") or item.get("change_buy")
        change_24h = calc_percent_from_change(price, change)

        return {
            "price": format_usd_oz(price),
            "change_24h": change_24h,
            "change_class": get_change_class(change_24h),
            "note": "Giá vàng thế giới XAU/USD, nguồn vang.today, đơn vị USD/oz."
        }

    try:
        data = yf.download(
            "GC=F",
            period="7d",
            interval="1d",
            progress=False,
            auto_adjust=False
        )

        if data.empty:
            return {
                "price": "N/A",
                "change_24h": "N/A",
                "change_class": "neutral",
                "note": "Không lấy được dữ liệu vàng thế giới."
            }

        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        data = data.dropna()

        latest_close = float(data.iloc[-1]["Close"])

        if len(data) < 2:
            return {
                "price": format_usd_oz(latest_close),
                "change_24h": "N/A",
                "change_class": "neutral",
                "note": "Dữ liệu vàng thế giới từ Yahoo Finance GC=F."
            }

        previous_close = float(data.iloc[-2]["Close"])
        change_percent = ((latest_close - previous_close) / previous_close) * 100
        change_24h = format_percent(change_percent)

        return {
            "price": format_usd_oz(latest_close),
            "change_24h": change_24h,
            "change_class": get_change_class(change_24h),
            "note": "Dữ liệu vàng thế giới từ Yahoo Finance Gold Futures GC=F."
        }

    except Exception as e:
        print(f"ERROR loading world gold: {e}")

        return {
            "price": "N/A",
            "change_24h": "N/A",
            "change_class": "neutral",
            "note": "Lỗi khi lấy dữ liệu vàng thế giới."
        }


def get_gold_price():
    domestic = get_domestic_gold_price()
    world = get_world_gold_price()

    return {
        "domestic": domestic,
        "world": world,
        "buy": domestic.get("buy", "N/A"),
        "sell": domestic.get("sell", "N/A"),
        "change": domestic.get("change_24h", "N/A"),
        "note": f"{domestic.get('note', '')} {world.get('note', '')}"
    }


def get_vnindex():
    try:
        data = yf.download(
            "^VNINDEX.VN",
            period="10d",
            interval="1d",
            progress=False,
            auto_adjust=False
        )

        if data.empty:
            return {
                "value": "N/A",
                "change": "N/A",
                "change_percent": "N/A",
                "change_class": "neutral",
                "note": "Không lấy được dữ liệu VNINDEX từ Yahoo Finance."
            }

        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        data = data.dropna()

        latest_close = float(data.iloc[-1]["Close"])

        if len(data) < 2:
            return {
                "value": f"{latest_close:,.2f}",
                "change": "N/A",
                "change_percent": "N/A",
                "change_class": "neutral",
                "note": "Dữ liệu VNINDEX lấy từ Yahoo Finance ticker ^VNINDEX.VN."
            }

        previous_close = float(data.iloc[-2]["Close"])
        change_value = latest_close - previous_close
        change_percent = (change_value / previous_close) * 100 if previous_close else 0

        sign = "+" if change_value >= 0 else ""
        change_text = f"{sign}{change_value:,.2f} điểm / {sign}{change_percent:.2f}%"
        change_percent_text = f"{sign}{change_percent:.2f}%"

        return {
            "value": f"{latest_close:,.2f}",
            "change": change_text,
            "change_percent": change_percent_text,
            "change_class": get_change_class(change_percent_text),
            "note": "Dữ liệu VNINDEX lấy từ Yahoo Finance ticker ^VNINDEX.VN, so với phiên liền trước."
        }

    except Exception as e:
        print(f"ERROR loading VNINDEX: {e}")

        return {
            "value": "N/A",
            "change": "N/A",
            "change_percent": "N/A",
            "change_class": "neutral",
            "note": "Lỗi khi lấy dữ liệu VNINDEX."
        }
