import os
import concurrent.futures
import yfinance as yf
import pandas as pd
from textblob import TextBlob
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# Set up Chrome options globally
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")

# List of popular selectors to try for article text
SELECTORS = [
    "div.body.yf-tsvcyu",
    "div.article-body",
    "div#articleBody",
    "div#story-body",
    "article",
    "div.articleContent",
    "div.article__content",
]

def scrape_article_text(driver, url: str) -> str:
    """
    Use a provided Selenium webdriver instance to open the URL and scrape article text.
    Waits dynamically until one of the popular selectors returns an element with non-empty text.
    If dynamic waiting fails, fall back to BeautifulSoup with the same selectors,
    and, as a last resort, returns the text from all <p> tags.
    """
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 10)

        def element_present(drv):
            for selector in SELECTORS:
                try:
                    element = drv.find_element(By.CSS_SELECTOR, selector)
                    if element and element.text.strip():
                        return element
                except Exception:
                    continue
            return False

        element = wait.until(element_present)
        text = element.text
        if text.strip():
            return text
    except Exception as e:
        print(f"Dynamic wait failed for {url}: {e}")

    # Fallback using BeautifulSoup
    try:
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        for selector in SELECTORS:
            container = soup.select_one(selector)
            if container and container.get_text(strip=True):
                return container.get_text(separator="\n")
        # Last resort: return text from all <p> tags.
        paragraphs = soup.find_all("p")
        return "\n".join(p.get_text() for p in paragraphs)
    except Exception as e:
        print(f"Fallback scraping failed for {url}: {e}")
        return ""

def fetch_company_news(ticker: str) -> list:
    """
    Fetch news from yfinance for a given ticker.
    For each news item with an available URL, scrape additional text using a single Selenium driver instance.
    Extracts publication timestamp (pubDate) if available.
    Combines the headline, summary, and scraped text, computes sentiment, and adds a 'pubDate' column.
    """
    stock = yf.Ticker(ticker)
    news = stock.news
    if not news:
        print(f"No news found for {ticker}")
        return []

    # Create one Selenium driver instance per ticker to reuse across news items.
    driver = webdriver.Chrome(options=chrome_options)
    output = []
    try:
        for item in news:
            details = item.get("content", item)
            url = None
            if "canonicalUrl" in details and isinstance(details["canonicalUrl"], dict):
                url = details["canonicalUrl"].get("url")
            elif "clickThroughUrl" in details and isinstance(details["clickThroughUrl"], dict):
                url = details["clickThroughUrl"].get("url")
            else:
                url = details.get("link") or details.get("url") or details.get("previewUrl")

            additional_text = ""
            if url:
                additional_text = scrape_article_text(driver, url)
            else:
                print(f"No URL available for news item: {details}")

            headline = details.get("title", "")
            summary = details.get("summary", "")
            pub_date = details.get("pubDate", "")
            combined_text = "\n".join(part for part in [headline, summary, additional_text] if part)

            blob = TextBlob(combined_text)
            sentiment_polarity = blob.sentiment.polarity
            sentiment_subjectivity = blob.sentiment.subjectivity

            output_item = {
                "ticker": ticker,
                "headline": headline,
                "pubDate": pub_date,
                "full_text": combined_text,
                "sentiment_polarity": sentiment_polarity,
                "sentiment_subjectivity": sentiment_subjectivity,
                "url": url
            }
            output.append(output_item)
    except Exception as e:
        print(f"Error processing news for {ticker}: {e}")
    finally:
        driver.quit()
    return output

def load_company_tickers(filepath: str) -> list:
    df = pd.read_csv(filepath)
    return df['ticker'].tolist()

def save_news_to_csv(news_data: list, filepath: str):
    df_news = pd.DataFrame(news_data)
    df_news.to_csv(filepath, index=False)
    print(f"Historical news dataset saved to {filepath}")

def main():
    companies_filepath = os.path.join("../stock_model/data_extraction", "data", "companies.csv")
    output_filepath = os.path.join("../stock_model/data_extraction", "data", "historical_news.csv")

    tickers = load_company_tickers(companies_filepath)
    all_news = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        future_to_ticker = {executor.submit(fetch_company_news, ticker): ticker for ticker in tickers}
        for future in concurrent.futures.as_completed(future_to_ticker):
            ticker = future_to_ticker[future]
            try:
                news_items = future.result()
                all_news.extend(news_items)
                print(f"Fetched news for {ticker}")
            except Exception as exc:
                print(f"Ticker {ticker} generated an exception: {exc}")

    os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
    save_news_to_csv(all_news, output_filepath)

if __name__ == "__main__":
    main()
