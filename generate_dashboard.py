import html
import re
from datetime import datetime

from modules.news import get_all_news
from modules.market import get_bitcoin_price, get_gold_price, get_vnindex
from modules.charts import get_history_with_rsi, build_candlestick_svg
from modules.ai_summary import get_ai_summary

try:
    from modules.crypto_alpha import build_crypto_alpha
except Exception:
    build_crypto_alpha = None

try:
    from modules.career_opportunities import build_career_opportunities
except Exception:
    build_career_opportunities = None


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

    text = str(value)
    match = re.search(r"[-+]?\d+(\.\d+)?", text)

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


def is_financial_news(item):
    text = f"{item.get('title', '')} {item.get('summary', '')}".lower()
    return any(keyword.lower() in text for keyword in NEWS_KEYWORDS)


def filter_curated_news(news_items, max_items=15):
    curated = [item for item in news_items if is_financial_news(item)]

    if len(curated) < 6:
        curated = news_items

    return curated[:max_items]


def filter_crypto_items(items, limit=8):
    filtered = []

    for item in items or []:
        symbol = str(item.get("symbol", "")).upper()

        if not symbol:
            continue

        if symbol in STABLECOINS:
            continue

        filtered.append(item)

        if len(filtered) >= limit:
            break

    return filtered


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
        fear_greed = int(fear_greed)

        if fear_greed <= 25:
            risk_score -= 2
            drivers.append("Crypto Fear & Greed ở vùng sợ hãi")
        elif fear_greed >= 75:
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

    if is_na(domestic_gold.get("sell")):
        warnings.append("Vàng SJC trong nước chưa có dữ liệu khả dụng.")

    if is_na(world_gold.get("price")):
        warnings.append("Vàng thế giới chưa có dữ liệu khả dụng.")

    if is_na(bitcoin.get("price_usd")):
        warnings.append("Bitcoin chưa có dữ liệu giá USD.")

    if is_na(vnindex.get("value")):
        warnings.append("VNINDEX chưa có dữ liệu chỉ số.")

    if charts.get("vnindex", {}).get("rsi") == "N/A":
        warnings.append("RSI VNINDEX chưa đủ dữ liệu hoặc Yahoo Finance trả dữ liệu không đầy đủ.")

    if not crypto_alpha:
        warnings.append("Crypto Alpha chưa lấy được dữ liệu.")

    if not career_data:
        warnings.append("Career Opportunities chưa lấy được dữ liệu remote job.")

    if not warnings:
        warnings.append("Dữ liệu chính đang hoạt động bình thường.")

    return warnings


def get_action_items(mood, bitcoin, gold, vnindex, crypto_alpha, career_data):
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
        remote_jobs = career_data.get("remote_jobs", [])
        client_ops = career_data.get("client_opportunities", [])

        if remote_jobs:
            items.append(f"Xem {len(remote_jobs)} remote job phù hợp trong mục Cơ hội nghề nghiệp.")

        if client_ops:
            items.append("Ưu tiên tiếp cận nhóm khách hàng dễ chốt: học lái xe, sửa máy lạnh, trung tâm đào tạo.")

    items.append("Không dùng dashboard như khuyến nghị mua bán; chỉ dùng để phát hiện tín hiệu cần nghiên cứu thêm.")

    return items[:6]


def render_list(items):
    return "".join([f"<li>{safe_text(item)}</li>" for item in items])


def render_news_column(source_name, items):
    if not items:
        return f"""
        <section class="news-column">
            <h3>{safe_text(source_name)}</h3>
            <p class="muted">Chưa có tin phù hợp.</p>
        </section>
        """

    cards_html = ""

    for item in items[:5]:
        title = item.get("title", "Không có tiêu đề")
        summary = item.get("summary", "Chưa có mô tả.")
        link = item.get("link", "#")

        cards_html += f"""
        <article class="news-card">
            <a href="{safe_text(link)}" target="_blank" rel="noopener noreferrer">{title}</a>
            <p>{summary}</p>
        </article>
        """

    return f"""
    <section class="news-column">
        <h3>{safe_text(source_name)}</h3>
        {cards_html}
    </section>
    """


def render_chart_card(title, chart_html, rsi_value, rsi_note):
    return f"""
    <section class="chart-card">
        <div class="chart-card-header">
            <div>
                <span class="eyebrow">Technical Analysis</span>
                <h3>{safe_text(title)}</h3>
            </div>
            <div class="rsi-pill">RSI: {safe_text(rsi_value)}</div>
        </div>
        <p class="chart-note">{safe_text(rsi_note)}</p>
        <div class="chart-box">{chart_html}</div>
    </section>
    """


