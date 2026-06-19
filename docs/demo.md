# IntelStock Demo

This file is a short walkthrough for reviewing the project quickly.

## What To Open

1. Launch the dashboard at `frontend/dashboard.py`.
2. Start on the `Home` page in the sidebar.
3. Visit `Overview`, `Stock Research`, `Sentiment`, `Portfolio`, and `AI Chat`.

## Suggested Demo Flow

1. Open the dashboard and show the shared sidebar navigation.
2. Highlight the main dashboard cards, ticker bar, and sector performance chart.
3. Go to `Stock Research` and search for `RELIANCE`, `TCS`, or `INFY`.
4. Show the AI analysis panel with summary, recommendation, catalyst, and support/resistance levels.
5. Open `AI Chat` and try one of these prompts:
   - `Analyze RELIANCE`
   - `Nifty outlook today`
   - `Top IT stocks to watch`
   - `HDFC near-term view`
6. Show the sentiment radar and the portfolio allocation page.

## Demo Points To Mention

- The sidebar is shared across pages and stays reopenable.
- The app is styled for a dark, market-terminal look.
- The research and chat pages now return structured insight data instead of generic placeholder text.
- The project includes a free hosting path through Streamlit Community Cloud.

## Quick Start Commands

```bash
python -m pip install -r requirements/base.txt
python -m streamlit run frontend/dashboard.py
```

If port `8501` is busy, run:

```bash
python -m streamlit run frontend/dashboard.py --server.port 8509
```