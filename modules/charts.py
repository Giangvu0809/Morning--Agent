import yfinance as yf
import pandas as pd


def calculate_rsi(close_series, period=14):
    delta = close_series.diff()

    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi


def get_history_with_rsi(ticker, period="3mo", interval="1d"):
    try:
        data = yf.download(
            ticker,
            period=period,
            interval=interval,
            progress=False,
            auto_adjust=False
        )

        if data.empty:
            return [], "N/A", "Không có dữ liệu chart."

        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        data = data.reset_index()
        data["RSI"] = calculate_rsi(data["Close"], period=14)

        chart_rows = []

        for _, row in data.tail(90).iterrows():
            date_value = row["Date"]
            date_label = date_value.strftime("%d/%m")

            open_value = row["Open"]
            high_value = row["High"]
            low_value = row["Low"]
            close_value = row["Close"]
            rsi_value = row["RSI"]

            if (
                pd.isna(open_value)
                or pd.isna(high_value)
                or pd.isna(low_value)
                or pd.isna(close_value)
            ):
                continue

            chart_rows.append({
                "date": date_label,
                "open": round(float(open_value), 2),
                "high": round(float(high_value), 2),
                "low": round(float(low_value), 2),
                "close": round(float(close_value), 2),
                "rsi": None if pd.isna(rsi_value) else round(float(rsi_value), 2)
            })

        latest_rsi = chart_rows[-1]["rsi"] if chart_rows else "N/A"

        if latest_rsi == "N/A" or latest_rsi is None:
            rsi_note = "Chưa đủ dữ liệu RSI."
        elif latest_rsi >= 70:
            rsi_note = "RSI cao: vùng mua mạnh/quá mua."
        elif latest_rsi <= 30:
            rsi_note = "RSI thấp: vùng bán mạnh/quá bán."
        else:
            rsi_note = "RSI trung tính."

        return chart_rows, latest_rsi, rsi_note

    except Exception as e:
        print(f"ERROR loading history for {ticker}: {e}")
        return [], "N/A", "Không lấy được dữ liệu chart."


def build_candlestick_svg(chart_data, title, price_label, rsi_label):
    if not chart_data:
        return f"<div class='chart-empty'>Không có dữ liệu chart cho {title}.</div>"

    width = 920
    height = 390

    padding_left = 60
    padding_right = 30
    padding_top = 35

    price_height = 230

    rsi_top = 295
    rsi_height = 65

    chart_width = width - padding_left - padding_right

    highs = [item["high"] for item in chart_data]
    lows = [item["low"] for item in chart_data]

    min_price = min(lows)
    max_price = max(highs)

    if min_price == max_price:
        min_price = min_price * 0.98
        max_price = max_price * 1.02

    candle_gap = chart_width / max(len(chart_data), 1)
    candle_width = max(3, min(10, candle_gap * 0.55))

    candles_svg = ""
    rsi_points = []

    for index, item in enumerate(chart_data):
        x = padding_left + index * candle_gap + candle_gap / 2

        open_price = item["open"]
        high_price = item["high"]
        low_price = item["low"]
        close_price = item["close"]

        y_open = padding_top + ((max_price - open_price) / (max_price - min_price)) * price_height
        y_high = padding_top + ((max_price - high_price) / (max_price - min_price)) * price_height
        y_low = padding_top + ((max_price - low_price) / (max_price - min_price)) * price_height
        y_close = padding_top + ((max_price - close_price) / (max_price - min_price)) * price_height

        candle_top = min(y_open, y_close)
        candle_height = abs(y_open - y_close)

        if candle_height < 2:
            candle_height = 2

        candle_class = "candle-up" if close_price >= open_price else "candle-down"

        candles_svg += f"""
            <line
                x1="{x:.2f}"
                y1="{y_high:.2f}"
                x2="{x:.2f}"
                y2="{y_low:.2f}"
                class="{candle_class}"
            />

            <rect
                x="{x - candle_width / 2:.2f}"
                y="{candle_top:.2f}"
                width="{candle_width:.2f}"
                height="{candle_height:.2f}"
                class="{candle_class}"
            />
        """

        if item["rsi"] is not None:
            y_rsi = rsi_top + ((100 - item["rsi"]) / 100) * rsi_height
            rsi_points.append(f"{x:.2f},{y_rsi:.2f}")

    first_date = chart_data[0]["date"]
    last_date = chart_data[-1]["date"]

    latest = chart_data[-1]
    latest_close = latest["close"]
    latest_rsi = latest["rsi"]

    latest_rsi_text = "N/A" if latest_rsi is None else f"{latest_rsi:.2f}"

    return f"""
    <div class="chart-wrapper">
        <div class="chart-title">{title}</div>

        <svg viewBox="0 0 {width} {height}" class="chart-svg" role="img">

            <line x1="{padding_left}" y1="{padding_top}" x2="{width - padding_right}" y2="{padding_top}" class="grid-line" />
            <line x1="{padding_left}" y1="{padding_top + price_height}" x2="{width - padding_right}" y2="{padding_top + price_height}" class="grid-line" />

            <text x="10" y="{padding_top + 5}" class="axis-text">{max_price:,.2f}</text>
            <text x="10" y="{padding_top + price_height}" class="axis-text">{min_price:,.2f}</text>

            {candles_svg}

            <line x1="{padding_left}" y1="{rsi_top}" x2="{width - padding_right}" y2="{rsi_top}" class="grid-line" />
            <line x1="{padding_left}" y1="{rsi_top + rsi_height * 0.3}" x2="{width - padding_right}" y2="{rsi_top + rsi_height * 0.3}" class="rsi-high-line" />
            <line x1="{padding_left}" y1="{rsi_top + rsi_height * 0.7}" x2="{width - padding_right}" y2="{rsi_top + rsi_height * 0.7}" class="rsi-low-line" />
            <line x1="{padding_left}" y1="{rsi_top + rsi_height}" x2="{width - padding_right}" y2="{rsi_top + rsi_height}" class="grid-line" />

            <text x="10" y="{rsi_top + 5}" class="axis-text">RSI 100</text>
            <text x="10" y="{rsi_top + rsi_height * 0.3 + 5}" class="axis-text">70</text>
            <text x="10" y="{rsi_top + rsi_height * 0.7 + 5}" class="axis-text">30</text>
            <text x="10" y="{rsi_top + rsi_height}" class="axis-text">0</text>

            <polyline fill="none" class="rsi-line" points="{" ".join(rsi_points)}" />

            <text x="{padding_left}" y="{height - 8}" class="axis-text">{first_date}</text>
            <text x="{width - padding_right - 45}" y="{height - 8}" class="axis-text">{last_date}</text>

        </svg>

        <div class="chart-meta">
            <span>{price_label}: <strong>{latest_close:,.2f}</strong></span>
            <span>{rsi_label}: <strong>{latest_rsi_text}</strong></span>
        </div>
    </div>
    """
