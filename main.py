import streamlit as st
import requests
import pandas as pd
import plotly.graph_objs as go

# -- API Endpoints
ALL_COINS_URL = "https://api.binance.com/api/v3/ticker/price"
COIN_BY_SYMBOL_URL = "https://api.binance.com/api/v3/ticker/price?symbol={}"
COIN_24H_STATS_URL = "https://api.binance.com/api/v3/ticker/24hr?symbol={}"

# -- Page Setup
st.set_page_config("🚀 Crypto Currency Agent", layout="wide")
st.title("💰 Crypto Currency Agent")
st.markdown("Real-time crypto data using the [Binance API](https://api.binance.com)")

# -- CSS Styling
st.markdown("""
    <style>
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            padding: 10px 20px;
            border-radius: 8px;
            font-size: 16px;
        }
        .main {
            background-color: #f1f2f6;
        }
        .stTextInput>div>input {
            font-size: 16px;
            padding: 8px;
        }
    </style>
""", unsafe_allow_html=True)

# -- Symbol Input Section
st.sidebar.header("🔍 Search Coin")
symbol = st.sidebar.text_input("Enter coin symbol (e.g., BTCUSDT)", value="BTCUSDT")
get_data = st.sidebar.button("Get Price")

# -- Watchlist Section
watchlist = st.sidebar.text_area("📌 Watchlist (comma separated symbols)", "BTCUSDT,ETHUSDT,DOGEUSDT")

# -- Single Coin Output
if get_data and symbol:
    try:
        sym = symbol.upper()
        price_res = requests.get(COIN_BY_SYMBOL_URL.format(sym)).json()
        stats_res = requests.get(COIN_24H_STATS_URL.format(sym)).json()

        st.subheader(f"📈 {sym} Overview")
        col1, col2 = st.columns(2)
        col1.metric("Current Price (USD)", price_res['price'])
        col2.metric("24h Change (%)", f"{stats_res['priceChangePercent']}%", delta_color="normal")

        # Chart
        st.markdown("#### 📊 24h Price Change Chart")
        df_chart = pd.DataFrame({
            "Open": [float(stats_res["openPrice"])],
            "High": [float(stats_res["highPrice"])],
            "Low": [float(stats_res["lowPrice"])],
            "Last Price": [float(stats_res["lastPrice"])]
        })

        fig = go.Figure(data=[
            go.Bar(name='Open', x=["Open"], y=df_chart["Open"]),
            go.Bar(name='High', x=["High"], y=df_chart["High"]),
            go.Bar(name='Low', x=["Low"], y=df_chart["Low"]),
            go.Bar(name='Last', x=["Last Price"], y=df_chart["Last Price"])
        ])
        st.plotly_chart(fig)

    except Exception as e:
        st.error(f"Error fetching data for {symbol.upper()}: {e}")

# -- All Coins Table
st.markdown("---")
st.subheader("📃 Live Market Prices")

try:
    response = requests.get(ALL_COINS_URL).json()
    df = pd.DataFrame(response)
    df['price'] = df['price'].astype(float)
    df = df.sort_values(by='price', ascending=False)
    st.dataframe(df, use_container_width=True)
except Exception as e:
    st.error("Failed to load coin list.")

# -- Watchlist Prices
if watchlist:
    st.markdown("### 📌 Watchlist Overview")
    cols = st.columns(len(watchlist.split(',')))
    for idx, coin in enumerate(watchlist.split(',')):
        coin = coin.strip().upper()
        try:
            res = requests.get(COIN_BY_SYMBOL_URL.format(coin)).json()
            cols[idx].metric(coin, f"${res['price']}")
        except:
            cols[idx].error(f"{coin} not found")
