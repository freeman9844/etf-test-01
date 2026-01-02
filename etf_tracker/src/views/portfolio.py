import streamlit as st
import pandas as pd
from src import database, styles

def render():
    styles.apply_global_styles()
    
    st.title("ETF 등록 및 관리")
    
    # Input Form
    with st.form("add_etf_form"):
        col1, col2, col3 = st.columns(3)
        ticker_input = col1.text_input("티커 (예: SCHD)").upper().strip()
        shares = col2.number_input("수량", min_value=0.01, step=0.01)
        avg_cost = col3.number_input("평단가 ($)", min_value=0.01, step=0.01)
        
        st.markdown("💡 티커를 입력하고 추가 버튼을 누르면 카테고리가 **자동으로** 분석됩니다.")
        
        submitted = st.form_submit_button("추가 / 업데이트")
        if submitted and ticker_input and shares > 0:
            from src import fetcher
            
            # Fetch Category via API
            with st.spinner(f"{ticker_input} 정보 조회 중..."):
                market_data = fetcher.get_market_data([ticker_input])
                if not market_data.empty:
                    raw_sector = market_data.iloc[0].get('Sector', 'Unknown')
                    category = fetcher.map_sector_to_category(raw_sector)
                else:
                    category = "기타"
            
            database.add_holding(ticker_input, shares, avg_cost, category)
            st.success(f"저장되었습니다: {ticker_input} (카테고리: {category})")
            st.rerun()

    # Display Holdings
    st.subheader("보유 종목 현황")
    holdings = database.get_holdings()
    
    # ---------------------------------------------------------
    # Smart Sheet Sync Section (Mockup based)
    # ---------------------------------------------------------
    from src import utils
    import datetime
    
    st.markdown("### 스마트 시트 동기화")
    
    col_sync, col_guide = st.columns(2)
    
    with col_sync:
        st.markdown("""
            <div class="sync-card">
                <div class="sync-title">🔗 Smart Sync</div>
                <div class="sync-desc">구글 시트의 <b>URL 주소</b>를 전체 복사해 넣거나 <b>ID</b>를 입력하세요.</div>
        """, unsafe_allow_html=True)
        
        gs_url = st.text_input("URL/ID 입력", 
                              placeholder="https://docs.google.com/spreadsheets/d/...", 
                              label_visibility="collapsed")
        
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            if st.button("🔄 불러오기", use_container_width=True, type="primary"):
                if gs_url:
                    with st.spinner("구글 시트 데이터 동기화 중..."):
                        success, msg = utils.import_from_url(gs_url)
                        if success:
                            st.session_state['sync_status'] = "동기화 완료!"
                            st.rerun()
                        else:
                            st.error(msg)
                else:
                    st.warning("URL을 입력해주세요.")
                    
        with btn_col2:
            csv_data = utils.export_to_csv()
            st.download_button(
                label="📥 CSV 내보내기",
                data=csv_data,
                file_name=f"etf_portfolio_{datetime.date.today()}.csv",
                mime="text/csv",
                use_container_width=True
            )
            
        if 'sync_status' in st.session_state:
            st.markdown(f'<div class="status-badge">{st.session_state["sync_status"]}</div>', unsafe_allow_html=True)
            # We keep it visible, it will clear on next manual interaction or rerun if we wanted
            
        st.markdown('</div>', unsafe_allow_html=True) # Close sync-card

    with col_guide:
        st.markdown("""
            <div class="sync-card">
                <div class="sync-title">🎯 연동 설정 가이드</div>
                <div class="sync-desc">H열(8번째 열)에 실시간 시세 수식을 추가하면 수익률이 자동 계산됩니다.</div>
                <div class="guide-box">
                    Header: Ticker, Name, Shares, AvgPrice, Yield, Months, Category, CurrentPrice
                </div>
                <div style="font-size: 14px; color: #888;">
                    <ul style="margin-left: -20px;">
                        <li><b>백업 팁</b>: 내보낸 CSV 파일의 내용을 시트의 A열부터 붙여넣으면 데이터 백업이 완료됩니다.</li>
                        <li><b>H2 수식</b>: <code>=GOOGLEFINANCE(A2, "price")</code></li>
                        <li><b>공유 설정</b>: 파일 > 공유 > 웹에 게시 > <b>쉼표로 구분된 값(.csv)</b></li>
                    </ul>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # File Uploader as secondary option (Small)
    with st.expander("또는 CSV 파일 직접 업로드"):
        uploaded_file = st.file_uploader("CSV 파일 선택", type=["csv"])
        if uploaded_file is not None:
            content = uploaded_file.getvalue().decode("utf-8")
            if st.button("파일에서 가져오기"):
                success, msg = utils.import_from_csv(content)
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

    st.markdown("---")
    
    if holdings:
        df = pd.DataFrame(holdings, columns=['ID', 'Ticker', 'Shares', 'Avg Cost', 'Category', 'Currency'])
        display_df = df.rename(columns={
            'Ticker': '티커',
            'Shares': '수량',
            'Avg Cost': '평단가',
            'Category': '카테고리',
            'Currency': '통화'
        })
        st.dataframe(display_df, use_container_width=True)
        
        with st.expander("종목 삭제"):
            ticker_to_del = st.selectbox("삭제할 티커 선택", df['Ticker'].unique())
            if st.button("삭제"):
                database.delete_holding(ticker_to_del)
                st.warning(f"삭제되었습니다: {ticker_to_del}")
                st.rerun()
    else:
        st.info("등록된 종목이 없습니다. 위 양식을 통해 추가해주세요.")
