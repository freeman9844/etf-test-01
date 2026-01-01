import streamlit as st
from src import database

# Page Configuration
st.set_page_config(page_title="Global ETF Portfolio Tracker", layout="wide", page_icon="📈")

def main():
    # Initialize basic resources
    database.init_db()

    st.sidebar.title("메뉴")
    page = st.sidebar.radio("이동", ["대시보드", "ETF 등록/관리", "배당 캘린더"])

    if page == "대시보드":
        from src.views import dashboard
        dashboard.render()
    elif page == "ETF 등록/관리":
        from src.views import portfolio
        portfolio.render()
    elif page == "배당 캘린더":
        from src.views import calendar
        calendar.render()

if __name__ == "__main__":
    main()
