# infinity_portal/exchange_monitor.py (NEW FILE)

import asyncio
import aiohttp
from typing import Dict, List
from datetime import datetime
from loguru import logger

class ExchangeMonitor:
    """
    Monitors price feeds from multiple exchanges
    Calculates trust scores and detects anomalies
    """
    
    def __init__(self):
        self.exchanges = {
            'binance': 'https://api.binance.com/api/v3/ticker/price',
            'coinbase': 'https://api.coinbase.com/v2/prices',
            'kraken': 'https://api.kraken.com/0/public/Ticker'
        }
        self.trust_scores = {
            'binance': 0.85,
            'coinbase': 0.85,
            'kraken': 0.85
        }
        self.last_update_times = {}
        self.price_history = {}
    
    async def fetch_price(
        self, 
        exchange: str, 
        symbol: str
    ) -> Dict:
        """Fetch price from specific exchange"""
        try:
            async with aiohttp.ClientSession() as session:
                if exchange == 'binance':
                    url = f"{self.exchanges[exchange]}?symbol={symbol}USDT"
                    async with session.get(url) as response:
                        data = await response.json()
                        price = float(data['price'])
                        
                elif exchange == 'coinbase':
                    url = f"{self.exchanges[exchange]}/{symbol}-USD/spot"
                    async with session.get(url) as response:
                        data = await response.json()
                        price = float(data['data']['amount'])
                        
                elif exchange == 'kraken':
                    # Kraken uses different symbol format
                    kraken_symbol = f"X{symbol}ZUSD"
                    url = f"{self.exchanges[exchange]}?pair={kraken_symbol}"
                    async with session.get(url) as response:
                        data = await response.json()
                        pair_data = list(data['result'].values())[0]
                        price = float(pair_data['c'][0])  # Last trade price
                
                self.last_update_times[exchange] = datetime.now()
                
                return {
                    'exchange': exchange,
                    'price': price,
                    'timestamp': datetime.now().isoformat(),
                    'success': True
                }
                
        except Exception as e:
            logger.error(f"Error fetching from {exchange}: {e}")
            return {
                'exchange': exchange,
                'price': None,
                'timestamp': datetime.now().isoformat(),
                'success': False,
                'error': str(e)
            }
    
    async def fetch_all_prices(self, symbol: str) -> Dict[str, Dict]:
        """Fetch prices from all exchanges simultaneously"""
        tasks = [
            self.fetch_price(exchange, symbol)
            for exchange in self.exchanges.keys()
        ]
        results = await asyncio.gather(*tasks)
        
        return {r['exchange']: r for r in results}
    
    def calculate_price_spread(self, prices: Dict[str, Dict]) -> Dict:
        """
        Calculate spread across exchanges
        
        Returns:
            {
                'spread_percent': float,
                'max_price': float,
                'min_price': float,
                'avg_price': float,
                'risk_level': str
            }
        """
        valid_prices = [
            p['price'] for p in prices.values() 
            if p['success'] and p['price']
        ]
        
        if len(valid_prices) < 2:
            return {
                'spread_percent': 0,
                'risk_level': 'HIGH',
                'explanation': 'Insufficient price data'
            }
        
        max_price = max(valid_prices)
        min_price = min(valid_prices)
        avg_price = sum(valid_prices) / len(valid_prices)
        
        spread_percent = ((max_price - min_price) / avg_price) * 100
        
        # Determine risk level
        if spread_percent > 2.0:
            risk_level = 'HIGH'
            risk_code = 'FD01'
        elif spread_percent > 0.5:
            risk_level = 'MEDIUM'
            risk_code = 'FD01'
        else:
            risk_level = 'LOW'
            risk_code = None
        
        return {
            'spread_percent': round(spread_percent, 3),
            'max_price': max_price,
            'min_price': min_price,
            'avg_price': avg_price,
            'risk_level': risk_level,
            'risk_code': risk_code
        }
    
    def update_trust_scores(self, prices: Dict[str, Dict]) -> Dict[str, float]:
        """
        Update trust scores based on feed quality
        
        Factors:
        - Feed delay
        - Price outliers
        - Connection stability
        """
        now = datetime.now()
        
        for exchange, data in prices.items():
            current_trust = self.trust_scores[exchange]
            
            # Penalty for failed fetch
            if not data['success']:
                current_trust *= 0.5
                logger.warning(f"{exchange} feed failed, trust: {current_trust}")
            
            # Penalty for delayed feed
            if exchange in self.last_update_times:
                delay = (now - self.last_update_times[exchange]).total_seconds()
                if delay > 10:
                    current_trust *= 0.7
                    logger.warning(
                        f"{exchange} feed delayed by {delay}s, trust: {current_trust}"
                    )
            
            # Price outlier detection
            if data['success'] and data['price']:
                all_prices = [
                    p['price'] for p in prices.values() 
                    if p['success'] and p['price']
                ]
                if len(all_prices) > 1:
                    avg = sum(all_prices) / len(all_prices)
                    deviation = abs(data['price'] - avg) / avg
                    
                    if deviation > 0.05:  # 5% deviation
                        current_trust *= 0.6
                        logger.warning(
                            f"{exchange} price outlier detected, trust: {current_trust}"
                        )
            
            self.trust_scores[exchange] = max(0.1, current_trust)  # Floor at 0.1
        
        return self.trust_scores
    
    def get_risk_factors(self, prices: Dict[str, Dict], spread: Dict) -> List[Dict]:
        """
        Generate list of active risk factors
        """
        risk_factors = []
        now = datetime.now()
        
        # Check for delayed feeds
        for exchange, last_update in self.last_update_times.items():
            delay = (now - last_update).total_seconds()
            if delay > 10:
                risk_factors.append({
                    'code': 'FD04',
                    'severity': 'MEDIUM' if delay < 30 else 'HIGH',
                    'message': f"{exchange.capitalize()} feed delayed by {int(delay)} seconds"
                })
        
        # Check price spread
        if spread['risk_code']:
            risk_factors.append({
                'code': spread['risk_code'],
                'severity': spread['risk_level'],
                'message': f"{spread['spread_percent']:.2f}% price spread across exchanges"
            })
        
        # Check for failed feeds
        for exchange, data in prices.items():
            if not data['success']:
                risk_factors.append({
                    'code': 'FD03',
                    'severity': 'HIGH',
                    'message': f"{exchange.capitalize()} feed connection failed"
                })
        
        return risk_factors