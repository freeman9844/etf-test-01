import yfinance as yf
import pandas as pd
import streamlit as st
import logging
from typing import List, Optional, Any

# Configure Logger
logger = logging.getLogger(__name__)

SECTOR_MAP = {
    'Technology': '기술',
    'Healthcare': '헬스케어',
    'Financial Services': '금융',
    'Consumer Cyclical': '소비재(임의)',
    'Consumer Defensive': '소비재(필수)',
    'Communication Services': '통신',
    'Industrials': '산업재',
    'Energy': '에너지',
    'Utilities': '유틸리티',
    'Real Estate': '부동산',
    'Basic Materials': '기초소재'
}

def map_sector_to_category(sector: str) -> str:
    """Maps a raw yfinance sector to a Korean category."""
    if not sector or sector == 'Unknown':
        return '기타'
    return SECTOR_MAP.get(sector, sector)

@st.cache_data(ttl=900)
def get_market_data(tickers: List[str]) -> pd.DataFrame:
    """
    Fetches real-time market data for a list of tickers using yfinance.
    
    Args:
        tickers: List of ticker symbols (e.g. ['SCHD', 'JEPI'])
        
    Returns:
        DataFrame containing market data. Returns empty DataFrame on failure.
    """
    if not tickers:
        return pd.DataFrame()
    
    unique_tickers = list(set([t.upper() for t in tickers]))
    results = []
    
    logger.info(f"Fetching market data for: {unique_tickers}")

    for t_symbol in unique_tickers:
        try:
            t = yf.Ticker(t_symbol)
            # Fetch info (network call)
            info = t.info
            
            # Defensive coding for missing keys
            price = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('previousClose') or 0.0
            # Yield Handling
            # yfinance 'dividendYield' is usually Percentage (e.g. 3.74 for 3.74%)
            # 'trailingAnnualDividendYield' is usually Decimal (e.g. 0.0374)
            div_yield = info.get('dividendYield')
            
            if div_yield is not None:
                # Assume if it's from 'dividendYield', it's a percentage. 
                # Normalize to decimal for consistency
                div_yield = div_yield / 100.0
            else:
                # Fallback
                div_yield = info.get('trailingAnnualDividendYield', 0)
                # trailingAnnualDividendYield is already decimal usually.
                if div_yield is None: div_yield = 0

            sector = info.get('sector', 'Unknown')
            name = info.get('shortName', t_symbol)
            
            results.append({
                'Ticker': t_symbol,
                'Current Price': float(price),
                'Yield': float(div_yield),
                'Sector': str(sector),
                'Name': str(name)
            })
        except Exception as e:
            logger.error(f"Failed to fetch data for {t_symbol}: {e}")
            # Continue to next ticker even if one fails
            continue
            
    return pd.DataFrame(results)

@st.cache_data(ttl=86400)
def get_dividend_history(ticker: str) -> pd.DataFrame:
    """
    Fetches historical dividend data for a single ticker.
    
    Args:
        ticker: Ticker symbol
        
    Returns:
        DataFrame with 'Date' and 'Dividends' columns, sorted by Date descending.
    """
    try:
        t = yf.Ticker(ticker)
        hist = t.dividends
        
        if hist is None or hist.empty:
            logger.warning(f"No dividend history found for {ticker}")
            return pd.DataFrame(columns=['Date', 'Dividends'])

        df = pd.DataFrame(hist)
        df.reset_index(inplace=True)
        
        # Standardize columns
        df.columns = ['Date', 'Dividends']
        df['Date'] = pd.to_datetime(df['Date']).dt.tz_localize(None)
        
        return df.sort_values(by='Date', ascending=False)
        
    except Exception as e:
        logger.error(f"Error fetching dividends for {ticker}: {e}")
        return pd.DataFrame(columns=['Date', 'Dividends'])
