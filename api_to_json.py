#!/usr/bin/env python3
"""
This module fetches news articles for a list of stock tickers and saves them as JSON files.

The module reads a list of stock tickers from 'tickers.txt', fetches news articles for each ticker
using the Polygon API, and writes the articles to individual JSON files in the 'data/json' directory.

Arguments:
    -e, --skip-empty: If specified, skip tickers whose JSON files are empty.
    -n, --skip-new: If specified, skip tickers whose JSON files do not already exist.
    -t, --skip-threshold: If specified, skip tickers whose JSON files have fewer entries than the given threshold.

Functions:
    main: The main function that orchestrates reading tickers, fetching news articles, and writing them to files.

Usage:
    Run this module as a script to fetch news articles for the tickers listed in 'tickers.txt' and save them as JSON files.
"""
import argparse
import json
from pathlib import Path

from polygon import get_ticker_news


if __name__ == '__main__':
    parser = argparse.ArgumentParser('api_to_json')
    parser.add_argument('-e', '--skip-empty', help="If ticker's json file is empty skip checking the API", action='store_true')
    parser.add_argument('-n', '--skip-new', help="If ticker's json file doesn't already exist skip it", action='store_true')
    parser.add_argument('-t', '--skip-threshold', help="If ticker's json file has less than this many entries skip it", type=int)
    args = parser.parse_args()
    
    with open('tickers.txt', 'r', encoding='utf-8') as tickers:
        for ticker in tickers:
            ticker = ticker.rstrip()
            
            if args.skip_new:
                ticker_json = Path(f'data/json/{ticker}.json')
                if not ticker_json.is_file():
                    print(f'Skipping ${ticker} since it is new')
            
            with open(f'data/json/{ticker}.json', 'r+') as f:
                published_utc = '2024-07-01'
                lines = f.readlines()
                line_count = len(lines)
                # Update the file if it already has content and use news after the existing ones
                if line_count >= args.skip_threshold:
                    last_line = lines[-1]
                    last_json = json.loads(last_line)
                    published_utc = last_json['published_utc']
                elif args.skip_threshold:
                    print(f'Skipping ${ticker} since it only has {line_count} articles')
                    continue
                elif args.skip_empty:
                    print(f'Skipping ${ticker} since it is empty')
                    continue
                
                print(f'Querying Polygon for news on ${ticker}')
                articles = get_ticker_news(ticker, published_utc)
                
                articles_count = len(articles)
                if articles_count > 0:
                    print(f'Found {articles_count} new articles for {ticker}')
                else:
                    print(f'No new news found for {ticker}')
                    continue
                
                for article in articles:
                    f.write(f'{json.dumps(article)}\n')
