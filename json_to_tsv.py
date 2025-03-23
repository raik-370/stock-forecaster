#!/usr/bin/env python3
"""
This script reads ticker symbols from a file, processes corresponding JSON files containing articles,
and writes the processed data to TSV files.

The script performs the following steps:
1. Reads ticker symbols from 'tickers.txt'.
2. For each ticker symbol, reads the corresponding JSON file from the 'data/json/' directory.
3. Parses each article in the JSON file using the `parse_ticker_article` function from the `polygon` module.
4. Writes the parsed data to a TSV file in the 'data/tsv/' directory.

The output TSV file contains the following columns:
- ticker
- published_utc
- publisher
- title
- sentiment
- sentiment_reasoning

Arguments:
    -t, --skip-threshold: If the ticker's JSON file has fewer entries than this threshold, it will be skipped.

Usage:
    python json_to_tsv.py
"""
import argparse
import json

from polygon import parse_ticker_article

if __name__ == '__main__':
    parser = argparse.ArgumentParser('json_to_tsv')
    parser.add_argument('-t', '--skip-threshold', help="If ticker's json file has less than this many entries skip it", type=int)
    args = parser.parse_args()
    
    with open('tickers.txt', 'r', encoding='utf-8') as tickers:
        for ticker in tickers:
            ticker = ticker.rstrip()
            with open(f'data/json/{ticker}.json', 'r') as articles:
                articles_count = len(articles.readlines())
                if args.skip_threshold and articles_count < args.skip_threshold:
                    print(f'Skipping ${ticker} since it only has {articles_count} articles')
                    continue
                print(f'Processing ${ticker}')
                    
                with open(f'data/tsv/{ticker}.tsv', 'w', encoding='utf-8') as f:
                    f.write('ticker\tpublished_utc\tpublisher\ttitle\tsentiment\tsentiment_reasoning\n')
                    
                    for article in articles:
                        line = parse_ticker_article(ticker, json.loads(article))
                        if line:
                            f.write(line)
