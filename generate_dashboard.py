from modules.dashboard_data import build_dashboard_context
from modules.dashboard_layout import render_dashboard


def main():
    context = build_dashboard_context()
    html = render_dashboard(context)

    with open("index.html", "w", encoding="utf-8") as file:
        file.write(html)

    print("Dashboard generated successfully: index.html")


if __name__ == "__main__":
    main()
