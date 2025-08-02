# SimplifiCare Finance

A Python toolkit for financial market analysis and tracking, focusing on S&P 500 companies and market cap rankings.

## Features

- 📊 S&P 500 constituents tracking
- 💹 Market capitalization analysis
- 📈 Ranking changes monitoring
- 📑 Historical data tracking
- 📊 CSV export capabilities

## Installation

From TestPyPI:
```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple simplificare-finance
```

From PyPI (once published):
```bash
pip install simplificare-finance
```

## Dependencies

- Python >= 3.12
- pandas
- finvizfinance
- beautifulsoup4
- requests

## Quick Start

```python
from discovery.tracker import SP500RankingTracker
from discovery.discoverer import SP500Discoverer

# Initialize the tracker
tracker = SP500RankingTracker(top_n=50)

# Run analysis and export results
results = tracker.run_analysis(export_csv=True)
```

## Documentation

### Market Cap Tracking

The package monitors market capitalization changes for S&P 500 companies and tracks their relative rankings over time. It automatically saves historical data and compares changes over 15-day periods.

```python
# Example: Track top 50 companies with custom data file
tracker = sp500RankingTracker(
    data_file='custom_tracking_data.json',
    top_n=50,
    discoverer=sp500Discoverer()
)
results = tracker.run_analysis()
```

### Data Export

Results can be exported to CSV format for further analysis:

```python
tracker.export_to_csv(results, "sp500_rankings.csv")
```

## Development

To contribute to this project:

1. Clone the repository
2. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```
3. Run tests:
   ```bash
   pytest
   ```

## License

MIT License

## Author

SimplifiCare Team

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.


## Creating a new release

Learn how to create a new release on the <a href="https://packaging.python.org/guides/section-build-and-publish/" title="External link" target="_blank" rel="noopener">Python Packaging User Guide</a>
