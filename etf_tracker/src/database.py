import sqlite3
import os
import logging
from typing import List, Optional, Tuple, Any
from contextlib import contextmanager

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
DB_PATH = os.path.join(DATA_DIR, 'portfolio.db')

@contextmanager
def get_db_connection():
    """
    Context manager for SQLite database connection.
    Ensures connection is closed properly even if errors occur.
    """
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()

def init_db() -> None:
    """Initializes the database table if it doesn't exist."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS holdings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticker TEXT UNIQUE NOT NULL,
                    shares REAL NOT NULL,
                    avg_cost REAL NOT NULL,
                    sector TEXT,
                    currency TEXT DEFAULT 'USD'
                )
            ''')
            conn.commit()
            logger.info(f"Database initialized successfully at {DB_PATH}")
    except sqlite3.Error as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

def add_holding(ticker: str, shares: float, avg_cost: float, sector: Optional[str] = None, currency: str = 'USD') -> None:
    """
    Adds a new holding or updates an existing one (Upsert).
    
    Args:
        ticker: ETF Ticker Symbol
        shares: Number of shares
        avg_cost: Average cost basis
        sector: Sector classification (optional)
        currency: Currency code (default USD)
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO holdings (ticker, shares, avg_cost, sector, currency)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(ticker) DO UPDATE SET
                    shares = excluded.shares,
                    avg_cost = excluded.avg_cost,
                    sector = excluded.sector
            ''', (ticker.upper(), shares, avg_cost, sector, currency))
            conn.commit()
            logger.info(f"Upserted holding: {ticker.upper()}")
    except sqlite3.Error as e:
        logger.error(f"Error adding holding {ticker}: {e}")
        raise

def get_holdings() -> List[Tuple[Any, ...]]:
    """Retrieves all holdings from the database."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM holdings')
            rows = cursor.fetchall()
            return rows
    except sqlite3.Error as e:
        logger.error(f"Error retrieving holdings: {e}")
        return []

def delete_holding(ticker: str) -> None:
    """Deletes a holding by ticker."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM holdings WHERE ticker = ?', (ticker.upper(),))
            conn.commit()
            logger.info(f"Deleted holding: {ticker.upper()}")
    except sqlite3.Error as e:
        logger.error(f"Error deleting holding {ticker}: {e}")
        raise

if __name__ == '__main__':
    init_db()
