import requests
import yfinance as yf
import pandas as pd


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


def format_vnd(value):
    try:
        return f"{float(value):,.0f} VND/lượng"
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


def extract_gold_price(data):
    if not data:
        return None

    possible_lists = []

    if isinstance(data, list):
        possible_lists.append(data)

    if isinstance(data, dict):
        for key in ["data", "prices", "items", "results"]:
            if isinstance(data.get(key), list):
                possible_lists.append(data.get(key))

        for value in data.values():
            if isinstance(value, list):
                possible_lists.append(value)

    for items in possible_lists:
        for item in items:
            if not isinstance(item, dict):
                continue

            text = " ".join(
                str(item.get(k, ""))
                for k in ["code", "name", "type", "brand", "gold_type"]
            ).lower()

            if (
                "sjc" in text
                or "sjl1l10" in text
                or "vngsjc" in text
            ):
                buy = (
                    item.get("buy")
                    or item.get("buy_price")
                    or item.get("buyPrice")
                    or item.get("bid")
                )

                sell = (
                    item.get("sell")
                    or item.get("sell_price")
                    or item.get("sellPrice")
                    or item.get("ask")
                )

                updated = (
                    item.get("updated_at")
                    or item.get("updatedAt")
                    or item.get("time")
                    or item.get("date")
                    or ""
                )

                if buy and sell:
                    return {
                        "buy": buy,
                        "sell": sell,
                        "updated": updated
                    }

    if isinstance(data, dict):
        buy = (
            data.get("buy")
            or data.get("buy_price")
            or data.get("buyPrice")
            or data.get("bid")
        )

        sell = (
            data.get("sell")
            or data.get("sell_price")
            or data.get("sellPrice")
            or data.get("ask")
        )

        updated = (
            data.get("updated_at")
            or data.get("updatedAt")
            or data.get("time")
            or data.get("date")
            or ""
        )

        if buy and sell:
            return {
                "buy": buy,
                "sell": sell,
                "updated": updated
            }

    return None


def get_gold_price():
    api_urls = [
        "https://www.vang.today/api/v1/gold/SJL1L10",
        "https://www.vang.today/api/v1/gold/VNGSJC",
        "https://giavang.now/api/v1/gold/SJL1L10",
        "https://giavang.now/api/v1/gold/VNGSJC",
    ]

    for url in api_urls:
        data = safe_request_json(url)

        gold_data = extract_gold_price(data)

        if gold_data:
            buy = gold_data.get("buy")
            sell = gold_data.get("sell")
            updated = gold_data.get("updated", "")

            note = "Giá vàng trong nước SJC, đơn vị VND/lượng."
            if updated:
                note += f" Cập nhật: {updated}."

            return {
                "buy": format_vnd(buy),
                "sell": format_vnd(sell),
                "change": "Đang cập nhật",
                "note": note
            }

    return {
        "buy": "N/A",
        "sell": "N/A",
        "change": "N/A",
        "note": "Chưa lấy được giá vàng trong nước. Chart bên dưới vẫn dùng dữ liệu vàng quốc tế Gold Futures: GC=F."
    }


def get_vnindex():
    try:
        data = yf.download(
            "^VNINDEX.VN",
            period="7d",
            interval="1d",
            progress=False,
            auto_adjust=False
        )

        if data.empty:
            return {
                "value": "N/A",
                "change": "N/A",
                "note": "Không lấy được dữ liệu VNINDEX từ Yahoo Finance."
            }

        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        data = data.dropna()
        latest = data.iloc[-1]

        close = float(latest["Close"])
        open_price = float(latest["Open"])

        change_value = close - open_price
        change_percent = (change_value / open_price) * 100 if open_price else 0

        sign = "+" if change_value >= 0 else ""

        return {
            "value": f"{close:,.2f}",
            "change": f"{sign}{change_value:,.2f} điểm / {sign}{change_percent:.2f}%",
            "note": "Dữ liệu VNINDEX lấy từ Yahoo Finance ticker ^VNINDEX.VN."
        }

    except Exception as e:
        print(f"ERROR loading VNINDEX: {e}")

        return {
            "value": "N/A",
            "change": "N/A",
            "note": "Lỗi khi lấy dữ liệu VNINDEX."
        }
