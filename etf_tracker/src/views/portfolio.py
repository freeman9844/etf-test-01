import streamlit as st
import pandas as pd
from src import database, styles

def render():
    styles.apply_global_styles()
    
    st.title("ETF 등록 및 관리")
    
    # Input Form
    with st.form("add_etf_form"):
        col1, col2, col3, col4 = st.columns(4)
        ticker = col1.text_input("티커 (예: SCHD)")
        shares = col2.number_input("수량", min_value=0.01, step=0.01)
        avg_cost = col3.number_input("평단가 ($)", min_value=0.01, step=0.01)
        
        # General Categories
        categories = ["기술", "배당", "성장", "지수", "채권", "부동산", "에너지", "기타"]
        category = col4.selectbox("카테고리", categories)
        
        submitted = st.form_submit_button("추가 / 업데이트")
        if submitted and ticker and shares > 0:
            database.add_holding(ticker, shares, avg_cost, category)
            st.success(f"저장되었습니다: {ticker.upper()} ({category})")
            st.rerun()

    # Display Holdings
    st.subheader("보유 종목 현황")
    holdings = database.get_holdings()
    
    # Export/Import Actions
    col_exp, col_imp = st.columns(2)
    
    with col_exp:
        from src import utils
        csv_data = utils.export_to_csv()
        st.download_button(
            label="📈 Google Sheets로 내보내기 (CSV)",
            data=csv_data,
            file_name="etf_portfolio_export.csv",
            mime="text/csv"
        )
        
    with col_imp:
        uploaded_file = st.file_uploader("📥 Google Sheets에서 가져오기 (CSV)", type=["csv"])
        if uploaded_file is not None:
            content = uploaded_file.getvalue().decode("utf-8")
            if st.button("데이터 동기화 (가져오기)"):
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
