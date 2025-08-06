import csv
from datetime import datetime
import json
import os


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