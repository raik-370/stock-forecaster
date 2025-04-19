#!/usr/bin/env python3
"""
This script fetches news articles and optionally stock data for a list of stock tickers, saving them as JSON files.

The script reads a list of stock tickers from 'tickers.txt', fetches news articles for each ticker
using the Polygon API, and writes the articles to individual JSON files in the 'data/news/json' directory.
If the `--stock-data` flag is provided, it also fetches stock price data and saves it to 'data/trades/json'.

Arguments:
    -v, --verbose: Output additional information to the console, such as skipped tickers.
    -e, --skip-empty: Skip tickers whose JSON files are empty.
    -n, --skip-new: Skip tickers whose JSON files do not already exist.
    -t, --skip-threshold: Skip tickers whose JSON files have fewer entries than the specified threshold.
    -s, --stock-data: Fetch and save stock price data for tickers with new articles.

Functions:
    main: The main function that orchestrates reading tickers, fetching news articles, fetching stock data (if enabled),
          and writing the results to files.

Usage:
    Run this script to fetch news articles (and optionally stock data) for the tickers listed in 'tickers.txt'.
    Example:
        ./api_to_json.py -vent 265 -s
"""
import argparse
from datetime import datetime
import json
from pathlib import Path

from polygon import get_ticker_news, get_ticker_prices

# Github Copilot used for Docstrings, proofread by Blaine Traudt

if __name__ == '__main__':
    parser = argparse.ArgumentParser('api_to_json')
    parser.add_argument('-v', '--verbose', help="If ticker is skipped, output that it was skipped to console", action='store_true')
    parser.add_argument('-e', '--skip-empty', help="If ticker's json file is empty skip checking the API", action='store_true')
    parser.add_argument('-n', '--skip-new', help="If ticker's json file doesn't already exist skip it", action='store_true')
    parser.add_argument('-t', '--skip-threshold', help="If ticker's json file has less than this many entries skip it", type=int)
    parser.add_argument('-s', '--stock-data', help="Whether to grab stock data or not for tickers with new articles", action='store_true')
    args = parser.parse_args()

    with open('tickers.txt', 'r', encoding='utf-8') as tickers:
        for ticker in tickers:
            ticker = ticker.rstrip()

            if args.skip_new:
                ticker_file = Path(f'data/news/json/{ticker}.json')
                if not ticker_file.is_file():
                    print(f'Skipping ${ticker} since it is new')

            with open(f'data/news/json/{ticker}.json', 'r+', encoding='utf-8') as news_file:
                INITIAL_UTC = '2024-07-01'
                published_utc = INITIAL_UTC
                lines = news_file.readlines()
                line_count = len(lines)
                # Update the file if it already has content and use news after the existing ones
                if args.skip_threshold is None or line_count >= args.skip_threshold:
                    if line_count > 0:
                        last_line = lines[-1]
                        last_json = json.loads(last_line)
                        published_utc = last_json['published_utc']
                elif args.skip_threshold:
                    if args.verbose:
                        print(f'Skipping ${ticker} since it only has {line_count} articles')
                    continue
                elif args.skip_empty:
                    if args.verbose:
                        print(f'Skipping ${ticker} since it is empty')
                    continue

                print(f'Querying Polygon for news on ${ticker}')
                articles = get_ticker_news(ticker, published_utc)

                # Stock data
                if args.stock_data:
                    with open(f'data/trades/json/{ticker}.json', 'w', encoding='utf8') as trades_file:
                        today = datetime.today().strftime('%Y-%m-%d')
                        stock_data = get_ticker_prices(ticker, INITIAL_UTC, today)
                        for day in stock_data:
                            trades_file.write(f'{json.dumps(day)}\n')

                articles_count = len(articles)
                if articles_count > 0:
                    print(f'Found {articles_count} new articles for ${ticker}')
                else:
                    print(f'No new news found for ${ticker}')
                    continue

                for article in articles:
                    news_file.write(f'{json.dumps(article)}\n')
