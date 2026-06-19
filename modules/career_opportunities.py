import re
import requests
from datetime import datetime


REMOTE_OK_API = "https://remoteok.com/api"
WEWORKREMOTELY_RSS = "https://weworkremotely.com/categories/remote-sales-and-marketing-jobs.rss"


TARGET_KEYWORDS = [
    "google ads",
    "ppc",
    "paid search",
    "digital marketing",
    "performance marketing",
    "lead generation",
    "seo",
    "content marketing",
    "growth marketing",
    "marketing assistant",
    "virtual assistant",
    "research assistant",
    "ai automation",
    "automation",
    "no-code",
]


BEGINNER_FRIENDLY_KEYWORDS = [
    "junior",
    "assistant",
    "entry",
    "intern",
    "fresher",
    "trainee",
    "specialist",
    "coordinator",
]


def safe_get(url, timeout=20):
    try:
        response = requests.get(
            url,
            timeout=timeout,
            headers={
                "User-Agent": "Morning-Agent-Career-Scanner/1.0"
            },
        )
        response.raise_for_status()
        return response
    except Exception as exc:
        print(f"[career_opportunities] request failed: {url} - {exc}")
        return None


def clean_text(value):
    if not value:
        return ""

    value = re.sub(r"<.*?>", "", str(value))
    value = value.replace("&amp;", "&")
    value = value.replace("&nbsp;", " ")
    return value.strip()


def score_job(title, company="", description="", tags=None):
    tags = tags or []
    text = " ".join([
        title or "",
        company or "",
        description or "",
        " ".join(tags),
    ]).lower()

    score = 40
    reasons = []

    for keyword in TARGET_KEYWORDS:
        if keyword in text:
            score += 8
            reasons.append(f"Liên quan đến {keyword}")

    for keyword in BEGINNER_FRIENDLY_KEYWORDS:
        if keyword in text:
            score += 10
            reasons.append("Có dấu hiệu phù hợp người mới/junior")
            break

    if "google ads" in text or "ppc" in text or "paid search" in text:
        score += 15
        reasons.append("Phù hợp hướng Google Ads/PPC")

    if "lead generation" in text:
        score += 12
        reasons.append("Phù hợp hướng tìm lead/khách hàng")

    if "ai" in text or "automation" in text:
        score += 10
        reasons.append("Liên quan AI/automation")

    if "senior" in text or "manager" in text or "head of" in text or "director" in text:
        score -= 18
        reasons.append("Có thể hơi cao so với level hiện tại")

    score = max(0, min(score, 100))

    if not reasons:
        reasons.append("Có thể phù hợp để tham khảo thị trường remote")

    return score, reasons[:3]


def fetch_remoteok_jobs(limit=12):
    response = safe_get(REMOTE_OK_API)

    if not response:
        return []

    try:
        data = response.json()
    except Exception as exc:
        print(f"[career_opportunities] remoteok json error: {exc}")
        return []

    jobs = []

    for item in data:
        if not isinstance(item, dict):
            continue

        if "position" not in item:
            continue

        title = clean_text(item.get("position"))
        company = clean_text(item.get("company"))
        description = clean_text(item.get("description"))
        tags = item.get("tags") or []
        url = item.get("url") or item.get("apply_url") or "https://remoteok.com"

        score, reasons = score_job(title, company, description, tags)

        if score < 55:
            continue

        salary_min = item.get("salary_min")
        salary_max = item.get("salary_max")

        salary = "Không công khai"
        if salary_min or salary_max:
            salary = f"${salary_min or '?'} - ${salary_max or '?'} / year"

        jobs.append({
            "title": title,
            "company": company or "RemoteOK Company",
            "location": "Remote",
            "salary": salary,
            "source": "RemoteOK",
            "url": url,
            "match_score": score,
            "reasons": reasons,
            "tags": tags[:6],
        })

    jobs = sorted(jobs, key=lambda x: x["match_score"], reverse=True)
    return jobs[:limit]


