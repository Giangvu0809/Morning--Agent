from modules.dashboard_utils import vn_now, FAST_MODE
from modules.dashboard_utils import filter_curated_news, group_news_by_source

from modules.sections_market import render_market_section
from modules.sections_career import render_career_section
from modules.sections_business import render_business_section
from modules.sections_personal import render_personal_section


def render_dashboard(context):
    current_time = vn_now()
    now = current_time.strftime("%d/%m/%Y %H:%M:%S")

    news_items = context["news_items"]
    curated_news = filter_curated_news(news_items, max_items=15)
    grouped_news = group_news_by_source(curated_news)

    return f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Morning Agent</title>
    {render_styles()}
</head>

<body>
    <main class="page">
        <header class="hero">
            <div>
                <h1>Morning Agent</h1>
                <p>
                    Dashboard phân tích tài chính, cơ hội nghề nghiệp, cơ hội kinh doanh
                    và briefing cá nhân. Thời gian hiển thị theo giờ Việt Nam.
                </p>
            </div>

            <div class="time-chip">Cập nhật: {now} GMT+7 · FAST_MODE: {str(FAST_MODE)}</div>
        </header>

        {render_market_section(context, curated_news, grouped_news)}
        {render_career_section(context)}
        {render_business_section(context)}
        {render_personal_section(context)}
    </main>
