import html
from datetime import datetime

from modules.news import get_news
from modules.market import get_market_data
from modules.charts import generate_charts
from modules.ai_summary import generate_ai_summary

try:
    from modules.crypto_alpha import build_crypto_alpha, format_crypto_alpha_text
except Exception:
    build_crypto_alpha = None
    format_crypto_alpha_text = None


def safe_text(value, default="N/A"):
    if value is None:
        return default
    return html.escape(str(value))


def safe_number(value, digits=2, default="N/A"):
    try:
        return f"{float(value):,.{digits}f}"
    except Exception:
        return default


def safe_percent(value, digits=2, default="N/A"):
    try:
        value = float(value)
        sign = "+" if value > 0 else ""
        return f"{sign}{value:.{digits}f}%"
    except Exception:
        return default


def format_price(value, prefix="$", suffix="", digits=2):
    try:
        return f"{prefix}{float(value):,.{digits}f}{suffix}"
    except Exception:
        return "N/A"


def get_change_class(value):
    try:
        value = float(value)
        if value > 0:
            return "positive"
        if value < 0:
            return "negative"
    except Exception:
        pass
    return "neutral"


def render_news_column(title, items):
    cards = []

    for item in items:
        item_title = safe_text(item.get("title"))
        link = safe_text(item.get("link", "#"))
        summary = safe_text(item.get("summary", ""))

        cards.append(f"""
        <article class="news-card">
            <a href="{link}" target="_blank" rel="noopener noreferrer">{item_title}</a>
            <p>{summary}</p>
        </article>
        """)

    return f"""
    <section class="news-column">
        <h3>{safe_text(title)}</h3>
        {''.join(cards) if cards else '<p class="muted">Chưa có dữ liệu tin tức.</p>'}
    </section>
    """


def render_chart_card(title, svg_content):
    if not svg_content:
        svg_content = '<div class="empty-chart">Chưa có dữ liệu biểu đồ</div>'

    return f"""
    <section class="chart-card">
        <h3>{safe_text(title)}</h3>
        <div class="chart-box">
            {svg_content}
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
            <p class="muted">Chưa có dữ liệu Crypto Alpha. Hãy kiểm tra file <code>modules/crypto_alpha.py</code>.</p>
        </section>
        """

    fear_greed = crypto_alpha.get("fear_greed", {}) or {}
    top_alpha = crypto_alpha.get("top_alpha", [])[:8]
    top_gainers = crypto_alpha.get("top_gainers", [])[:5]
    top_losers = crypto_alpha.get("top_losers", [])[:5]

    alpha_cards = []

    for coin in top_alpha:
        symbol = safe_text(coin.get("symbol"))
        name = safe_text(coin.get("name"))
        score = safe_number(coin.get("alpha_score"), 0)
        change_24h = coin.get("change_24h")
        change_class = get_change_class(change_24h)
        volume = format_price(coin.get("volume_24h"), prefix="$", digits=0)
        funding = coin.get("funding_rate")
        reasons = coin.get("reasons") or []
        reason_text = safe_text("; ".join(reasons[:2]) if reasons else "Chưa có tín hiệu nổi bật")

        alpha_cards.append(f"""
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
                <strong class="{change_class}">{safe_percent(change_24h)}</strong>
            </div>
            <div class="metric-row">
                <span>Volume</span>
                <strong>{volume}</strong>
            </div>
            <div class="metric-row">
                <span>Funding</span>
                <strong>{safe_percent((funding or 0) * 100, 4) if funding is not None else "N/A"}</strong>
            </div>
            <p>{reason_text}</p>
        </article>
        """)

    gainers_html = "".join([
        f"""
        <li>
            <span>{safe_text(item.get("symbol"))}</span>
            <strong class="{get_change_class(item.get("change_24h"))}">{safe_percent(item.get("change_24h"))}</strong>
        </li>
        """
        for item in top_gainers
    ])

    losers_html = "".join([
        f"""
        <li>
            <span>{safe_text(item.get("symbol"))}</span>
            <strong class="{get_change_class(item.get("change_24h"))}">{safe_percent(item.get("change_24h"))}</strong>
        </li>
        """
        for item in top_losers
    ])

    return f"""
    <section class="panel">
        <div class="panel-header">
            <div>
                <span class="eyebrow">Crypto Alpha</span>
                <h2>Crypto Alpha Agent</h2>
            </div>
            <div class="updated-pill">Updated: {safe_text(crypto_alpha.get("updated_at"))}</div>
        </div>

        <div class="sentiment-card">
            <span>Fear & Greed Index</span>
            <strong>{safe_text(fear_greed.get("value"))}</strong>
            <em>{safe_text(fear_greed.get("classification"))}</em>
        </div>

        <div class="alpha-grid">
            {''.join(alpha_cards) if alpha_cards else '<p class="muted">Chưa có tín hiệu alpha nổi bật.</p>'}
        </div>

        <div class="mini-lists">
            <div>
                <h3>Top Gainers 24h</h3>
                <ul>{gainers_html or '<li class="muted">Chưa có dữ liệu</li>'}</ul>
            </div>
            <div>
                <h3>Top Losers 24h</h3>
                <ul>{losers_html or '<li class="muted">Chưa có dữ liệu</li>'}</ul>
            </div>
        </div>
    </section>
    """


