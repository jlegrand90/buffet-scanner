#!/usr/bin/env python3
"""
Buffett Value Scanner
Scans quality stocks for Buffett-style value opportunities.
Criteria: ROE > 15%, Debt/Equity < 0.5, P/E < 25, Market Cap > $10B, Positive FCF
"""

import json
import yfinance as yf
from datetime import datetime
from pathlib import Path

# Buffett-style quality stocks to scan (37 tickers)
STOCKS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "BRK.B", "JPM", "V", "JNJ",
    "UNH", "PG", "MA", "HD", "CVX", "MRK", "ABBV", "KO", "PEP",
    "COST", "WMT", "MCD", "DIS", "VZ", "T", "BAC", "WFC", "C",
    "GS", "MS", "BLK", "SPG", "O", "TGT", "LOW", "NKE", "SBUX",
    "INTC", "IBM"
]

def get_stock_data(ticker):
    """Fetch key metrics for a stock."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Get key metrics
        pe = info.get('trailingPE', None)
        roe = info.get('returnOnEquity', None)
        debt_equity = info.get('debtToEquity', None)
        market_cap = info.get('marketCap', None)
        fcf = info.get('freeCashflow', None)
        price = info.get('currentPrice', info.get('previousClose', None))
        name = info.get('shortName', ticker)
        
        # Convert ROE from decimal to percentage if needed
        if roe and roe < 1:
            roe = roe * 100
            
        return {
            'ticker': ticker,
            'name': name,
            'price': price,
            'pe': pe,
            'roe': roe,
            'debt_equity': debt_equity,
            'market_cap': market_cap,
            'fcf': fcf
        }
    except Exception as e:
        return None

def is_buffett_pick(data):
    """Check if stock meets Buffett criteria."""
    if not data:
        return False
    
    # Must have positive FCF
    if not data['fcf'] or data['fcf'] <= 0:
        return False
    
    # ROE > 15%
    if not data['roe'] or data['roe'] < 15:
        return False
    
    # P/E < 25 (value)
    if not data['pe'] or data['pe'] > 25:
        return False
    
    # Debt/Equity < 0.5 (low debt)
    if data['debt_equity'] and data['debt_equity'] > 50:  # yfinance returns as percentage
        return False
    
    # Market cap > $10B
    if not data['market_cap'] or data['market_cap'] < 10_000_000_000:
        return False
    
    return True

def scan_stocks():
    """Scan all stocks and return picks."""
    print(f"📊 Scanning {len(STOCKS)} stocks...")
    
    picks = []
    all_data = []
    
    for ticker in STOCKS:
        print(f"  Fetching {ticker}...")
        data = get_stock_data(ticker)
        if data:
            all_data.append(data)
            if is_buffett_pick(data):
                picks.append(data)
                print(f"    ✓ {ticker} - PICK!")
            else:
                print(f"    ✗ {ticker}")
    
    return picks, all_data

def generate_html(picks, all_data):
    """Generate GitHub Pages HTML."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # Sort picks by ROE (highest first)
    picks.sort(key=lambda x: x['roe'] or 0, reverse=True)
    
    picks_html = ""
    for pick in picks:
        picks_html += f"""
        <div class="card">
            <h3>{pick['ticker']}</h3>
            <p class="name">{pick['name']}</p>
            <div class="metric"><span class="label">Price</span><span class="value">${pick['price']:.2f}</span></div>
            <div class="metric"><span class="label">P/E</span><span class="value">{pick['pe']:.1f}</span></div>
            <div class="metric"><span class="label">ROE</span><span class="value">{pick['roe']:.1f}%</span></div>
            <div class="metric"><span class="label">D/E</span><span class="value">{pick['debt_equity']:.2f}</span></div>
            <div class="descriptors">
                <div class="descriptor"><span class="desc-label">Price</span><span class="desc-text">Current share price</span></div>
                <div class="descriptor"><span class="desc-label">P/E</span><span class="desc-text">Price-to-earnings ratio (value &lt; 25)</span></div>
                <div class="descriptor"><span class="desc-label">ROE</span><span class="desc-text">Return on equity (profitability &gt; 15%)</span></div>
                <div class="descriptor"><span class="desc-label">D/E</span><span class="desc-text">Debt-to-equity (low debt &lt; 0.5)</span></div>
            </div>
        </div>
        """
    
    if not picks:
        picks_html = "<p class='no-picks'>No picks today - market too expensive!</p>"
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Buffett Value Scanner</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            padding: 20px;
            color: #fff;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        header {{ 
            text-align: center; 
            padding: 40px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            margin-bottom: 40px;
        }}
        h1 {{ font-size: 2.5rem; margin-bottom: 10px; }}
        .subtitle {{ color: #8892b0; font-size: 1.1rem; }}
        .timestamp {{ color: #64ffda; font-size: 0.9rem; margin-top: 10px; }}
        .grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); 
            gap: 20px; 
        }}
        .card {{ 
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 12px;
            padding: 24px;
            transition: transform 0.2s, border-color 0.2s;
        }}
        .card:hover {{ 
            transform: translateY(-4px); 
            border-color: #64ffda;
        }}
        .card h3 {{ 
            font-size: 1.8rem; 
            color: #64ffda;
            margin-bottom: 8px;
        }}
        .card .name {{ 
            color: #8892b0; 
            font-size: 0.95rem; 
            margin-bottom: 16px;
            min-height: 40px;
        }}
        .metric {{ 
            display: flex; 
            justify-content: space-between; 
            padding: 8px 0;
            border-bottom: 1px solid rgba(255,255,255,0.05);
        }}
        .metric:last-child {{ border-bottom: none; }}
        .label {{ color: #8892b0; }}
        .value {{ color: #e6f1ff; font-weight: 600; }}
        .descriptors {{ 
            margin-top: 16px; 
            padding-top: 16px;
            border-top: 1px solid rgba(255,255,255,0.1);
        }}
        .descriptor {{ 
            margin-bottom: 8px; 
            font-size: 0.8rem;
        }}
        .descriptor:last-child {{ margin-bottom: 0; }}
        .desc-label {{ 
            color: #64ffda; 
            font-weight: 600;
            margin-right: 4px;
        }}
        .desc-text {{ color: #8892b0; font-size: 0.75rem; line-height: 1.3; }}
        .no-picks {{ 
            text-align: center; 
            padding: 60px 20px; 
            color: #8892b0;
            font-size: 1.2rem;
        }}
        .criteria {{ 
            background: rgba(100, 255, 218, 0.1);
            border: 1px solid rgba(100, 255, 218, 0.3);
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 30px;
        }}
        .criteria h2 {{ color: #64ffda; margin-bottom: 12px; font-size: 1.3rem; }}
        .criteria ul {{ 
            list-style: none; 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 8px;
        }}
        .criteria li {{ color: #8892b0; font-size: 0.9rem; }}
        .criteria li::before {{ content: "✓ "; color: #64ffda; }}
        .footer {{ 
            text-align: center; 
            padding: 40px 0; 
            color: #8892b0;
            font-size: 0.9rem;
        }}
        @media (max-width: 600px) {{
            h1 {{ font-size: 1.8rem; }}
            .grid {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📊 Buffett Value Scanner</h1>
            <p class="subtitle">Scanning 37 quality stocks for Buffett-style value opportunities</p>
            <p class="timestamp">Last updated: {timestamp}</p>
        </header>
        
        <div class="criteria">
            <h2>Screening Criteria</h2>
            <ul>
                <li>ROE > 15%</li>
                <li>P/E Ratio < 25</li>
                <li>Debt/Equity < 0.5</li>
                <li>Market Cap > $10B</li>
                <li>Positive Free Cash Flow</li>
            </ul>
        </div>
        
        <h2 style="margin-bottom: 20px; color: #64ffda;">Today's Picks ({len(picks)})</h2>
        <div class="grid">
            {picks_html}
        </div>
        
        <div class="footer">
            <p>Built for Joshua | Auto-refreshes daily at 9:00 AM</p>
        </div>
    </div>
</body>
</html>
"""
    return html

def main():
    """Main entry point."""
    output_dir = Path(__file__).parent / "docs"
    output_dir.mkdir(exist_ok=True)
    
    # Scan stocks
    picks, all_data = scan_stocks()
    
    print(f"\n📈 Found {len(picks)} Buffett-style picks")
    
    # Generate HTML
    html = generate_html(picks, all_data)
    
    # Save to docs folder (for GitHub Pages)
    output_path = output_dir / "index.html"
    output_path.write_text(html)
    
    # Also save JSON data
    data_path = output_dir / "data.json"
    data_path.write_text(json.dumps({
        'timestamp': datetime.now().isoformat(),
        'picks': picks,
        'all_data': all_data
    }, indent=2))
    
    print(f"✓ Generated: {output_path}")
    print(f"✓ Generated: {data_path}")
    
    # Print picks summary
    if picks:
        print(f"\n💙 Today's Picks: {', '.join([p['ticker'] for p in picks])}")
    else:
        print("\n⚠️  No picks today - market too expensive!")

if __name__ == "__main__":
    main()
