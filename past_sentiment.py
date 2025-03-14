#!/usr/bin/env python3
"""
This module fetches news articles related to stocks from the Polygon.io API, processes the data, 
and saves it to CSV files. The main functionality includes:

- Reading stock ticker symbols from a file.
- Fetching news articles for each ticker symbol from the Polygon.io API.
- Extracting relevant information such as publication date, sentiment, and sentiment reasoning.
- Saving the extracted information to CSV files.

The module uses the `requests` library to make API calls and the `dotenv` library for API keys.

Functions:
    get_api_data(ticker: str, date: str) -> Tuple[List[str], str]:

Usage:
    Run the module as a script to fetch and save news data for tickers listed in 'tickers.txt'.
"""
from time import sleep
from polygon import get_ticker_news


if __name__ == '__main__':
    with open('tickers.txt', 'r', encoding='utf-8') as tickers:
        for ticker in tickers:
            ticker = ticker.rstrip()
            with open(f'data/{ticker}.tsv', 'w', encoding='utf-8') as f:
                f.write('ticker\tpublished_utc\tsentiment\tsentiment_reasoning\n')
                last_run_published_utc = '2024-07-01T00:00:00Z'
                while True:
                    api_lines, api_last_published_utc = get_ticker_news(ticker, last_run_published_utc)
                    f.write('\n'.join(api_lines))
                    sleep(12)
                    if api_last_published_utc == last_run_published_utc:
                        break
                    f.write('\n')
                    last_run_published_utc = api_last_published_utc