def render_dashboard(news_data, market_data, charts, ai_summary, crypto_alpha=None):
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    btc = market_data.get("bitcoin", {}) or {}
    vnindex = market_data.get("vnindex", {}) or {}
    domestic_gold = market_data.get("domestic_gold", {}) or market_data.get("gold_domestic", {}) or {}
    world_gold = market_data.get("world_gold", {}) or market_data.get("gold_world", {}) or {}

    btc_change = btc.get("change_24h") or btc.get("change_percent")
    vnindex_change = vnindex.get("change_percent") or vnindex.get("change")
    domestic_gold_change = domestic_gold.get("change_sell") or domestic_gold.get("change_percent")
    world_gold_change = world_gold.get("change_24h") or world_gold.get("change_percent")

    crypto_alpha_html = render_crypto_alpha_section(crypto_alpha)

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
            --panel-2: #111f32;
            --border: rgba(255,255,255,0.08);
            --text: #e8eefc;
            --muted: #8b9ab4;
            --positive: #24d18b;
            --negative: #ff5c7a;
            --accent: #56a3ff;
            --gold: #ffd166;
        }}

        * {{
            box-sizing: border-box;
        }}

        body {{
            margin: 0;
            font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            background:
                radial-gradient(circle at top left, rgba(86,163,255,0.16), transparent 32%),
                radial-gradient(circle at top right, rgba(255,209,102,0.12), transparent 28%),
                var(--bg);
            color: var(--text);
        }}

        a {{
            color: inherit;
            text-decoration: none;
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
            font-size: clamp(32px, 5vw, 56px);
            line-height: 1;
            letter-spacing: -0.04em;
        }}

        .hero p {{
            color: var(--muted);
            max-width: 720px;
            font-size: 16px;
            line-height: 1.7;
        }}

        .time-chip, .updated-pill {{
            border: 1px solid var(--border);
            background: rgba(255,255,255,0.05);
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

        .kpi-card, .panel, .chart-card, .news-column {{
            background: linear-gradient(180deg, rgba(255,255,255,0.055), rgba(255,255,255,0.025));
            border: 1px solid var(--border);
            border-radius: 24px;
            box-shadow: 0 22px 60px rgba(0,0,0,0.22);
        }}

        .kpi-card {{
            padding: 20px;
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
        }}

        .kpi-card em {{
            display: block;
            margin-top: 8px;
            font-style: normal;
            font-size: 13px;
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

        h2, h3 {{
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
            white-space: pre-wrap;
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
        }}

        .positive {{
            color: var(--positive);
        }}

        .negative {{
            color: var(--negative);
        }}

        .neutral {{
            color: var(--muted);
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
            margin-bottom: 18px;
        }}

        .sentiment-card span {{
            color: var(--muted);
        }}

        .sentiment-card strong {{
            font-size: 24px;
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

        .metric-row strong.positive {{
            color: var(--positive);
        }}

        .metric-row strong.negative {{
            color: var(--negative);
        }}

        .alpha-card p {{
            color: var(--muted);
            font-size: 13px;
            line-height: 1.55;
            margin-bottom: 0;
        }}

        .mini-lists {{
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
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
            padding: 9px 0;
            border-bottom: 1px solid rgba(255,255,255,0.06);
        }}

        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 16px;
            margin-bottom: 18px;
        }}

        .chart-card {{
            padding: 20px;
            overflow: hidden;
        }}

        .chart-box {{
            margin-top: 14px;
            overflow-x: auto;
        }}

        .chart-box svg {{
            max-width: 100%;
            height: auto;
        }}

        .empty-chart {{
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

        .muted {{
            color: var(--muted);
        }}

        code {{
            color: var(--gold);
        }}

        @media (max-width: 1100px) {{
            .kpi-grid, .market-grid, .alpha-grid, .charts-grid, .news-grid {{
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }}
        }}

        @media (max-width: 720px) {{
            .hero, .panel-header {{
                flex-direction: column;
            }}

            .kpi-grid, .market-grid, .alpha-grid, .charts-grid, .news-grid, .mini-lists {{
                grid-template-columns: 1fr;
            }}

            .time-chip, .updated-pill {{
                white-space: normal;
            }}
        }}
    </style>
</head>
<body>
    <main class="page">
        <header class="hero">
            <div>
                <h1>Bảng tổng hợp tin tức ngày {datetime.now().strftime("%d/%m/%Y")}</h1>
                <p>Morning Agent Finance theo dõi tin tức, thị trường, vàng, VNINDEX, Bitcoin và tín hiệu Crypto Alpha để hỗ trợ ra quyết định mỗi ngày.</p>
            </div>
            <div class="time-chip">Cập nhật lần cuối: {now}</div>
        </header>

        <section class="kpi-grid">
            <article class="kpi-card">
                <span>Tổng tin nóng</span>
                <strong>{sum(len(v or []) for v in news_data.values())}</strong>
                <em class="neutral">VnExpress / Dân Trí / BBC</em>
            </article>
            <article class="kpi-card">
                <span>Bitcoin</span>
                <strong>{format_price(btc.get("price"))}</strong>
                <em class="{get_change_class(btc_change)}">{safe_percent(btc_change)}</em>
            </article>
            <article class="kpi-card">
                <span>Vàng thế giới</span>
                <strong>{format_price(world_gold.get("price"), prefix="$", suffix="/oz")}</strong>
                <em class="{get_change_class(world_gold_change)}">{safe_percent(world_gold_change)}</em>
            </article>
            <article class="kpi-card">
                <span>VNINDEX</span>
                <strong>{safe_number(vnindex.get("price") or vnindex.get("value"))}</strong>
                <em class="{get_change_class(vnindex_change)}">{safe_percent(vnindex_change)}</em>
            </article>
        </section>

        <section class="panel">
            <div class="panel-header">
                <div>
                    <span class="eyebrow">AI Brief</span>
                    <h2>AI Market Brief</h2>
                </div>
            </div>
            <div class="brief">{safe_text(ai_summary)}</div>
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
                    <span>Bitcoin</span>
                    <strong>{format_price(btc.get("price"))}</strong>
                    <em class="{get_change_class(btc_change)}">{safe_percent(btc_change)}</em>
                </article>

                <article class="market-item">
                    <span>Vàng SJC trong nước</span>
                    <strong>{safe_number(domestic_gold.get("sell"), 0)} VND</strong>
                    <em class="{get_change_class(domestic_gold_change)}">Mua: {safe_number(domestic_gold.get("buy"), 0)} | Bán: {safe_number(domestic_gold.get("sell"), 0)}</em>
                </article>

                <article class="market-item">
                    <span>Vàng thế giới</span>
                    <strong>{format_price(world_gold.get("price"), prefix="$", suffix="/oz")}</strong>
                    <em class="{get_change_class(world_gold_change)}">{safe_percent(world_gold_change)}</em>
                </article>

                <article class="market-item">
                    <span>VNINDEX</span>
                    <strong>{safe_number(vnindex.get("price") or vnindex.get("value"))}</strong>
                    <em class="{get_change_class(vnindex_change)}">{safe_percent(vnindex_change)}</em>
                </article>
            </div>
        </section>

        <section class="charts-grid">
            {render_chart_card("Bitcoin Chart", charts.get("bitcoin"))}
            {render_chart_card("Vàng thế giới Chart", charts.get("gold"))}
            {render_chart_card("VNINDEX Chart", charts.get("vnindex"))}
        </section>

        <section class="news-grid">
            {render_news_column("VnExpress", news_data.get("vnexpress", []))}
            {render_news_column("Dân Trí", news_data.get("dantri", []))}
            {render_news_column("BBC", news_data.get("bbc", []))}
        </section>
    </main>
</body>
</html>"""


def main():
    news_data = get_news()
    market_data = get_market_data()
    charts = generate_charts(market_data)

    crypto_alpha = None
    crypto_alpha_text = ""

    if build_crypto_alpha:
        try:
            crypto_alpha = build_crypto_alpha()
            if format_crypto_alpha_text:
                crypto_alpha_text = format_crypto_alpha_text(crypto_alpha)
        except Exception as exc:
            print(f"[generate_dashboard] Crypto Alpha error: {exc}")

    ai_context = {
        "news": news_data,
        "market": market_data,
        "crypto_alpha": crypto_alpha_text,
    }

    try:
        ai_summary = generate_ai_summary(ai_context)
    except TypeError:
        ai_summary = generate_ai_summary(news_data, market_data)
    except Exception as exc:
        print(f"[generate_dashboard] AI summary error: {exc}")
        ai_summary = "Chưa tạo được AI Market Brief. Vui lòng kiểm tra OPENAI_API_KEY hoặc module ai_summary.py."

    html_content = render_dashboard(
        news_data=news_data,
        market_data=market_data,
        charts=charts,
        ai_summary=ai_summary,
        crypto_alpha=crypto_alpha,
    )

    with open("index.html", "w", encoding="utf-8") as file:
        file.write(html_content)

    print("Dashboard generated successfully: index.html")


if __name__ == "__main__":
    main()
