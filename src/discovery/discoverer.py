import time
from finvizfinance.quote import finvizfinance
import pandas as pd


class SP500Discoverer:
    
    def __init__(self, top_n=50):
        self.description = "The S&P 500 is a stock market index that measures the stock performance of 500 large companies listed on stock exchanges in the United States."
        self.sp500_symbols = self.get_sp500_symbols()
        self.top_50_symbols = None

    def get_sp500_symbols(self):
        """Fetch current S&P 500 constituents from datahub.io"""
        try:
            print("📥 Fetching current S&P 500 constituents...")
            url = 'https://datahub.io/core/s-and-p-500-companies/_r/-/data/constituents.csv'
            sp500_data = pd.read_csv(url)
            symbol_data = sp500_data['Symbol'].tolist()
            
            cleaned_symbols = []
            for symbol in symbol_data:
                symbol = str(symbol).strip()
                if symbol == 'BRK.B':
                    symbol = 'BRK-B'
                
                if symbol == 'BF.B':
                    symbol = 'BP-B'
                cleaned_symbols.append(symbol)
            
            print(f"✅ Successfully fetched {len(cleaned_symbols)} S&P 500 symbols")
            return cleaned_symbols
            
        except Exception as e:
            print(f"❌ Error fetching S&P 500 constituents: {e}")
            print("🔄 Falling back to manual list of major companies...")
            
            return [
                'AAPL', 'MSFT', 'NVDA', 'AMZN', 'GOOGL', 'GOOG', 'META', 'TSLA', 
                'AVGO', 'BRK-B', 'WMT', 'JPM', 'LLY', 'V', 'UNH', 'ORCL', 'MA', 
                'XOM', 'NFLX', 'COST', 'HD', 'PG', 'JNJ', 'BAC', 'CRM', 'ABBV', 
                'CVX', 'KO', 'WFC', 'TMUS', 'MCD', 'ADBE', 'TMO', 'CSCO', 'PFE',
                'INTC', 'CMCSA', 'DIS', 'MRK', 'PEP', 'INTU', 'AMD', 'AXP', 'NOW',
                'NKE', 'QCOM', 'IBM', 'TXN', 'HON', 'UNP'
            ]
    
    def collect_market_cap_data(self):
        """Collect market cap data for all S&P 500 companies to determine top 50"""
        print(f"🔍 Collecting market cap data for {len(self.sp500_symbols)} S&P 500 companies...")
        print("This may take a few minutes due to rate limiting...")
        
        market_cap_data = {}
        failed_symbols = []
        
        for i, symbol in enumerate(self.sp500_symbols):
            try:
                stock = finvizfinance(symbol)
                fundamentals = stock.ticker_fundament()
                
                market_cap_str = fundamentals.get('Market Cap', 'N/A')
                market_cap_numeric = self.get_market_cap_value(market_cap_str)
                
                if market_cap_numeric > 0:
                    market_cap_data[symbol] = {
                        'company': fundamentals.get('Company', 'N/A'),
                        'market_cap_str': market_cap_str,
                        'market_cap_numeric': market_cap_numeric,
                        'sector': fundamentals.get('Sector', 'N/A')
                    }
                
                if (i + 1) % 25 == 0:
                    print(f"  ✅ Processed {i + 1}/{len(self.sp500_symbols)} symbols "
                          f"({len(market_cap_data)} valid)")
                
                time.sleep(0.8)
                
            except Exception as e:
                failed_symbols.append(symbol)
                print(f"  ❌ Failed: {symbol} - {str(e)}")
                continue
        
        print(f"\n📊 Successfully collected data for {len(market_cap_data)} companies")
        if failed_symbols:
            print(f"⚠️  Failed symbols ({len(failed_symbols)}): {failed_symbols[:10]}{'...' if len(failed_symbols) > 10 else ''}")
        
        sorted_companies = sorted(market_cap_data.items(), 
                                key=lambda x: x[1]['market_cap_numeric'], 
                                reverse=True)
        
        top_companies = sorted_companies[:self.top_n]
        self.top_50_symbols = [symbol for symbol, _ in top_companies]
        
        print(f"\n🏆 Selected TOP {len(self.top_50_symbols)} companies by market cap:")
        print("-" * 70)
        for i, (symbol, data) in enumerate(top_companies[:10], 1):
            print(f"{i:2d}. {symbol:6s} - {data['company'][:35]:35s} {data['market_cap_str']:>10s}")
        if len(top_companies) > 10:
            print(f"    ... and {len(top_companies) - 10} more companies")
        
        return market_cap_data

    def get_market_cap_value(self, market_cap_str):
        """Convert market cap string to numeric value for comparison"""
        if not market_cap_str or market_cap_str == 'N/A':
            return 0
        
        cap = market_cap_str.replace('$', '').replace(',', '')
        
        if 'T' in cap:
            return float(cap.replace('T', '')) * 1000
        elif 'B' in cap:
            return float(cap.replace('B', ''))
        elif 'M' in cap:
            return float(cap.replace('M', '')) / 1000
        else:
            try:
                return float(cap) / 1000000000
            except:
                return 0


    def collect_current_data(self):
        """Collect current market data for top 50 companies by market cap"""
        if self.top_50_symbols is None:
            print("🔄 First time run - determining top 50 companies by market cap...")
            self.collect_market_cap_data()
        
        current_data = {}
        failed_symbols = []
        
        print(f"🔍 Collecting detailed data for top {len(self.top_50_symbols)} companies...")
        
        for i, symbol in enumerate(self.top_50_symbols):
            try:
                stock = finvizfinance(symbol)
                fundamentals = stock.ticker_fundament()
                
                market_cap_str = fundamentals.get('Market Cap', 'N/A')
                market_cap_numeric = self.get_market_cap_value(market_cap_str)
                
                current_data[symbol] = {
                    'company': fundamentals.get('Company', 'N/A'),
                    'market_cap_str': market_cap_str,
                    'market_cap_numeric': market_cap_numeric,
                    'price': fundamentals.get('Price', 'N/A'),
                    'perf_ytd': fundamentals.get('Perf YTD', 'N/A'),
                    'perf_year': fundamentals.get('Perf Year', 'N/A'),
                    'perf_3y': fundamentals.get('Perf 3Y', 'N/A'),
                    'sector': fundamentals.get('Sector', 'N/A'),
                    'industry': fundamentals.get('Industry', 'N/A'),
                    'pe_ratio': fundamentals.get('P/E', 'N/A'),
                    'roe': fundamentals.get('ROE', 'N/A')
                }
                
                if (i + 1) % 10 == 0:
                    print(f"  ✅ Processed {i + 1}/{len(self.top_50_symbols)} symbols")
                
                time.sleep(0.5)
                
            except Exception as e:
                failed_symbols.append(symbol)
                print(f"  ❌ Failed to get data for {symbol}: {str(e)}")
                continue
        
        if failed_symbols:
            print(f"⚠️  Failed to retrieve data for: {failed_symbols}")
        
        return current_data
    
    def calculate_rankings(self, data):
        """Calculate rankings based on market cap"""
        valid_companies = {k: v for k, v in data.items() 
                          if v.get('market_cap_numeric', 0) > 0}
        
        sorted_companies = sorted(valid_companies.items(), 
                                key=lambda x: x[1]['market_cap_numeric'], 
                                reverse=True)
        
        rankings = {}
        for rank, (symbol, data) in enumerate(sorted_companies, 1):
            rankings[symbol] = {
                'rank': rank,
                'market_cap_numeric': data['market_cap_numeric'],
                'market_cap_str': data['market_cap_str'],
                'company': data['company']
            }
        
        return rankings

    
    def get_description(self):
        return self.description
    