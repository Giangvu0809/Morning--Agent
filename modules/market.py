import requests


def safe_request_json(url, params=None, timeout=15):
    try:
        response = requests.get(
            url,
            params=params,
            timeout=timeout,
            headers={
                "User-Agent": "Morning-Financial-Agent/1.0"
            }
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
            "note": "Chưa lấy được dữ liệu Bitcoin."
        }

    btc = data["bitcoin"]

    price_usd = format_number(btc.get("usd"), 2)
    price_vnd = format_number(btc.get("vnd"), 0)
    change_24h_raw = btc.get("usd_24h_change")

    if change_24h_raw is None:
        change_24h = "N/A"
        trend = "Chưa có dữ liệu biến động 24h."
    else:
        change_24h = f"{float(change_24h_raw):.2f}%"
        trend = "Tăng trong 24h" if float(change_24h_raw) > 0 else "Giảm trong 24h"

    return {
        "price_usd": price_usd,
        "price_vnd": price_vnd,
        "change_24h": change_24h,
        "note": trend
    }


def get_gold_price():
    return {
        "buy": "Đang kết nối",
        "sell": "Đang kết nối",
        "change": "Đang cập nhật",
        "note": "Chart bên dưới đang dùng dữ liệu vàng quốc tế Gold Futures."
    }


def get_vnindex():
    return {
        "value": "Đang kết nối",
        "change": "Đang cập nhật",
        "note": "Sẽ nối nguồn dữ liệu VNINDEX ở bước kế tiếp."
    }
