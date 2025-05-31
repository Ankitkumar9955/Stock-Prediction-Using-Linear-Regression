import requests
import os

# Use the API key directly (not recommended) or securely load from environment variables
API_KEY = "b8f649d415dc42e39f4a42efaca95180"  # Directly hardcoded (Replace if needed)
# API_KEY = os.getenv("NEWS_API_KEY")  # Recommended approach for security

def get_stock_news(stock_symbol):
    """Fetch the latest news for a given stock symbol."""
    url = f"https://newsapi.org/v2/everything?q={stock_symbol}&apiKey={API_KEY}"
    response = requests.get(url).json()

    if "articles" in response:
        return [article["title"] for article in response["articles"][:5]]
    else:
        return ["No news found or API limit exceeded."]
