from modules.dashboard_utils import safe_text, clean_price_prefix, render_list, filter_crypto_items


def render_market_section(context, curated_news, grouped_news):
    bitcoin = context["bitcoin"]
    gold = context["gold"]
    vnindex = context["vnindex"]
    charts = context["charts"]
    crypto_alpha = context["crypto_alpha"]
    ai_summary = context["ai_summary"]
    mood = context["mood"]
    data_warnings = context["data_warnings"]

    domestic_gold = gold.get("domestic", {}) or {}
    world_gold = gold.get("world", {}) or {}

    return f"""
    <details class="dashboard-section" open>
        <summary>
            <div class="summary-title">
                <span>Market Intelligence</span>
                <strong>Thị trường & phân tích tài chính</strong>
            </div>
            <div class="summary-meta">Click để đóng/mở</div>
        </summary>

        <div class="section-body">
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
                    <span>VNINDEX</span>
                    <strong>{safe_text(vnindex.get("value"))}</strong>
                    <em class="{safe_text(vnindex.get("change_class", "neutral"))}">
                        {safe_text(vnindex.get("change_percent"))}
                    </em>
                </article>

                <article class="kpi-card">
                    <span>Curated News</span>
                    <strong>{len(curated_news)}</strong>
                    <em class="neutral">Tin đã lọc theo chủ đề tài chính</em>
                </article>
            </section>

            <section class="panel">
                <div class="panel-header">
                    <div>
                        <span class="eyebrow">Executive Summary</span>
                        <h2>Market Brief</h2>
                    </div>
                </div>

                <div class="executive-grid">
                    <article class="insight-card">
                        <h3>Tổng quan</h3>
                        <p>{safe_text(mood["summary"])}</p>
                    </article>

                    <article class="insight-card">
                        <h3>Động lực chính</h3>
                        <ul>{render_list(mood["drivers"])}</ul>
                    </article>

                    <article class="insight-card">
                        <h3>Data Quality</h3>
                        <ul>{render_list(data_warnings)}</ul>
                    </article>
                </div>
            </section>

            <section class="panel">
                <div class="panel-header">
                    <div>
                        <span class="eyebrow">AI Analysis</span>
                        <h2>AI Market Brief</h2>
                    </div>
                </div>
                <div class="brief">{ai_summary}</div>
            </section>

            {render_crypto_alpha_section(crypto_alpha)}

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
        </div>
    </details>
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
            <p>{safe_text(reason_text)}</p>
        </article>
        """

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
        </div>

        <div class="alpha-grid">
            {alpha_cards if alpha_cards else '<p class="muted">Chưa có tín hiệu alpha nổi bật.</p>'}
        </div>
    </section>
    """
