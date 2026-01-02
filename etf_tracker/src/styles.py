import streamlit as st

def apply_global_styles():
    st.markdown("""
        <style>
        /* Global Background and Font adjustments if necessary, 
           but Streamlit theme handles most. We focus on components. */
        
        /* Card Container Styling */
        .stCard {
            background-color: #121212; /* Darker background for contrast if needed */
        }
        
        div.css-1r6slb0.e1tzin5v2 { /* Streamlit container adjustments */
            background-color: #1E1E1E;
            border: 1px solid #333;
            padding: 20px;
            border-radius: 10px;
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
        
        /* Calendar Card Styling */
        .calendar-card {
            background-color: #151515;
            border-radius: 12px;
            padding: 20px;
            border: 1px solid #2A2A2A;
            height: 180px; /* Fixed height for uniformity */
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            margin-bottom: 15px;
        }
        
        .cal-month {
            font-size: 18px;
            font-weight: bold;
            color: #E0E0E0;
        }
        
        .cal-amount {
            font-size: 24px;
            font-weight: bold;
            color: #FFA500; /* Orange/Gold Accent */
            text-align: right;
        }
        
        .cal-note {
            font-size: 13px;
            color: #666;
            margin-top: 5px;
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
        
        /* Text Colors */
        .positive { color: #00CC96; }
        .negative { color: #EF553B; }
        .neutral { color: #888; }
        
        </style>
    """, unsafe_allow_html=True)

def render_metric_card(label, value, delta=None, icon=None, color_class=""):
    delta_html = ""
    if delta:
        delta_html = f'<span class="metric-delta {color_class}">{delta}</span>'
    
    icon_span = f'<span>{icon}</span>' if icon else ""
    
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label} {icon_span}</div>
            <div class="metric-value">{value} {delta_html}</div>
        </div>
    """, unsafe_allow_html=True)

def render_calendar_card(month_name, amount_str, tickers_str):
    """
    Renders a calendar month card.
    """
    st.markdown(f"""
        <div class="calendar-card">
            <div class="cal-month">{month_name}</div>
            <div>
                <div class="cal-amount">{amount_str}</div>
                <div class="cal-note">{tickers_str}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
