import streamlit as st
import datetime
import plotly.express as px
from src import database, fetcher, analytics, styles

def render():
    styles.apply_global_styles() # Use shared styles
    
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("포트폴리오 대시보드")
        st.caption("자산 현황과 수익률을 실시간으로 확인하세요.")
    with col2:
        st.markdown(f"<div style='text-align: right; color: #888;'>오늘 날짜<br><span style='font-size: 18px; color: #FFF;'>{datetime.date.today().strftime('%Y-%m-%d')}</span></div>", unsafe_allow_html=True)
    
    st.markdown("---")

    # 1. Load Data
    holdings = database.get_holdings()
    
    # Default values
    total_value = 0.0
    total_cost = 0.0
    total_gain = 0.0
    total_gain_pct = 0.0
    annual_income = 0.0
    
    df = analytics.calculate_portfolio_metrics(holdings, fetcher.get_market_data([h[1] for h in holdings])) if holdings else None
    
    if df is not None and not df.empty:
        total_value = df['Market Value'].sum()
        total_cost = df['Cost Basis'].sum()
        total_gain = total_value - total_cost
        total_gain_pct = (total_gain / total_cost * 100) if total_cost > 0 else 0.0
        annual_income = df['Est. Annual Income'].sum()

    # 2. Metrics Cards
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        styles.render_metric_card("총 투자금", f"${total_cost:,.0f}", icon="💲")
    with c2:
        delta_color = "positive" if total_gain >= 0 else "negative"
        styles.render_metric_card("평가 금액", f"${total_value:,.0f}", "↗" if total_gain >=0 else "↘", icon="📈", color_class=delta_color)
    with c3:
        delta_color = "positive" if total_gain_pct >= 0 else "negative"
        styles.render_metric_card("수익률", f"{total_gain_pct:.2f}%", icon="①", color_class=delta_color)
    with c4:
        styles.render_metric_card("연 예상 배당금", f"${annual_income:,.0f}", icon="🕒", color_class="positive")

    st.markdown("###")

    # 3. List Section
    st.subheader("보유 종목 리스트")
    
    if df is not None and not df.empty:
        display_df = df.copy()
        
        display_df = display_df.rename(columns={
            'Ticker': 'TICKER',
            'Category': '카테고리',
            'Shares': '수량',
            'Avg Cost': '평단가',
            'Current Price': '현재가',
            'Total Gain (%)': '수익률',
            'Yield': '배당률',
            'Market Value': '평가액'
        })
        
        # Format
        display_df['평단가'] = display_df['평단가'].apply(lambda x: f"${x:,.2f}")
        display_df['현재가'] = display_df['현재가'].apply(lambda x: f"${x:,.2f}")
        display_df['평가액'] = display_df['평가액'].apply(lambda x: f"${x:,.2f}")
        display_df['수익률'] = display_df['수익률'].apply(lambda x: f"{x:.2f}%")
        display_df['배당률'] = display_df['배당률'].apply(lambda x: f"{x * 100:.2f}%")
        
        cols = ['TICKER', '카테고리', '수량', '평단가', '현재가', '수익률', '배당률', '평가액']
        st.dataframe(display_df[cols], use_container_width=True, hide_index=True)
    else:
        st.info("등록된 ETF가 없습니다. 'ETF 등록' 탭에서 종목을 추가하세요.")
