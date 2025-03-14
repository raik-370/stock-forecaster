#!/usr/bin/env python3
"""
This module provides functionality to interact with the Polygon.io API to fetch and parse news articles related to a specific stock ticker.

Functions:
    polygon_request(url: str) -> Response:
        Sends a GET request to the given URL with an API key and handles rate limiting.

    get_ticker_news(ticker: str, date: str) -> List[dict]:
        Fetches news articles for a specific ticker symbol published after a given date.

    parse_ticker_news(ticker: str, articles: dict) -> List[str]:
        Parses the fetched news articles to extract relevant information such as publication date, sentiment, and sentiment reasoning.
"""
from time import sleep
from typing import List

from dotenv import dotenv_values
import requests
from requests import Response

API_KEY = dotenv_values('.env').get('API_KEY')

# Github Copilot used for Docstrings, proofread by Blaine Traudt

def polygon_request(url: str) -> Response:
    """
    Sends a GET request to the specified URL with an API key and handles rate limiting.
    Args:
        url (str): The URL to send the GET request to.
    Returns:
        Response: The response object from the GET request.
    Raises:
        requests.exceptions.RequestException: If an error occurs during the request.
    """
    r = requests.get(f'{url}&apiKey={API_KEY}', timeout=12)
    # Rate limiting logic
    if r.status_code != 200:
        if r.status_code == 429:
            sleep(12)
        return polygon_request(url)
    return r

def get_ticker_news(ticker: str, date: str) -> List[dict]:
    """
    Fetch news articles for a given ticker symbol from a specified date.
    This function sends a request to the Polygon API to retrieve news articles
    related to the provided ticker symbol that were published after the specified date.
    It handles pagination to gather all articles beyond the initial 1000 results.
    Args:
        ticker (str): The ticker symbol for which to fetch news articles.
        date (str): The date in 'YYYY-MM-DD' format to fetch articles published after.
    Returns:
        List[dict]: A list of dictionaries, each containing details of a news article.
    """
    BASE_URL = 'https://api.polygon.io/v2/reference/news?order=asc&limit=1000&sort=published_utc'
    url = f'{BASE_URL}&ticker={ticker}&published_utc.gt={date}'
    r = polygon_request(url)
    data = r.json()
    articles: list = data['results']
    # Gather articles past 1000
    try:
        while url:
            url = data['next_url']
            r = polygon_request(url)
            data = r.json()
            new_articles = data['results']
            articles += new_articles
            url = data['next_url']
    finally:
        return articles

def parse_ticker_article(ticker: str, article: str) -> str:
    """
    Parses an article dictionary to extract and format information related to a specific ticker.
    Args:
        ticker (str): The ticker symbol to look for in the article's insights.
        article (str): A dictionary containing article information, including publication details and insights.
    Returns:
        str: A formatted string containing the ticker, publication date, publisher name, title, sentiment, 
             and sentiment reasoning, separated by tabs. Returns None if the ticker is not found in the insights.
    """
    published_utc = article['published_utc']
    publisher = article['publisher']['name']
    title = article['title']
    sentiment = None
    sentiment_reasoning = ''
    try:
        insights = article['insights']
    except KeyError:
        return None
    for insight in insights:
        if insight['ticker'] == ticker:
            sentiment = insight['sentiment']
            sentiment_reasoning = insight['sentiment_reasoning'].replace('\t', '    ')
            break
    if sentiment:
        line = f'{ticker}\t{published_utc}\t{publisher}\t{title}\t{sentiment}\t{sentiment_reasoning}\n'
        return line
