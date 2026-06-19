from modules.dashboard_utils import safe_text


def render_business_section(context):
    career_data = context["career_data"]

    if not career_data:
        body = '<p class="muted">Chưa có dữ liệu Business Opportunities.</p>'
        count = 0
    else:
        client_ops = career_data.get("client_opportunities", [])[:5]
        count = len(client_ops)

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

        body = f"""
        <div class="section-title-row">
            <h3>Đối tượng dễ chốt dịch vụ Google Ads</h3>
            <span class="tag">{count} nhóm</span>
        </div>
        <div class="client-grid">
            {client_html}
        </div>
        """

    return f"""
    <details class="dashboard-section">
        <summary>
            <div class="summary-title">
                <span>Business Opportunities</span>
                <strong>Cơ hội kinh doanh</strong>
            </div>
            <div class="summary-meta">{count} nhóm khách hàng</div>
        </summary>

        <div class="section-body">
            {body}
        </div>
    </details>
    """
