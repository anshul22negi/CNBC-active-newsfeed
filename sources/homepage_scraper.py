import requests
from bs4 import BeautifulSoup
from sources.base_source import BaseSource
import undetected_chromedriver as uc
import os
import logging
import re
from datetime import datetime
import time
import feedparser


class HomepageScraperSource(BaseSource):
    """
    Scrapes the homepages of Reuters, AP News, and ANI News for latest headlines.
    """
    def __init__(self):
        self.sites = [
            # {
            #     "name": "Reuters",
            #     "url": "https://www.reuters.com/",
            #     "parser": self.parse_reuters
            # },
            # {
            #     "name": "AP News",
            #     "url": "https://apnews.com/",
            #     "parser": self.parse_apnews
            # },
            # {
            #     "name": "ANI News",
            #     "url": "https://aninews.in/",
            #     "parser": self.parse_aninews
            # },
            {
                "name": "CNBC India",
                "url": "https://www.cnbc.com/india/",
                "parser": self.parse_cnbc_india
            },
            {
                "name": "CNBC World",
                "url": "https://www.cnbc.com/world/",
                "parser": self.parse_cnbc_world
            }
        ]
        # Set up logging
        if not os.path.exists('logs'):
            os.makedirs('logs')
        logging.basicConfig(filename='logs/homepage_scraper.log', level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')

    def extract_date_from_url(self, url, article_soup=None):
        # First, try to extract from <time data-testid="published-timestamp" datetime=...>
        if article_soup:
            time_tag = article_soup.find("time", attrs={"data-testid": "published-timestamp"})
            if time_tag and time_tag.get("datetime"):
                print(f"[DEBUG] Found published-timestamp in <time>: {time_tag['datetime']} for URL: {url}")
                return time_tag["datetime"]
            # Try meta tag
            meta = article_soup.find("meta", attrs={"name": "article:published_time"})
            if meta and meta.get("content"):
                print(f"[DEBUG] Found published-timestamp in <meta>: {meta['content']} for URL: {url}")
                return meta["content"]
        # Fallback: extract from URL
        match = re.search(r"/(20\d{2})/(\d{2})/(\d{2})/", url)
        if match:
            try:
                date_val = datetime.strptime("-".join(match.groups()), "%Y-%m-%d").isoformat()
                print(f"[DEBUG] Extracted date from URL: {date_val} for URL: {url}")
                return date_val
            except Exception as e:
                print(f"[DEBUG] Failed to parse date from URL: {url} with error: {e}")
                return None
        match = re.search(r"/(20\d{2})/(\d{2})/(\d{2})/[^/]+\.html", url)
        if match:
            try:
                date_val = datetime.strptime("-".join(match.groups()), "%Y-%m-%d").isoformat()
                print(f"[DEBUG] Extracted date from URL (html): {date_val} for URL: {url}")
                return date_val
            except Exception as e:
                print(f"[DEBUG] Failed to parse date from URL (html): {url} with error: {e}")
                return None
        print(f"[DEBUG] No date found for URL: {url}")
        return None

    def fetch_cnbc_rss_india(self):
        url = "https://www.cnbc.com/id/20910258/device/rss/rss.html"  # CNBC India RSS
        feed = feedparser.parse(url)
        articles = []
        for entry in feed.entries:
            articles.append({
                "title": entry.get("title"),
                "url": entry.get("link"),
                "last_updated": entry.get("published") or entry.get("updated")
            })
        return articles

    def fetch_cnbc_rss_world(self):
        url = "https://www.cnbc.com/id/100727362/device/rss/rss.html"  # CNBC World RSS
        feed = feedparser.parse(url)
        articles = []
        for entry in feed.entries:
            articles.append({
                "title": entry.get("title"),
                "url": entry.get("link"),
                "last_updated": entry.get("published") or entry.get("updated")
            })
        return articles

    def fetch_news(self):
        logging.info("Fetching headlines from CNBC India and CNBC World RSS feeds...")
        all_headlines = []
        # Comment out Selenium-based logic for CNBC
        # chrome_options = uc.ChromeOptions()
        # ...
        # for site in self.sites:
        #     ...
        # Instead, use RSS feeds
        all_headlines.extend(self.fetch_cnbc_rss_india())
        all_headlines.extend(self.fetch_cnbc_rss_world())
        return all_headlines

    def get_last_updated(self, url):
        try:
            resp = requests.head(url, timeout=10)
            last_modified = resp.headers.get("Last-Modified")
            if last_modified:
                return last_modified
            date = resp.headers.get("Date")
            if date:
                return date
        except Exception as e:
            logging.warning(f"Could not fetch last updated date for {url}: {e}")
        return None

    def parse_reuters(self, soup):
        # Reuters: headlines are in <a data-testid="Heading" ...>
        headlines = []
        for a in soup.find_all("a", attrs={"data-testid": "TitleLink"}):
            title = a.get_text(strip=True)
            url = a.get("href")
            if url and not url.startswith("http"):
                url = "https://www.reuters.com" + url
            if title and url:
                headlines.append({"title": title, "url": url})
        return headlines

    def parse_apnews(self, soup):
        # AP News: headlines are in <a class="Component-headline-...">
        headlines = []
        for a in soup.find_all("a", class_=lambda x: x and x.startswith("Component-headline-")):
            title = a.get_text(strip=True)
            url = a.get("href")
            if url and not url.startswith("http"):
                url = "https://apnews.com" + url
            if title and url:
                headlines.append({"title": title, "url": url})
        return headlines

    def parse_aninews(self, soup):
        # ANI News: headlines are in <a class="news-title" ...>
        headlines = []
        for a in soup.find_all("a", class_="news-title"):
            title = a.get_text(strip=True)
            url = a.get("href")
            if url and not url.startswith("http"):
                url = "https://aninews.in" + url
            if title and url:
                headlines.append({"title": title, "url": url})
        return headlines

    def parse_cnbc_india(self, soup):
        articles = []
        for a in soup.find_all("a", href=True):
            url = a["href"]
            if re.search(r"/20\d{2}/\d{2}/\d{2}/", url):
                title = a.get_text(strip=True)
                if not title:
                    continue
                try:
                    import requests
                    resp = requests.get(url if url.startswith("http") else f"https://www.cnbc.com{url}")
                    article_soup = BeautifulSoup(resp.text, "html.parser")
                except Exception:
                    article_soup = None
                last_updated = self.extract_date_from_url(url, article_soup)
                articles.append({"title": title, "url": url, "last_updated": last_updated})
        return articles

    def parse_cnbc_world(self, soup):
        articles = []
        for a in soup.find_all("a", href=True):
            url = a["href"]
            if re.search(r"/20\d{2}/\d{2}/\d{2}/", url):
                title = a.get_text(strip=True)
                if not title:
                    continue
                try:
                    import requests
                    resp = requests.get(url if url.startswith("http") else f"https://www.cnbc.com{url}")
                    article_soup = BeautifulSoup(resp.text, "html.parser")
                except Exception:
                    article_soup = None
                last_updated = self.extract_date_from_url(url, article_soup)
                articles.append({"title": title, "url": url, "last_updated": last_updated})
        return articles

    def test_proxy(self):
        response = requests.get(
            url='https://proxy.scrapeops.io/v1/',
            params={
                'api_key': 'YOUR_API_KEY',
                'url': 'https://www.reuters.com/',
                'bypass': 'cloudflare_level_1',
            },
        )
        print(response.content)

        cache_url = "http://webcache.googleusercontent.com/search?q=cache:https://www.reuters.com/"
        response = requests.get(cache_url) 