</body>
</html>
"""


def render_styles():
    return """
    <style>
        :root {
            --bg: #070b14;
            --border: rgba(255, 255, 255, 0.09);
            --text: #e8eefc;
            --muted: #8b9ab4;
            --positive: #24d18b;
            --negative: #ff5c7a;
            --accent: #56a3ff;
            --gold: #ffd166;
        }

        * { box-sizing: border-box; }

        body {
            margin: 0;
            font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            background:
                radial-gradient(circle at top left, rgba(86, 163, 255, 0.18), transparent 32%),
                radial-gradient(circle at top right, rgba(255, 209, 102, 0.12), transparent 28%),
                var(--bg);
            color: var(--text);
        }

        a { color: inherit; text-decoration: none; }

        .page {
            width: min(1440px, 94vw);
            margin: 0 auto;
            padding: 32px 0 56px;
        }

        .hero {
            display: flex;
            justify-content: space-between;
            gap: 24px;
            align-items: flex-start;
            margin-bottom: 24px;
        }

        .hero h1 {
            margin: 0;
            font-size: clamp(34px, 5vw, 60px);
            line-height: 1;
            letter-spacing: -0.055em;
        }

        .hero p {
            color: var(--muted);
            max-width: 880px;
            font-size: 16px;
            line-height: 1.7;
        }

        .time-chip, .updated-pill, .rsi-pill, .tag {
            border: 1px solid var(--border);
            background: rgba(255, 255, 255, 0.05);
            padding: 10px 14px;
            border-radius: 999px;
            color: var(--muted);
            white-space: nowrap;
            font-size: 13px;
        }

        .dashboard-section {
            margin-bottom: 18px;
            border: 1px solid var(--border);
            border-radius: 28px;
            background: linear-gradient(180deg, rgba(255,255,255,0.065), rgba(255,255,255,0.025));
            box-shadow: 0 22px 60px rgba(0, 0, 0, 0.23);
            overflow: hidden;
        }

        .dashboard-section > summary {
            cursor: pointer;
            list-style: none;
            padding: 22px 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 18px;
        }

        .dashboard-section > summary::-webkit-details-marker { display: none; }

        .summary-title {
            display: flex;
            flex-direction: column;
            gap: 6px;
        }

        .summary-title span {
            color: var(--accent);
            text-transform: uppercase;
            letter-spacing: 0.14em;
            font-size: 11px;
            font-weight: 800;
        }

        .summary-title strong {
            font-size: 26px;
            letter-spacing: -0.03em;
        }

        .summary-meta {
            color: var(--muted);
            font-size: 13px;
        }

        .section-body { padding: 0 24px 24px; }

        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(5, minmax(0, 1fr));
            gap: 16px;
            margin-bottom: 18px;
        }

        .kpi-card, .panel, .chart-card, .news-column,
        .insight-card, .fulltime-box, .job-card, .client-card {
            background: rgba(255,255,255,0.04);
            border: 1px solid var(--border);
            border-radius: 20px;
            padding: 18px;
        }

        .kpi-card span, .market-item span {
            color: var(--muted);
            font-size: 13px;
        }

        .kpi-card strong, .market-item strong {
            display: block;
            font-size: 24px;
            margin-top: 8px;
            word-break: break-word;
        }

        .kpi-card em, .market-item em {
            display: block;
            margin-top: 8px;
            font-style: normal;
            font-size: 13px;
            line-height: 1.5;
        }

        .panel { margin-bottom: 18px; }

        .panel-header, .chart-card-header, .section-title-row, .job-top, .coin-line {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 16px;
            margin-bottom: 18px;
        }

        .eyebrow {
            color: var(--accent);
            text-transform: uppercase;
            letter-spacing: 0.14em;
            font-size: 11px;
            font-weight: 800;
        }

        h2, h3, h4 {
            margin: 0;
            letter-spacing: -0.03em;
        }

        h2 { font-size: 26px; }
        h3 { font-size: 18px; }
        h4 { margin-top: 18px; font-size: 15px; }

        .executive-grid, .market-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 14px;
        }

        .market-grid { grid-template-columns: repeat(4, minmax(0, 1fr)); }

        .insight-card p, .fulltime-box p, .client-card p {
            color: var(--muted);
            line-height: 1.65;
            margin-bottom: 0;
        }

        ul { color: var(--muted); line-height: 1.65; }

        .brief { color: #d7e2f7; line-height: 1.75; }

        .positive { color: var(--positive) !important; }
        .negative { color: var(--negative) !important; }
        .neutral, .muted { color: var(--muted) !important; }

        .crypto-overview {
            display: flex;
            gap: 18px;
            align-items: center;
            flex-wrap: wrap;
            margin-bottom: 18px;
        }

        .sentiment-card {
            display: flex;
            align-items: center;
            gap: 14px;
            width: fit-content;
            padding: 14px 16px;
            border-radius: 18px;
            background: rgba(255,255,255,0.05);
            border: 1px solid var(--border);
        }

        .sentiment-card span { color: var(--muted); }
        .sentiment-card strong { font-size: 26px; color: var(--gold); }
        .sentiment-card em { font-style: normal; }

        .alpha-grid, .jobs-grid, .client-grid, .news-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 14px;
        }

        .alpha-grid { grid-template-columns: repeat(4, minmax(0, 1fr)); }
        .client-grid { grid-template-columns: repeat(5, minmax(0, 1fr)); }

        .coin-symbol { font-size: 22px; font-weight: 900; }
        .coin-name, .job-card p { color: var(--muted); font-size: 13px; }

        .score-badge, .match-score {
            min-width: 48px;
            text-align: center;
            padding: 8px 10px;
            border-radius: 14px;
            background: rgba(86,163,255,0.16);
            color: var(--accent);
            font-weight: 900;
        }

        .metric-row {
            display: flex;
            justify-content: space-between;
            gap: 12px;
            margin: 8px 0;
            color: var(--muted);
            font-size: 13px;
        }

        .mini-lists {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 14px;
            margin-top: 18px;
        }

        .mini-lists > div {
            padding: 16px;
            border-radius: 18px;
            background: rgba(255,255,255,0.035);
            border: 1px solid var(--border);
        }

        .mini-lists ul {
            padding: 0;
            margin: 14px 0 0;
            list-style: none;
        }

        .mini-lists li {
            display: flex;
            justify-content: space-between;
            gap: 12px;
            padding: 9px 0;
            border-bottom: 1px solid rgba(255,255,255,0.06);
        }

        .career-layout { display: grid; gap: 22px; }

        .job-meta, .tag-row {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin: 12px 0;
        }

        .job-meta span, .tag-row span {
            border: 1px solid var(--border);
            background: rgba(255,255,255,0.045);
            color: var(--muted);
            border-radius: 999px;
            padding: 6px 10px;
            font-size: 12px;
        }

        .apply-link {
            display: inline-flex;
            margin-top: 14px;
            color: var(--accent);
            font-weight: 800;
        }

        .charts-grid {
            display: grid;
            grid-template-columns: 1fr;
            gap: 16px;
            margin-bottom: 18px;
        }

        .chart-box { overflow-x: auto; }
        .chart-wrapper { min-width: 760px; }
        .chart-title { display: none; }

        .chart-svg {
            width: 100%;
            height: auto;
            background: rgba(255,255,255,0.025);
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 18px;
        }

        .chart-empty {
            color: var(--muted);
            min-height: 220px;
            display: grid;
            place-items: center;
            border: 1px dashed var(--border);
            border-radius: 16px;
        }

        .grid-line { stroke: rgba(255,255,255,0.12); stroke-width: 1; }
        .axis-text { fill: #8b9ab4; font-size: 12px; }
        .candle-up { stroke: var(--positive); fill: var(--positive); }
        .candle-down { stroke: var(--negative); fill: var(--negative); }
        .rsi-line { stroke: var(--accent); stroke-width: 2.2; }

        .rsi-high-line {
            stroke: rgba(255, 92, 122, 0.55);
            stroke-width: 1;
            stroke-dasharray: 5 5;
        }

        .rsi-low-line {
            stroke: rgba(36, 209, 139, 0.55);
            stroke-width: 1;
            stroke-dasharray: 5 5;
        }

        .chart-meta {
            display: flex;
            gap: 14px;
            flex-wrap: wrap;
            margin-top: 12px;
            color: var(--muted);
            font-size: 13px;
        }

        .news-card {
            padding: 14px 0;
            border-bottom: 1px solid rgba(255,255,255,0.07);
        }

        .news-card:last-child { border-bottom: none; }

        .news-card a {
            display: block;
            font-weight: 800;
            line-height: 1.45;
        }

        .news-card p {
            color: var(--muted);
            font-size: 13px;
            line-height: 1.6;
            margin: 8px 0 0;
        }

        @media (max-width: 1200px) {
            .kpi-grid, .market-grid, .alpha-grid, .news-grid,
            .executive-grid, .jobs-grid, .client-grid {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }

            .mini-lists { grid-template-columns: 1fr; }
        }

        @media (max-width: 720px) {
            .hero, .panel-header, .chart-card-header, .section-title-row,
            .job-top, .coin-line, .dashboard-section > summary {
                flex-direction: column;
            }

            .kpi-grid, .market-grid, .alpha-grid, .news-grid,
            .executive-grid, .jobs-grid, .client-grid {
                grid-template-columns: 1fr;
            }

            .time-chip, .updated-pill, .rsi-pill { white-space: normal; }

            .hero h1 { font-size: 36px; }
        }
    </style>
    """
