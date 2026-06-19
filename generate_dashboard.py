import html
from datetime import datetime

from modules.news import get_all_news
from modules.market import get_bitcoin_price, get_gold_price, get_vnindex
from modules.charts import get_history_with_rsi, build_candlestick_svg
from modules.ai_summary import get_ai_summary

try:
    from modules.crypto_alpha import build_crypto_alpha, format_crypto_alpha_text
except Exception:
    build_crypto_alpha = None
    format_crypto_alpha_text = None


def safe_text(value, default="N/A"):
    if value is None:
        return default
    return html.escape(str(value))


def get_change_class_from_text(value):
    if value is None:
        return "neutral"

    text = str(value).strip()

    if text.startswith("+"):
        return "positive"

    if text.startswith("-"):
        return "negative"

    return "neutral"


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


def render_news_column(source_name, items):
    if not items:
        return f"""
        <section class="news-column">
            <h3>{safe_text(source_name)}</h3>
            <p class="muted">Chưa có dữ liệu tin tức.</p>
        </section>
        """

    cards_html = ""

    for item in items:
        title = item.get("title", "Không có tiêu đề")
        summary = item.get("summary", "Chưa có mô tả.")
        link = item.get("link", "#")

        cards_html += f"""
        <article class="news-card">
            <a href="{safe_text(link)}" target="_blank" rel="noopener noreferrer">
                {title}
            </a>
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
                <span class="eyebrow">Technical Chart</span>
                <h3>{safe_text(title)}</h3>
            </div>
            <div class="rsi-pill">RSI: {safe_text(rsi_value)}</div>
        </div>
        <div class="chart-note">{safe_text(rsi_note)}</div>
        <div class="chart-box">
            {chart_html}
        </div>
    </section>
    """


def render_crypto_alpha_section(crypto_alpha):
    if not crypto_alpha:
        return """
        <section class="panel">
            <div class="panel-header">
                <div>
                    <span class="eyebrow">Crypto Alpha</span>
                    <h2>Crypto Alpha Agent</h2>
                </div>
            </div>
            <p class="muted">
                Chưa có dữ liệu Crypto Alpha. Hãy kiểm tra file
                <code>modules/crypto_alpha.py</code> hoặc kết nối API.
            </p>
        </section>
        """

    fear_greed = crypto_alpha.get("fear_greed", {}) or {}
    top_alpha = crypto_alpha.get("top_alpha", [])[:8]
    top_gainers = crypto_alpha.get("top_gainers", [])[:5]
    top_losers = crypto_alpha.get("top_losers", [])[:5]
    top_volume = crypto_alpha.get("top_volume", [])[:5]

    alpha_cards = ""

    for coin in top_alpha:
        symbol = safe_text(coin.get("symbol"))
        name = safe_text(coin.get("name"))
        score = coin.get("alpha_score", 0)
        change_24h = coin.get("change_24h")
        change_class = "neutral"

        try:
            if float(change_24h or 0) > 0:
                change_class = "positive"
            elif float(change_24h or 0) < 0:
                change_class = "negative"
        except Exception:
            pass

        try:
            change_text = f"{float(change_24h):+.2f}%"
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
                <div class="score-badge">{safe_text(score)}</div>
            </div>

            <div class="metric-row">
                <span>24h</span>
                <strong class="{change_class}">{safe_text(change_text)}</strong>
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

    def render_coin_list(items):
        output = ""

        for item in items:
            symbol = item.get("symbol", "N/A")
            change = item.get("change_24h")

            try:
                change_text = f"{float(change):+.2f}%"
            except Exception:
                change_text = "N/A"

            change_class = "positive" if str(change_text).startswith("+") else "negative" if str(change_text).startswith("-") else "neutral"

            output += f"""
            <li>
                <span>{safe_text(symbol)}</span>
                <strong class="{change_class}">{safe_text(change_text)}</strong>
            </li>
            """

        return output or '<li class="muted">Chưa có dữ liệu</li>'

    def render_volume_list(items):
        output = ""

        for item in items:
            symbol = item.get("symbol", "N/A")

            try:
                volume_text = f"${float(item.get('volume_24h') or 0):,.0f}"
            except Exception:
                volume_text = "N/A"

            output += f"""
            <li>
                <span>{safe_text(symbol)}</span>
                <strong>{safe_text(volume_text)}</strong>
            </li>
            """

        return output or '<li class="muted">Chưa có dữ liệu</li>'

    return f"""
    <section class="panel">
        <div class="panel-header">
            <div>
                <span class="eyebrow">Crypto Alpha</span>
                <h2>Crypto Alpha Agent</h2>
            </div>
            <div class="updated-pill">
                Updated: {safe_text(crypto_alpha.get("updated_at"))}
            </div>
        </div>

        <div class="crypto-overview">
            <div class="sentiment-card">
                <span>Fear & Greed Index</span>
                <strong>{safe_text(fear_greed.get("value"))}</strong>
                <em>{safe_text(fear_greed.get("classification"))}</em>
            </div>

            <p class="muted">
                Agent theo dõi CoinGecko, Binance Futures, funding rate và tâm lý thị trường
                để phát hiện token có tín hiệu volume, momentum hoặc funding bất thường.
            </p>
        </div>

        <div class="alpha-grid">
            {alpha_cards if alpha_cards else '<p class="muted">Chưa có tín hiệu alpha nổi bật.</p>'}
        </div>

        <div class="mini-lists">
            <div>
                <h3>Top Gainers 24h</h3>
                <ul>{render_coin_list(top_gainers)}</ul>
            </div>

            <div>
                <h3>Top Losers 24h</h3>
                <ul>{render_coin_list(top_losers)}</ul>
            </div>

            <div>
                <h3>Top Volume 24h</h3>
                <ul>{render_volume_list(top_volume)}</ul>
            </div>
        </div>
    </section>
    """


