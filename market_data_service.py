"""Real-time market data service using Binance API"""
import requests
from typing import Dict, List, Optional
from datetime import datetime
import time
import random


class MarketDataService:
    """Service to fetch real-time market data from Binance (with fallback)"""
    
    def __init__(self):
        # Try multiple endpoints
        self.endpoints = [
            "https://api.binance.us/api/v3",
        ]
        self.current_endpoint_index = 0
        self.symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"]
        self.cache = {}
        self.cache_timestamp = 0
        self.cache_duration = 10  # Cache for 10 seconds
        self.use_fallback = False
        
        # Realistic base prices for fallback
        self.base_prices = {
            "BTC": 67000.0,
            "ETH": 3500.0,
            "SOL": 170.0,
            "BNB": 600.0
        }
    
    def get_ticker(self, symbol: str) -> Optional[Dict]:
        """Get 24h ticker data for a symbol"""
        try:
            url = f"{self.base_url}/ticker/24hr"
            params = {"symbol": symbol}
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            return None
    
    def get_all_tickers(self) -> Dict[str, Dict]:
        """Get ticker data for all tracked symbols with caching and fallback"""
        current_time = time.time()
        
        # Return cached data if still valid
        if self.cache and (current_time - self.cache_timestamp) < self.cache_duration:
            return self.cache
        
        # Try to fetch real data if not using fallback
        if not self.use_fallback:
            result = self._try_fetch_real_data()
            if result:
                self.cache = result
                self.cache_timestamp = current_time
                return result
        
        # Use simulated realistic data as fallback
        return self._get_simulated_data()
    
    def get_current_prices(self) -> Dict[str, float]:
        """Get just the current prices for all symbols"""
        tickers = self.get_all_tickers()
        return {symbol: data['price'] for symbol, data in tickers.items()}
    
    def _try_fetch_real_data(self) -> Optional[Dict[str, Dict]]:
        """Try to fetch real data from Binance API"""
        # Try each endpoint
        for i in range(len(self.endpoints)):
            endpoint = self.endpoints[self.current_endpoint_index]
            try:
                url = f"{endpoint}/ticker/24hr"
                response = requests.get(url, timeout=5)
                response.raise_for_status()
                all_tickers = response.json()
                
                result = {}
                for ticker in all_tickers:
                    if ticker['symbol'] in self.symbols:
                        symbol_name = ticker['symbol'].replace('USDT', '')
                        result[symbol_name] = {
                            'symbol': symbol_name,
                            'price': float(ticker['lastPrice']),
                            'change': float(ticker['priceChange']),
                            'change_percent': float(ticker['priceChangePercent']),
                            'high': float(ticker['highPrice']),
                            'low': float(ticker['lowPrice']),
                            'volume': float(ticker['volume']),
                            'quote_volume': float(ticker['quoteVolume']),
                            'timestamp': datetime.now().isoformat(),
                            'source': 'binance'
                        }
                
                if result:
                    print(f"✅ Successfully fetched real data from {endpoint}")
                    return result
                    
            except Exception as e:
                print(f"⚠️  Failed to fetch from {endpoint}: {e}")
                # Try next endpoint
                self.current_endpoint_index = (self.current_endpoint_index + 1) % len(self.endpoints)
        
        # All endpoints failed
        print("⚠️  All Binance endpoints failed, using simulated data")
        self.use_fallback = True
        return None
    
    def _get_simulated_data(self) -> Dict[str, Dict]:
        """Generate realistic simulated market data"""
        result = {}
        
        for symbol in ["BTC", "ETH", "SOL", "BNB"]:
            # Simulate realistic price movements
            base_price = self.base_prices[symbol]
            # Random walk with slight trend
            price_change = random.uniform(-0.03, 0.03)  # ±3%
            current_price = base_price * (1 + price_change)
            
            # Update base price for next iteration (trending)
            self.base_prices[symbol] = current_price
            
            change_percent = price_change * 100
            
            result[symbol] = {
                'symbol': symbol,
                'price': current_price,
                'change': current_price * price_change,
                'change_percent': change_percent,
                'high': current_price * 1.05,
                'low': current_price * 0.95,
                'volume': random.uniform(10000, 50000),
                'quote_volume': current_price * random.uniform(10000, 50000),
                'timestamp': datetime.now().isoformat(),
                'source': 'simulated'
            }
        
        return result
    
    def format_for_display(self) -> List[Dict]:
        """Format market data for dashboard display"""
        tickers = self.get_all_tickers()
        formatted = []
        
        for symbol, data in tickers.items():
            formatted.append({
                'symbol': symbol,
                'price': data['price'],
                'change': data['change_percent'],
                'high': data['high'],
                'low': data['low'],
                'volume': data['volume'],
                'source': data.get('source', 'unknown')
            })
        
        return formatted
    
    def is_using_real_data(self) -> bool:
        """Check if service is using real Binance data"""
        return not self.use_fallback


# Global instance
_market_service = None

def get_market_service() -> MarketDataService:
    """Get or create global market data service instance"""
    global _market_service
    if _market_service is None:
        _market_service = MarketDataService()
    return _market_service


if __name__ == "__main__":
    # Test the service
    service = MarketDataService()
    print("Fetching real-time market data from Binance...")
    print("=" * 60)
    
    data = service.get_all_tickers()
    for symbol, info in data.items():
        print(f"\n{symbol}:")
        print(f"  Price: ${info['price']:,.2f}")
        print(f"  24h Change: {info['change_percent']:+.2f}%")
        print(f"  24h High: ${info['high']:,.2f}")
        print(f"  24h Low: ${info['low']:,.2f}")
        print(f"  24h Volume: {info['volume']:,.2f}")
