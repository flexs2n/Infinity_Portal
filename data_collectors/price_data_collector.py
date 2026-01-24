import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from loguru import logger
import json


class PriceDataCollector:
    """
    Fetch and cache historical price data
    """
    
    def __init__(self, cache_dir: str = "data/historical"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True, parents=True)
    
    def fetch_data(
        self,
        ticker: str,
        years: int = 5,
        use_cache: bool = True
    ) -> Optional[pd.DataFrame]:
        """
        Fetch historical price data with caching
        
        Args:
            ticker: Stock symbol
            years: Years of history
            use_cache: Whether to use cached data
        
        Returns:
            DataFrame with OHLCV data
        """
        cache_file = self.cache_dir / f"{ticker}_{years}Y.csv"
        cache_meta = self.cache_dir / f"{ticker}_{years}Y_meta.json"
        
        # Check cache
        if use_cache and cache_file.exists():
            # Check if cache is fresh (< 24 hours old)
            if cache_meta.exists():
                with open(cache_meta, 'r') as f:
                    meta = json.load(f)
                    cache_time = datetime.fromisoformat(meta['cached_at'])
                    
                    if (datetime.now() - cache_time).total_seconds() < 86400:
                        logger.info(f"📦 Using cached data for {ticker}")
                        return pd.read_csv(cache_file, index_col=0, parse_dates=True)
        
        # Fetch fresh data
        logger.info(f"📥 Fetching fresh data for {ticker}...")
        
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=years*365)
            
            data = yf.download(
                ticker,
                start=start_date,
                end=end_date,
                progress=False
            )
            
            if data.empty:
                logger.error(f"No data for {ticker}")
                return None
            
            # Save to cache
            data.to_csv(cache_file)
            
            with open(cache_meta, 'w') as f:
                json.dump({
                    'ticker': ticker,
                    'years': years,
                    'cached_at': datetime.now().isoformat(),
                    'rows': len(data)
                }, f)
            
            logger.info(f"✅ Fetched {len(data)} days of data")
            
            return data
            
        except Exception as e:
            logger.error(f"Error fetching data: {e}")
            return None
    
    def get_latest_price(self, ticker: str) -> Optional[float]:
        """Get current price"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            return info.get('currentPrice') or info.get('regularMarketPrice')
        except:
            return None