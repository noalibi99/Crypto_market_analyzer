import plotly.graph_objs as go
import pandas as pd
import streamlit as st

def plot_candlestick(df: pd.DataFrame, symbol: str):
    trace_candle = go.Candlestick(
        x=df.index,
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name="Candlestick"
    )
    
    traces = [trace_candle]
    ma_colors = ['blue', 'orange', 'red']
    
    for (period, color) in zip([20, 50, 200], ma_colors):
        if f'MA_{period}' in df.columns:
            traces.append(go.Scatter(
                x=df.index,
                y=df[f'MA_{period}'],
                name=f'MA {period}',
                line=dict(color=color)
            ))
    
    traces.append(go.Bar(
        x=df.index,
        y=df['volume'],
        name="Volume",
        yaxis="y2",
        opacity=0.3
    ))

    layout = go.Layout(
        title=f"{symbol} Technical Analysis",
        xaxis=dict(title="Date"),
        yaxis=dict(
            title="Price (USDT)",
            titlefont=dict(size=14),
            side="left"
        ),
        yaxis2=dict(
            title="Volume",
            overlaying="y",
            side="right"
        ),
        height=800
    )

    fig = go.Figure(data=traces, layout=layout)
    st.plotly_chart(fig, use_container_width=True)

def plot_price_evolution(df: pd.DataFrame, symbol: str):
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['close'],
        name="Closing Price",
        line=dict(color='blue')
    ))
    
    fig.update_layout(
        title=f"{symbol} Price Evolution",
        xaxis_title="Date",
        yaxis_title="Price (USDT)",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
