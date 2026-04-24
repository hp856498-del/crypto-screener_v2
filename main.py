import streamlit as st

from data import get_symbols, get_ohlcv, get_ohlcv_before_time
from scanner import detect_patterns, get_last_closed_candles
from scanner import detect_pattern_on_candles

st.set_page_config(page_title="Crypto Screener", layout="wide")

st.title("🚀 Crypto Screener")
selected_patterns = st.sidebar.multiselect(
    "Select Patterns",
    ["Inside Bar", "Bullish Engulfing", "Bearish Engulfing", "Bullish Harami", "Bearish Harami"],
    default=["Bullish Engulfing"]
)
timeframe = st.sidebar.selectbox(
    "Select Timeframe",
    ["15m", "30m", "1h", "3h", "4h", "1d"]
)
coin_limit = st.sidebar.selectbox(
    "Number of Coins",
    [50, 100, 200, 300],
    index=2
)
# ================== NEW CODE START ==================

st.markdown("---")
st.subheader("📅 Historical Candle Scan")

col1, col2 = st.columns(2)

with col1:
    selected_date = st.date_input("Select Date")

with col2:
    selected_time = st.time_input("Select Time")

if st.button("Run Historical Scan"):

    import datetime
    patterns = selected_patterns

    # Combine date + time
    target_datetime = datetime.datetime.combine(selected_date, selected_time)
    target_timestamp = int(target_datetime.timestamp() * 1000)

    # Future check
    if target_datetime > datetime.datetime.now():
        st.error("Future time select nahi kar sakte ❌")
    else:
        st.info("Scanning historical data... ⏳")

        results = []   # ✅ PROBLEM 2 FIX (yaha define hoga)

        symbols = get_symbols(coin_limit)

        for symbol in symbols:   # ✅ PROBLEM 3 FIX (loop yaha hoga)

            df = get_ohlcv_before_time(symbol, timeframe, target_timestamp)

            if df is None or len(df) < 2:
                continue

            c1, c2 = get_last_closed_candles(df, target_timestamp)

            if c1 is None:
                continue

            patterns_found = detect_pattern_on_candles(c1, c2, patterns)

            for p in patterns_found:
                results.append({
                    "Symbol": symbol,
                   "Pattern": p["pattern"],
                   "Signal": p["signal"],
                    "Time": str(target_datetime)
                })

        # ✅ PROBLEM 1 FIX (correct indentation)
        if results:
            st.success(f"{len(results)} patterns found ✅")
            st.dataframe(results)
        else:
            st.warning("Koi pattern nahi mila ❌")

# ================== NEW CODE END ==================

# NEW CODE END

# ================= SIDEBAR =================


enable_backscan = st.sidebar.checkbox("Scan Previous Candles")

backscan_range = st.sidebar.selectbox(
    "Backscan Range",
    [5, 10, 15],
    index=1
)

start = st.sidebar.button("🚀 Start Scanning")

# ================= MAIN =================

if start:
    st.info("Scanning market... please wait ⏳")

    symbols = get_symbols(coin_limit)

    results = []

    progress = st.progress(0)

    for i, symbol in enumerate(symbols):
        df = get_ohlcv(symbol, timeframe)

        if df is None or len(df) < 10:
            continue

        matches = detect_patterns(
            df,
            selected_patterns=patterns,
            backscan=enable_backscan,
            backscan_range=backscan_range
        )

        for m in matches:
            results.append({
                "Symbol": symbol,
                "Pattern": m["pattern"],
                "Signal": m["signal"],
                "Time": m["time"]
            })

        progress.progress((i + 1) / len(symbols))

    st.success(f"{len(results)} patterns found")

    if results:
        st.dataframe(results)
    else:
        st.warning("No patterns found")