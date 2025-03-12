import streamlit as st
import time
import logging
from datetime import datetime, timedelta

from src.api.binance_client import BinanceAPI
from src.data.market_data import get_market_info, fetch_candlesticks
from src.utils.formatting import format_currency, format_price_change, format_number
from src.utils.email_service import send_price_alert
from src.visualization.charts import plot_candlestick, plot_price_evolution
import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def display_market_info(market_data, symbol):
    if market_data is None:
        st.error("Market information unavailable")
        return

    st.markdown("""
        <style>
        .market-metric {
            font-size: 24px !important;
            font-weight: bold !important;
            color: white !important;
        }
        .market-label {
            font-size: 14px !important;
            color: gray !important;
            text-transform: uppercase !important;
        }
        .price-change {
            font-size: 20px !important;
            font-weight: bold !important;
        }
        </style>
    """, unsafe_allow_html=True)

    row1_cols = st.columns(5)
    row2_cols = st.columns(5)

    with row1_cols[0]:
        st.markdown(f"<p class='market-label'>LOW 24H</p>", unsafe_allow_html=True)
        st.markdown(f"<p class='market-metric'>${market_data['low_24h']:,.2f}</p>", unsafe_allow_html=True)

    with row1_cols[1]:
        st.markdown(f"<p class='market-label'>HIGH 24H</p>", unsafe_allow_html=True)
        st.markdown(f"<p class='market-metric'>${market_data['high_24h']:,.2f}</p>", unsafe_allow_html=True)

    changes = [
        ("1H PRICE CHANGE", market_data['price_change_1h']),
        ("24H PRICE CHANGE", market_data['price_change_24h']),
        ("7D PRICE CHANGE", market_data['price_change_7d'])
    ]

    for col, (label, value) in zip(row1_cols[2:], changes):
        with col:
            formatted_value, color, arrow = format_price_change(value)
            st.markdown(f"<p class='market-label'>{label}</p>", unsafe_allow_html=True)
            st.markdown(
                f"<p class='price-change' style='color: {color};'>{formatted_value}</p>",
                unsafe_allow_html=True
            )

    with row2_cols[0]:
        st.markdown("<p class='market-label'>VOLUME 24H</p>", unsafe_allow_html=True)
        st.markdown(f"<p class='market-metric'>{format_currency(market_data['volume_24h'])}</p>", unsafe_allow_html=True)

    with row2_cols[1]:
        st.markdown("<p class='market-label'>MARKET CAP</p>", unsafe_allow_html=True)
        st.markdown(f"<p class='market-metric'>{format_currency(market_data['market_cap'])}</p>", unsafe_allow_html=True)

    with row2_cols[2]:
        st.markdown("<p class='market-label'>CIRCULATION SUPPLY</p>", unsafe_allow_html=True)
        st.markdown(
            f"<p class='market-metric'>BTC {format_number(market_data['circulation_supply'])}</p>",
            unsafe_allow_html=True
        )

    with row2_cols[3]:
        st.markdown("<p class='market-label'>TOTAL MAXIMUM SUPPLY</p>", unsafe_allow_html=True)
        st.markdown(
            f"<p class='market-metric'>BTC {format_number(market_data['max_supply'])}</p>",
            unsafe_allow_html=True
        )

    with row2_cols[4]:
        st.markdown("<p class='market-label'>ALL-TIME HIGH</p>", unsafe_allow_html=True)
        st.markdown(f"<p class='market-metric'>${market_data['all_time_high']:,.0f}</p>", unsafe_allow_html=True)

def display_account_info(client):
    st.markdown("---")
    st.subheader("Account Information")
    
    balances = client.get_account_info()
    if balances:
        col1, col2, col3 = st.columns(3)
        
        for balance in balances[:3]:
            with col1:
                st.write(f"**{balance['asset']}**")
            with col2:
                st.write(f"Available: {float(balance['free']):.8f}")
            with col3:
                st.write(f"In Order: {float(balance['locked']):.8f}")

def main():
    st.set_page_config(
        layout="wide", 
        page_title="Crypto Trading Platform", 
        initial_sidebar_state="collapsed"
    )

    try:
        client = BinanceAPI()
    except Exception as e:
        st.error(f"Error connecting to Binance: {e}")
        return

    st.title("Advanced Market Trend Analysis Platform")

    with st.sidebar:
        symbol = st.selectbox(
            "Select Symbol",
            config.DEFAULT_SYMBOLS
        )

        st.subheader("Alert Configuration")
        enable_alerts = st.checkbox("Enable Price Alerts")
        alert_price = None
        email = None
        if enable_alerts:
            alert_price = st.number_input("Alert Price (USDT)", min_value=0.0, step=0.1)
            email = st.text_input("Alert Email")

        interval = st.selectbox(
            "Select Interval",
            config.INTERVALS
        )

        if interval not in ["1w", "1M"]:
            period_options = {
                "1 Day": 1,
                "1 Week": 7,
                "1 Month": 30,
                "3 Months": 90,
                "6 Months": 180,
                "1 Year": 365
            }
            selected_period = st.selectbox("Select Period", list(period_options.keys()))
            days = period_options[selected_period]
        else:
            days = 365

        auto_refresh = st.checkbox("Auto-refresh (60s)", value=True)

    placeholder = st.empty()

    while True:
        try:
            with placeholder.container():
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days)

                with st.spinner("Fetching market data..."):
                    df = fetch_candlesticks(client, symbol, interval, start_date, end_date)
                    market_data = get_market_info(client, symbol)

                if df is not None and not df.empty:
                    display_market_info(market_data, symbol)

                    tab1, tab2, tab4 = st.tabs([
                        "Technical Analysis",
                        "Price Evolution",
                        "Data"
                    ])

                    with tab1:
                        plot_candlestick(df, symbol)

                    with tab2:
                        plot_price_evolution(df, symbol)

                    with tab4:
                        st.subheader(f"Latest {symbol} Data")
                        st.dataframe(
                            df.style.format({
                                'open': '${:,.2f}',
                                'high': '${:,.2f}',
                                'low': '${:,.2f}',
                                'close': '${:,.2f}',
                                'volume': '{:,.0f}'
                            })
                        )

                    if enable_alerts and alert_price and email and df['close'].iloc[-1] <= alert_price:
                        success = send_price_alert(symbol, df['close'].iloc[-1], alert_price, email)
                        if success:
                            st.success("Price alert email sent successfully!")

                    display_account_info(client)
                    
                    footer = """
                        <style>
                            .footer {
                                position: fixed;
                                bottom: 0;
                                left: 0;
                                width: 100%;
                                background-color: #f1f1f1;
                                text-align: center;
                                padding: 10px 0;
                                font-size: 12px;
                                color: #555;
                            }
                        </style>
                        <div class="footer">
                            Copyright M&K
                        </div>
                    """
                    st.markdown(footer, unsafe_allow_html=True)
                else:
                    st.error("Failed to fetch market data. Please check your connection and try again.")

        except Exception as e:
            logger.error(f"Error in main loop: {str(e)}")
            st.error(f"An error occurred: {str(e)}")
            time.sleep(5)
            continue

        if not auto_refresh:
            break

        time.sleep(60)

if __name__ == "__main__":
    main()
