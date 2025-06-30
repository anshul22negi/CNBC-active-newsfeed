import os
from dotenv import load_dotenv

load_dotenv()

# News API configuration
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
# Comma-separated list of country codes (e.g., "us,gb").
# An empty string fetches global headlines. Defaults to global.
NEWS_API_COUNTRY = os.getenv("NEWS_API_COUNTRY", "")

# Twitter API configuration
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET_KEY = os.getenv("TWITTER_API_SECRET_KEY")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")

# List of verified Twitter accounts to follow
VERIFIED_TWITTER_ACCOUNTS = [
    "Reuters",
    "AP",
    "BBCBreaking"
]

# LLM API configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Time to wait between fetching new articles, in seconds
FETCH_INTERVAL = 30 
