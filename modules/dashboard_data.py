from modules.dashboard_utils import FAST_MODE, parse_percent, filter_curated_news

from modules.news import get_all_news
from modules.market import get_bitcoin_price, get_gold_price, get_vnindex
from modules.charts import get_history_with_rsi, build_candlestick_svg
from modules.ai_summary import get_ai_summary

try:
    from modules.cache import get_or_set_cache
except Exception:
    get_or_set_cache = None

try:
    from modules.crypto_alpha import build_crypto_alpha
except Exception:
    build_crypto_alpha = None

try:
    from modules.career_opportunities import build_career_opportunities
except Exception:
    build_career_opportunities = None


def cached(name, builder, max_age_minutes=60):
    if get_or_set_cache:
        return get_or_set_cache(name, builder, max_age_minutes=max_age_minutes)
    return builder()


def build_fast_charts():
    return {
        "bitcoin": {
            "html": "<div class='chart-empty'>FAST_MODE: Chart sẽ được cập nhật ở bản full build.</div>",
            "rsi": "N/A",
            "note": "Chart đang tạm ẩn để tăng tốc build.",
        },
        "gold": {
            "html": "<div class='chart-empty'>FAST_MODE: Chart sẽ được cập nhật ở bản full build.</div>",
            "rsi": "N/A",
            "note": "Chart đang tạm ẩn để tăng tốc build.",
        },
        "vnindex": {
            "html": "<div class='chart-empty'>FAST_MODE: Chart sẽ được cập nhật ở bản full build.</div>",
            "rsi": "N/A",
            "note": "Chart đang tạm ẩn để tăng tốc build.",
        },
    }


def build_charts():
    btc_history, btc_rsi, btc_rsi_note = get_history_with_rsi("BTC-USD")
    gold_history, gold_rsi, gold_rsi_note = get_history_with_rsi("GC=F")
    vnindex_history, vnindex_rsi, vnindex_rsi_note = get_history_with_rsi("^VNINDEX.VN")

    return {
        "bitcoin": {
            "html": build_candlestick_svg(btc_history, "Bitcoin / USD", "BTC Close", "RSI 14"),
            "rsi": btc_rsi,
            "note": btc_rsi_note,
        },
        "gold": {
            "html": build_candlestick_svg(gold_history, "Gold Futures / USD", "Gold Close", "RSI 14"),
            "rsi": gold_rsi,
            "note": gold_rsi_note,
        },
        "vnindex": {
            "html": build_candlestick_svg(vnindex_history, "VNINDEX", "VNINDEX Close", "RSI 14"),
            "rsi": vnindex_rsi,
            "note": vnindex_rsi_note,
        },
    }


def get_market_mood(bitcoin, gold, vnindex, crypto_alpha):
    btc_change = parse_percent(bitcoin.get("change_24h"))
    gold_change = parse_percent((gold.get("world") or {}).get("change_24h"))
    vn_change = parse_percent(vnindex.get("change_percent"))
    fear_greed = ((crypto_alpha or {}).get("fear_greed") or {}).get("value")

    risk_score = 0
    drivers = []

    if btc_change is not None:
        if btc_change < -2:
            risk_score -= 2
            drivers.append("Bitcoin suy yếu")
        elif btc_change > 2:
            risk_score += 2
            drivers.append("Bitcoin tích cực")

    if gold_change is not None:
        if gold_change > 0.5:
            risk_score -= 1
            drivers.append("Vàng tăng, dòng tiền có xu hướng phòng thủ")
        elif gold_change < -0.5:
            risk_score += 1
            drivers.append("Vàng giảm, khẩu vị rủi ro có thể cải thiện")

    if vn_change is not None:
        if vn_change < -0.5:
            risk_score -= 1
            drivers.append("VNINDEX giảm")
        elif vn_change > 0.5:
            risk_score += 1
            drivers.append("VNINDEX tích cực")

    try:
        fg = int(fear_greed)
        if fg <= 25:
            risk_score -= 2
            drivers.append("Crypto Fear & Greed ở vùng sợ hãi")
        elif fg >= 75:
            risk_score += 1
            drivers.append("Crypto Fear & Greed ở vùng tham lam")
    except Exception:
        pass

    if risk_score <= -3:
        mood = "Risk-off"
        level = "Cao"
        summary = "Thị trường nghiêng về thận trọng, ưu tiên quản trị rủi ro và chờ tín hiệu xác nhận."
    elif risk_score >= 3:
        mood = "Risk-on"
        level = "Trung bình"
        summary = "Tâm lý thị trường cải thiện, có thể theo dõi các tài sản có động lượng tốt."
    else:
        mood = "Trung tính"
        level = "Vừa phải"
        summary = "Thị trường chưa có tín hiệu áp đảo, nên ưu tiên quan sát các vùng giá quan trọng."

    if not drivers:
        drivers = ["Dữ liệu chưa đủ mạnh để xác định động lực chính."]

    return {
        "mood": mood,
        "risk_level": level,
        "summary": summary,
        "drivers": drivers[:4],
    }


