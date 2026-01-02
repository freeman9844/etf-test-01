import streamlit as st
import pandas as pd
import datetime
import plotly.express as px
from src import database, fetcher, styles

def predict_future_dividends(holdings):
    if not holdings:
        return pd.DataFrame()

    predictions = []
    today = datetime.datetime.now()
    
    with st.spinner("예상 배당금 계산 중..."):
        for h in holdings:
            ticker = h[1]
            shares = h[2]
            
            hist = fetcher.get_dividend_history(ticker)
            if hist.empty:
                continue
            
            # Ensure 'Date' index is handled
            if 'Date' not in hist.columns: 
                hist.reset_index(inplace=True)
            
            # 1. Identify valid payment months from the last ~18 months
            # This handles irregular schedules better than fixed frequency
            lookback_date = today - datetime.timedelta(days=365 + 180)
            recent_hist = hist[hist['Date'] > lookback_date]
            
            if recent_hist.empty:
                # Fallback to the very last payment if no recent ones (unlikely but safe)
                payment_months = {hist.iloc[0]['Date'].month}
                latest_amt = hist.iloc[0]['Dividends']
            else:
                payment_months = set(recent_hist['Date'].dt.month.unique())
                latest_amt = recent_hist.iloc[0]['Dividends']
            
            # 2. Project for the next 12 months
            # If the month is in payment_months, we add it.
            for i in range(1, 13):
                future_date = today + pd.DateOffset(months=i)
                f_month = future_date.month
                
                if f_month in payment_months:
                    predictions.append({
                        'Ticker': ticker,
                        'Shares': shares,
                        'Pay Date': future_date, # Approximation of date
                        'Amount Per Share': latest_amt,
                        'Total Amount': latest_amt * shares,
                        'Month': future_date.strftime('%Y-%m'),
                        'MonthName': f"{f_month}월"
                    })
                    
    df = pd.DataFrame(predictions)
    return df

def render():
    styles.apply_global_styles() # Apply CSS
    
    holdings = database.get_holdings()
    if not holdings:
        st.info("보유 종목이 없습니다. 'ETF 등록' 탭에서 종목을 추가하세요.")
        return

    df_pred = predict_future_dividends(holdings)
    
    # ---------------------------------------------------------
    # Validation Logic
    # ---------------------------------------------------------
    from src import analytics
    # Fetch market data for accurate annual yield calculation
    tickers = [h[1] for h in holdings]
    market_data = fetcher.get_market_data(tickers)
    df_metrics = analytics.calculate_portfolio_metrics(holdings, market_data)
    
    annual_total = df_metrics['Est. Annual Income'].sum() if 'Est. Annual Income' in df_metrics.columns else 0.0
    calendar_total = df_pred['Total Amount'].sum() if not df_pred.empty else 0.0
    
    st.markdown("# 월별 배당 캘린더")
    styles.render_validation_card(annual_total, calendar_total)
    
    # ---------------------------------------------------------
    # Premium Grid Layout
    # ---------------------------------------------------------
    # Generate next 12 months list explicitly to show even empty months
    today = datetime.datetime.now()
    months_to_show = []
    for i in range(12):
        d = today + pd.DateOffset(months=i)
        m_key = d.strftime('%Y-%m')
        m_label = f"{int(d.strftime('%m'))}월" 
        months_to_show.append({'key': m_key, 'label': m_label})

    # Group by Month
    monthly_data = {}
    if not df_pred.empty:
        grouped = df_pred.groupby('Month')
        for m_key, group in grouped:
            total = group['Total Amount'].sum()
            # Prepare list of dicts for the new card style
            # Sort by amount descending
            items = []
            for _, row in group.sort_values(by='Total Amount', ascending=False).iterrows():
                items.append({
                    'ticker': row['Ticker'],
                    'amount': f"${row['Total Amount']:,.2f}"
                })
            monthly_data[m_key] = {'total': total, 'items': items}
            
    # Display Grid (Chunks of 4 to match mockup if possible, or 3 for standard layout)
    # The mockup shows 4 columns.
    for i in range(0, 12, 4):
        cols = st.columns(4)
        for j in range(4):
            idx = i + j
            if idx < 12:
                m = months_to_show[idx]
                m_key = m['key']
                m_label = m['label']
                
                data = monthly_data.get(m_key, {'total': 0.0, 'items': []})
                
                with cols[j]:
                    # Format amount with &dollar; to avoid Streamlit LaTeX issues
                    amount_str = f"&dollar;{data['total']:,.2f}"
                    styles.render_calendar_card(m_label, amount_str, data['items'])
