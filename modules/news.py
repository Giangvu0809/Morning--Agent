import feedparser
import html
import re


RSS_FEEDS = {
    "VnExpress": "https://vnexpress.net/rss/kinh-doanh.rss",
    "Dân Trí": "https://dantri.com.vn/rss/kinh-doanh.rss",
    "BBC": "https://feeds.bbci.co.uk/vietnamese/rss.xml",
}


def clean_summary(text):
    if not text:
        return "Chưa có mô tả ngắn cho bài viết này."

    text = re.sub("<.*?>", "", text)
    text = html.unescape(text)
    text = text.strip()

    if not text:
        return "Chưa có mô tả ngắn cho bài viết này."

    return html.escape(text)


def get_news_from_feed(source_name, rss_url, limit=5):
    feed = feedparser.parse(rss_url)
    news = []

    for entry in feed.entries[:limit]:
        title = html.escape(entry.get("title", "Không có tiêu đề"))
        link = entry.get("link", "#")
        summary = clean_summary(entry.get("summary", ""))

        news.append({
            "source": source_name,
            "title": title,
            "summary": summary,
            "link": link
        })

    return news


def get_all_news(limit_per_source=5):
    all_news = []

    for source_name, rss_url in RSS_FEEDS.items():
        try:
            items = get_news_from_feed(source_name, rss_url, limit=limit_per_source)
            all_news.extend(items)
        except Exception as e:
            print(f"ERROR loading {source_name}: {e}")

    return all_news
