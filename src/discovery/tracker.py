import csv
from datetime import datetime
import json
import os
import time
from finvizfinance.quote import finvizfinance
from finvizfinance.screener import Overview
import pandas as pd

from .discoverer import SP500Discoverer   # Changed from relative to absolute import   

class SP500RankingTracker:
    
    def __init__(self, data_file='sp500_tracking_data.json', top_n=50):
        self.data_file = data_file
        self.discoverer = SP500Discoverer(top_n=top_n)
        self.historical_data = self.load_historical_data()



    def run_analysis(self, export_csv=True):
        """Run the complete analysis"""
        print("🎯 Starting S&P 500 Ranking Analysis...")
        print(f"📅 Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        current_data = self.discoverer.collect_current_data()
        
        if not current_data:
            print("❌ No data collected. Exiting.")
            return
        
        current_rankings = self.discoverer.calculate_rankings(current_data)
        
        print(f"\n📊 Successfully ranked {len(current_rankings)} companies")
        
        ranking_changes = self.analyze_ranking_changes(current_rankings)
        
        self.generate_report(ranking_changes)
        
        if export_csv and ranking_changes:
            self.export_to_csv(ranking_changes)
        
        print(f"\n✅ Analysis complete! Next analysis recommended in 15 days.")
        
        return ranking_changes
    
    # def collect_current_data(self):
    #     """Collect current market data for top 50 companies by market cap"""
    #     if self.top_50_symbols is None:
    #         print("🔄 First time run - determining top 50 companies by market cap...")
    #         self.collect_market_cap_data()
        
    #     current_data = {}
    #     failed_symbols = []
        
    #     print(f"🔍 Collecting detailed data for top {len(self.top_50_symbols)} companies...")
        
    #     for i, symbol in enumerate(self.top_50_symbols):
    #         try:
    #             stock = finvizfinance(symbol)
    #             fundamentals = stock.ticker_fundament()
                
    #             market_cap_str = fundamentals.get('Market Cap', 'N/A')
    #             market_cap_numeric = self.get_market_cap_value(market_cap_str)
                
    #             current_data[symbol] = {
    #                 'company': fundamentals.get('Company', 'N/A'),
    #                 'market_cap_str': market_cap_str,
    #                 'market_cap_numeric': market_cap_numeric,
    #                 'price': fundamentals.get('Price', 'N/A'),
    #                 'perf_ytd': fundamentals.get('Perf YTD', 'N/A'),
    #                 'perf_year': fundamentals.get('Perf Year', 'N/A'),
    #                 'perf_3y': fundamentals.get('Perf 3Y', 'N/A'),
    #                 'sector': fundamentals.get('Sector', 'N/A'),
    #                 'industry': fundamentals.get('Industry', 'N/A'),
    #                 'pe_ratio': fundamentals.get('P/E', 'N/A'),
    #                 'roe': fundamentals.get('ROE', 'N/A')
    #             }
                
    #             if (i + 1) % 10 == 0:
    #                 print(f"  ✅ Processed {i + 1}/{len(self.top_50_symbols)} symbols")
                
    #             time.sleep(0.5)
                
    #         except Exception as e:
    #             failed_symbols.append(symbol)
    #             print(f"  ❌ Failed to get data for {symbol}: {str(e)}")
    #             continue
        
    #     if failed_symbols:
    #         print(f"⚠️  Failed to retrieve data for: {failed_symbols}")
        
    #     return current_data


    
    def load_historical_data(self):
        """Load historical tracking data from JSON file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    return json.load(f)
            except:
                print(f"Error loading {self.data_file}, starting fresh")
        return {}
    
    def save_historical_data(self):
        """Save historical data to JSON file"""
        with open(self.data_file, 'w') as f:
            json.dump(self.historical_data, f, indent=2)
    
    # def get_market_cap_value(self, market_cap_str):
    #     """Convert market cap string to numeric value for comparison"""
    #     if not market_cap_str or market_cap_str == 'N/A':
    #         return 0
        
    #     cap = market_cap_str.replace('$', '').replace(',', '')
        
    #     if 'T' in cap:
    #         return float(cap.replace('T', '')) * 1000
    #     elif 'B' in cap:
    #         return float(cap.replace('B', ''))
    #     elif 'M' in cap:
    #         return float(cap.replace('M', '')) / 1000
    #     else:
    #         try:
    #             return float(cap) / 1000000000
    #         except:
    #             return 0
    
    # def get_sp500_symbols(self):
    #     """Fetch current S&P 500 constituents from datahub.io"""
    #     try:
    #         print("📥 Fetching current S&P 500 constituents...")
    #         url = 'https://datahub.io/core/s-and-p-500-companies/_r/-/data/constituents.csv'
    #         sp500_data = pd.read_csv(url)
    #         symbol_data = sp500_data['Symbol'].tolist()
            
    #         cleaned_symbols = []
    #         for symbol in symbol_data:
    #             symbol = str(symbol).strip()
    #             if symbol == 'BRK.B':
    #                 symbol = 'BRK-B'
                
    #             if symbol == 'BF.B':
    #                 symbol = 'BP-B'
    #             cleaned_symbols.append(symbol)
            
    #         print(f"✅ Successfully fetched {len(cleaned_symbols)} S&P 500 symbols")
    #         return cleaned_symbols
            
    #     except Exception as e:
    #         print(f"❌ Error fetching S&P 500 constituents: {e}")
    #         print("🔄 Falling back to manual list of major companies...")
            
    #         return [
    #             'AAPL', 'MSFT', 'NVDA', 'AMZN', 'GOOGL', 'GOOG', 'META', 'TSLA', 
    #             'AVGO', 'BRK-B', 'WMT', 'JPM', 'LLY', 'V', 'UNH', 'ORCL', 'MA', 
    #             'XOM', 'NFLX', 'COST', 'HD', 'PG', 'JNJ', 'BAC', 'CRM', 'ABBV', 
    #             'CVX', 'KO', 'WFC', 'TMUS', 'MCD', 'ADBE', 'TMO', 'CSCO', 'PFE',
    #             'INTC', 'CMCSA', 'DIS', 'MRK', 'PEP', 'INTU', 'AMD', 'AXP', 'NOW',
    #             'NKE', 'QCOM', 'IBM', 'TXN', 'HON', 'UNP'
    #         ]
    
    # def collect_market_cap_data(self):
    #     """Collect market cap data for all S&P 500 companies to determine top 50"""
    #     print(f"🔍 Collecting market cap data for {len(self.sp500_symbols)} S&P 500 companies...")
    #     print("This may take a few minutes due to rate limiting...")
        
    #     market_cap_data = {}
    #     failed_symbols = []
        
    #     for i, symbol in enumerate(self.sp500_symbols):
    #         try:
    #             stock = finvizfinance(symbol)
    #             fundamentals = stock.ticker_fundament()
                
    #             market_cap_str = fundamentals.get('Market Cap', 'N/A')
    #             market_cap_numeric = self.get_market_cap_value(market_cap_str)
                
    #             if market_cap_numeric > 0:
    #                 market_cap_data[symbol] = {
    #                     'company': fundamentals.get('Company', 'N/A'),
    #                     'market_cap_str': market_cap_str,
    #                     'market_cap_numeric': market_cap_numeric,
    #                     'sector': fundamentals.get('Sector', 'N/A')
    #                 }
                
    #             if (i + 1) % 25 == 0:
    #                 print(f"  ✅ Processed {i + 1}/{len(self.sp500_symbols)} symbols "
    #                       f"({len(market_cap_data)} valid)")
                
    #             time.sleep(0.8)
                
    #         except Exception as e:
    #             failed_symbols.append(symbol)
    #             print(f"  ❌ Failed: {symbol} - {str(e)}")
    #             continue
        
    #     print(f"\n📊 Successfully collected data for {len(market_cap_data)} companies")
    #     if failed_symbols:
    #         print(f"⚠️  Failed symbols ({len(failed_symbols)}): {failed_symbols[:10]}{'...' if len(failed_symbols) > 10 else ''}")
        
    #     sorted_companies = sorted(market_cap_data.items(), 
    #                             key=lambda x: x[1]['market_cap_numeric'], 
    #                             reverse=True)
        
    #     top_companies = sorted_companies[:self.top_n]
    #     self.top_50_symbols = [symbol for symbol, _ in top_companies]
        
    #     print(f"\n🏆 Selected TOP {len(self.top_50_symbols)} companies by market cap:")
    #     print("-" * 70)
    #     for i, (symbol, data) in enumerate(top_companies[:10], 1):
    #         print(f"{i:2d}. {symbol:6s} - {data['company'][:35]:35s} {data['market_cap_str']:>10s}")
    #     if len(top_companies) > 10:
    #         print(f"    ... and {len(top_companies) - 10} more companies")
        
    #     return market_cap_data
    
    
    # def calculate_rankings(self, data):
    #     """Calculate rankings based on market cap"""
    #     valid_companies = {k: v for k, v in data.items() 
    #                       if v.get('market_cap_numeric', 0) > 0}
        
    #     sorted_companies = sorted(valid_companies.items(), 
    #                             key=lambda x: x[1]['market_cap_numeric'], 
    #                             reverse=True)
        
    #     rankings = {}
    #     for rank, (symbol, data) in enumerate(sorted_companies, 1):
    #         rankings[symbol] = {
    #             'rank': rank,
    #             'market_cap_numeric': data['market_cap_numeric'],
    #             'market_cap_str': data['market_cap_str'],
    #             'company': data['company']
    #         }
        
    #     return rankings
    
    def analyze_ranking_changes(self, current_rankings):
        """Analyze ranking changes from previous collection"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        self.historical_data[today] = {
            'rankings': current_rankings,
            'timestamp': datetime.now().isoformat()
        }
        
        comparison_date = None
        comparison_data = None
        
        for date_str in sorted(self.historical_data.keys(), reverse=True):
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            if (datetime.now() - date_obj).days >= 15:
                comparison_date = date_str
                comparison_data = self.historical_data[date_str]['rankings']
                break
        
        if not comparison_data:
            print("📅 No historical data from 15+ days ago. This will be the baseline.")
            self.save_historical_data()
            return []
        
        ranking_changes = []
        
        for symbol in current_rankings:
            current_rank = current_rankings[symbol]['rank']
            previous_rank = comparison_data.get(symbol, {}).get('rank', None)
            
            if previous_rank is not None:
                rank_change = previous_rank - current_rank
                
                if rank_change != 0:
                    current_cap = current_rankings[symbol]['market_cap_numeric']
                    previous_cap = comparison_data[symbol]['market_cap_numeric']
                    cap_change_pct = ((current_cap - previous_cap) / previous_cap) * 100
                    
                    ranking_changes.append({
                        'symbol': symbol,
                        'company': current_rankings[symbol]['company'],
                        'current_rank': current_rank,
                        'previous_rank': previous_rank,
                        'rank_change': rank_change,
                        'current_market_cap': current_rankings[symbol]['market_cap_str'],
                        'market_cap_change_pct': cap_change_pct,
                        'direction': 'UP' if rank_change > 0 else 'DOWN'
                    })
        
        ranking_changes.sort(key=lambda x: x['rank_change'], reverse=True)
        
        print(f"\n📊 Comparison with data from {comparison_date} ({(datetime.now() - datetime.strptime(comparison_date, '%Y-%m-%d')).days} days ago)")
        
        self.save_historical_data()
        return ranking_changes
    
    def generate_report(self, ranking_changes):
        """Generate and display the analysis report"""
        if not ranking_changes:
            print("No ranking changes to report.")
            return
        
        print("\n" + "="*80)
        print("🚀 S&P 500 RANKING MOVERS - BIGGEST INCREASES (Last 15+ Days)")
        print("="*80)
        
        top_movers_up = [change for change in ranking_changes if change['rank_change'] > 0][:10]
        
        if top_movers_up:
            print(f"\n📈 TOP {len(top_movers_up)} BIGGEST RANKING INCREASES:")
            print("-" * 80)
            
            for i, mover in enumerate(top_movers_up, 1):
                print(f"{i:2d}. {mover['symbol']:6s} - {mover['company'][:30]:30s}")
                print(f"     Rank: #{mover['previous_rank']:3d} → #{mover['current_rank']:3d} "
                      f"(+{mover['rank_change']:2d} positions)")
                print(f"     Market Cap: {mover['current_market_cap']:>10s} "
                      f"({mover['market_cap_change_pct']:+6.1f}%)")
                print()
        
        top_movers_down = [change for change in ranking_changes if change['rank_change'] < 0][:10]
        
        if top_movers_down:
            print(f"\n📉 TOP {len(top_movers_down)} BIGGEST RANKING DECREASES:")
            print("-" * 80)
            
            for i, mover in enumerate(top_movers_down, 1):
                print(f"{i:2d}. {mover['symbol']:6s} - {mover['company'][:30]:30s}")
                print(f"     Rank: #{mover['previous_rank']:3d} → #{mover['current_rank']:3d} "
                      f"({mover['rank_change']:3d} positions)")
                print(f"     Market Cap: {mover['current_market_cap']:>10s} "
                      f"({mover['market_cap_change_pct']:+6.1f}%)")
                print()
    
    def export_to_csv(self, ranking_changes, filename=None):
        """Export results to CSV file"""
        if not filename:
            filename = f"sp500_ranking_changes_{datetime.now().strftime('%Y%m%d')}.csv"
        
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['symbol', 'company', 'current_rank', 'previous_rank', 
                         'rank_change', 'direction', 'current_market_cap', 'market_cap_change_pct']
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for change in ranking_changes:
                writer.writerow(change)
        
        print(f"📁 Results exported to: {filename}")
    

def main():
    """Main function to run the tracker"""

    tracker = SP500RankingTracker(top_n=50)
    results = tracker.run_analysis(export_csv=True)
    return results

if __name__ == "__main__":
    main()