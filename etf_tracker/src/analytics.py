import pandas as pd
import logging
from typing import List, Tuple, Any, Optional

# Configure Logger
logger = logging.getLogger(__name__)

def calculate_portfolio_metrics(holdings: List[Tuple[Any, ...]], market_data: pd.DataFrame) -> pd.DataFrame:
    """
    Combines holdings (DB) with market_data (yfinance) to calculate portfolio metrics.
    
    Args:
        holdings: List of tuples from database [(id, ticker, shares, avg_cost, sector, currency), ...]
        market_data: DataFrame with columns ['Ticker', 'Current Price', 'Yield', 'Sector', 'Name']
        
    Returns:
        DataFrame with calculated metrics (Market Value, Gains, etc.)
    """
    if not holdings:
        logger.info("No holdings provided for calculation.")
        return pd.DataFrame()
        
    # Convert DB tuples to DataFrame
    df = pd.DataFrame(holdings, columns=['ID', 'Ticker', 'Shares', 'Avg Cost', 'Category', 'Currency'])
    
    # Merge with market data
    if market_data.empty:
        logger.warning("Market data is empty. Using Avg Cost as Current Price.")
        df['Current Price'] = df['Avg Cost'] 
        df['Yield'] = 0.0
        df['Name'] = df['Ticker']
        df['Category_Live'] = 'Unknown'
    else:
        # Merge on Ticker
        df = df.merge(market_data, on='Ticker', how='left')
        
        # Fill missing values for tickers that failed to fetch
        df['Current Price'] = df['Current Price'].fillna(df['Avg Cost'])
        df['Yield'] = df['Yield'].fillna(0.0)
        df['Name'] = df['Name'].fillna(df['Ticker'])
        
    # Category Logic: 
    # Prioritize DB Category if it exists. yfinance sector is in 'Sector'.
    if 'Sector' in df.columns:
        df['Category'] = df['Category'].fillna('').replace('', None).fillna(df['Sector'])
    
    # Map to general categories if it's still yfinance raw sector
    sector_map = {
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
    
    df['Category'] = df['Category'].fillna('Unknown').replace('', 'Unknown')
    df['Category'] = df['Category'].apply(lambda x: sector_map.get(x, x))

    # Financial Calculations
    try:
        df['Market Value'] = df['Shares'] * df['Current Price']
        df['Cost Basis'] = df['Shares'] * df['Avg Cost']
        df['Total Gain ($)'] = df['Market Value'] - df['Cost Basis']
        
        # Safe Division for Percentage
        df['Total Gain (%)'] = df.apply(
            lambda row: (row['Total Gain ($)'] / row['Cost Basis'] * 100) if row['Cost Basis'] > 0 else 0.0, 
            axis=1
        )
        
        df['Est. Annual Income'] = df['Market Value'] * df['Yield']
        
        # Portfolio Weight
        total_value = df['Market Value'].sum()
        if total_value > 0:
            df['Weight (%)'] = (df['Market Value'] / total_value) * 100
        else:
            df['Weight (%)'] = 0.0
            
    except Exception as e:
        logger.error(f"Error during metric calculation: {e}")
        return pd.DataFrame()
        
    return df
