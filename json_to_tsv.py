#!/usr/bin/env python3
"""
This script reads ticker symbols from a file, processes corresponding JSON files containing articles,
and writes the processed data to TSV files.

The script performs the following steps:
1. Reads ticker symbols from 'tickers.txt'.
2. For each ticker symbol, reads the corresponding JSON file from 'data/json/' directory.
3. Parses each article in the JSON file using the `parse_ticker_article` function from the `polygon` module.
4. Writes the parsed data to a TSV file in the 'data/tsv/' directory.

The output TSV file contains the following columns:
- ticker
- published_utc
- publisher
- title
- sentiment
- sentiment_reasoning

Usage:
    python json_to_tsv.py
"""
import json

from polygon import parse_ticker_article

if __name__ == '__main__':
    with open('tickers.txt', 'r', encoding='utf-8') as tickers:
        for ticker in tickers:
            ticker = ticker.rstrip()
            with open(f'data/json/{ticker}.json', 'r') as articles:
                with open(f'data/tsv/{ticker}.tsv', 'w', encoding='utf-8') as f:
                    f.write('ticker\tpublished_utc\tpublisher\ttitle\tsentiment\tsentiment_reasoning\n')
                    for article in articles:
                        line = parse_ticker_article(ticker, json.loads(article))
                        if line:
                            f.write(line)
