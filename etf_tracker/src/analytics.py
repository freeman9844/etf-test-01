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
    df = pd.DataFrame(holdings, columns=['ID', 'Ticker', 'Shares', 'Avg Cost', 'Sector', 'Currency'])
    
    # Merge with market data
    if market_data.empty:
        logger.warning("Market data is empty. Using Avg Cost as Current Price.")
        df['Current Price'] = df['Avg Cost'] 
        df['Yield'] = 0.0
        df['Name'] = df['Ticker']
        df['Sector_Live'] = 'Unknown'
    else:
        # Merge on Ticker
        df = df.merge(market_data, on='Ticker', how='left')
        
        # Fill missing values for tickers that failed to fetch
        df['Current Price'] = df['Current Price'].fillna(df['Avg Cost'])
        df['Yield'] = df['Yield'].fillna(0.0)
        df['Name'] = df['Name'].fillna(df['Ticker'])
        
    # Sector Logic: 
    # Prioritize DB Sector (from df['Sector']) if it exists and is not empty.
    # market_data also has 'Sector'.
    if 'Sector_y' in df.columns:
        # Preferred logic when merge creates suffixes
        df['Sector'] = df['Sector_x'].fillna('').replace('', None).fillna(df['Sector_y'])
    elif 'Sector' not in df.columns and 'Sector_y' not in df.columns:
        # Fallback if somehow Sector is missing
        df['Sector'] = 'Unknown'
    
    # Final cleanup
    df['Sector'] = df['Sector'].fillna('Unknown').replace('', 'Unknown')

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
