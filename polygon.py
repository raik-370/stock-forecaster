#!/usr/bin/env python3
"""
This module fetches news articles related to stocks from the Polygon.io API,
The module uses the `requests` library to make API calls and the `dotenv` library for API keys.

Functions:
    get_api_data(ticker: str, date: str) -> Tuple[List[str], str]:
"""
from time import sleep
from typing import List

import requests
from dotenv import dotenv_values

API_KEY = dotenv_values('.env').get('API_KEY')
BASE_URL = 'https://api.polygon.io/v2/reference/news?order=asc&limit=1000&sort=published_utc'

def get_ticker_news(ticker: str, date: str, articles: dict = {}) -> dict:
    url = f'{BASE_URL}&ticker={ticker}&published_utc.gt={date}&apiKey={API_KEY}'
    r = requests.get(url, timeout=12)
    if r.status_code != 200:
        if r.status_code == 429:
            sleep(12)
        return get_ticker_news(ticker, date)
    data = r.json()
    articles = data['results']
    count = data['count']
    if count < 1000:
        return articles
    return articles

def parse_ticker_news(ticker:str, articles: dict) -> List[str]:
    lines = []
    for article in articles:
        published_utc = article['published_utc']
        sentiment = None
        sentiment_reasoning = ''
        try:
            insights = article['insights']
        except KeyError:
            continue
        for insight in insights:
            if insight['ticker'] == ticker:
                sentiment = insight['sentiment']
                sentiment_reasoning = insight['sentiment_reasoning'].replace('\t', '   ')
                break
        if sentiment:
            line = f'{ticker}\t{published_utc}\t{sentiment}\t{sentiment_reasoning}'
            lines.append(line)
    return lines