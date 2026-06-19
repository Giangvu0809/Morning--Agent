import requests
from datetime import datetime


COINGECKO_MARKETS_URL = "https://api.coingecko.com/api/v3/coins/markets"
BINANCE_FUTURES_24H_URL = "https://fapi.binance.com/fapi/v1/ticker/24hr"
BINANCE_FUNDING_URL = "https://fapi.binance.com/fapi/v1/premiumIndex"
FEAR_GREED_URL = "https://api.alternative.me/fng/"


DEFAULT_COINS = [
    "bitcoin",
    "ethereum",
    "solana",
    "binancecoin",
    "ripple",
    "dogecoin",
    "cardano",
    "avalanche-2",
    "chainlink",
    "toncoin",
]


def safe_get_json(url, params=None, timeout=15):
    try:
        response = requests.get(url, params=params, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except Exception as exc:
        print(f"[crypto_alpha] API error: {url} - {exc}")
        return None


def get_coingecko_markets(vs_currency="usd", limit=50):
    params = {
        "vs_currency": vs_currency,
        "order": "volume_desc",
        "per_page": limit,
        "page": 1,
        "sparkline": "false",
        "price_change_percentage": "1h,24h,7d",
    }

    data = safe_get_json(COINGECKO_MARKETS_URL, params=params)

    if not isinstance(data, list):
        return []

    results = []

    for coin in data:
        results.append({
            "id": coin.get("id"),
            "symbol": str(coin.get("symbol", "")).upper(),
            "name": coin.get("name"),
            "price": coin.get("current_price"),
            "market_cap": coin.get("market_cap"),
            "volume_24h": coin.get("total_volume"),
            "change_1h": coin.get("price_change_percentage_1h_in_currency"),
            "change_24h": coin.get("price_change_percentage_24h_in_currency"),
            "change_7d": coin.get("price_change_percentage_7d_in_currency"),
        })

    return results


def get_binance_24h():
    data = safe_get_json(BINANCE_FUTURES_24H_URL)

    if not isinstance(data, list):
        return {}

    results = {}

    for item in data:
        symbol = item.get("symbol", "")

        if not symbol.endswith("USDT"):
            continue

        base_symbol = symbol.replace("USDT", "")

        try:
            results[base_symbol] = {
                "symbol": symbol,
                "price_change_percent": float(item.get("priceChangePercent", 0)),
                "quote_volume": float(item.get("quoteVolume", 0)),
                "last_price": float(item.get("lastPrice", 0)),
            }
        except Exception:
            continue

    return results


def get_funding_rates():
    data = safe_get_json(BINANCE_FUNDING_URL)

    if not isinstance(data, list):
        return {}

    results = {}

    for item in data:
        symbol = item.get("symbol", "")

        if not symbol.endswith("USDT"):
            continue

        base_symbol = symbol.replace("USDT", "")

        try:
            results[base_symbol] = {
                "symbol": symbol,
                "mark_price": float(item.get("markPrice", 0)),
                "funding_rate": float(item.get("lastFundingRate", 0)),
                "next_funding_time": item.get("nextFundingTime"),
            }
        except Exception:
            continue

    return results


def get_fear_greed():
    data = safe_get_json(FEAR_GREED_URL, params={"limit": 1})

    try:
        item = data["data"][0]
        return {
            "value": int(item.get("value")),
            "classification": item.get("value_classification"),
            "timestamp": item.get("timestamp"),
        }
    except Exception:
        return {
            "value": None,
            "classification": "Unknown",
            "timestamp": None,
        }


def score_coin(coin, binance_data=None, funding_data=None, fear_greed=None):
    score = 0
    reasons = []

    change_24h = coin.get("change_24h") or 0
    change_7d = coin.get("change_7d") or 0
    volume_24h = coin.get("volume_24h") or 0
    market_cap = coin.get("market_cap") or 0

    if volume_24h > 0 and market_cap > 0:
        volume_ratio = volume_24h / market_cap
    else:
        volume_ratio = 0

    if volume_ratio >= 0.15:
        score += 30
        reasons.append("Volume 24h rất cao so với market cap")
    elif volume_ratio >= 0.08:
        score += 20
        reasons.append("Volume 24h tăng đáng chú ý")

    if change_24h >= 10:
        score += 25
        reasons.append("Giá tăng mạnh trong 24h")
    elif change_24h >= 5:
        score += 15
        reasons.append("Động lượng giá tích cực trong 24h")

    if change_24h <= -10:
        score += 15
        reasons.append("Giảm mạnh, có thể xuất hiện cơ hội bắt đáy rủi ro cao")

    if change_7d >= 15:
        score += 15
        reasons.append("Xu hướng 7 ngày tích cực")

    symbol = coin.get("symbol", "")

    if binance_data and symbol in binance_data:
        quote_volume = binance_data[symbol].get("quote_volume", 0)

        if quote_volume >= 1_000_000_000:
            score += 20
            reasons.append("Thanh khoản futures rất lớn trên Binance")

    if funding_data and symbol in funding_data:
        funding_rate = funding_data[symbol].get("funding_rate", 0)

        if funding_rate >= 0.0005:
            score -= 10
            reasons.append("Funding rate cao, long có thể đang quá đông")
        elif funding_rate <= -0.0003:
            score += 10
            reasons.append("Funding rate âm, có thể xuất hiện short squeeze nếu giá đảo chiều")

    if fear_greed:
        fg_value = fear_greed.get("value")

        if fg_value is not None:
            if fg_value <= 25:
                score += 10
                reasons.append("Thị trường đang sợ hãi, có thể có cơ hội tích lũy")
            elif fg_value >= 75:
                score -= 10
                reasons.append("Thị trường quá tham lam, cần quản trị rủi ro")

    return max(score, 0), reasons


def build_crypto_alpha():
    markets = get_coingecko_markets(limit=50)
    binance_24h = get_binance_24h()
    funding_rates = get_funding_rates()
    fear_greed = get_fear_greed()

    scored = []

    for coin in markets:
        score, reasons = score_coin(
            coin,
            binance_data=binance_24h,
            funding_data=funding_rates,
            fear_greed=fear_greed,
        )

        scored.append({
            **coin,
            "alpha_score": score,
            "reasons": reasons,
            "funding_rate": funding_rates.get(coin.get("symbol", ""), {}).get("funding_rate"),
        })

    top_alpha = sorted(scored, key=lambda x: x["alpha_score"], reverse=True)[:10]
    top_volume = sorted(
        scored,
        key=lambda x: (x.get("volume_24h") or 0),
        reverse=True
    )[:10]
    top_gainers = sorted(
        scored,
        key=lambda x: (x.get("change_24h") or 0),
        reverse=True
    )[:10]
    top_losers = sorted(
        scored,
        key=lambda x: (x.get("change_24h") or 0)
    )[:10]

    return {
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "fear_greed": fear_greed,
        "top_alpha": top_alpha,
        "top_volume": top_volume,
        "top_gainers": top_gainers,
        "top_losers": top_losers,
    }


def format_crypto_alpha_text(alpha_data):
    fear_greed = alpha_data.get("fear_greed", {})
    top_alpha = alpha_data.get("top_alpha", [])[:5]

    lines = []

    lines.append("Crypto Alpha Signals")
    lines.append("")
    lines.append(
        f"Fear & Greed: {fear_greed.get('value', 'N/A')} - {fear_greed.get('classification', 'Unknown')}"
    )
    lines.append("")
    lines.append("Top cơ hội theo Alpha Score:")

    for coin in top_alpha:
        reasons = coin.get("reasons") or []
        reason_text = "; ".join(reasons[:2]) if reasons else "Chưa có tín hiệu nổi bật"

        lines.append(
            f"- {coin.get('symbol')} | Score: {coin.get('alpha_score')} | "
            f"24h: {round(coin.get('change_24h') or 0, 2)}% | {reason_text}"
        )

    return "\n".join(lines)