def fallback_remote_jobs():
    raw_jobs = [
        {
            "title": "Google Ads Assistant / PPC Assistant",
            "company": "Small Marketing Agency",
            "location": "Remote",
            "salary": "$500 - $1,500/month",
            "source": "Fallback",
            "url": "https://remoteok.com/remote-marketing-jobs",
            "tags": ["Google Ads", "PPC", "Marketing"],
        },
        {
            "title": "Lead Generation Specialist",
            "company": "B2B Service Company",
            "location": "Remote",
            "salary": "$600 - $1,800/month",
            "source": "Fallback",
            "url": "https://remoteok.com/remote-sales-jobs",
            "tags": ["Lead Generation", "Research", "CRM"],
        },
        {
            "title": "Digital Marketing Assistant",
            "company": "Online Business",
            "location": "Remote",
            "salary": "$500 - $1,500/month",
            "source": "Fallback",
            "url": "https://remoteok.com/remote-marketing-jobs",
            "tags": ["Digital Marketing", "SEO", "Ads"],
        },
        {
            "title": "AI Automation Assistant",
            "company": "Automation Agency",
            "location": "Remote",
            "salary": "$700 - $2,000/month",
            "source": "Fallback",
            "url": "https://remoteok.com/remote-ai-jobs",
            "tags": ["AI", "Automation", "No-code"],
        },
    ]

    jobs = []

    for item in raw_jobs:
        score, reasons = score_job(
            item["title"],
            item["company"],
            "",
            item.get("tags", []),
        )

        item["match_score"] = score
        item["reasons"] = reasons
        jobs.append(item)

    return jobs


def build_fulltime_placeholder():
    return {
        "status": "waiting_for_cv",
        "message": "Chưa có CV. Sau khi bạn gửi CV, agent sẽ phân tích năng lực và tìm full-time job phù hợp.",
        "suggested_roles": [
            "Digital Marketing Executive",
            "Google Ads Junior Specialist",
            "Performance Marketing Assistant",
            "AI Automation Assistant",
            "Lead Generation Executive",
        ],
        "next_steps": [
            "Upload CV bản PDF/DOCX.",
            "Agent sẽ trích xuất kỹ năng, kinh nghiệm, project cá nhân.",
            "Agent sẽ tìm job phù hợp trên thị trường và chấm điểm match.",
            "Dashboard sẽ hiển thị job nên apply trước.",
        ],
    }


def build_client_opportunities():
    return [
        {
            "segment": "Trung tâm học lái xe",
            "lead_score": 90,
            "why": "Nhu cầu tìm học viên rõ ràng, khách thường tìm trực tiếp trên Google.",
            "offer": "Gói thử nghiệm Google Ads 30 ngày, phí setup/quản lý thấp.",
        },
        {
            "segment": "Dịch vụ sửa máy lạnh",
            "lead_score": 88,
            "why": "Nhu cầu khẩn cấp, từ khóa địa phương dễ ra lead.",
            "offer": "Chạy Search Ads theo khu vực, đo cuộc gọi/Zalo.",
        },
        {
            "segment": "Trung tâm tiếng Anh nhỏ",
            "lead_score": 84,
            "why": "Cần học viên liên tục, dễ chốt gói ngân sách nhỏ.",
            "offer": "Chiến dịch tìm học viên mới theo khóa học.",
        },
        {
            "segment": "Visa / du học nhỏ",
            "lead_score": 82,
            "why": "Lead có giá trị cao, người dùng tìm kiếm chủ động.",
            "offer": "Landing page + Google Search Ads theo quốc gia.",
        },
        {
            "segment": "Rèm cửa / nội thất nhỏ",
            "lead_score": 78,
            "why": "Đơn hàng đủ lớn, chỉ cần vài khách/tháng là thấy hiệu quả.",
            "offer": "Chạy từ khóa theo khu vực và nhóm sản phẩm.",
        },
    ]


def build_career_opportunities():
    remote_jobs = fetch_remoteok_jobs(limit=10)

    if not remote_jobs:
        remote_jobs = fallback_remote_jobs()

    return {
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "remote_jobs": remote_jobs,
        "fulltime_jobs": build_fulltime_placeholder(),
        "client_opportunities": build_client_opportunities(),
    }
