# Buffett Value Scanner

Scans 37 quality stocks daily for Buffett-style value opportunities.

## Setup

1. **Create GitHub repo:**
   ```bash
   # Go to github.com/new and create: jlegrand90/buffett-scanner
   # Enable GitHub Pages: Settings → Pages → Source: main branch, folder: /docs
   ```

2. **Push code:**
   ```bash
   cd ~/.hermes/joshua/buffett-scanner
   git remote add origin git@github.com:jlegrand90/buffett-scanner.git
   git branch -M main
   git push -u origin main
   ```

3. **Enable GitHub Pages:**
   - Go to repo Settings → Pages
   - Source: `main` branch, folder: `/docs`
   - Save → wait 2-3 minutes for deployment

4. **Test locally:**
   ```bash
   cd ~/.hermes/joshua/buffett-scanner
   source venv/bin/activate
   python3 scanner.py
   ```

## Auto-Refresh (9 AM Daily)

```bash
# Add cron job
crontab -e

# Add this line:
0 9 * * * cd ~/.hermes/joshua/buffett-scanner && source venv/bin/activate && python3 scanner.py && git add docs/ && git commit -m "Daily scan $(date +\%Y-\%m-\%d)" && git push
```

## Criteria

- ROE > 15%
- P/E Ratio < 25
- Debt/Equity < 0.5
- Market Cap > $10B
- Positive Free Cash Flow

## Today's Output

- `docs/index.html` - Dashboard (GitHub Pages)
- `docs/data.json` - Raw data

---

Built for Joshua | 💙
