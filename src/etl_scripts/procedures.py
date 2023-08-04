# Import libraries
import pandas as pd
import numpy as np
import time
import datetime
from gnews import GNews
import nltk
from newspaper import Article

# ---------------------------------------------------------------- ******************************** ----------------------------------------------------------------
def fetch_daily_stock_articles(stock_code, n_days=2, max_articles=25):
    """
    Fetch daily stock articles based on the stock code and the number of days up to the current date.
    
    Args:
        stock_code (str): The stock code to search for news articles
        n_days (int): Fetch news from the past n days up to the current date
        max_articles (int): Max number of articles to fetch
    Returns:
        fetched_news_df (pandas.DataFrame): The DataFrame containing the retrieved news articles related to the stock code.
    """
    # Initialize GNews
    google_news = GNews(language='id', country="Indonesia", max_results=max_articles)
    
    # Get the current date and calculate the start date
    today = datetime.date.today()
    google_news.start_date = today - datetime.timedelta(days=n_days)
    google_news.end_date = today

    # Fetch the news articles from Google News
    news_items = google_news.get_news(f"{stock_code}")
    fetched_news_df = pd.DataFrame(news_items)
    
    # Initialize lists to store article full text and images
    full_texts = []
    image_urls = []

    # Iterate through each URL in the fetched news DataFrame
    for url in fetched_news_df["url"]:
        # Download and parse the article
        article = Article(url)
        
        try:
            article.download()
            article.parse()
            
            # Get the full text of the article
            full_text = article.text
            full_texts.append(full_text)
            
            # Get the first image from the article
            image = list(article.images)[0] if article.images else None
            image_urls.append(image)
            
        except Exception as e:
            print(f"Error when downloading and parsing article from {url}: {e}")
            # Add placeholder values for the article and image
            full_texts.append(f"Error when downloading and parsing article from {url}: {e}")
            image_urls.append(f"Error when downloading and parsing article from {url}: {e}")

        # Sleep to avoid getting blocked
        time.sleep(10)

    # Add the article full text and image URL to the DataFrame
    fetched_news_df["full_text"] = full_texts
    fetched_news_df["image_url"] = image_urls

    # Add the entity to the DataFrame
    fetched_news_df["entity"] = f"{stock_code}"

    return fetched_news_df

# ---------------------------------------------------------------- ******************************** ----------------------------------------------------------------
def cleaning_fetched_articles(df):
    """
    Clean up the dataframe that contains the fetched articles. This function will remove unnecessary characters from the 
    full text articles such as html tags, rename some columns, and also extract informations like date published and publisher name.

    Args:
        df (Pandas DataFrame): The dataframe that contains the fetched articles
    Returns:
        fetched_news_df (Pandas DataFrame): The cleaned dataframe
    """
    # Copy from the original dataframe
    fetched_news_df = df.copy()

    # Exclude the rows that contain error messages
    fetched_news_df = fetched_news_df[~fetched_news_df["full_text"].str.contains("Error when downloading and parsing article")]

    # Clean the full text column
    fetched_news_df["full_text"] = fetched_news_df["full_text"].replace("\n", "||", regex=True)
    fetched_news_df["full_text"] = fetched_news_df["full_text"].replace("\r", "||", regex=True)
    fetched_news_df["full_text"] = fetched_news_df["full_text"].replace(r"\\", "", regex=True)

    # Rename the columns, extrack publisher and published date
    fetched_news_df = fetched_news_df.rename(columns={"published date":"published_time"})
    fetched_news_df["source_publisher"] = fetched_news_df["publisher"].apply(lambda x: x["title"])

    fetched_news_df["published_time"] = pd.to_datetime(fetched_news_df["published_time"])
    fetched_news_df["published_date"] = fetched_news_df["published_time"].dt.date

    # Reorder the columns
    fetched_news_df = fetched_news_df[["entity", "source_publisher", "title", "full_text", "url","published_time", "published_date", "image_url"]]
    
    return fetched_news_df



# test call the functions
bbca_df = fetch_daily_stock_articles("BBCA", n_days=3, max_articles=5)
bbca_df_2 = cleaning_fetched_articles(bbca_df)
print(bbca_df_2)