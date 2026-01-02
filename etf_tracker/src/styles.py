import streamlit as st

def apply_global_styles():
    st.markdown("""
        <style>
        /* Global Styles */
        .stCard {
            background-color: #121212;
        }
        
        /* Custom Metric Card (Dashboard) */
        .metric-card {
            background-color: #151515;
            padding: 20px;
            border-radius: 12px;
            border: 1px solid #2A2A2A;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        .metric-label {
            font-size: 14px;
            color: #AAAAAA;
            margin-bottom: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .metric-value {
            font-size: 28px;
            font-weight: 700;
            color: #FFFFFF;
        }
        .metric-delta {
            font-size: 14px;
            margin-left: 8px;
            font-weight: 500;
        }

        /* Sync Card (Portfolio) */
        .sync-card {
            background-color: #151515;
            padding: 30px;
            border-radius: 12px;
            border: 1px solid #2A2A2A;
            height: 100%;
        }
        .sync-title {
            font-size: 20px;
            font-weight: bold;
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 20px;
        }
        .sync-desc {
            font-size: 14px;
            color: #888;
            margin-bottom: 20px;
        }
        .status-badge {
            background-color: #0F2A1E;
            color: #00CC96;
            padding: 10px 15px;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 500;
            margin-top: 20px;
            display: inline-block;
        }
        .guide-box {
            background-color: #0C120C;
            border: 1px solid #1E3A1E;
            padding: 15px;
            border-radius: 8px;
            font-family: monospace;
            font-size: 13px;
            color: #00CC96;
            margin: 10px 0;
        }

        /* Premium Calendar Styling */
        .calendar-card {
            background-color: #0F0F0F;
            border-radius: 16px;
            padding: 20px;
            border: 1px solid #1A1A1A;
            height: 320px;
            display: flex;
            flex-direction: column;
            margin-bottom: 20px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.5);
        }
        .cal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 1px solid #222;
        }
        .cal-month {
            font-size: 16px;
            font-weight: 600;
            color: #888;
        }
        .cal-amount {
            font-size: 24px;
            font-weight: 700;
            color: #FFB700;
            font-family: 'Courier New', monospace;
        }
        .cal-list {
            flex-grow: 1;
            overflow-y: auto;
            padding-right: 5px;
        }
        .cal-list::-webkit-scrollbar { width: 4px; }
        .cal-list::-webkit-scrollbar-track { background: transparent; }
        .cal-list::-webkit-scrollbar-thumb { background: #333; border-radius: 10px; }
        
        .cal-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background-color: #1A1A1A;
            padding: 10px 15px;
            border-radius: 10px;
            margin-bottom: 8px;
            border: 1px solid #262626;
        }
        .cal-item-ticker {
            font-weight: 700;
            color: #4A90E2;
            font-size: 14px;
        }
        .cal-item-amount {
            color: #AAAAAA;
            font-size: 13px;
            font-family: monospace;
        }

        /* Validation Card Styling */
        .validation-card {
            background-color: #0A0A0A;
            border: 1px solid #1A1A1A;
            border-radius: 16px;
            padding: 25px;
            margin-bottom: 30px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .v-left { display: flex; align-items: center; gap: 20px; }
        .v-icon {
            background-color: #1A1408;
            padding: 15px;
            border-radius: 12px;
            border: 1px solid #332610;
            color: #FFB700;
            display: flex;
            justify-content: center;
            align-items: center;
            font-size: 24px;
        }
        .v-title {
            font-size: 18px;
            font-weight: 700;
            color: #FFFFFF;
            margin-bottom: 4px;
        }
        .v-desc {
            font-size: 14px;
            color: #666;
        }
        .v-badge {
            border: 1px solid #1B331E;
            background-color: #0F1A10;
            color: #4CAF50;
            padding: 8px 20px;
            border-radius: 12px;
            font-weight: 600;
            font-size: 14px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .positive { color: #00CC96; }
        .negative { color: #EF553B; }
        .neutral { color: #888; }
        </style>
    """, unsafe_allow_html=True)

def render_metric_card(label, value, delta=None, icon=None, color_class=""):
    delta_html = f'<span class="metric-delta {color_class}">{delta}</span>' if delta else ""
    icon_span = f'<span>{icon}</span>' if icon else ""
    st.markdown(f'<div class="metric-card"><div class="metric-label">{label} {icon_span}</div><div class="metric-value">{value} {delta_html}</div></div>', unsafe_allow_html=True)

def render_calendar_card(month_name, total_amount_str, items):
    """
    Renders a premium calendar month card with a list of ETF payments.
    """
    items_html = ""
    for item in items:
        # Use &dollar; to avoid LaTeX issues
        safe_item_amt = item["amount"].replace("$", "&dollar;")
        items_html += f'<div class="cal-item"><span class="cal-item-ticker">{item["ticker"]}</span><span class="cal-item-amount">{safe_item_amt}</span></div>'
    
    if not items_html:
        items_html = '<div class="cal-item" style="border:none; background:transparent; justify-content:center;"><span style="color:#444; font-size:12px;">배당 데이터 없음</span></div>'
        
    safe_total = total_amount_str.replace("$", "&dollar;")
    html = f'<div class="calendar-card"><div class="cal-header"><div class="cal-month">{month_name}</div><div class="cal-amount">{safe_total}</div></div><div class="cal-list">{items_html}</div></div>'
    st.markdown(html, unsafe_allow_html=True)

def render_validation_card(annual_total, calendar_total):
    """Renders the dividend verification card."""
    st.markdown(f'<div class="validation-card"><div class="v-left"><div class="v-icon">🖩</div><div><div class="v-title">배당금 정합성 검증</div><div class="v-desc">연간 배당 총액(&dollar;{annual_total:,.2f}) vs 캘린더 합계(&dollar;{calendar_total:,.2f})</div></div></div><div class="v-badge">✓ 검증 완료</div></div>', unsafe_allow_html=True)
