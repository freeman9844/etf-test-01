import pandas as pd
import io
import datetime
import logging
from typing import List, Tuple, Any
from src import database, fetcher, analytics

logger = logging.getLogger(__name__)

# Target Headers from Google Sheet
GS_HEADERS = ['Ticker', 'Name', 'Shares', 'AvgPrice', 'Yield', 'Months', 'Category', 'CurrentPrice']

def export_to_csv() -> str:
    """
    Exports current holdings to a CSV string matching the Google Sheet format.
    Format: Ticker, Name, Shares, AvgPrice, Yield, Months, Category, CurrentPrice
    """
    holdings = database.get_holdings()
    if not holdings:
        return ",".join(GS_HEADERS) + "\n"
    
    # Fetch latest market data for enrichment (Name, Yield, CurrentPrice)
    tickers = [h[1] for h in holdings]
    market_data = fetcher.get_market_data(tickers)
    
    # Calculate metrics to get clean data
    df_metrics = analytics.calculate_portfolio_metrics(holdings, market_data)
    
    # Prepare Export DataFrame
    export_rows = []
    for _, row in df_metrics.iterrows():
        # Mapping to GS_HEADERS
        export_rows.append({
            'Ticker': row['Ticker'],
            'Name': row.get('Name', row['Ticker']),
            'Shares': row['Shares'],
            'AvgPrice': row['Avg Cost'],
            'Yield': f"{row.get('Yield', 0) * 100:.2f}%", # Display as %
            'Months': "", # Placeholder for payment months if we had them easily
            'Category': row.get('Sector', 'Unknown'),
            'CurrentPrice': row.get('Current Price', row['Avg Cost'])
        })
    
    df_export = pd.DataFrame(export_rows, columns=GS_HEADERS)
    return df_export.to_csv(index=False)

def import_from_csv(csv_content: str) -> Tuple[bool, str]:
    """
    Imports holdings from a CSV string matching the Google Sheet format.
    Required columns: Ticker, Shares, AvgPrice
    """
    try:
        # Some Google Sheets CSVs might have multiple header rows or weird formatting
        # We assume standard CSV for now.
        df = pd.read_csv(io.StringIO(csv_content))
        
        # Mapping variations
        col_map = {
            'Ticker': 'ticker',
            'Shares': 'shares',
            'AvgPrice': 'avg_cost',
            'Category': 'sector'
        }
        
        # Check if minimal required columns exist (Ticker, Shares, AvgPrice)
        # Using case-insensitive check and fuzzy match
        actual_cols = df.columns.tolist()
        found_map = {}
        for target, internal in col_map.items():
            for actual in actual_cols:
                if target.lower() == actual.lower():
                    found_map[internal] = actual
                    break
        
        required_internal = ['ticker', 'shares', 'avg_cost']
        missing = [ri for ri in required_internal if ri not in found_map]
        
        if missing:
            return False, f"필수 컬럼이 누락되었습니다: {', '.join(missing)} (원래 헤더: {', '.join(GS_HEADERS)})"
            
        count = 0
        for _, row in df.iterrows():
            ticker = str(row[found_map['ticker']]).strip().upper()
            shares = float(row[found_map['shares']])
            avg_cost = float(row[found_map['avg_cost']])
            sector = str(row[found_map['sector']]) if 'sector' in found_map and pd.notna(row[found_map['sector']]) else None
            
            if ticker and not pd.isna(shares) and shares > 0:
                database.add_holding(ticker, shares, avg_cost, sector)
                count += 1
                
        return True, f"성공적으로 {count}개의 항목을 가져왔습니다."
        
    except Exception as e:
        logger.error(f"Error importing CSV: {e}")
        return False, f"오류 발생: {str(e)}"
