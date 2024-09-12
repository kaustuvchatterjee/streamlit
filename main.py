import algotrade
import yfinance as yf
import streamlit as st
from datetime import datetime as dt
import time
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly

st.cache_data.clear()
st.set_page_config(
      page_title='Algo Trade',
      page_icon=":material/waterfall_chart:",
      layout="wide",
      )
st.markdown("""
        <style>
               .block-container {
                    padding-top: 1rem;
                    padding-bottom: 0rem;
                    padding-left: 5rem;
                    padding-right: 5rem;
                }
        </style>
        """, unsafe_allow_html=True)

#----------------INPUTS-----------------------------------
tickers, ticker_names = algotrade.get_tickers('tickers.csv')
st.sidebar.title('Parameters')
with st.sidebar:
    st.session_state.ticker_name = st.selectbox(label='Ticker', options=ticker_names, )
    # st.session_state.index = st.session_state.ticker_names.index(ticker_name)
    duration = st.number_input(label='Duration (days)', min_value=30, max_value=730, value=180, step=30)

#---------------FETCH DATA----------------------------------
ticker = tickers[ticker_names.index(st.session_state.ticker_name)]

# Historical Data
data, live_data, last_updated, hist_status = algotrade.get_ticker_data(ticker, duration)
if hist_status == 1:
    data = algotrade.get_macd(data)
    pchange = 100*(data.iloc[-1]['Close'] - data.iloc[-2]['Close'])/data.iloc[-2]['Close']
#-------------------PLOT------------------------------------
# traces
ub_plot = go.Scatter(
    x = data['Date'],
    y = data['upper_bound'],
    mode = 'lines',
    line = dict(color='lightblue', width=0),
    name = 'Upper Bound'
)

lb_plot = go.Scatter(
    x = data['Date'],
    y = data['lower_bound'],
    mode = 'lines',
    line = dict(color='lightblue', width=0),
    fill = 'tonexty',
    fillcolor = 'rgba(31, 119, 180, 0.1)',
    name = 'Lower Bound'
)

sma_plot = go.Scatter(
    x = data['Date'],
    y = data['sma'],
    mode = 'lines',
    line = dict(color='#1f77b4', width=1),
    name = 'SMA'
)

close_plot = go.Scatter(
    x = data['Date'],
    y = data['Close'],
    mode = 'lines',
    line = dict(color='lightgray', width=1),
    name = 'Close'
)

candle_stick = go.Candlestick(
    x = data['Date'],
    open = data['Open'],
    close = data['Close'],
    high = data['High'],
    low = data['Low'],
    name = 'Candlestick'
)

rsi_plot = go.Scatter(
    x = data['Date'],
    y = data['rsi'],
    mode = 'lines',
    line = dict(color='red', width=2),
    name = 'RSI'
)

macd_plot = go.Bar(
    x= data['Date'],
    y = data['MACD_Histo'],
    marker_color = data['Color'],
    name='MACD'
)

# Figure
fig = make_subplots(rows=3, cols=1, row_heights=[0.6,0.2,0.2], vertical_spacing=0, shared_xaxes=True)
plot1 = [ub_plot, lb_plot, sma_plot, close_plot, candle_stick]
plot2 = [rsi_plot]
plot3 = [macd_plot]


#subplot1
fig.add_traces(plot1, rows=1, cols=1)
fig.add_annotation(
      x=0,
      y=1,
      text = f"{st.session_state.ticker_name}",
      font=dict(size=20),
      showarrow=False,
      xanchor = 'left',
      yanchor = 'bottom',
      xref='x domain',
      yref='y domain',
      row = 1,
      col = 1,
)

if pchange>=0:
      fig.add_hline(y=data.iloc[-2]['Close'], line_color='black', line_width=0.3)
      fig.add_annotation(
            x=data.iloc[-1]['Date'],
            y=data.iloc[-2]['Close'],
            text=f"{data.iloc[-2]['Close']:.2f}",
            showarrow=False,
            xanchor="left",
            yanchor='top'
            )      
      fig.add_hline(y=data.iloc[-1]['Close'], line_color='green', line_width=0.3)
      fig.add_annotation(
            x=data.iloc[-1]['Date'],
            y=data.iloc[-1]['Close'],
            text=f"{data.iloc[-1]['Close']:.2f}",
            font=dict(color="green"),
            showarrow=False,
            xanchor="left",
            yanchor='bottom'
            )
else:
      fig.add_hline(y=data.iloc[-2]['Close'], line_color='black', line_width=0.3)
      fig.add_annotation(
            x=data.iloc[-1]['Date'],
            y=data.iloc[-2]['Close'],
            text=f"{data.iloc[-2]['Close']:.2f}",
            showarrow=False,
            xanchor="left",
            yanchor='bottom'
            )      
      fig.add_hline(y=data.iloc[-1]['Close'], line_color='red', line_width=0.3)
      fig.add_annotation(
            x=data.iloc[-1]['Date'],
            y=data.iloc[-1]['Close'],
            text=f"{data.iloc[-1]['Close']:.2f}",
            font=dict(color="red"),
            showarrow=False,
            xanchor="left",
            yanchor='top'
            )
