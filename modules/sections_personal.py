from modules.dashboard_utils import render_list


def render_personal_section(context):
    action_items = context["action_items"]

    return f"""
    <details class="dashboard-section" open>
        <summary>
            <div class="summary-title">
                <span>Personal AI Briefing</span>
                <strong>Việc nên làm hôm nay</strong>
            </div>
            <div class="summary-meta">Daily action list</div>
        </summary>

        <div class="section-body">
            <section class="panel">
                <div class="executive-grid">
                    <article class="insight-card">
                        <h3>Hành động ưu tiên</h3>
                        <ul>{render_list(action_items)}</ul>
                    </article>

                    <article class="insight-card">
                        <h3>Hướng kiếm tiền gần nhất</h3>
                        <ul>
                            <li>Apply các remote job phù hợp trong mục Career Opportunities.</li>
                            <li>Tiếp cận nhóm khách hàng dễ chốt Google Ads trong mục Business Opportunities.</li>
                            <li>Xây case study nhỏ từ chính Morning Agent để tăng uy tín.</li>
                        </ul>
                    </article>

                    <article class="insight-card">
                        <h3>Gợi ý phát triển tiếp</h3>
                        <ul>
                            <li>Upload CV để kích hoạt Full-time Job Matching.</li>
                            <li>Thêm module tìm lead thật theo khu vực TP.HCM/Hà Nội.</li>
                            <li>Thêm email/Zalo outreach template cho từng nhóm khách hàng.</li>
                        </ul>
                    </article>
                </div>
            </section>
        </div>
    </details>
    """
