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
                    
                    # Selection Button
                    if st.button(f"{m_label} 상세", key=f"btn_{m_key}"):
                        st.session_state['selected_month'] = m_key
                        st.session_state['selected_month_label'] = m_label

    # Detailed Breakdown Section
    if 'selected_month' in st.session_state:
        m_key = st.session_state['selected_month']
        m_label = st.session_state['selected_month_label']
        
        st.markdown("---")
        st.subheader(f"📊 {m_label} 배당 상세 내역 ({m_key})")
        
        if not df_pred.empty:
            month_details = df_pred[df_pred['Month'] == m_key].copy()
            
            if not month_details.empty:
                # Rename for UI
                display_details = month_details.rename(columns={
                    'Ticker': '티커',
                    'Pay Date': '지급 예정일',
                    'Amount Per Share': '주당 배당금',
                    'Total Amount': '총 배당금',
                    'Shares': '보유 수량'
                })
                
                # Format
                display_details['지급 예정일'] = display_details['지급 예정일'].dt.strftime('%Y-%m-%d')
                display_details['주당 배당금'] = display_details['주당 배당금'].apply(lambda x: f"${x:,.2f}")
                display_details['총 배당금'] = display_details['총 배당금'].apply(lambda x: f"${x:,.2f}")
                
                cols_to_show = ['지급 예정일', '티커', '보유 수량', '주당 배당금', '총 배당금']
                st.dataframe(display_details[cols_to_show], use_container_width=True, hide_index=True)
            else:
                st.write("해당 월에는 예정된 배당금이 없습니다.")
        else:
            st.write("데이터를 불러올 수 없습니다.")
        
        if st.button("상세 내역 닫기"):
            del st.session_state['selected_month']
            st.rerun()
