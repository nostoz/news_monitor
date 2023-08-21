import feedparser
import pandas as pd
from dateutil import parser as timeparser
import json
import concurrent.futures

from utils import *
from sentiment_nlp import SentimentNLP
from db_wrapper import DBWrapper

class RSSFeedParser:

    def __init__(self, rss_feeds, keywords, nlp_pipe:SentimentNLP, db_wrapper:DBWrapper):
        """
        Initializes the RSSFeedParser.

        Args:
            rss_feeds (list): A list of dictionaries containing RSS feed information.
            keywords (list): A list of keyword dictionaries for sentiment analysis.
            nlp_pipe (SentimentNLP): An instance of SentimentNLP for sentiment analysis.
            db_wrapper (DBWrapper): An instance of DBWrapper for database operations.
        """
        self.logger = set_logger(name=__name__, log_file='rss_feed_parser.log', log_level='INFO')
        self.rss_feeds = rss_feeds
        self.keywords = keywords
        self.df_feeds = None
        self.nlp_pipe = nlp_pipe
        self.db_wrapper = db_wrapper

    def get_df_feeds(self, datetime_filter=None):
        """
        Retrieves filtered DataFrame feeds based on the specified datetime filter.

        Args:
            datetime_filter (datetime, optional): The datetime filter to apply. Defaults to None.

        Returns:
            pandas.DataFrame: The filtered DataFrame feeds.
        """
        if datetime_filter:
            return self.df_feeds[self.df_feeds['timestamp'] >= datetime_filter.timestamp()]
        return self.df_feeds

    @timeit
    def _parse_and_analyze_single_rss_feed(self, rss_feed, dump_json=False, datetime_filter=None, known_articles_ids=[]):
        """
        Parses and analyzes a single RSS feed for news alerts.

        Args:
            rss_feed (dict): The dictionary containing RSS feed information.
            dump_json (bool, optional): Whether to dump feed data to JSON. Defaults to False.
            datetime_filter (datetime, optional): The datetime filter to exclude older news. Defaults to None.
            known_articles_ids (list, optional): List of known article IDs. Defaults to an empty list.

        Returns:
            pandas.DataFrame: The DataFrame containing parsed news alerts.
        """
        df_feed = pd.DataFrame(columns=["id", "timestamp", "datetime", "title", "summary",\
                                         "source", "rss_feed_weight", "keyword", "keyword_weight", \
                                            "sentiment_score", "sentiment_label", "custom_score"])
        feed = None
        try:
            feed = feedparser.parse(rss_feed['url'])
        except Exception as e:
            self.logger.error(f"feedparser failed on url : {rss_feed['url']} with exception:\n{e}")
        
        if feed:
            if dump_json == True:
                with open(f"{rss_feed['name']}.json", 'w') as fp:
                    json.dump(feed, fp)
            
            for item in feed.entries:
                datetime_published = timeparser.parse(item.published)

                # skip news olrder than datetime_filter
                if (datetime_filter and datetime_published < datetime_filter) or item.id in known_articles_ids:
                    continue

                summary = item.summary if 'summary' in item.keys() else ''
                df_feed.loc[df_feed.shape[0]] = {
                    "id": item.id,
                    "timestamp": int(datetime_published.timestamp()),
                    "datetime": item.published,
                    "title": item.title,
                    "summary": summary,
                    "source": item.link,
                    "rss_feed_weight": rss_feed['weight']
                }
            
            df_feed = self.nlp_pipe.get_sentiment(self.keywords, df_feed.reset_index(drop=True))

        return df_feed
    
    @timeit
    def parse_and_analyze_rss_feeds(self, dump_json=False, save_to_db=True, datetime_filter=None, exclude_known_articles=True):
        """
        Parses and analyzes all RSS feeds for news alerts.

        Args:
            dump_json (bool, optional): Whether to dump feed data to JSON. Defaults to False.
            save_to_db (bool, optional): Whether to save results to the database. Defaults to True.
            datetime_filter (datetime, optional): The datetime filter to exclude older news. Defaults to None.
            exclude_known_articles (bool, optional): Whether to exclude known articles. Defaults to True.

        Returns:
            pandas.DataFrame: The DataFrame containing parsed and analyzed news alerts.
        """
        if exclude_known_articles:
            known_articles_ids = self.db_wrapper.get_article_ids_from_db()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(self._parse_and_analyze_single_rss_feed, rss_feed, dump_json, datetime_filter, known_articles_ids)\
                        for rss_feed in self.rss_feeds]
            concurrent.futures.wait(futures)
            self.df_feeds = pd.concat([future.result() for future in futures])

            if save_to_db :
                self.db_wrapper.save_to_db(self.df_feeds, table_name="rss_feeds", if_exists='append', index=False)

        return self.df_feeds

