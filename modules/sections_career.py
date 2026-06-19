from modules.dashboard_utils import safe_text, render_list


def render_career_section(context):
    career_data = context["career_data"]

    if not career_data:
        body = '<p class="muted">Chưa có dữ liệu nghề nghiệp. Hãy kiểm tra module career_opportunities.py.</p>'
        job_count = 0
    else:
        remote_jobs = career_data.get("remote_jobs", [])[:10]
        fulltime = career_data.get("fulltime_jobs", {}) or {}
        job_count = len(remote_jobs)

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

        body = f"""
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
                    <ul>{render_list(fulltime.get("suggested_roles", []))}</ul>

                    <h4>Cách kích hoạt</h4>
                    <ul>{render_list(fulltime.get("next_steps", []))}</ul>
                </div>
            </section>
        </div>
        """

    return f"""
    <details class="dashboard-section">
        <summary>
            <div class="summary-title">
                <span>Career Opportunities</span>
                <strong>Cơ hội nghề nghiệp</strong>
            </div>
            <div class="summary-meta">{job_count} remote jobs</div>
        </summary>

        <div class="section-body">
            {body}
        </div>
    </details>
    """