for i in range(len(data)):
            if (data.iloc[i]['z_cross'] == 1) | (data.iloc[i]['z_cross'] == -1):
                fig.add_vline(data.iloc[i]['Date'], line_color='lightgray', line_width=0.3)
for i in range(len(data)):
            if data.iloc[i]['trade_signal'] == 1:
                fig.add_vline(data.iloc[i]['Date'], line_color='red', line_width=0.8)
            if data.iloc[i]['trade_signal'] == -1:
                fig.add_vline(data.iloc[i]['Date'], line_color='green', line_width=0.8)

#subplot2
fig.add_traces(plot2, rows=2, cols=1)
fig.add_hline(y=70, line_color='red', line_dash='dash', row=2, col=1)
fig.add_hline(y=30, line_color='teal', line_dash='dash', row=2, col=1)
fig.add_annotation(
      x=0,
      y=1,
      text = "RSI",
      font=dict(size=20),
      showarrow=False,
      xanchor = 'left',
      xref='x domain',
      yref='y domain',
      row = 2,
      col = 1,
)
for i in range(len(data)):
            if (data.iloc[i]['z_cross'] == 1) | (data.iloc[i]['z_cross'] == -1):
                fig.add_vline(data.iloc[i]['Date'], line_color='lightgray', line_width=0.3)
for i in range(len(data)):
            if data.iloc[i]['trade_signal'] == 1:
                fig.add_vline(data.iloc[i]['Date'], line_color='red', line_width=0.8)
            if data.iloc[i]['trade_signal'] == -1:
                fig.add_vline(data.iloc[i]['Date'], line_color='green', line_width=0.8)
#subplot3
fig.add_traces(plot3, rows=3, cols=1)
fig.add_annotation(
      x=0,
      y=1,
      text = "MACD",
      font=dict(size=20),
      showarrow=False,
      xanchor = 'left',
      xref='x domain',
      yref='y domain',
      row = 3,
      col = 1,
)
for i in range(len(data)):
            if (data.iloc[i]['z_cross'] == 1) | (data.iloc[i]['z_cross'] == -1):
                fig.add_vline(data.iloc[i]['Date'], line_color='lightgray', line_width=0.3)
for i in range(len(data)):
            if data.iloc[i]['trade_signal'] == 1:
                fig.add_vline(data.iloc[i]['Date'], line_color='red', line_width=0.8)
            if data.iloc[i]['trade_signal'] == -1:
                fig.add_vline(data.iloc[i]['Date'], line_color='green', line_width=0.8)


# Figure Layout
layout = {
    "height": 600,
    "showlegend": False,
    "xaxis": {"rangeslider": {"visible": False}},
    "yaxis2": {"range": [0,100]},
    "yaxis3": {"showticklabels": False},
}
fig.update_layout(layout)

fig2 = go.Figure()
today_plot = go.Candlestick(
      x=live_data['Datetime'],
      open=live_data['Open'],
      close=live_data['Close'],
      high=live_data['High'],
      low=live_data['Low']
)

fig2.add_trace(today_plot)

layout = {
    "height": 600,
    "showlegend": False,
    "xaxis": {"rangeslider": {"visible": False}},
}
fig2.update_layout(layout)
#----------------PAGE----------------------------
st.title(f"{st.session_state.ticker_name}")
cols = st.columns([0.5,0.2,0.3])
st.markdown("""
            <style>
            .big-font-green {
            font-size:36px !important;
            color:green;
            }
            .big-font-red{
            font-size:36px !important;
            color:red;
            }
            </style>
            """, unsafe_allow_html=True)

with cols[0]:
    if pchange>0:          
        st.markdown(f'<p class="big-font-green"><b>{data.iloc[-1]['Close']:.2f} <span>&uarr;</span></b> ({pchange:.2f}%)</p>', unsafe_allow_html=True)
    else:
        st.markdown(f'<p class="big-font-red"><b>{data.iloc[-1]['Close']:.2f} <span>&darr;</span></b> ({pchange:.2f}%)</p>', unsafe_allow_html=True)
    
with cols[1]:
    st.markdown(f"**Prev Close**: {data.iloc[-2]['Close']:.2f}<br> \
                **High**: {data.iloc[-1]['High']:.2f}<br> \
                **Open**: {data.iloc[-1]['Open']:.2f}<br> \
                **Low**: {data.iloc[-1]['Low']:.2f}", unsafe_allow_html=True)
with cols[2]:
    st.markdown(f"*Updated on {last_updated}*", unsafe_allow_html=True)
    refresh = st.button('Refresh')

tab1, tab2 = st.tabs(['Historical', 'Current'])

with tab1:
    st.plotly_chart(fig)

with tab2:
      st.plotly_chart(fig2)


if refresh:
      st.rerun()