def render_crypto_alpha_section(crypto_alpha):
    if not crypto_alpha:
        return """
        <section class="panel">
            <div class="panel-header">
                <div>
                    <span class="eyebrow">Opportunity Radar</span>
                    <h2>Crypto Alpha Signals</h2>
                </div>
            </div>
            <p class="muted">Chưa có dữ liệu Crypto Alpha.</p>
        </section>
        """

    fear_greed = crypto_alpha.get("fear_greed", {}) or {}
    top_alpha = filter_crypto_items(crypto_alpha.get("top_alpha", []), limit=8)
    top_gainers = filter_crypto_items(crypto_alpha.get("top_gainers", []), limit=5)
    top_losers = filter_crypto_items(crypto_alpha.get("top_losers", []), limit=5)
    top_volume = filter_crypto_items(crypto_alpha.get("top_volume", []), limit=5)

    alpha_cards = ""

    for coin in top_alpha:
        symbol = safe_text(coin.get("symbol"))
        name = safe_text(coin.get("name"))
        score = safe_text(coin.get("alpha_score", 0))
        change_24h = coin.get("change_24h")
        cls = "neutral"

        try:
            change_num = float(change_24h or 0)
            change_text = f"{change_num:+.2f}%"

            if change_num > 0:
                cls = "positive"
            elif change_num < 0:
                cls = "negative"
        except Exception:
            change_text = "N/A"

        try:
            volume_text = f"${float(coin.get('volume_24h') or 0):,.0f}"
        except Exception:
            volume_text = "N/A"

        funding = coin.get("funding_rate")

        try:
            funding_text = f"{float(funding) * 100:+.4f}%" if funding is not None else "N/A"
        except Exception:
            funding_text = "N/A"

        reasons = coin.get("reasons") or []
        reason_text = "; ".join(reasons[:2]) if reasons else "Chưa có tín hiệu nổi bật."

        alpha_cards += f"""
        <article class="alpha-card">
            <div class="coin-line">
                <div>
                    <div class="coin-symbol">{symbol}</div>
                    <div class="coin-name">{name}</div>
                </div>
                <div class="score-badge">{score}</div>
            </div>
            <div class="metric-row">
                <span>24h</span>
                <strong class="{cls}">{safe_text(change_text)}</strong>
            </div>
            <div class="metric-row">
                <span>Volume</span>
                <strong>{safe_text(volume_text)}</strong>
            </div>
            <div class="metric-row">
                <span>Funding</span>
                <strong>{safe_text(funding_text)}</strong>
            </div>
            <p>{safe_text(reason_text)}</p>
        </article>
        """

    def render_change_list(items):
        html_items = ""

        for item in items:
            symbol = item.get("symbol", "N/A")
            change = item.get("change_24h")

            try:
                change_num = float(change or 0)
                change_text = f"{change_num:+.2f}%"
                cls = "positive" if change_num > 0 else "negative" if change_num < 0 else "neutral"
            except Exception:
                change_text = "N/A"
                cls = "neutral"

            html_items += f"""
            <li>
                <span>{safe_text(symbol)}</span>
                <strong class="{cls}">{safe_text(change_text)}</strong>
            </li>
            """

        return html_items or '<li class="muted">Chưa có dữ liệu</li>'

    def render_volume_list(items):
        html_items = ""

        for item in items:
            symbol = item.get("symbol", "N/A")

            try:
                volume = f"${float(item.get('volume_24h') or 0):,.0f}"
            except Exception:
                volume = "N/A"

            html_items += f"""
            <li>
                <span>{safe_text(symbol)}</span>
                <strong>{safe_text(volume)}</strong>
            </li>
            """

        return html_items or '<li class="muted">Chưa có dữ liệu</li>'

    return f"""
    <section class="panel">
        <div class="panel-header">
            <div>
                <span class="eyebrow">Opportunity Radar</span>
                <h2>Crypto Alpha Signals</h2>
            </div>
            <div class="updated-pill">Updated: {safe_text(crypto_alpha.get("updated_at"))}</div>
        </div>

        <div class="crypto-overview">
            <div class="sentiment-card">
                <span>Fear & Greed</span>
                <strong>{safe_text(fear_greed.get("value"))}</strong>
                <em>{safe_text(fear_greed.get("classification"))}</em>
            </div>

            <p class="muted">
                Bộ lọc đã loại stablecoin khỏi danh sách tín hiệu. Alpha Score ưu tiên volume,
                động lượng giá, thanh khoản futures và funding rate bất thường.
            </p>
        </div>

        <div class="alpha-grid">
            {alpha_cards if alpha_cards else '<p class="muted">Chưa có tín hiệu alpha nổi bật.</p>'}
        </div>

        <div class="mini-lists">
            <div>
                <h3>Top Gainers 24h</h3>
                <ul>{render_change_list(top_gainers)}</ul>
            </div>
            <div>
                <h3>Top Losers 24h</h3>
                <ul>{render_change_list(top_losers)}</ul>
            </div>
            <div>
                <h3>Top Volume 24h</h3>
                <ul>{render_volume_list(top_volume)}</ul>
            </div>
        </div>
    </section>
    """