def get_data_quality_warnings(bitcoin, gold, vnindex, charts, crypto_alpha, career_data):
    warnings = []

    domestic_gold = gold.get("domestic", {}) or {}
    world_gold = gold.get("world", {}) or {}

    if not domestic_gold.get("sell") or domestic_gold.get("sell") == "N/A":
        warnings.append("Vàng SJC trong nước chưa có dữ liệu khả dụng.")

    if not world_gold.get("price") or world_gold.get("price") == "N/A":
        warnings.append("Vàng thế giới chưa có dữ liệu khả dụng.")

    if not bitcoin.get("price_usd") or bitcoin.get("price_usd") == "N/A":
        warnings.append("Bitcoin chưa có dữ liệu giá USD.")

    if not vnindex.get("value") or vnindex.get("value") == "N/A":
        warnings.append("VNINDEX chưa có dữ liệu chỉ số.")

    if charts.get("vnindex", {}).get("rsi") == "N/A":
        warnings.append("RSI VNINDEX chưa đủ dữ liệu hoặc Yahoo Finance trả dữ liệu không đầy đủ.")

    if not crypto_alpha:
        warnings.append("Crypto Alpha chưa lấy được dữ liệu.")

    if not career_data:
        warnings.append("Career Opportunities chưa lấy được dữ liệu remote job.")

    if FAST_MODE:
        warnings.append("FAST_MODE đang bật: chart và AI brief chi tiết được rút gọn để tăng tốc build.")

    if not warnings:
        warnings.append("Dữ liệu chính đang hoạt động bình thường.")

    return warnings


def get_action_items(bitcoin, gold, vnindex, crypto_alpha, career_data):
    items = []

    fear_greed = ((crypto_alpha or {}).get("fear_greed") or {}).get("value")
    btc_change = parse_percent(bitcoin.get("change_24h"))
    gold_change = parse_percent((gold.get("world") or {}).get("change_24h"))
    vn_change = parse_percent(vnindex.get("change_percent"))

    if btc_change is not None:
        if btc_change < -2:
            items.append("Theo dõi Bitcoin có giữ được vùng hỗ trợ gần nhất hay không.")
        elif btc_change > 2:
            items.append("Theo dõi Bitcoin có duy trì được động lượng tăng trong phiên tiếp theo không.")

    try:
        fg = int(fear_greed)
        if fg <= 25:
            items.append("Crypto đang ở vùng sợ hãi, ưu tiên quan sát thay vì FOMO.")
        elif fg >= 75:
            items.append("Crypto đang hưng phấn, cần kiểm soát rủi ro khi đuổi giá.")
    except Exception:
        pass

    if gold_change is not None:
        if gold_change > 0:
            items.append("Theo dõi vàng thế giới vì dòng tiền phòng thủ có dấu hiệu tăng.")
        else:
            items.append("Theo dõi vàng thế giới để xác nhận xu hướng giảm hay chỉ là điều chỉnh ngắn hạn.")

    if vn_change is not None:
        if vn_change > 0:
            items.append("Quan sát nhóm cổ phiếu dẫn dắt VNINDEX nếu chỉ số tiếp tục tích cực.")
        elif vn_change < 0:
            items.append("Theo dõi thanh khoản VNINDEX để đánh giá áp lực bán.")

    if career_data:
        if career_data.get("remote_jobs"):
            items.append(f"Xem {len(career_data.get('remote_jobs', []))} remote job phù hợp trong mục Cơ hội nghề nghiệp.")

        if career_data.get("client_opportunities"):
            items.append("Ưu tiên tiếp cận nhóm khách hàng dễ chốt: học lái xe, sửa máy lạnh, trung tâm đào tạo.")

    items.append("Không dùng dashboard như khuyến nghị mua bán; chỉ dùng để phát hiện tín hiệu cần nghiên cứu thêm.")

    return items[:6]


def build_dashboard_context():
    print(f"FAST_MODE: {FAST_MODE}")

    news_items = cached("news", lambda: get_all_news(limit_per_source=8), max_age_minutes=60)

    bitcoin = cached("bitcoin", get_bitcoin_price, max_age_minutes=30)
    gold = cached("gold", get_gold_price, max_age_minutes=60)
    vnindex = cached("vnindex", get_vnindex, max_age_minutes=60)

    if FAST_MODE:
        charts = build_fast_charts()
    else:
        charts = cached("charts", build_charts, max_age_minutes=720)

    crypto_alpha = None
    if build_crypto_alpha:
        crypto_alpha = cached(
            "crypto_alpha",
            build_crypto_alpha,
            max_age_minutes=60 if FAST_MODE else 30,
        )

    career_data = None
    if build_career_opportunities:
        career_data = cached(
            "career_opportunities",
            build_career_opportunities,
            max_age_minutes=720 if FAST_MODE else 180,
        )

    if FAST_MODE:
        ai_summary = """
        <p><strong>FAST_MODE đang bật.</strong></p>
        <p>AI Market Brief chi tiết sẽ được cập nhật trong bản full build. Dashboard hiện ưu tiên tốc độ, dữ liệu thị trường, crypto alpha và cơ hội nghề nghiệp.</p>
        """
    else:
        ai_summary = get_ai_summary(
            news_items=filter_curated_news(news_items, max_items=10),
            bitcoin=bitcoin,
            gold=gold,
            vnindex=vnindex,
        )

    mood = get_market_mood(bitcoin, gold, vnindex, crypto_alpha)
    data_warnings = get_data_quality_warnings(bitcoin, gold, vnindex, charts, crypto_alpha, career_data)
    action_items = get_action_items(bitcoin, gold, vnindex, crypto_alpha, career_data)

    return {
        "news_items": news_items,
        "bitcoin": bitcoin,
        "gold": gold,
        "vnindex": vnindex,
        "charts": charts,
        "crypto_alpha": crypto_alpha,
        "career_data": career_data,
        "ai_summary": ai_summary,
        "mood": mood,
        "data_warnings": data_warnings,
        "action_items": action_items,
    }