def build_charts():
    btc_history, btc_rsi, btc_rsi_note = get_history_with_rsi("BTC-USD")
    gold_history, gold_rsi, gold_rsi_note = get_history_with_rsi("GC=F")
    vnindex_history, vnindex_rsi, vnindex_rsi_note = get_history_with_rsi("^VNINDEX.VN")

    btc_chart = build_candlestick_svg(
        btc_history,
        "Bitcoin / USD",
        "BTC Close",
        "RSI 14"
    )

    gold_chart = build_candlestick_svg(
        gold_history,
        "Gold Futures / USD",
        "Gold Close",
        "RSI 14"
    )

    vnindex_chart = build_candlestick_svg(
        vnindex_history,
        "VNINDEX",
        "VNINDEX Close",
        "RSI 14"
    )

    return {
        "bitcoin": {
            "html": btc_chart,
            "rsi": btc_rsi,
            "note": btc_rsi_note,
        },
        "gold": {
            "html": gold_chart,
            "rsi": gold_rsi,
            "note": gold_rsi_note,
        },
        "vnindex": {
            "html": vnindex_chart,
            "rsi": vnindex_rsi,
            "note": vnindex_rsi_note,
        },
    }


def build_html(news_items, bitcoin, gold, vnindex, ai_summary, charts, crypto_alpha):
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    today = datetime.now().strftime("%d/%m/%Y")

    grouped_news = group_news_by_source(news_items)
    crypto_alpha_html = render_crypto_alpha_section(crypto_alpha)

    domestic_gold = gold.get("domestic", {}) or {}
    world_gold = gold.get("world", {}) or {}

    total_news = len(news_items)

    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Morning Agent Finance</title>

    <style>
        :root {{
            --bg: #070b14;
            --panel: #101828;
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
                radial-gradient(circle at top right, rgba(255, 209, 102, 0.13), transparent 28%),
                radial-gradient(circle at 50% 30%, rgba(182, 140, 255, 0.08), transparent 36%),
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
            gap: 24px;
            align-items: flex-start;
            margin-bottom: 24px;
        }}

        .hero h1 {{
            margin: 0;
            font-size: clamp(34px, 5vw, 58px);
            line-height: 1;
            letter-spacing: -0.05em;
        }}

        .hero p {{
            color: var(--muted);
            max-width: 780px;
            font-size: 16px;
            line-height: 1.7;
        }}

        .time-chip,
        .updated-pill,
        .rsi-pill {{
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
            grid-template-columns: repeat(4, minmax(0, 1fr));
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
        }}

        .kpi-card {{
            padding: 20px;
            min-height: 136px;
        }}

        .kpi-card span {{
            display: block;
            color: var(--muted);
            font-size: 13px;
            margin-bottom: 8px;
        }}

        .kpi-card strong {{
            display: block;
            font-size: 26px;
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

        .panel-header {{
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
        h3 {{
            margin: 0;
            letter-spacing: -0.03em;
        }}

        h2 {{
            font-size: 26px;
        }}

        h3 {{
            font-size: 18px;
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

        .coin-line {{
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

        .coin-name {{
            color: var(--muted);
            font-size: 13px;
        }}

        .score-badge {{
            min-width: 44px;
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

        .chart-card-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 14px;
            margin-bottom: 10px;
        }}

        .chart-note {{
            color: var(--muted);
            font-size: 13px;
            margin-bottom: 14px;
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

        @media (max-width: 1100px) {{
            .kpi-grid,
            .market-grid,
            .alpha-grid,
            .news-grid {{
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }}

            .mini-lists {{
                grid-template-columns: 1fr;
            }}
        }}

        @media (max-width: 720px) {{
            .hero,
            .panel-header,
            .chart-card-header {{
                flex-direction: column;
            }}

            .kpi-grid,
            .market-grid,
            .alpha-grid,
            .news-grid {{
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
                <h1>Bảng tổng hợp tin tức ngày {today}</h1>
                <p>
                    Morning Agent Finance theo dõi tin tức, Bitcoin, vàng, VNINDEX,
                    RSI kỹ thuật và tín hiệu Crypto Alpha để hỗ trợ bạn phát hiện
                    cơ hội, rủi ro và xu hướng đáng chú ý mỗi ngày.
                </p>
            </div>

            <div class="time-chip">Cập nhật lần cuối: {now}</div>
        </header>

        <section class="kpi-grid">
            <article class="kpi-card">
                <span>Tổng tin nóng</span>
                <strong>{total_news}</strong>
                <em class="neutral">VnExpress / Dân Trí / BBC</em>
            </article>

            <article class="kpi-card">
                <span>Bitcoin</span>
                <strong>${safe_text(bitcoin.get("price_usd"))}</strong>
                <em class="{safe_text(bitcoin.get("change_class", "neutral"))}">
                    {safe_text(bitcoin.get("change_24h"))}
                </em>
            </article>

            <article class="kpi-card">
                <span>Vàng thế giới</span>
                <strong>{safe_text(world_gold.get("price"))}</strong>
                <em class="{safe_text(world_gold.get("change_class", "neutral"))}">
                    {safe_text(world_gold.get("change_24h"))}
                </em>
            </article>

            <article class="kpi-card">
                <span>VNINDEX</span>
                <strong>{safe_text(vnindex.get("value"))}</strong>
                <em class="{safe_text(vnindex.get("change_class", "neutral"))}">
                    {safe_text(vnindex.get("change_percent"))}
                </em>
            </article>
        </section>

        <section class="panel">
            <div class="panel-header">
                <div>
                    <span class="eyebrow">AI Brief</span>
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
                    <span class="eyebrow">Market Data</span>
                    <h2>Market Snapshot</h2>
                </div>
            </div>

            <div class="market-grid">
                <article class="market-item">
                    <span>Bitcoin USD</span>
                    <strong>${safe_text(bitcoin.get("price_usd"))}</strong>
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
                    <span>Vàng SJC trong nước</span>
                    <strong>{safe_text(domestic_gold.get("sell"))}</strong>
                    <em class="{safe_text(domestic_gold.get("change_class", "neutral"))}">
                        Mua: {safe_text(domestic_gold.get("buy"))}<br>
                        Bán: {safe_text(domestic_gold.get("sell"))}<br>
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
            {render_chart_card("Bitcoin Chart", charts["bitcoin"]["html"], charts["bitcoin"]["rsi"], charts["bitcoin"]["note"])}
            {render_chart_card("Vàng thế giới Chart", charts["gold"]["html"], charts["gold"]["rsi"], charts["gold"]["note"])}
            {render_chart_card("VNINDEX Chart", charts["vnindex"]["html"], charts["vnindex"]["rsi"], charts["vnindex"]["note"])}
        </section>

        <section class="news-grid">
            {render_news_column("VnExpress", grouped_news.get("VnExpress", []))}
            {render_news_column("Dân Trí", grouped_news.get("Dân Trí", []))}
            {render_news_column("BBC", grouped_news.get("BBC", []))}
        </section>
    </main>
</body>
</html>
"""


def main():
    print("Loading news...")
    news_items = get_all_news(limit_per_source=5)

    print("Loading market data...")
    bitcoin = get_bitcoin_price()
    gold = get_gold_price()
    vnindex = get_vnindex()

    print("Loading charts...")
    charts = build_charts()

    print("Loading Crypto Alpha...")
    crypto_alpha = None
    crypto_alpha_text = ""

    if build_crypto_alpha:
        try:
            crypto_alpha = build_crypto_alpha()

            if format_crypto_alpha_text:
                crypto_alpha_text = format_crypto_alpha_text(crypto_alpha)
        except Exception as exc:
            print(f"ERROR loading Crypto Alpha: {exc}")
    else:
        print("Crypto Alpha module not available.")

    print("Generating AI summary...")
    try:
        ai_summary = get_ai_summary(
            news_items=news_items,
            bitcoin=bitcoin,
            gold=gold,
            vnindex=vnindex,
        )

        if crypto_alpha_text:
            ai_summary += f"""
            <p><strong>Crypto Alpha:</strong></p>
            <p>{safe_text(crypto_alpha_text).replace(chr(10), "<br>")}</p>
            """

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
    )

    with open("index.html", "w", encoding="utf-8") as file:
        file.write(html_content)

    print("Dashboard generated successfully: index.html")


if __name__ == "__main__":
    main()