def render_career_opportunities_section(career_data):
    if not career_data:
        return """
        <section class="panel">
            <div class="panel-header">
                <div>
                    <span class="eyebrow">Career Opportunities</span>
                    <h2>Cơ hội nghề nghiệp</h2>
                </div>
            </div>
            <p class="muted">Chưa có dữ liệu nghề nghiệp. Hãy kiểm tra module career_opportunities.py.</p>
        </section>
        """

    remote_jobs = career_data.get("remote_jobs", [])[:10]
    fulltime = career_data.get("fulltime_jobs", {}) or {}
    client_ops = career_data.get("client_opportunities", [])[:5]

    remote_html = ""

    for job in remote_jobs:
        reasons = job.get("reasons") or []
        tags = job.get("tags") or []
        tags_html = "".join([f"<span>{safe_text(tag)}</span>" for tag in tags[:4]])

        remote_html += f"""
        <article class="job-card">
            <div class="job-top">
                <div>
                    <h3>{safe_text(job.get("title"))}</h3>
                    <p>{safe_text(job.get("company"))} · {safe_text(job.get("location"))}</p>
                </div>
                <div class="match-score">{safe_text(job.get("match_score"))}%</div>
            </div>

            <div class="job-meta">
                <span>{safe_text(job.get("salary"))}</span>
                <span>{safe_text(job.get("source"))}</span>
            </div>

            <ul>{render_list(reasons)}</ul>

            <div class="tag-row">{tags_html}</div>

            <a class="apply-link" href="{safe_text(job.get("url", "#"))}" target="_blank" rel="noopener noreferrer">
                Xem job / Apply →
            </a>
        </article>
        """

    fulltime_roles = fulltime.get("suggested_roles", [])
    fulltime_steps = fulltime.get("next_steps", [])

    client_html = ""

    for lead in client_ops:
        client_html += f"""
        <article class="client-card">
            <div class="job-top">
                <div>
                    <h3>{safe_text(lead.get("segment"))}</h3>
                    <p>{safe_text(lead.get("why"))}</p>
                </div>
                <div class="match-score">{safe_text(lead.get("lead_score"))}</div>
            </div>
            <p><strong>Gợi ý chào bán:</strong> {safe_text(lead.get("offer"))}</p>
        </article>
        """

    return f"""
    <section class="panel">
        <div class="panel-header">
            <div>
                <span class="eyebrow">Career Opportunities</span>
                <h2>Cơ hội nghề nghiệp</h2>
            </div>
            <div class="updated-pill">Updated: {safe_text(career_data.get("updated_at"))}</div>
        </div>

        <div class="career-layout">
            <section>
                <div class="section-title-row">
                    <h3>Remote Jobs phù hợp</h3>
                    <span class="tag">{len(remote_jobs)} job</span>
                </div>
                <div class="jobs-grid">
                    {remote_html if remote_html else '<p class="muted">Chưa tìm thấy remote job phù hợp.</p>'}
                </div>
            </section>

            <section>
                <div class="section-title-row">
                    <h3>Full-time Jobs theo CV</h3>
                    <span class="tag">Chờ CV</span>
                </div>

                <div class="fulltime-box">
                    <p>{safe_text(fulltime.get("message"))}</p>

                    <h4>Nhóm vị trí có thể phù hợp</h4>
                    <ul>{render_list(fulltime_roles)}</ul>

                    <h4>Cách kích hoạt</h4>
                    <ul>{render_list(fulltime_steps)}</ul>
                </div>
            </section>

            <section>
                <div class="section-title-row">
                    <h3>Đối tượng dễ chốt dịch vụ Google Ads</h3>
                    <span class="tag">{len(client_ops)} nhóm</span>
                </div>
                <div class="client-grid">
                    {client_html}
                </div>
            </section>
        </div>
    </section>
    """


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


