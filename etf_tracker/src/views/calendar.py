import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
from src import database, fetcher, styles

def predict_future_dividends(holdings):
    if not holdings:
        return pd.DataFrame()

    predictions = []
    
    with st.spinner("예상 배당금 계산 중..."):
        for h in holdings:
            ticker = h[1]
            shares = h[2]
            
            hist = fetcher.get_dividend_history(ticker)
            if hist.empty:
                continue
            
            today = datetime.datetime.now()
            last_year = today - datetime.timedelta(days=365)
            # Use 'Dividends' column. Fetcher ensures column names.
            if 'Date' not in hist.columns: 
                hist.reset_index(inplace=True)
            
            recent_payments = hist[hist['Date'] > last_year]
            count = len(recent_payments)
            
            frequency_months = 3 
            if count >= 8: frequency_months = 1 
            elif count <= 1: frequency_months = 12 
            elif count >= 3: frequency_months = 3 
            else: frequency_months = 6 
            
            if hist.empty: continue
            
            last_payment = hist.iloc[0]
            last_amt = last_payment['Dividends']
            last_date = last_payment['Date']
            
            next_date = last_date
            
            # Project ahead
            for _ in range(12 // frequency_months + 4): 
                next_date = next_date + pd.DateOffset(months=frequency_months)
                
                if next_date > today:
                    predictions.append({
                        'Ticker': ticker,
                        'Shares': shares,
                        'Pay Date': next_date,
                        'Amount Per Share': last_amt,
                        'Total Amount': last_amt * shares,
                        'Month': next_date.strftime('%Y-%m'),
                        'MonthName': next_date.strftime('%-m월') # e.g. 1월, 2월 (MacOS/Linux %-m might vary, safe fallback below)
                    })
                    
    df = pd.DataFrame(predictions)
    return df

def render():
    styles.apply_global_styles() # Apply CSS
    
    st.title("배당 캘린더")
    st.caption("새로운 ETF를 추가하고 정보를 관리하세요.")
    
    date_str = datetime.date.today().strftime('%Y/%m/%d')
    st.markdown(f"<div style='text-align: right; color: #888; margin-top: -50px;'>오늘 날짜<br><span style='font-size: 18px; color: #FFF;'>{date_str}</span></div>", unsafe_allow_html=True)
    st.markdown("---")

    holdings = database.get_holdings()
    if not holdings:
        st.info("보유 종목이 없습니다. 'ETF 등록' 탭에서 종목을 추가하세요.")
        return

    df_pred = predict_future_dividends(holdings)
    
    # Grid Layout
    st.subheader("🗓️ 월별 예상 배당금 (USD)")
    
    # Generate next 12 months list explicitly to show even empty months
    today = datetime.datetime.now()
    months_to_show = []
    for i in range(12):
        d = today + pd.DateOffset(months=i)
        m_key = d.strftime('%Y-%m')
        # Windows uses # to remove padding, Unix uses -. Let's just use int cast.
        m_label = f"{int(d.strftime('%m'))}월" 
        months_to_show.append({'key': m_key, 'label': m_label})

    # Rows of 3
    # Group by Month
    monthly_data = {}
    if not df_pred.empty:
        grouped = df_pred.groupby('Month')
        for m_key, group in grouped:
            total = group['Total Amount'].sum()
            # Get list of tickers
            tickers = ", ".join(group['Ticker'].unique())
            monthly_data[m_key] = {'total': total, 'tickers': tickers}
            
    # Display Grid
    # Iterate in chunks of 3
    for i in range(0, 12, 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < 12:
                m = months_to_show[i+j]
                m_key = m['key']
                m_label = m['label']
                
                data = monthly_data.get(m_key, {'total': 0.0, 'tickers': '배당 없음'})
                
                with cols[j]:
                    amount_str = f"${data['total']:,.2f}"
                    styles.render_calendar_card(m_label, amount_str, data['tickers'])
