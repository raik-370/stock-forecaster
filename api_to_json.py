#!/usr/bin/env python3
"""
This module fetches news articles for a list of stock tickers and saves them as JSON files.

The module reads a list of stock tickers from 'tickers.txt', fetches news articles for each ticker
using the Polygon API, and writes the articles to individual JSON files in the 'data/json' directory.

Functions:
    main: The main function that orchestrates reading tickers, fetching news articles, and writing them to files.

Usage:
    Run this module as a script to fetch news articles for the tickers listed in 'tickers.txt' and save them as JSON files.
"""
import json

from polygon import get_ticker_news


if __name__ == '__main__':
    with open('tickers.txt', 'r', encoding='utf-8') as tickers:
        for ticker in tickers:
            ticker = ticker.rstrip()
            with open(f'data/json/{ticker}.json', 'w') as f:
                articles = get_ticker_news(ticker, '2024-07-01')
                for article in articles:
                    f.write(f'{json.dumps(article)}\n')