def build_html(news_items, bitcoin, gold, vnindex, ai_summary, charts, crypto_alpha, career_data):
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    today = datetime.now().strftime("%d/%m/%Y")

    curated_news = filter_curated_news(news_items, max_items=15)
    grouped_news = group_news_by_source(curated_news)

    domestic_gold = gold.get("domestic", {}) or {}
    world_gold = gold.get("world", {}) or {}

    mood = get_market_mood(bitcoin, gold, vnindex, crypto_alpha)
    data_warnings = get_data_quality_warnings(bitcoin, gold, vnindex, charts, crypto_alpha, career_data)
    action_items = get_action_items(mood, bitcoin, gold, vnindex, crypto_alpha, career_data)

    crypto_alpha_html = render_crypto_alpha_section(crypto_alpha)
    career_html = render_career_opportunities_section(career_data)

    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Morning Financial Intelligence</title>

    <style>
        :root {{
            --bg: #070b14;
            --panel: rgba(16, 24, 40, 0.86);
            --panel-soft: rgba(255, 255, 255, 0.045);
            --border: rgba(255, 255, 255, 0.09);
            --text: #e8eefc;
            --muted: #8b9ab4;
            --positive: #24d18b;
            --negative: #ff5c7a;
            --accent: #56a3ff;
            --gold: #ffd166;
            --purple: #b68cff;
        }}

        * {{
            box-sizing: border-box;
        }}

        body {{
            margin: 0;
            font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            background:
                radial-gradient(circle at top left, rgba(86, 163, 255, 0.18), transparent 32%),
                radial-gradient(circle at top right, rgba(255, 209, 102, 0.12), transparent 28%),
                radial-gradient(circle at 50% 22%, rgba(182, 140, 255, 0.08), transparent 36%),
                var(--bg);
            color: var(--text);
        }}

        a {{
            color: inherit;
            text-decoration: none;
        }}

        code {{
            color: var(--gold);
        }}

        .page {{
            width: min(1440px, 94vw);
            margin: 0 auto;
            padding: 32px 0 56px;
        }}

        .hero {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 24px;
            margin-bottom: 24px;
        }}

        .hero h1 {{
            margin: 0;
            font-size: clamp(34px, 5vw, 60px);
            line-height: 1;
            letter-spacing: -0.055em;
        }}

        .hero p {{
            color: var(--muted);
            max-width: 850px;
            font-size: 16px;
            line-height: 1.7;
        }}

        .time-chip,
        .updated-pill,
        .rsi-pill,
        .tag {{
            border: 1px solid var(--border);
            background: rgba(255, 255, 255, 0.05);
            padding: 10px 14px;
            border-radius: 999px;
            color: var(--muted);
            white-space: nowrap;
            font-size: 13px;
        }}

        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(5, minmax(0, 1fr));
            gap: 16px;
            margin-bottom: 18px;
        }}

        .kpi-card,
        .panel,
        .chart-card,
        .news-column {{
            background: linear-gradient(180deg, rgba(255,255,255,0.06), rgba(255,255,255,0.025));
            border: 1px solid var(--border);
            border-radius: 24px;
            box-shadow: 0 22px 60px rgba(0, 0, 0, 0.23);
            backdrop-filter: blur(14px);
        }}

        .kpi-card {{
            padding: 20px;
            min-height: 130px;
        }}

        .kpi-card span {{
            display: block;
            color: var(--muted);
            font-size: 13px;
            margin-bottom: 8px;
        }}

        .kpi-card strong {{
            display: block;
            font-size: 24px;
            letter-spacing: -0.03em;
            word-break: break-word;
        }}

        .kpi-card em {{
            display: block;
            margin-top: 8px;
            font-style: normal;
            font-size: 13px;
            line-height: 1.5;
        }}

        .panel {{
            padding: 24px;
            margin-bottom: 18px;
        }}

        .panel-header,
        .chart-card-header,
        .section-title-row {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 16px;
            margin-bottom: 18px;
        }}

        .eyebrow {{
            color: var(--accent);
            text-transform: uppercase;
            letter-spacing: 0.14em;
            font-size: 11px;
            font-weight: 800;
        }}

        h2,
        h3,
        h4 {{
            margin: 0;
            letter-spacing: -0.03em;
        }}

        h2 {{
            font-size: 26px;
        }}

        h3 {{
            font-size: 18px;
        }}

        h4 {{
            margin-top: 18px;
            font-size: 15px;
        }}

        .executive-grid {{
            display: grid;
            grid-template-columns: 1.1fr 1fr 1fr;
            gap: 14px;
        }}

        .insight-card,
        .fulltime-box,
        .job-card,
        .client-card {{
            background: rgba(255,255,255,0.04);
            border: 1px solid var(--border);
            border-radius: 18px;
            padding: 18px;
        }}

        .insight-card p,
        .fulltime-box p,
        .client-card p {{
            color: var(--muted);
            line-height: 1.65;
            margin-bottom: 0;
        }}

        .insight-card ul,
        .fulltime-box ul,
        .job-card ul {{
            margin: 12px 0 0;
            padding-left: 20px;
            color: var(--muted);
            line-height: 1.65;
        }}

        .mood-badge {{
            display: inline-flex;
            gap: 8px;
            align-items: center;
            padding: 10px 14px;
            border-radius: 999px;
            background: rgba(86,163,255,0.14);
            color: var(--accent);
            font-weight: 800;
            margin-top: 12px;
        }}

        .brief {{
            color: #d7e2f7;
            line-height: 1.75;
        }}

        .brief p:first-child {{
            margin-top: 0;
        }}

        .brief p:last-child {{
            margin-bottom: 0;
        }}

        .market-grid {{
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 14px;
        }}

        .market-item {{
            background: rgba(255,255,255,0.04);
            border: 1px solid var(--border);
            border-radius: 18px;
            padding: 16px;
        }}

        .market-item span {{
            color: var(--muted);
            font-size: 13px;
        }}

        .market-item strong {{
            display: block;
            font-size: 22px;
            margin: 8px 0;
            word-break: break-word;
        }}

        .market-item em {{
            font-style: normal;
            font-size: 13px;
            line-height: 1.5;
        }}

        .positive {{
            color: var(--positive) !important;
        }}

        .negative {{
            color: var(--negative) !important;
        }}

        .neutral {{
            color: var(--muted) !important;
        }}

        .muted {{
            color: var(--muted);
        }}

        .crypto-overview {{
            display: flex;
            align-items: center;
            gap: 18px;
            margin-bottom: 18px;
            flex-wrap: wrap;
        }}

        .crypto-overview p {{
            max-width: 760px;
            line-height: 1.65;
            margin: 0;
        }}

        .sentiment-card {{
            display: flex;
            align-items: center;
            gap: 14px;
            width: fit-content;
            padding: 14px 16px;
            border-radius: 18px;
            background: rgba(255,255,255,0.05);
            border: 1px solid var(--border);
        }}

        .sentiment-card span {{
            color: var(--muted);
        }}

        .sentiment-card strong {{
            font-size: 26px;
            color: var(--gold);
        }}

        .sentiment-card em {{
            font-style: normal;
            color: var(--text);
        }}

        .alpha-grid {{
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 14px;
        }}

        .alpha-card {{
            padding: 16px;
            border-radius: 18px;
            background: rgba(255,255,255,0.04);
            border: 1px solid var(--border);
        }}

        .coin-line,
        .job-top {{
            display: flex;
            justify-content: space-between;
            gap: 12px;
            align-items: flex-start;
            margin-bottom: 14px;
        }}

        .coin-symbol {{
            font-size: 22px;
            font-weight: 900;
        }}

        .coin-name,
        .job-card p {{
            color: var(--muted);
            font-size: 13px;
        }}

        .score-badge,
        .match-score {{
            min-width: 48px;
            text-align: center;
            padding: 8px 10px;
            border-radius: 14px;
            background: rgba(86,163,255,0.16);
            color: var(--accent);
            font-weight: 900;
        }}

        .metric-row {{
            display: flex;
            justify-content: space-between;
            gap: 12px;
            margin: 8px 0;
            color: var(--muted);
            font-size: 13px;
        }}

        .metric-row strong {{
            color: var(--text);
        }}

        .alpha-card p {{
            color: var(--muted);
            font-size: 13px;
            line-height: 1.55;
            margin-bottom: 0;
        }}

        .mini-lists {{
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 14px;
            margin-top: 18px;
        }}

        .mini-lists > div {{
            padding: 16px;
            border-radius: 18px;
            background: rgba(255,255,255,0.035);
            border: 1px solid var(--border);
        }}

        .mini-lists ul {{
            padding: 0;
            margin: 14px 0 0;
            list-style: none;
        }}

        .mini-lists li {{
            display: flex;
            justify-content: space-between;
            gap: 12px;
            padding: 9px 0;
            border-bottom: 1px solid rgba(255,255,255,0.06);
        }}

        .career-layout {{
            display: grid;
            gap: 22px;
        }}

        .jobs-grid {{
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 14px;
        }}

        .client-grid {{
            display: grid;
            grid-template-columns: repeat(5, minmax(0, 1fr));
            gap: 14px;
        }}

        .job-meta,
        .tag-row {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin: 12px 0;
        }}

        .job-meta span,
        .tag-row span {{
            border: 1px solid var(--border);
            background: rgba(255,255,255,0.045);
            color: var(--muted);
            border-radius: 999px;
            padding: 6px 10px;
            font-size: 12px;
        }}

        .apply-link {{
            display: inline-flex;
            margin-top: 14px;
            color: var(--accent);
            font-weight: 800;
        }}

        .charts-grid {{
            display: grid;
            grid-template-columns: 1fr;
            gap: 16px;
            margin-bottom: 18px;
        }}

        .chart-card {{
            padding: 20px;
            overflow: hidden;
        }}

        .chart-note {{
            color: var(--muted);
            font-size: 13px;
            margin: 0 0 14px;
        }}

        .chart-box {{
            overflow-x: auto;
        }}

        .chart-wrapper {{
            min-width: 760px;
        }}

        .chart-title {{
            display: none;
        }}

        .chart-svg {{
            width: 100%;
            height: auto;
            background: rgba(255,255,255,0.025);
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 18px;
        }}

        .grid-line {{
            stroke: rgba(255,255,255,0.12);
            stroke-width: 1;
        }}

        .axis-text {{
            fill: #8b9ab4;
            font-size: 12px;
        }}

        .candle-up {{
            stroke: var(--positive);
            fill: var(--positive);
        }}

        .candle-down {{
            stroke: var(--negative);
            fill: var(--negative);
        }}

        .rsi-line {{
            stroke: var(--accent);
            stroke-width: 2.2;
        }}

        .rsi-high-line {{
            stroke: rgba(255, 92, 122, 0.55);
            stroke-width: 1;
            stroke-dasharray: 5 5;
        }}

        .rsi-low-line {{
            stroke: rgba(36, 209, 139, 0.55);
            stroke-width: 1;
            stroke-dasharray: 5 5;
        }}

        .chart-meta {{
            display: flex;
            gap: 14px;
            flex-wrap: wrap;
            margin-top: 12px;
            color: var(--muted);
            font-size: 13px;
        }}

        .chart-meta strong {{
            color: var(--text);
        }}

        .chart-empty {{
            color: var(--muted);
            min-height: 220px;
            display: grid;
            place-items: center;
            border: 1px dashed var(--border);
            border-radius: 16px;
        }}

        .news-grid {{
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 16px;
        }}

        .news-column {{
            padding: 20px;
        }}

        .news-card {{
            padding: 14px 0;
            border-bottom: 1px solid rgba(255,255,255,0.07);
        }}

        .news-card:last-child {{
            border-bottom: none;
        }}

        .news-card a {{
            display: block;
            font-weight: 800;
            line-height: 1.45;
        }}

        .news-card a:hover {{
            color: var(--accent);
        }}

        .news-card p {{
            color: var(--muted);
            font-size: 13px;
            line-height: 1.6;
            margin: 8px 0 0;
        }}

        @media (max-width: 1200px) {{
            .kpi-grid {{
                grid-template-columns: repeat(3, minmax(0, 1fr));
            }}

            .market-grid,
            .alpha-grid,
            .news-grid,
            .executive-grid,
            .jobs-grid {{
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }}

            .client-grid {{
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }}

            .mini-lists {{
                grid-template-columns: 1fr;
            }}
        }}

        @media (max-width: 720px) {{
            .hero,
            .panel-header,
            .chart-card-header,
            .section-title-row {{
                flex-direction: column;
            }}

            .kpi-grid,
            .market-grid,
            .alpha-grid,
            .news-grid,
            .executive-grid,
            .jobs-grid,
            .client-grid {{
                grid-template-columns: 1fr;
            }}

            .time-chip,
            .updated-pill,
            .rsi-pill {{
                white-space: normal;
            }}

            .hero h1 {{
                font-size: 36px;
            }}
        }}
    </style>
