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
from typing import List, Tuple

import requests
from dotenv import dotenv_values

API_KEY = dotenv_values('.env').get('API_KEY')
BASE_URL = 'https://api.polygon.io/v2/reference/news?order=asc&limit=1000&sort=published_utc'

def get_api_data(ticker: str, date: str) -> Tuple[List[str], str]:
    """
    Fetches API data for a given ticker and date, processes the data, and returns relevant lines.
    Args:
        ticker (str): The stock ticker symbol to fetch data for.
        date (str): The date from which to start fetching data (in UTC format).
    Returns:
        Tuple[List[str], str]: A dictionary containing:
            - 'lines': A list of strings, each representing an article with the format 
              'ticker,published_utc,sentiment,sentiment_reasoning'.
            - 'last_published_utc': The UTC timestamp of the last published article.
    """
    url = f'{BASE_URL}&ticker={ticker}&published_utc.gt={date}&apiKey={API_KEY}'
    r = requests.get(url, timeout=12)
    if r.status_code != 200:
        if r.status_code == 429:
            sleep(12)
        return get_api_data(ticker, date)
    data = r.json()
    articles = data['results']
    lines = []
    last_published_utc = date
    for article in articles:
        published_utc = article['published_utc']
        last_published_utc = published_utc
        sentiment = None
        sentiment_reasoning = ''
        try:
            insights = article['insights']
        except KeyError:
            continue
        for insight in insights:
            if insight['ticker'] == ticker:
                sentiment = insight['sentiment']
                sentiment_reasoning = insight['sentiment_reasoning']
                break
        if sentiment:
            line = f'{ticker}\t{published_utc}\t{sentiment}\t{sentiment_reasoning}'
            lines.append(line)
    return (lines, last_published_utc)


if __name__ == '__main__':
    with open('tickers.txt', 'r', encoding='utf-8') as tickers:
        for ticker in tickers:
            ticker = ticker.rstrip()
            with open(f'data/{ticker}.tsv', 'w', encoding='utf-8') as f:
                f.write('ticker\tpublished_utc\tsentiment\tsentiment_reasoning\n')
                last_run_published_utc = '2024-07-01T00:00:00Z'
                while True:
                    api_lines, api_last_published_utc = get_api_data(ticker, last_run_published_utc)
                    f.write('\n'.join(api_lines))
                    sleep(12)
                    if api_last_published_utc == last_run_published_utc:
                        break
                    last_run_published_utc = api_last_published_utc
