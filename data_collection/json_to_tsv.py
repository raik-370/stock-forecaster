#!/usr/bin/env python3
"""
This script processes JSON files containing stock-related articles and trade data for a list of ticker symbols,
and converts the data into TSV (Tab-Separated Values) format.

The script performs the following steps:
1. Reads ticker symbols from 'tickers.txt'.
2. For each ticker symbol:
    a. Reads the corresponding JSON file from the 'data/news/json/' directory.
    b. Parses each article in the JSON file using the `parse_ticker_article` function from the `polygon` module.
    c. Writes the parsed article data to a TSV file in the 'data/news/tsv/' directory.
    d. Reads the corresponding JSON file from the 'data/trades/json/' directory.
    e. Parses each trade in the JSON file using the `parse_ticker_trade` function from the `polygon` module.
    f. Writes the parsed trade data to a TSV file in the 'data/trades/tsv/' directory.

The output TSV files contain the following columns:
- For articles:
  - ticker
  - published_utc
  - publisher
  - title
  - sentiment
  - sentiment_reasoning
- For trades:
  - ticker
  - date
  - open
  - high
  - low
  - close
  - volume
  - volume_weighted
  - trades

Arguments:
     -s, --stock-data: Flag to indicate whether to process stock data.
     -t, --skip-threshold: If the ticker's JSON file has fewer entries than this threshold, it will be skipped.

Usage:
     python json_to_tsv.py [options]
"""
import argparse
import json

from polygon import parse_ticker_article, parse_ticker_trade

# Github Copilot used for Docstrings, proofread by Blaine Traudt

if __name__ == '__main__':
    parser = argparse.ArgumentParser('json_to_tsv')
    parser.add_argument('-s', '--stock-data', help="Whether to convert stock data or not", action='store_true')
    parser.add_argument('-t', '--skip-threshold', help="If ticker's json file has less than this many entries skip it", type=int)
    args = parser.parse_args()

    with open('tickers.txt', 'r', encoding='utf-8') as tickers:
        for ticker in tickers:
            ticker = ticker.rstrip()
            with open(f'data/news/json/{ticker}.json', 'r', encoding='utf-8') as articles:
                articles_lines = articles.readlines()
                articles_count = len(articles_lines)
                if args.skip_threshold and articles_count < args.skip_threshold:
                    print(f'Skipping ${ticker} since it only has {articles_count} articles')
                    continue
                print(f'Processing ${ticker}')

                with open(f'data/news/tsv/{ticker}.tsv', 'w', encoding='utf-8') as f:
                    f.write('ticker\tpublished_utc\tpublisher\ttitle\tsentiment\tsentiment_reasoning\n')

                    for article in articles_lines:
                        line = parse_ticker_article(ticker, json.loads(article))
                        if line:
                            f.write(line)

                with open(f'data/trades/json/{ticker}.json', 'r', encoding='utf-8') as trades:
                    with open(f'data/trades/tsv/{ticker}.tsv', 'w', encoding='utf-8') as f:
                        f.write('ticker\tdate\topen\thigh\tlow\tclose\tvolume\tvolume_weighted\ttrades\n')

                        trades_lines = trades.readlines()

                        for trade in trades_lines:
                            line = parse_ticker_trade(ticker, json.loads(trade))
                            if line:
                                f.write(line)