</head>

<body>
    <main class="page">
        <header class="hero">
            <div>
                <h1>Morning Financial Intelligence</h1>
                <p>
                    Bản tin phân tích tài chính và cơ hội thu nhập tự động ngày {today}: thị trường,
                    crypto alpha, tin tức, remote job, full-time job theo CV và nhóm khách hàng dễ chốt dịch vụ.
                </p>
            </div>

            <div class="time-chip">Cập nhật: {now}</div>
        </header>

        <section class="kpi-grid">
            <article class="kpi-card">
                <span>Market Mood</span>
                <strong>{safe_text(mood["mood"])}</strong>
                <em class="neutral">Risk Level: {safe_text(mood["risk_level"])}</em>
            </article>

            <article class="kpi-card">
                <span>Bitcoin</span>
                <strong>{safe_text(clean_price_prefix(bitcoin.get("price_usd")))}</strong>
                <em class="{safe_text(bitcoin.get("change_class", "neutral"))}">
                    {safe_text(bitcoin.get("change_24h"))}
                </em>
            </article>

            <article class="kpi-card">
                <span>Gold World</span>
                <strong>{safe_text(world_gold.get("price"))}</strong>
                <em class="{safe_text(world_gold.get("change_class", "neutral"))}">
                    {safe_text(world_gold.get("change_24h"))}
                </em>
            </article>

            <article class="kpi-card">
                <span>Remote Jobs</span>
                <strong>{len((career_data or {}).get("remote_jobs", []))}</strong>
                <em class="neutral">Job phù hợp đã lọc</em>
            </article>

            <article class="kpi-card">
                <span>Client Leads</span>
                <strong>{len((career_data or {}).get("client_opportunities", []))}</strong>
                <em class="neutral">Nhóm dễ chốt Google Ads</em>
            </article>
        </section>

        <section class="panel">
            <div class="panel-header">
                <div>
                    <span class="eyebrow">Executive Summary</span>
                    <h2>Market & Opportunity Brief</h2>
                </div>
                <span class="tag">{safe_text(mood["mood"])}</span>
            </div>

            <div class="executive-grid">
                <article class="insight-card">
                    <h3>Tổng quan</h3>
                    <div class="mood-badge">{safe_text(mood["mood"])} · Risk {safe_text(mood["risk_level"])}</div>
                    <p>{safe_text(mood["summary"])}</p>
                </article>

                <article class="insight-card">
                    <h3>Động lực chính</h3>
                    <ul>{render_list(mood["drivers"])}</ul>
                </article>

                <article class="insight-card">
                    <h3>Việc nên theo dõi</h3>
                    <ul>{render_list(action_items)}</ul>
                </article>
            </div>
        </section>

        {career_html}

        <section class="panel">
            <div class="panel-header">
                <div>
                    <span class="eyebrow">AI Analysis</span>
                    <h2>AI Market Brief</h2>
                </div>
            </div>

            <div class="brief">
                {ai_summary}
            </div>
        </section>

        {crypto_alpha_html}

        <section class="panel">
            <div class="panel-header">
                <div>
                    <span class="eyebrow">Risk Monitor</span>
                    <h2>Data Quality & Risk Checklist</h2>
                </div>
            </div>

            <div class="executive-grid">
                <article class="insight-card">
                    <h3>Data Quality</h3>
                    <ul>{render_list(data_warnings)}</ul>
                </article>

                <article class="insight-card">
                    <h3>Gold Signal</h3>
                    <p>
                        Vàng thế giới: <strong>{safe_text(world_gold.get("price"))}</strong>,
                        biến động <strong class="{safe_text(world_gold.get("change_class", "neutral"))}">
                        {safe_text(world_gold.get("change_24h"))}</strong>.
                        Vàng SJC: <strong>{safe_text(domestic_gold.get("sell"))}</strong>.
                    </p>
                </article>

                <article class="insight-card">
                    <h3>VNINDEX Signal</h3>
                    <p>
                        VNINDEX hiện ở <strong>{safe_text(vnindex.get("value"))}</strong>,
                        biến động <strong class="{safe_text(vnindex.get("change_class", "neutral"))}">
                        {safe_text(vnindex.get("change"))}</strong>.
                    </p>
                </article>
            </div>
        </section>

        <section class="panel">
            <div class="panel-header">
                <div>
                    <span class="eyebrow">Market Data</span>
                    <h2>Market Overview</h2>
                </div>
            </div>

            <div class="market-grid">
                <article class="market-item">
                    <span>Bitcoin USD</span>
                    <strong>{safe_text(clean_price_prefix(bitcoin.get("price_usd")))}</strong>
                    <em class="{safe_text(bitcoin.get("change_class", "neutral"))}">
                        {safe_text(bitcoin.get("change_24h"))} — {safe_text(bitcoin.get("note"))}
                    </em>
                </article>

                <article class="market-item">
                    <span>Bitcoin VND</span>
                    <strong>{safe_text(bitcoin.get("price_vnd"))} VND</strong>
                    <em class="{safe_text(bitcoin.get("change_class", "neutral"))}">
                        {safe_text(bitcoin.get("change_24h"))}
                    </em>
                </article>

                <article class="market-item">
                    <span>Vàng SJC</span>
                    <strong>{safe_text(domestic_gold.get("sell"))}</strong>
                    <em class="{safe_text(domestic_gold.get("change_class", "neutral"))}">
                        Mua: {safe_text(domestic_gold.get("buy"))}<br>
                        24h: {safe_text(domestic_gold.get("change_24h"))}
                    </em>
                </article>

                <article class="market-item">
                    <span>Vàng thế giới</span>
                    <strong>{safe_text(world_gold.get("price"))}</strong>
                    <em class="{safe_text(world_gold.get("change_class", "neutral"))}">
                        {safe_text(world_gold.get("change_24h"))}
                    </em>
                </article>

                <article class="market-item">
                    <span>VNINDEX</span>
                    <strong>{safe_text(vnindex.get("value"))}</strong>
                    <em class="{safe_text(vnindex.get("change_class", "neutral"))}">
                        {safe_text(vnindex.get("change"))}
                    </em>
                </article>
            </div>
        </section>

        <section class="charts-grid">
            {render_chart_card("Bitcoin Technical Chart", charts["bitcoin"]["html"], charts["bitcoin"]["rsi"], charts["bitcoin"]["note"])}
            {render_chart_card("Gold Technical Chart", charts["gold"]["html"], charts["gold"]["rsi"], charts["gold"]["note"])}
            {render_chart_card("VNINDEX Technical Chart", charts["vnindex"]["html"], charts["vnindex"]["rsi"], charts["vnindex"]["note"])}
        </section>

        <section class="panel">
            <div class="panel-header">
                <div>
                    <span class="eyebrow">Curated News</span>
                    <h2>Tin tức tài chính đã lọc</h2>
                </div>
                <span class="tag">{len(curated_news)} tin</span>
            </div>

            <section class="news-grid">
                {render_news_column("VnExpress", grouped_news.get("VnExpress", []))}
                {render_news_column("Dân Trí", grouped_news.get("Dân Trí", []))}
                {render_news_column("BBC", grouped_news.get("BBC", []))}
            </section>
        </section>
    </main>
</body>
</html>
"""


def main():
    print("Loading news...")
    news_items = get_all_news(limit_per_source=8)

    print("Loading market data...")
    bitcoin = get_bitcoin_price()
    gold = get_gold_price()
    vnindex = get_vnindex()

    print("Loading charts...")
    charts = build_charts()

    print("Loading Crypto Alpha...")
    crypto_alpha = None

    if build_crypto_alpha:
        try:
            crypto_alpha = build_crypto_alpha()
        except Exception as exc:
            print(f"ERROR loading Crypto Alpha: {exc}")
    else:
        print("Crypto Alpha module not available.")

    print("Loading Career Opportunities...")
    career_data = None

    if build_career_opportunities:
        try:
            career_data = build_career_opportunities()
        except Exception as exc:
            print(f"ERROR loading Career Opportunities: {exc}")
    else:
        print("Career Opportunities module not available.")

    print("Generating AI summary...")
    try:
        ai_summary = get_ai_summary(
            news_items=filter_curated_news(news_items, max_items=10),
            bitcoin=bitcoin,
            gold=gold,
            vnindex=vnindex,
        )
    except Exception as exc:
        print(f"ERROR generating AI summary: {exc}")
        ai_summary = """
        <p><strong>AI Market Brief chưa tạo được.</strong></p>
        <p>Dashboard vẫn chạy bình thường. Vui lòng kiểm tra OPENAI_API_KEY hoặc module ai_summary.py.</p>
        """

    print("Rendering dashboard...")
    html_content = build_html(
        news_items=news_items,
        bitcoin=bitcoin,
        gold=gold,
        vnindex=vnindex,
        ai_summary=ai_summary,
        charts=charts,
        crypto_alpha=crypto_alpha,
        career_data=career_data,
    )

    with open("index.html", "w", encoding="utf-8") as file:
        file.write(html_content)

    print("Dashboard generated successfully: index.html")


if __name__ == "__main__":
    main()
